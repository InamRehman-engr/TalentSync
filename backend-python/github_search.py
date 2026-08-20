"""
GitHub candidate search — clean rewrite.

Design goals
------------
* Single responsibility per function: parse, build, search, enrich, score are separate.
* No magic numbers: every constant is named and explained.
* Fix PyGithub PaginatedList slicing bug (iterate with a counter instead).
* Richer relevance signal: followers, total stars, language match, bio depth.
* Retry on transient 5xx before giving up.
* Progressive query plans with a clean early-exit.
* Typed throughout; dataclasses are immutable where mutation isn't needed.
"""

from __future__ import annotations

import logging
import math
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any

from github import Auth, Github, GithubException, RateLimitExceededException, BadCredentialsException

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GITHUB_PAT: str = os.getenv("GITHUB_PAT", "")

# Hard cap on results from any single GitHub search query.
_QUERY_PAGE_LIMIT = 8

# How many candidates we'll enrich (full profile fetch) at most.
_MAX_ENRICH = 10

# Seconds to wait before retrying a transient GitHub error.
_RETRY_DELAYS = (0.75,)  # one retry keeps latency bounded for synchronous UI searches

# GitHub "in:" is reserved syntax; these words break free-text queries when bare.
_SYNTAX_WORDS = frozenset(
    {"in", "at", "on", "the", "a", "an", "and", "or", "for", "with", "to", "of", "is"}
)

# ---------------------------------------------------------------------------
# Public exception
# ---------------------------------------------------------------------------


class GitHubSearchError(Exception):
    """Raised for unrecoverable search failures (bad PAT, hard rate-limit, etc.)."""

    def __init__(self, message: str, status_code: int = 503) -> None:
        super().__init__(message)
        self.status_code = status_code


# ---------------------------------------------------------------------------
# Intent parsing
# ---------------------------------------------------------------------------

# "backend engineer in Karachi" → role="backend engineer", location="Karachi"
_RE_ROLE_IN_LOC = re.compile(
    r"^(?P<role>.+?)\s+(?:in|near|from|based\s+in)\s+(?P<location>[A-Za-z][\w\s,\-'.]+)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SearchIntent:
    """Normalised, validated inputs — the single source of truth for a search."""

    role: str = ""
    location: str = ""
    skills: tuple[str, ...] = ()
    language: str = ""
    # All meaningful tokens for post-hoc relevance scoring (lower-cased, deduped).
    score_tokens: tuple[str, ...] = ()


def _clean_token(text: str) -> str:
    """Strip characters that confuse GitHub's query parser."""
    return re.sub(r'[^\w\s\-+.\']', " ", text).strip()


def _tokenize(text: str, *, drop_syntax_words: bool = True) -> list[str]:
    """
    Split cleaned text into meaningful tokens.

    We only drop syntax words when building free-text query strings, not when
    building score_tokens — 'Go' as a language should not be silently removed.
    """
    tokens = []
    for raw in _clean_token(text).split():
        tok = raw.strip(".,")
        if not tok:
            continue
        if drop_syntax_words and tok.lower() in _SYNTAX_WORDS:
            continue
        tokens.append(tok)
    return tokens


def _safe_text(text: str) -> str:
    return " ".join(_tokenize(text, drop_syntax_words=True))


def _split_list_field(text: str) -> list[str]:
    """'Python, FastAPI / Django' → ['Python', 'FastAPI', 'Django']"""
    return [
        tok
        for chunk in re.split(r"[,+/|;]+", text or "")
        if (tok := _safe_text(chunk))
    ]


def parse_intent(
    *,
    query: str = "",
    skill: str = "",
    location: str = "",
    language: str = "",
    project: str = "",
) -> SearchIntent:
    """
    Parse all caller-supplied strings into a single SearchIntent.

    Keeps concerns separated:
      1. Extract role/location from free-text query.
      2. Merge with explicit fields.
      3. Build score_tokens last (from the fully-resolved values).
    """
    # --- Step 1: extract role + optional location from free-text ---
    role_from_query = ""
    loc_from_query = ""
    if query.strip():
        m = _RE_ROLE_IN_LOC.match(query.strip())
        if m:
            role_from_query = _safe_text(m.group("role"))
            loc_from_query = m.group("location").strip(" .,")
        else:
            role_from_query = _safe_text(query)

    # --- Step 2: merge with explicit parameters (explicit wins) ---
    resolved_location = (location.strip(" .,") or loc_from_query).strip(" .,")
    resolved_language = (language or "").strip().lower()
    skills = tuple(_split_list_field(skill))
    projects = _split_list_field(project)

    # Role is the free-text query enriched by any skill/project hints.
    role_parts = list(dict.fromkeys(
        [p for p in [role_from_query] + list(skills) + projects if p]
    ))
    resolved_role = _safe_text(" ".join(role_parts))

    # --- Step 3: build score_tokens (no stop-word removal here) ---
    seen: set[str] = set()
    score_tokens: list[str] = []
    for source in (resolved_role, resolved_location, resolved_language, *skills, *projects):
        for tok in source.lower().split():
            if len(tok) >= 2 and tok not in seen:
                seen.add(tok)
                score_tokens.append(tok)

    return SearchIntent(
        role=resolved_role,
        location=resolved_location,
        skills=skills,
        language=resolved_language,
        score_tokens=tuple(score_tokens),
    )


# ---------------------------------------------------------------------------
# Query building
# ---------------------------------------------------------------------------


def _loc_qualifier(location: str) -> str:
    if not location:
        return ""
    return f'location:"{location.replace(chr(34), "")}"'


def _lang_qualifier(language: str) -> str:
    return f"language:{language}" if language else ""


def _qualifiers(intent: SearchIntent) -> str:
    parts = [_loc_qualifier(intent.location), _lang_qualifier(intent.language)]
    return " ".join(p for p in parts if p)


@dataclass(frozen=True)
class QueryPlan:
    """
    One search strategy.  Plans are tried in order (strict → loose) and we
    stop as soon as we have enough raw candidates.
    """
    label: str
    # Base score assigned to hits from this plan (before per-candidate adjustment).
    base_score: int
    user_queries: tuple[str, ...]
    repo_queries: tuple[str, ...] = ()


def _dedup(*items: str) -> tuple[str, ...]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        normalized = " ".join(item.split())
        if normalized and normalized not in seen:
            seen.add(normalized)
            out.append(normalized)
    return tuple(out)


def build_query_plans(intent: SearchIntent) -> list[QueryPlan]:
    """
    Return an ordered list of QueryPlans from most to least specific.

    Plans:
      1. role + location  (score 75) — tightest signal
      2. role only        (score 60) — widen geo
      3. skills/language  (score 48) — widen role
      4. location only    (score 40) — last resort
    """
    qual = _qualifiers(intent)
    role = intent.role
    loc_q = _loc_qualifier(intent.location)
    lang_q = _lang_qualifier(intent.language)

    plans: list[QueryPlan] = []

    # --- Plan 1: role + location ---
    if role and intent.location:
        first_word = role.split()[0]
        plans.append(QueryPlan(
            label="role+location",
            base_score=75,
            user_queries=_dedup(
                f'type:user "{role}" {qual}',
                f"type:user {role} {qual}",
                f"type:user {first_word} {qual}",
            ),
            repo_queries=_dedup(
                f'"{role}" {qual} stars:>0',
                f"{role} in:name,description {qual} stars:>0",
            ),
        ))

    # --- Plan 2: role only ---
    if role:
        bio_queries = [
            f'type:user "{role}" in:bio {lang_q}',
            f"type:user {role} in:bio {lang_q}",
        ]
        for sk in intent.skills[:2]:
            bio_queries.append(f"type:user {sk} in:bio {lang_q}")
        plans.append(QueryPlan(
            label="role",
            base_score=60,
            user_queries=_dedup(*bio_queries, f"type:user {role} {lang_q}"),
            repo_queries=_dedup(
                f"{role} stars:>0 {lang_q}",
                f"{role} in:name,description stars:>0 {lang_q}",
            ),
        ))

    # --- Plan 3: skills / language only ---
    if intent.skills or intent.language:
        skill_queries = [f"type:user {sk} in:bio {loc_q}" for sk in intent.skills[:3]]
        if intent.language:
            skill_queries.append(f"type:user {lang_q} {loc_q} repos:>2")
        plans.append(QueryPlan(
            label="skills",
            base_score=48,
            user_queries=_dedup(*skill_queries),
            repo_queries=_dedup(f"stars:>0 {lang_q} {loc_q}") if intent.language else (),
        ))

    # --- Plan 4: location only ---
    if intent.location:
        plans.append(QueryPlan(
            label="location",
            base_score=40,
            user_queries=_dedup(
                f"type:user {loc_q} repos:>2",
                f"type:user {loc_q} followers:>1",
            ),
        ))

    # --- Fallback ---
    if not plans:
        plans.append(QueryPlan(
            label="default",
            base_score=35,
            user_queries=("type:user repos:>5",),
            repo_queries=("stars:>10",),
        ))

    return plans


# ---------------------------------------------------------------------------
# Relevance scoring
# ---------------------------------------------------------------------------

# Weights for the composite relevance score (max 100).
_W_TOKEN_MATCH    = 8   # per matching score token found in profile text
_W_TOKEN_BONUS    = 6   # bonus when ≥3 tokens match (diverse signal)
_W_LOCATION_EXACT = 18  # profile.location contains the search location
_W_LOCATION_BIO   = 8   # location appears anywhere in bio/name but not location field
_W_ROLE_WORD      = 5   # per role word found (capped)
_W_FOLLOWER_LOG   = 6   # log-scaled follower score (community standing)
_W_STAR_LOG       = 6   # log-scaled total-stars score (output quality)
_W_LANGUAGE_MATCH = 8   # primary language matches search language


def _log_score(value: int, scale: int = 100) -> float:
    """Map a count to [0, 1] via log scale so outliers don't dominate."""
    if value <= 0:
        return 0.0
    return min(math.log1p(value) / math.log1p(scale), 1.0)


def relevance_score(
    *,
    login: str,
    bio: str,
    location_field: str,
    top_languages: list[str],
    repo_names: list[str],
    followers: int,
    total_stars: int,
    intent: SearchIntent,
    base_score: int,
) -> int:
    """
    Composite relevance score [0, 100].

    Inputs: GitHub profile metadata + the resolved SearchIntent.
    All string comparisons are case-insensitive.
    """
    haystack = " ".join(
        [login, bio, location_field, " ".join(top_languages), " ".join(repo_names)]
    ).lower()

    score = float(base_score)

    # Token matching
    matched = sum(1 for tok in intent.score_tokens if tok in haystack)
    score += matched * _W_TOKEN_MATCH
    if matched >= 3:
        score += _W_TOKEN_BONUS

    # Location signal
    loc_lower = intent.location.lower()
    if loc_lower and loc_lower in location_field.lower():
        score += _W_LOCATION_EXACT
    elif loc_lower and loc_lower in haystack:
        score += _W_LOCATION_BIO

    # Role word matching (capped to avoid runaway scores on long role strings)
    if intent.role:
        role_words = [
            w for w in intent.role.lower().split() if w not in _SYNTAX_WORDS and len(w) >= 2
        ]
        role_hits = sum(1 for w in role_words if w in haystack)
        score += min(role_hits * _W_ROLE_WORD, _W_ROLE_WORD * 4)

    # Community signal (followers, stars) — log-scaled so outliers don't distort
    score += _log_score(followers, scale=1_000) * _W_FOLLOWER_LOG
    score += _log_score(total_stars, scale=500) * _W_STAR_LOG

    # Language match
    if intent.language and intent.language in [lang.lower() for lang in top_languages]:
        score += _W_LANGUAGE_MATCH

    return min(round(score), 100)


# ---------------------------------------------------------------------------
# GitHub client & retry
# ---------------------------------------------------------------------------


def _get_client() -> Github:
    if not GITHUB_PAT:
        raise GitHubSearchError(
            "GITHUB_PAT is not set. Create a token at github.com/settings/tokens.",
            status_code=503,
        )
    if GITHUB_PAT.startswith("glpat-"):
        raise GitHubSearchError(
            "GITHUB_PAT looks like a GitLab token (glpat-…). GitHub tokens start with ghp_.",
            status_code=503,
        )
    return Github(auth=Auth.Token(GITHUB_PAT), per_page=30)


def _retry_github(fn, *args, **kwargs):
    """
    Call fn(*args, **kwargs) with up to len(_RETRY_DELAYS) retries on transient
    5xx errors.  RateLimitExceededException and BadCredentialsException are
    re-raised immediately without retry.
    """
    last_exc: Exception | None = None
    for attempt, delay in enumerate([0.0] + list(_RETRY_DELAYS)):
        if delay:
            time.sleep(delay)
        try:
            return fn(*args, **kwargs)
        except (RateLimitExceededException, BadCredentialsException):
            raise
        except GithubException as exc:
            status = getattr(exc, "status", 0) or 0
            if status < 500:
                raise  # 4xx errors won't improve on retry
            last_exc = exc
            log.warning("Transient GitHub error (attempt %d): %s", attempt + 1, exc)
        except Exception as exc:
            last_exc = exc
            log.warning("Unexpected error (attempt %d): %s", attempt + 1, exc)
    raise GitHubSearchError(f"GitHub request failed after retries: {last_exc}", status_code=503)


# ---------------------------------------------------------------------------
# Profile enrichment
# ---------------------------------------------------------------------------


def _safe_str(obj: Any, attr: str, default: str = "") -> str:
    return str(getattr(obj, attr, None) or default)


def _safe_int(obj: Any, attr: str, default: int = 0) -> int:
    try:
        return int(getattr(obj, attr, None) or default)
    except (TypeError, ValueError):
        return default


def _fetch_top_repos(user, limit: int = 5) -> list[dict[str, Any]]:
    """
    Fetch up to `limit` repos sorted by stars.

    PyGithub returns a PaginatedList — we must iterate with a counter
    rather than slicing (PaginatedList does not support __getitem__ slicing
    reliably without fetching all pages).
    """
    repos: list[dict[str, Any]] = []
    try:
        paginated = user.get_repos(sort="stars", direction="desc")
        for repo in paginated:
            if len(repos) >= limit:
                break
            repos.append({
                "name":        _safe_str(repo, "name"),
                "stars":       _safe_int(repo, "stargazers_count"),
                "language":    _safe_str(repo, "language"),
                "url":         _safe_str(repo, "html_url"),
                "description": (_safe_str(repo, "description"))[:120],
            })
    except GithubException as exc:
        log.warning("Repo fetch failed for %s: %s", _safe_str(user, "login", "?"), exc)
    return repos


def _total_stars(repos: list[dict[str, Any]]) -> int:
    return sum(r.get("stars", 0) for r in repos)


def _build_candidate(
    user,
    *,
    intent: SearchIntent,
    base_score: int,
    pre_fetched_repos: list[dict[str, Any]] | None = None,
    partial: bool = False,
) -> dict[str, Any]:
    """
    Convert a GitHub user object (full or partial) into a candidate dict.
    """
    repos = pre_fetched_repos if pre_fetched_repos is not None else _fetch_top_repos(user)
    top_languages = list({r["language"] for r in repos if r.get("language")})
    repo_names    = [r["name"] for r in repos if r.get("name")]
    login         = _safe_str(user, "login")
    bio           = _safe_str(user, "bio")
    location_field = _safe_str(user, "location")
    followers     = _safe_int(user, "followers")

    score = relevance_score(
        login=login,
        bio=bio,
        location_field=location_field,
        top_languages=top_languages,
        repo_names=repo_names,
        followers=followers,
        total_stars=_total_stars(repos),
        intent=intent,
        base_score=base_score,
    )

    return {
        "id":           f"github:{login}",
        "source":       "github",
        "name":         _safe_str(user, "name") or login,
        "email":        _safe_str(user, "email"),
        "title":        intent.role or "GitHub Developer",
        "location":     location_field,
        "skills":       ", ".join(top_languages),
        "match_score":  score,
        "status":       "available",
        "summary":      bio[:300] if bio else f"GitHub user with {_safe_int(user, 'public_repos')} public repos.",
        "github_url":   _safe_str(user, "html_url") or f"https://github.com/{login}",
        "avatar_url":   _safe_str(user, "avatar_url"),
        "top_repos":    repos,
        "followers":    followers,
        "public_repos": _safe_int(user, "public_repos"),
        "profile_partial": partial,
    }


# ---------------------------------------------------------------------------
# Raw search helpers
# ---------------------------------------------------------------------------

# Candidate metadata accumulated before enrichment.
@dataclass
class _RawHit:
    hit: Any                     # PyGithub NamedUser or Repository.owner (possibly partial)
    base_score: int
    pre_fetched_repos: list[dict[str, Any]] = field(default_factory=list)


def _iter_limited(paginated, limit: int):
    """Yield at most `limit` items from a PyGithub PaginatedList."""
    count = 0
    for item in paginated:
        if count >= limit:
            break
        yield item
        count += 1


def _search_users(client: Github, queries: tuple[str, ...], base_score: int) -> dict[str, _RawHit]:
    hits: dict[str, _RawHit] = {}
    for query in queries:
        if not query.strip():
            continue
        try:
            log.info("GitHub user search: %s", query)
            results = _retry_github(client.search_users, query)
            for user in _iter_limited(results, _QUERY_PAGE_LIMIT):
                login = _safe_str(user, "login")
                if not login:
                    continue
                if login in hits:
                    # Seen from a previous query in this plan — small bonus.
                    hits[login].base_score = min(hits[login].base_score + 4, 90)
                else:
                    hits[login] = _RawHit(hit=user, base_score=base_score)
        except GitHubSearchError:
            raise
        except GithubException as exc:
            log.warning("User search failed for %r: %s", query, exc)
    return hits


def _search_repo_owners(client: Github, queries: tuple[str, ...]) -> dict[str, _RawHit]:
    hits: dict[str, _RawHit] = {}
    for query in queries:
        if not query.strip():
            continue
        try:
            log.info("GitHub repo search: %s", query)
            results = _retry_github(client.search_repositories, query)
            for repo in _iter_limited(results, _QUERY_PAGE_LIMIT):
                owner = getattr(repo, "owner", None)
                if owner is None:
                    continue
                login = _safe_str(owner, "login")
                if not login:
                    continue
                repo_data: dict[str, Any] = {
                    "name":        _safe_str(repo, "name"),
                    "stars":       _safe_int(repo, "stargazers_count"),
                    "language":    _safe_str(repo, "language"),
                    "url":         _safe_str(repo, "html_url"),
                    "description": _safe_str(repo, "description")[:120],
                }
                if login in hits:
                    existing_names = {r["name"] for r in hits[login].pre_fetched_repos}
                    if repo_data["name"] not in existing_names:
                        hits[login].pre_fetched_repos.append(repo_data)
                else:
                    # Repo owners without a user-search match get a moderate base score.
                    hits[login] = _RawHit(hit=owner, base_score=62, pre_fetched_repos=[repo_data])
        except GitHubSearchError:
            raise
        except GithubException as exc:
            log.warning("Repo search failed for %r: %s", query, exc)
    return hits


def _merge(
    user_hits: dict[str, _RawHit],
    repo_hits: dict[str, _RawHit],
) -> dict[str, _RawHit]:
    """Merge two hit maps; users appearing in both get a score boost."""
    merged = dict(user_hits)
    for login, rh in repo_hits.items():
        if login in merged:
            # Appeared in both user search and repo search — stronger signal.
            merged[login].base_score = min(merged[login].base_score + 10, 90)
            existing = {r["name"] for r in merged[login].pre_fetched_repos}
            for r in rh.pre_fetched_repos:
                if r["name"] not in existing:
                    merged[login].pre_fetched_repos.append(r)
        else:
            merged[login] = rh
    return merged


def _run_plan(client: Github, plan: QueryPlan) -> dict[str, _RawHit]:
    user_hits = _search_users(client, plan.user_queries, plan.base_score)
    repo_hits = _search_repo_owners(client, plan.repo_queries)
    return _merge(user_hits, repo_hits)


# ---------------------------------------------------------------------------
# Enrichment
# ---------------------------------------------------------------------------


def _enrich(
    client: Github,
    login: str,
    raw: _RawHit,
    intent: SearchIntent,
) -> dict[str, Any] | None:
    """
    Fetch a full user profile and build a candidate dict.
    Falls back to the partial search-hit object if the full fetch fails.
    """
    try:
        full_user = _retry_github(client.get_user, login)
        return _build_candidate(
            full_user,
            intent=intent,
            base_score=raw.base_score,
            pre_fetched_repos=raw.pre_fetched_repos or None,
            partial=False,
        )
    except (GitHubSearchError, RateLimitExceededException, BadCredentialsException):
        raise
    except Exception as exc:
        log.warning("Full profile unavailable for %s (%s) — using partial data", login, exc)

    if raw.hit is not None:
        return _build_candidate(
            raw.hit,
            intent=intent,
            base_score=max(raw.base_score - 5, 30),
            pre_fetched_repos=raw.pre_fetched_repos,
            partial=True,
        )
    return None


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def search_github_users(
    *,
    query: str = "",
    skill: str = "",
    location: str = "",
    language: str = "",
    project: str = "",
    top_k: int = 10,
) -> tuple[list[dict[str, Any]], str | None]:
    """
    Search GitHub for candidate developers.

    Parameters
    ----------
    query    : free-text role description, optionally including location
               e.g. "backend engineer in Lahore"
    skill    : comma-separated skills  e.g. "FastAPI, PostgreSQL"
    location : explicit location override
    language : primary programming language  e.g. "python"
    project  : open-source project context  e.g. "django"
    top_k    : maximum number of results to return

    Returns
    -------
    (results, warning)
        results : list of candidate dicts, sorted by match_score descending
        warning : human-readable string if results are degraded, else None
    """
    intent = parse_intent(
        query=query, skill=skill, location=location, language=language, project=project,
    )
    plans = build_query_plans(intent)

    log.info(
        "Search intent — role=%r  location=%r  language=%r  skills=%r",
        intent.role, intent.location, intent.language, intent.skills,
    )

    try:
        client = _get_client()
    except GitHubSearchError:
        raise

    # ---- Progressive plan execution ----------------------------------------
    # Run plans in order (strict → loose).  Stop as soon as we have enough
    # raw candidates to fill top_k after enrichment losses.
    stop_after = min(max(top_k, 6), _MAX_ENRICH)
    accumulated: dict[str, _RawHit] = {}

    for plan in plans:
        plan_hits = _run_plan(client, plan)
        for login, rh in plan_hits.items():
            if login not in accumulated:
                accumulated[login] = rh
            else:
                accumulated[login].base_score = max(accumulated[login].base_score, rh.base_score)
                existing = {r["name"] for r in accumulated[login].pre_fetched_repos}
                for r in rh.pre_fetched_repos:
                    if r["name"] not in existing:
                        accumulated[login].pre_fetched_repos.append(r)
        if len(accumulated) >= stop_after:
            break

    if not accumulated:
        return [], None

    # ---- Enrich top candidates ---------------------------------------------
    # Sort by base_score before enrichment so we spend API quota on the most
    # promising hits.
    ranked_raw = sorted(
        accumulated.items(),
        key=lambda kv: kv[1].base_score,
        reverse=True,
    )[:_MAX_ENRICH]

    results: list[dict[str, Any]] = []
    partial_count = 0

    for login, raw in ranked_raw:
        if len(results) >= top_k:
            break
        try:
            candidate = _enrich(client, login, raw, intent)
        except RateLimitExceededException as exc:
            raise GitHubSearchError(
                "GitHub API rate limit exceeded. Try again later.", status_code=429
            ) from exc
        except BadCredentialsException as exc:
            raise GitHubSearchError(
                "Invalid GITHUB_PAT. Check your token at github.com/settings/tokens.",
                status_code=503,
            ) from exc

        if candidate is None:
            continue
        if candidate["profile_partial"]:
            partial_count += 1
        results.append(candidate)

    results.sort(key=lambda c: c["match_score"], reverse=True)

    # ---- Build warning if quality is degraded ------------------------------
    warning: str | None = None
    if partial_count == len(results) and partial_count:
        warning = (
            "GitHub returned profiles with limited detail (rate limit or permissions). "
            "Profile links are still valid."
        )
    elif partial_count:
        warning = f"{partial_count} profile(s) loaded with limited detail due to API rate limits."

    return results, warning