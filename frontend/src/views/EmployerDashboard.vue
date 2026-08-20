<script setup>
import { ref, reactive, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore, api } from "../stores/auth";
import Navbar from "../components/Navbar.vue";
import AppFooter from "../components/AppFooter.vue";
import SearchConfigModal from "../components/SearchConfigModal.vue";
import ResumeLibraryPanel from "../components/ResumeLibraryPanel.vue";
import {
  Search, Plus, Briefcase, MapPin, Clock, GraduationCap, Filter, X,
  Sparkles, LogOut, Github,
  ExternalLink, FileText, Brain, Pencil, Users, CheckCircle2,
} from "lucide-vue-next";

const router = useRouter();
const auth = useAuthStore();

if (!auth.isLoggedIn || !auth.isEmployer) {
  router.push("/login");
}

const tab = ref("search");

// === Candidate Search ===
const searchQuery = ref("");
const searchRequirements = ref("");
const searchConfig = reactive({
  skill: "",
  location: "",
  minExp: "",
  maxExp: "",
  language: "",
  project: "",
  sources: { pool: true, applications: true, uploads: true },
  includeGithub: false,
});
const showSearchModal = ref(false);
const searchResults = ref([]);
const searching = ref(false);
const hasSearched = ref(false);
const selectedCandidate = ref(null);
const sourcesUsed = ref([]);
const sourceCounts = ref({});
const githubError = ref("");
const searchError = ref("");
const showAdvancedFilters = ref(false);

const sourceLabels = {
  pool: "Talent Pool",
  applications: "Applications",
  uploads: "Uploads",
  github: "GitHub",
};

const tabLabels = {
  search: "Search Candidates",
  postjob: "Post a Job",
  myjobs: "My Jobs",
};

const tabOptions = [
  { key: "search", label: "Search", icon: Search },
  { key: "postjob", label: "Post Job", icon: Plus },
  { key: "myjobs", label: "My Jobs", icon: Briefcase },
];

const quickSearches = [
  { label: "Embedded Engineer", query: "embedded engineer", requirements: "Embedded C, experience: 1+" },
  { label: "Full-Stack Developer", query: "full stack developer", requirements: "React, experience: 2+" },
  { label: "Data Scientist", query: "data scientist", requirements: "Python, experience: 3+" },
  { label: "DevOps Engineer", query: "devops", requirements: "Docker, experience: 2+" },
];

function parseRequirementsText(text) {
  const parsed = {
    skill: "",
    location: "",
    minExp: "",
    maxExp: "",
    language: "",
    project: "",
  };

  if (!text.trim()) return parsed;

  const skillParts = [];
  const segments = text.split(/[\n,;]+/).map((part) => part.trim()).filter(Boolean);

  function parseExperience(rawValue) {
    const value = rawValue.toLowerCase().trim();
    const range = value.match(/(\d+)\s*(?:-|to)\s*(\d+)/i);
    if (range) {
      parsed.minExp = range[1];
      parsed.maxExp = range[2];
      return true;
    }

    const minimum = value.match(/(\d+)\s*\+?/);
    if (minimum) {
      parsed.minExp = minimum[1];
      return true;
    }

    return false;
  }

  segments.forEach((segment) => {
    const lower = segment.toLowerCase();
    if (lower.startsWith("location:")) {
      parsed.location = segment.slice(9).trim();
      return;
    }
    if (lower.startsWith("language:")) {
      parsed.language = segment.slice(9).trim();
      return;
    }
    if (lower.startsWith("project:") || lower.startsWith("repo:")) {
      parsed.project = segment.split(":").slice(1).join(":").trim();
      return;
    }
    if (lower.startsWith("experience:") || lower.startsWith("exp:")) {
      parseExperience(segment.split(":").slice(1).join(":").trim());
      return;
    }
    if (lower.includes("remote") && !parsed.location) {
      parsed.location = segment;
      return;
    }
    if (parseExperience(segment)) {
      return;
    }
    skillParts.push(segment);
  });

  parsed.skill = skillParts.join(", ");
  return parsed;
}

const activeSourceSummary = computed(() => {
  const labels = sourcesUsed.value.map((source) => sourceLabels[source] || source);
  return labels.length ? labels.join(" + ") : "Talent Pool";
});

const enabledSourceLabels = computed(() => {
  const labels = Object.entries(searchConfig.sources)
    .filter(([, value]) => value)
    .map(([key]) => sourceLabels[key] || key);

  if (searchConfig.includeGithub) labels.push(sourceLabels.github);
  return labels;
});

const activeFilterChips = computed(() => {
  const chips = [];
  if (searchQuery.value.trim()) chips.push({ label: "Query", value: searchQuery.value.trim() });
  if (searchRequirements.value.trim()) chips.push({ label: "Requirements", value: searchRequirements.value.trim() });
  if (searchConfig.skill.trim()) chips.push({ label: "Skill", value: searchConfig.skill.trim() });
  if (searchConfig.location.trim()) chips.push({ label: "Location", value: searchConfig.location.trim() });
  if (searchConfig.minExp || searchConfig.maxExp) {
    const min = searchConfig.minExp || "0";
    const max = searchConfig.maxExp || "Any";
    chips.push({ label: "Experience", value: `${min}-${max} yrs` });
  }
  if (searchConfig.language.trim()) chips.push({ label: "Language", value: searchConfig.language.trim() });
  if (searchConfig.project.trim()) chips.push({ label: "Project", value: searchConfig.project.trim() });
  return chips;
});

const workspacePanels = computed(() => [
  {
    label: "Workspace",
    value: tabLabels[tab.value],
  },
  {
    label: "Sources",
    value: enabledSourceLabels.value.length || 1,
    hint: enabledSourceLabels.value.length ? enabledSourceLabels.value.join(" · ") : "Pool",
  },
  {
    label: hasSearched.value ? "Results" : "Templates",
    value: hasSearched.value ? searchResults.value.length : quickSearches.length,
  },
]);

const jobPostingTips = [
  "Be specific with the title",
  "List must-have skills only",
  "Separate requirements from nice-to-haves",
];

async function searchCandidates() {
  searching.value = true;
  hasSearched.value = true;
  selectedCandidate.value = null;
  githubError.value = "";
  searchError.value = "";
  try {
    const parsedRequirements = parseRequirementsText(searchRequirements.value);
    searchConfig.skill = searchConfig.skill || parsedRequirements.skill;
    searchConfig.location = searchConfig.location || parsedRequirements.location;
    searchConfig.minExp = searchConfig.minExp || parsedRequirements.minExp;
    searchConfig.maxExp = searchConfig.maxExp || parsedRequirements.maxExp;
    searchConfig.language = searchConfig.language || parsedRequirements.language;
    searchConfig.project = searchConfig.project || parsedRequirements.project;

    const params = new URLSearchParams();
    if (searchQuery.value.trim()) params.append("q", searchQuery.value.trim());
    else if (searchConfig.skill) params.append("skill", searchConfig.skill);
    if (searchConfig.skill && searchQuery.value.trim()) params.append("skill", searchConfig.skill);
    if (searchConfig.location) params.append("location", searchConfig.location);
    if (searchConfig.minExp) params.append("min_exp", searchConfig.minExp);
    if (searchConfig.maxExp) params.append("max_exp", searchConfig.maxExp);
    if (searchConfig.language) params.append("language", searchConfig.language);
    if (searchConfig.project) params.append("project", searchConfig.project);

    const internalSources = Object.entries(searchConfig.sources)
      .filter(([, value]) => value)
      .map(([key]) => key);
    const githubOnly = searchConfig.includeGithub && !internalSources.length;

    if (!internalSources.length && !searchConfig.includeGithub) {
      searchError.value = "Select at least one search source or enable GitHub in Options.";
      searchResults.value = [];
      return;
    }

    if (internalSources.length) {
      params.append("sources", internalSources.join(","));
    } else {
      params.append("sources", "");
    }
    if (searchConfig.includeGithub) params.append("include_github", "true");

    const res = await api.get(`/candidates/search?${params.toString()}`, {
      timeout: 50000,
    });
    searchResults.value = res.data.candidates || [];
    sourcesUsed.value = res.data.sources_used || [];
    sourceCounts.value = res.data.source_counts || {};
    githubError.value = res.data.github_error || "";
    if (!searchResults.value.length && !githubError.value) {
      searchError.value = githubOnly
        ? "No GitHub developers matched. Try broader keywords, a language filter, or a project/repo name."
        : "No matches found. Try different keywords or enable more sources in Options.";
    }
  } catch (err) {
    console.error("Search error:", err);
    searchResults.value = [];
    searchError.value = err.response?.data?.error || "Search failed. Please try again.";
  } finally {
    searching.value = false;
  }
}

function onModalSearch(config) {
  searchConfig.sources.pool = config.sources.includes("pool");
  searchConfig.sources.applications = config.sources.includes("applications");
  searchConfig.sources.uploads = config.sources.includes("uploads");
  searchConfig.includeGithub = config.includeGithub;
  if (hasSearched.value || searchQuery.value.trim() || searchRequirements.value.trim()) {
    searchCandidates();
  }
}

function clearSearch() {
  searchQuery.value = "";
  searchRequirements.value = "";
  Object.assign(searchConfig, {
    skill: "",
    location: "",
    minExp: "",
    maxExp: "",
    language: "",
    project: "",
    sources: { pool: true, applications: true, uploads: true },
    includeGithub: false,
  });
  searchResults.value = [];
  hasSearched.value = false;
  selectedCandidate.value = null;
  sourcesUsed.value = [];
  sourceCounts.value = {};
  githubError.value = "";
  searchError.value = "";
}

function getScoreColor(score) {
  if (score >= 80) return "text-success-600 bg-success-50";
  if (score >= 60) return "text-warning-600 bg-warning-50";
  return "text-danger-500 bg-danger-50";
}

function getScoreLabel(score) {
  if (score >= 90) return "Excellent Match";
  if (score >= 75) return "Strong Match";
  if (score >= 60) return "Good Match";
  return "Partial Match";
}

function getSourceBadge(source) {
  const map = {
    pool: { label: "Talent Pool", class: "bg-primary-50 text-primary-700" },
    application: { label: "Application", class: "bg-blue-50 text-blue-700" },
    upload: { label: "Upload", class: "bg-purple-50 text-purple-700" },
    github: { label: "GitHub", class: "bg-neutral-800 text-white" },
  };
  return map[source] || map.pool;
}

function isSelected(candidate) {
  return selectedCandidate.value?.id === candidate.id;
}

// === Post a Job ===
const jobForm = reactive({
  title: "",
  company: auth.user?.company || "TalentSync",
  location: "",
  type: "Full-time",
  experience: "",
  skills: "",
  description: "",
  salary: "",
});
const postingJob = ref(false);
const jobPosted = ref(false);

async function postJob() {
  if (!jobForm.title || !jobForm.description) return;
  postingJob.value = true;
  try {
    await api.post("/jobs", {
      title: jobForm.title,
      company: jobForm.company,
      location: jobForm.location,
      type: jobForm.type,
      experience: jobForm.experience,
      skills: jobForm.skills,
      description: jobForm.description,
      salary: jobForm.salary,
    });
    jobPosted.value = true;
    Object.assign(jobForm, {
      title: "",
      location: "",
      experience: "",
      skills: "",
      description: "",
      salary: "",
    });
    setTimeout(() => {
      jobPosted.value = false;
    }, 3000);
  } catch {
    // silent
  } finally {
    postingJob.value = false;
  }
}

// === My Jobs ===
const myJobs = ref([]);
const loadingJobs = ref(false);

async function loadMyJobs() {
  loadingJobs.value = true;
  try {
    const res = await api.get("/jobs/mine");
    myJobs.value = res.data.jobs || [];
  } catch {
    myJobs.value = [];
  } finally {
    loadingJobs.value = false;
  }
}

const editingJobId = ref(null);
const editingJobForm = reactive({
  title: "",
  location: "",
  type: "Full-time",
  experience: "",
  skills: "",
  description: "",
  salary: "",
  status: "active",
});
const savingJob = ref(false);

const expandedJobId = ref(null);
const jobApplicationsById = reactive({});
const loadingApplicationsByJob = reactive({});
const applicationsErrorByJob = reactive({});

function startEditJob(job) {
  editingJobId.value = job.id;
  Object.assign(editingJobForm, {
    title: job.title || "",
    location: job.location || "",
    type: job.type || "Full-time",
    experience: job.experience || "",
    skills: job.skills || "",
    description: job.description || "",
    salary: job.salary || "",
    status: job.status || "active",
  });
}

function cancelEditJob() {
  editingJobId.value = null;
}

async function saveJobEdit(jobId) {
  if (!editingJobForm.title.trim() || !editingJobForm.description.trim()) return;
  savingJob.value = true;
  try {
    await api.patch(`/jobs/${jobId}`, {
      title: editingJobForm.title,
      location: editingJobForm.location,
      type: editingJobForm.type,
      experience: editingJobForm.experience,
      skills: editingJobForm.skills,
      description: editingJobForm.description,
      salary: editingJobForm.salary,
      status: editingJobForm.status,
    });
    await loadMyJobs();
    editingJobId.value = null;
  } finally {
    savingJob.value = false;
  }
}

async function loadJobApplications(jobId) {
  loadingApplicationsByJob[jobId] = true;
  applicationsErrorByJob[jobId] = "";
  try {
    const res = await api.get(`/jobs/${jobId}/applications`);
    jobApplicationsById[jobId] = res.data.applications || [];
  } catch (err) {
    jobApplicationsById[jobId] = [];
    applicationsErrorByJob[jobId] = err.response?.data?.error || "Could not load applications";
  } finally {
    loadingApplicationsByJob[jobId] = false;
  }
}

async function toggleJobApplications(jobId) {
  if (expandedJobId.value === jobId) {
    expandedJobId.value = null;
    return;
  }
  expandedJobId.value = jobId;
  if (!jobApplicationsById[jobId]) {
    await loadJobApplications(jobId);
  }
}

function switchTab(nextTab) {
  tab.value = nextTab;
  if (nextTab === "myjobs") loadMyJobs();
}

function applyQuickSearch(qs) {
  searchQuery.value = qs.query;
  searchRequirements.value = qs.requirements;
  searchCandidates();
}

const modalInitial = computed(() => ({
  sources: { ...searchConfig.sources },
  includeGithub: searchConfig.includeGithub,
}));
</script>

<template>
  <div class="min-h-screen employer-page">
    <Navbar />

    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
      <!-- Hero -->
      <section class="employer-hero mb-8">
        <div class="p-6 sm:p-8">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-5">
            <div>
              <p class="section-eyebrow text-primary-300">Employer workspace</p>
              <h1 class="mt-2 text-2xl sm:text-3xl font-semibold tracking-tight text-white">
                Welcome, {{ auth.user?.name || 'Employer' }}
              </h1>
              <p class="mt-1.5 text-sm text-neutral-400">
                {{ auth.user?.company || 'Your Company' }}
              </p>
            </div>
            <button
              @click="auth.logout(); router.push('/')"
              class="btn-press self-start sm:self-auto inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-neutral-300 hover:bg-white/10 hover:text-white transition-colors"
            >
              <LogOut class="w-4 h-4" /> Sign out
            </button>
          </div>

          <div class="mt-6 grid grid-cols-3 gap-3">
            <div
              v-for="panel in workspacePanels"
              :key="panel.label"
              class="hero-metric-card px-4 py-3.5"
            >
              <p class="text-[10px] uppercase tracking-wider text-neutral-500">{{ panel.label }}</p>
              <p class="mt-1 text-lg sm:text-xl font-semibold text-white truncate">{{ panel.value }}</p>
              <p v-if="panel.hint" class="mt-0.5 text-[11px] text-neutral-500 truncate">{{ panel.hint }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Tab navigation -->
      <nav class="employer-tabs mb-8" aria-label="Workspace sections">
        <button
          v-for="option in tabOptions"
          :key="option.key"
          @click="switchTab(option.key)"
          :class="tab === option.key ? 'employer-tab-active' : ''"
          class="employer-tab btn-press"
        >
          <component :is="option.icon" class="h-4 w-4 shrink-0" />
          <span class="hidden sm:inline">{{ option.label }}</span>
        </button>
      </nav>

      <div v-if="tab === 'search'">
        <div class="space-y-8">
          <div class="dashboard-shell p-5 sm:p-6">
            <div class="mb-6">
              <p class="section-eyebrow">Search</p>
              <h2 class="section-title mt-1">Find candidates</h2>
            </div>

            <div class="grid gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]">
              <div class="relative">
                <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                <input
                  v-model="searchQuery"
                  @keyup.enter="searchCandidates"
                  type="text"
                  placeholder="Role, skill, or keyword…"
                  class="w-full pl-11 pr-4 py-3 rounded-xl border border-neutral-200 bg-neutral-50/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400"
                />
              </div>
              <div>
                <input
                  v-model="searchRequirements"
                  @keyup.enter="searchCandidates"
                  type="text"
                  placeholder="Requirements: React, location: Remote, experience: 3+"
                  class="w-full px-4 py-3 rounded-xl border border-neutral-200 bg-neutral-50/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400"
                />
              </div>
              <div class="flex gap-2">
                <button @click="searchCandidates" :disabled="searching" class="btn-press flex-1 sm:flex-none px-5 py-3 rounded-xl bg-primary-600 text-white text-sm font-medium hover:bg-primary-700 disabled:opacity-50">
                  {{ searching ? 'Searching…' : 'Search' }}
                </button>
                <button @click="showSearchModal = true" class="btn-press px-4 py-3 rounded-xl border border-neutral-200 text-neutral-600 hover:bg-neutral-50 text-sm font-medium flex items-center gap-1.5">
                  <Filter class="w-4 h-4" />
                  <span class="hidden sm:inline">Sources</span>
                </button>
              </div>
            </div>

            <div class="mt-3">
              <button
                @click="showAdvancedFilters = !showAdvancedFilters"
                class="btn-press inline-flex items-center gap-1.5 rounded-xl border border-neutral-200 px-3 py-1.5 text-xs font-medium text-neutral-600 hover:bg-neutral-50"
              >
                <Filter class="w-3.5 h-3.5" />
                {{ showAdvancedFilters ? 'Hide advanced filters' : 'Advanced filters' }}
              </button>
            </div>

            <div v-if="showAdvancedFilters" class="mt-3 dashboard-muted-card p-4">
              <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                <div>
                  <label class="block text-[11px] text-neutral-500 mb-1">Skills</label>
                  <input
                    v-model="searchConfig.skill"
                    type="text"
                    placeholder="Python, FastAPI"
                    class="w-full px-3 py-2 rounded-lg border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200"
                  />
                </div>
                <div>
                  <label class="block text-[11px] text-neutral-500 mb-1">Location</label>
                  <input
                    v-model="searchConfig.location"
                    type="text"
                    placeholder="Remote or city"
                    class="w-full px-3 py-2 rounded-lg border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200"
                  />
                </div>
                <div>
                  <label class="block text-[11px] text-neutral-500 mb-1">Language</label>
                  <input
                    v-model="searchConfig.language"
                    type="text"
                    placeholder="JavaScript, Go"
                    class="w-full px-3 py-2 rounded-lg border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200"
                  />
                </div>
                <div>
                  <label class="block text-[11px] text-neutral-500 mb-1">Project / Repo</label>
                  <input
                    v-model="searchConfig.project"
                    type="text"
                    placeholder="billing-service"
                    class="w-full px-3 py-2 rounded-lg border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200"
                  />
                </div>
                <div>
                  <label class="block text-[11px] text-neutral-500 mb-1">Min experience</label>
                  <input
                    v-model="searchConfig.minExp"
                    type="number"
                    min="0"
                    placeholder="0"
                    class="w-full px-3 py-2 rounded-lg border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200"
                  />
                </div>
                <div>
                  <label class="block text-[11px] text-neutral-500 mb-1">Max experience</label>
                  <input
                    v-model="searchConfig.maxExp"
                    type="number"
                    min="0"
                    placeholder="10"
                    class="w-full px-3 py-2 rounded-lg border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200"
                  />
                </div>
              </div>
            </div>

            <div class="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2">
              <div class="flex flex-wrap gap-1.5 items-center">
                <span v-if="searchConfig.sources.pool" class="text-xs px-2.5 py-1 rounded-full bg-primary-50 text-primary-700">Pool</span>
                <span v-if="searchConfig.sources.applications" class="text-xs px-2.5 py-1 rounded-full bg-blue-50 text-blue-700">Applications</span>
                <span v-if="searchConfig.sources.uploads" class="text-xs px-2.5 py-1 rounded-full bg-purple-50 text-purple-700">Uploads</span>
                <span v-if="searchConfig.includeGithub" class="text-xs px-2.5 py-1 rounded-full bg-neutral-900 text-white flex items-center gap-1">
                  <Github class="w-3 h-3" /> GitHub
                </span>
                <button @click="showSearchModal = true" class="text-xs text-primary-600 hover:text-primary-700 font-medium ml-1">Edit</button>
              </div>

              <span v-if="hasSearched" class="text-xs text-neutral-400">
                {{ searchResults.length }} result{{ searchResults.length === 1 ? '' : 's' }}
                <template v-if="sourcesUsed.length"> · {{ activeSourceSummary }}</template>
              </span>
              <span v-if="githubError" class="text-xs text-warning-600">{{ githubError }}</span>
              <span v-else-if="searchError && hasSearched" class="text-xs text-warning-600">{{ searchError }}</span>
            </div>

            <div v-if="activeFilterChips.length" class="mt-3 flex flex-wrap gap-2">
              <span
                v-for="chip in activeFilterChips"
                :key="`${chip.label}-${chip.value}`"
                class="inline-flex items-center gap-1.5 rounded-full bg-neutral-100 px-3 py-1 text-xs text-neutral-600"
              >
                <span class="text-neutral-400">{{ chip.label }}</span>
                <span class="font-medium truncate max-w-[200px]">{{ chip.value }}</span>
              </span>
            </div>

            <div class="mt-5 flex flex-wrap gap-2">
              <button
                v-for="qs in quickSearches"
                :key="qs.label"
                @click="applyQuickSearch(qs)"
                class="btn-press text-xs px-3 py-1.5 rounded-full border border-neutral-200 text-neutral-600 hover:border-primary-300 hover:bg-primary-50 hover:text-primary-700 transition-colors"
              >{{ qs.label }}</button>
            </div>
          </div>
        </div>

        <div v-if="!hasSearched" class="text-center py-16">
          <div class="w-14 h-14 mx-auto mb-4 rounded-2xl bg-primary-50 flex items-center justify-center">
            <Sparkles class="w-7 h-7 text-primary-500" />
          </div>
          <h3 class="text-base font-semibold text-neutral-700">Search your talent pipeline</h3>
          <p class="text-sm text-neutral-400 mt-1 max-w-sm mx-auto">Pool, applications, uploads, and GitHub — one search.</p>
        </div>

        <div v-else-if="searching" class="grid md:grid-cols-2 gap-4 mt-8">
          <div v-for="i in 4" :key="i" class="dashboard-shell p-6 animate-pulse">
            <div class="h-4 bg-neutral-200 rounded w-1/3 mb-3"></div>
            <div class="h-3 bg-neutral-100 rounded w-2/3 mb-2"></div>
            <div class="h-3 bg-neutral-100 rounded w-1/2"></div>
          </div>
        </div>

        <div v-else-if="searchResults.length === 0 && hasSearched" class="text-center py-14 mt-6 rounded-2xl border border-dashed border-neutral-200 bg-neutral-50/50">
          <h3 class="text-base font-semibold text-neutral-700">No matches found</h3>
          <p v-if="searchError" class="text-sm text-warning-600 mt-1">{{ searchError }}</p>
          <p v-else-if="githubError" class="text-sm text-warning-600 mt-1">{{ githubError }}</p>
          <p v-else class="text-sm text-neutral-400 mt-1">Try broader keywords or more sources.</p>
          <div class="mt-4 flex justify-center gap-2">
            <button @click="showSearchModal = true" class="btn-press px-4 py-2 text-sm border border-neutral-200 rounded-xl text-neutral-600 hover:bg-white">Edit sources</button>
            <button @click="clearSearch" class="btn-press px-4 py-2 text-sm bg-primary-600 text-white rounded-xl hover:bg-primary-700">Clear</button>
          </div>
        </div>

        <div v-else class="mt-8">
          <div class="flex items-center justify-between gap-4 mb-5">
            <div>
              <p class="section-eyebrow">Results</p>
              <p class="mt-1 text-sm text-neutral-500">
                <span class="text-xl font-semibold text-neutral-900">{{ searchResults.length }}</span>
                candidate{{ searchResults.length === 1 ? '' : 's' }}
              </p>
              <div v-if="Object.keys(sourceCounts).length" class="flex flex-wrap gap-1.5 mt-2">
                <span v-if="sourceCounts.pool" class="text-[11px] px-2 py-0.5 rounded-full bg-primary-50 text-primary-700">{{ sourceCounts.pool }} pool</span>
                <span v-if="sourceCounts.application" class="text-[11px] px-2 py-0.5 rounded-full bg-blue-50 text-blue-700">{{ sourceCounts.application }} apps</span>
                <span v-if="sourceCounts.upload" class="text-[11px] px-2 py-0.5 rounded-full bg-purple-50 text-purple-700">{{ sourceCounts.upload }} uploads</span>
                <span v-if="sourceCounts.github" class="text-[11px] px-2 py-0.5 rounded-full bg-neutral-900 text-white">{{ sourceCounts.github }} github</span>
              </div>
            </div>
            <button @click="clearSearch" class="inline-flex items-center gap-1 rounded-xl border border-neutral-200 px-3 py-1.5 text-xs font-medium text-neutral-500 hover:text-neutral-700 hover:bg-neutral-50">
              <X class="w-3 h-3" /> Clear
            </button>
          </div>

          <div class="grid xl:grid-cols-2 gap-4">
            <div
              v-for="candidate in searchResults"
              :key="candidate.id"
              @click="selectedCandidate = isSelected(candidate) ? null : candidate"
              class="btn-press dashboard-card dashboard-card-hover p-5 sm:p-6 cursor-pointer"
              :class="isSelected(candidate) ? 'border-primary-300 ring-2 ring-primary-100 shadow-xl shadow-primary-100/40' : ''"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-start gap-3 flex-1 min-w-0">
                  <img
                    v-if="candidate.source === 'github' && candidate.avatar_url"
                    :src="candidate.avatar_url"
                    :alt="candidate.name"
                    class="w-12 h-12 rounded-2xl shrink-0 ring-2 ring-white"
                  />
                  <div class="min-w-0">
                    <div class="flex items-center gap-2 flex-wrap">
                      <h3 class="text-base sm:text-lg font-semibold text-neutral-900">{{ candidate.name }}</h3>
                      <span
                        class="text-[10px] font-semibold px-2.5 py-1 rounded-full uppercase tracking-[0.14em]"
                        :class="getSourceBadge(candidate.source).class"
                      >{{ getSourceBadge(candidate.source).label }}</span>
                    </div>
                    <p class="text-sm text-primary-700 font-medium truncate mt-1">{{ candidate.title }}</p>
                  </div>
                </div>
                <div class="text-sm font-bold px-3 py-1.5 rounded-full shrink-0" :class="getScoreColor(candidate.match_score)">
                  {{ candidate.match_score }}%
                </div>
              </div>

              <div class="mt-4 flex flex-wrap gap-2 text-xs text-neutral-600">
                <span v-if="candidate.location" class="inline-flex items-center gap-1 rounded-full bg-white px-3 py-1.5 border border-neutral-200">
                  <MapPin class="w-3 h-3" /> {{ candidate.location }}
                </span>
                <span v-if="candidate.experience" class="inline-flex items-center gap-1 rounded-full bg-white px-3 py-1.5 border border-neutral-200">
                  <Clock class="w-3 h-3" /> {{ candidate.experience }} yrs exp
                </span>
                <span v-if="candidate.education" class="inline-flex items-center gap-1 rounded-full bg-white px-3 py-1.5 border border-neutral-200">
                  <GraduationCap class="w-3 h-3" /> {{ candidate.education }}
                </span>
                <span v-if="candidate.source === 'upload' && candidate.ai_score" class="inline-flex items-center gap-1 rounded-full bg-white px-3 py-1.5 border border-neutral-200">
                  <Brain class="w-3 h-3" /> AI {{ candidate.ai_score }}%
                </span>
                <span v-if="(candidate.source === 'application' || candidate.source === 'upload') && candidate.ats_score" class="inline-flex items-center gap-1 rounded-full bg-white px-3 py-1.5 border border-neutral-200">
                  <FileText class="w-3 h-3" /> ATS {{ candidate.ats_score }}%
                </span>
              </div>

              <div v-if="candidate.skills" class="mt-4 flex flex-wrap gap-1.5">
                <span
                  v-for="skill in candidate.skills.split(',').slice(0, 4)"
                  :key="skill"
                  class="text-xs px-2.5 py-1 rounded-full bg-neutral-100 text-neutral-700"
                >{{ skill.trim() }}</span>
              </div>

              <p v-if="candidate.summary && candidate.source !== 'pool'" class="mt-3 text-sm text-neutral-600 leading-6 line-clamp-2">
                {{ candidate.summary }}
              </p>

              <div class="mt-4 flex items-center justify-between gap-3">
                <p class="text-xs font-medium" :class="getScoreColor(candidate.match_score)">
                  {{ getScoreLabel(candidate.match_score) }}
                </p>
                <p class="text-xs text-neutral-400">{{ isSelected(candidate) ? 'Collapse' : 'Details' }}</p>
              </div>

              <div v-if="isSelected(candidate)" class="mt-5 pt-5 border-t border-neutral-200/80">
                <template v-if="candidate.source === 'github'">
                  <a
                    :href="candidate.github_url"
                    target="_blank"
                    rel="noopener"
                    class="inline-flex items-center gap-1 text-xs text-primary-700 hover:underline mb-3"
                    @click.stop
                  >
                    <Github class="w-3.5 h-3.5" /> View GitHub profile
                    <ExternalLink class="w-3 h-3" />
                  </a>
                  <div v-if="candidate.top_repos?.length">
                    <p class="text-xs text-neutral-400 mb-2">Top repositories</p>
                    <div class="space-y-1.5">
                      <div
                        v-for="repo in candidate.top_repos"
                        :key="repo.name"
                        class="dashboard-muted-card flex items-center justify-between gap-3 text-xs bg-white px-3 py-2.5"
                      >
                        <span class="font-medium text-neutral-700">{{ repo.name }}</span>
                        <span class="text-neutral-400">
                          <span v-if="repo.language">{{ repo.language }}</span>
                          <span v-if="repo.stars"> &middot; {{ repo.stars }} stars</span>
                        </span>
                      </div>
                    </div>
                  </div>
                </template>

                <template v-else-if="candidate.source === 'application'">
                  <div class="grid sm:grid-cols-2 gap-3 text-xs">
                    <div><span class="text-neutral-400">Email</span><br />{{ candidate.email }}</div>
                    <div><span class="text-neutral-400">Applied for</span><br />{{ candidate.job_title }}</div>
                    <div><span class="text-neutral-400">Company</span><br />{{ candidate.company }}</div>
                    <div><span class="text-neutral-400">ATS Score</span><br />{{ candidate.ats_score }}%</div>
                  </div>
                  <p v-if="candidate.summary" class="mt-3 text-sm text-neutral-600 leading-6">{{ candidate.summary }}</p>
                </template>

                <template v-else-if="candidate.source === 'upload'">
                  <div class="grid sm:grid-cols-2 gap-3 text-xs">
                    <div v-if="candidate.location"><span class="text-neutral-400">Location</span><br />{{ candidate.location }}</div>
                    <div><span class="text-neutral-400">Uploaded</span><br />{{ candidate.uploaded_date }}</div>
                    <div v-if="candidate.ai_score"><span class="text-neutral-400">AI Fit</span><br />{{ candidate.ai_score }}%</div>
                    <div v-if="candidate.ats_score"><span class="text-neutral-400">ATS Score</span><br />{{ candidate.ats_score }}%</div>
                    <div v-if="candidate.source_filename" class="sm:col-span-2"><span class="text-neutral-400">File</span><br />{{ candidate.source_filename }}</div>
                  </div>
                  <div v-if="candidate.ai_evaluation" class="mt-3 p-3 rounded-xl bg-primary-50/70 border border-primary-100">
                    <p class="text-xs font-medium text-primary-700 mb-1 flex items-center gap-1"><Sparkles class="w-3 h-3" /> AI evaluation</p>
                    <p class="text-sm text-neutral-700 leading-6">{{ candidate.ai_evaluation }}</p>
                  </div>
                  <p v-if="candidate.summary" class="mt-3 text-sm text-neutral-600 leading-6">{{ candidate.summary }}</p>
                </template>

                <template v-else>
                  <div class="grid sm:grid-cols-2 gap-3 text-xs">
                    <div><span class="text-neutral-400">Email</span><br />{{ candidate.email }}</div>
                    <div><span class="text-neutral-400">Education</span><br />{{ candidate.education }}</div>
                  </div>
                  <div v-if="candidate.skills" class="mt-3">
                    <p class="text-xs text-neutral-400 mb-1">All Skills</p>
                    <div class="flex flex-wrap gap-1.5">
                      <span
                        v-for="skill in candidate.skills.split(',')"
                        :key="skill"
                        class="text-xs px-2 py-0.5 rounded-full bg-primary-50 text-primary-600"
                      >{{ skill.trim() }}</span>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>

        <ResumeLibraryPanel class="mt-8" />
      </div>

      <div v-if="tab === 'postjob'">
        <div class="grid gap-6 lg:grid-cols-[1fr_280px] items-start">
          <div class="dashboard-shell p-6 sm:p-8">
            <div class="mb-6">
              <p class="section-eyebrow">Hiring</p>
              <h2 class="section-title mt-1">Post a new role</h2>
            </div>

            <div v-if="jobPosted" class="mb-6 px-4 py-3 rounded-xl bg-success-50 text-success-700 text-sm font-medium border border-success-100">
              Job posted successfully!
            </div>

            <form @submit.prevent="postJob" class="space-y-5">
              <div class="grid sm:grid-cols-2 gap-4">
                <div>
                  <label class="text-xs font-medium text-neutral-600 mb-1.5 block">Job Title *</label>
                  <input v-model="jobForm.title" type="text" placeholder="Senior Frontend Engineer" class="w-full px-4 py-3 rounded-xl border border-neutral-200 text-sm focus:ring-2 focus:ring-primary-200 focus:border-primary-400 focus:outline-none" required />
                </div>
                <div>
                  <label class="text-xs font-medium text-neutral-600 mb-1.5 block">Company</label>
                  <input v-model="jobForm.company" type="text" class="w-full px-4 py-3 rounded-xl border border-neutral-200 text-sm focus:ring-2 focus:ring-primary-200 focus:border-primary-400 focus:outline-none" />
                </div>
              </div>

              <div class="grid sm:grid-cols-3 gap-4">
                <div>
                  <label class="text-xs font-medium text-neutral-600 mb-1.5 block">Location</label>
                  <input v-model="jobForm.location" type="text" placeholder="Remote" class="w-full px-4 py-3 rounded-xl border border-neutral-200 text-sm focus:ring-2 focus:ring-primary-200 focus:border-primary-400 focus:outline-none" />
                </div>
                <div>
                  <label class="text-xs font-medium text-neutral-600 mb-1.5 block">Type</label>
                  <select v-model="jobForm.type" class="w-full px-4 py-3 rounded-xl border border-neutral-200 text-sm focus:ring-2 focus:ring-primary-200 focus:border-primary-400 focus:outline-none">
                    <option>Full-time</option>
                    <option>Part-time</option>
                    <option>Contract</option>
                    <option>Internship</option>
                  </select>
                </div>
                <div>
                  <label class="text-xs font-medium text-neutral-600 mb-1.5 block">Experience</label>
                  <input v-model="jobForm.experience" type="text" placeholder="2-5 yrs" class="w-full px-4 py-3 rounded-xl border border-neutral-200 text-sm focus:ring-2 focus:ring-primary-200 focus:border-primary-400 focus:outline-none" />
                </div>
              </div>

              <div class="grid sm:grid-cols-2 gap-4">
                <div>
                  <label class="text-xs font-medium text-neutral-600 mb-1.5 block">Skills</label>
                  <input v-model="jobForm.skills" type="text" placeholder="React, Node.js, TypeScript" class="w-full px-4 py-3 rounded-xl border border-neutral-200 text-sm focus:ring-2 focus:ring-primary-200 focus:border-primary-400 focus:outline-none" />
                </div>
                <div>
                  <label class="text-xs font-medium text-neutral-600 mb-1.5 block">Salary</label>
                  <input v-model="jobForm.salary" type="text" placeholder="$80k – $120k" class="w-full px-4 py-3 rounded-xl border border-neutral-200 text-sm focus:ring-2 focus:ring-primary-200 focus:border-primary-400 focus:outline-none" />
                </div>
              </div>

              <div>
                <label class="text-xs font-medium text-neutral-600 mb-1.5 block">Description *</label>
                <textarea v-model="jobForm.description" rows="5" placeholder="Role responsibilities and requirements…" class="w-full px-4 py-3 rounded-xl border border-neutral-200 text-sm focus:ring-2 focus:ring-primary-200 focus:border-primary-400 focus:outline-none resize-none" required></textarea>
              </div>

              <button type="submit" :disabled="postingJob" class="btn-press w-full py-3 rounded-xl bg-primary-600 text-white text-sm font-medium hover:bg-primary-700 disabled:opacity-50 flex items-center justify-center gap-2">
                <Plus class="w-4 h-4" />
                {{ postingJob ? 'Posting…' : 'Post Job' }}
              </button>
            </form>
          </div>

          <aside class="dashboard-shell p-5 lg:sticky lg:top-24">
            <p class="section-eyebrow">Tips</p>
            <ul class="mt-4 space-y-3">
              <li
                v-for="(tip, i) in jobPostingTips"
                :key="tip"
                class="flex items-start gap-3 text-sm text-neutral-600"
              >
                <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary-50 text-xs font-semibold text-primary-700">{{ i + 1 }}</span>
                {{ tip }}
              </li>
            </ul>
          </aside>
        </div>
      </div>

      <div v-if="tab === 'myjobs'">
        <div class="flex items-center justify-between mb-6">
          <div>
            <p class="section-eyebrow">Openings</p>
            <h2 class="section-title mt-1">
              My Jobs
              <span v-if="!loadingJobs" class="text-neutral-400 font-normal text-lg ml-1">({{ myJobs.length }})</span>
            </h2>
          </div>
          <button @click="switchTab('postjob')" class="btn-press inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-primary-600 text-white text-sm font-medium hover:bg-primary-700">
            <Plus class="w-4 h-4" /> New job
          </button>
        </div>

        <div v-if="loadingJobs" class="space-y-3">
          <div v-for="i in 3" :key="i" class="dashboard-shell p-6 animate-pulse">
            <div class="h-4 bg-neutral-200 rounded w-1/3 mb-2"></div>
            <div class="h-3 bg-neutral-100 rounded w-1/2"></div>
          </div>
        </div>
        <div v-else-if="myJobs.length === 0" class="text-center py-16 rounded-2xl border border-dashed border-neutral-200 bg-neutral-50/50">
          <Briefcase class="w-10 h-10 mx-auto text-neutral-300 mb-3" />
          <h3 class="text-base font-semibold text-neutral-700">No jobs yet</h3>
          <p class="text-sm text-neutral-400 mt-1 mb-5">Post your first opening to start receiving applications.</p>
          <button @click="switchTab('postjob')" class="btn-press px-5 py-2.5 bg-primary-600 text-white text-sm rounded-xl font-medium inline-flex items-center gap-2 hover:bg-primary-700">
            <Plus class="w-4 h-4" /> Post a Job
          </button>
        </div>
        <div v-else class="space-y-3">
          <div v-for="job in myJobs" :key="job.id" class="dashboard-card dashboard-card-hover p-5 sm:p-6">
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <h3 class="text-base font-semibold text-neutral-900">{{ job.title }}</h3>
                <p class="text-sm text-neutral-500 mt-0.5">{{ job.company }} · {{ job.location }}</p>
              </div>
              <div class="flex items-center gap-2 shrink-0">
                <span class="text-xs px-2.5 py-1 rounded-full bg-primary-50 text-primary-700 font-medium">{{ job.type }}</span>
                <button
                  @click="startEditJob(job)"
                  class="btn-press inline-flex items-center gap-1 rounded-lg border border-neutral-200 px-2.5 py-1.5 text-xs text-neutral-600 hover:bg-neutral-50"
                >
                  <Pencil class="w-3.5 h-3.5" /> Edit
                </button>
              </div>
            </div>

            <div v-if="editingJobId === job.id" class="mt-4 rounded-xl border border-primary-100 bg-primary-50/50 p-4">
              <div class="grid gap-3 sm:grid-cols-2">
                <input v-model="editingJobForm.title" type="text" placeholder="Job title" class="w-full px-3 py-2.5 rounded-lg border border-neutral-200 text-sm" />
                <input v-model="editingJobForm.location" type="text" placeholder="Location" class="w-full px-3 py-2.5 rounded-lg border border-neutral-200 text-sm" />
                <select v-model="editingJobForm.type" class="w-full px-3 py-2.5 rounded-lg border border-neutral-200 text-sm">
                  <option>Full-time</option>
                  <option>Part-time</option>
                  <option>Contract</option>
                  <option>Internship</option>
                </select>
                <input v-model="editingJobForm.experience" type="text" placeholder="Experience" class="w-full px-3 py-2.5 rounded-lg border border-neutral-200 text-sm" />
                <input v-model="editingJobForm.skills" type="text" placeholder="Skills" class="w-full px-3 py-2.5 rounded-lg border border-neutral-200 text-sm sm:col-span-2" />
                <input v-model="editingJobForm.salary" type="text" placeholder="Salary" class="w-full px-3 py-2.5 rounded-lg border border-neutral-200 text-sm" />
                <select v-model="editingJobForm.status" class="w-full px-3 py-2.5 rounded-lg border border-neutral-200 text-sm">
                  <option value="active">active</option>
                  <option value="paused">paused</option>
                  <option value="closed">closed</option>
                </select>
                <textarea v-model="editingJobForm.description" rows="4" placeholder="Description" class="w-full px-3 py-2.5 rounded-lg border border-neutral-200 text-sm resize-none sm:col-span-2"></textarea>
              </div>
              <div class="mt-3 flex gap-2">
                <button @click="cancelEditJob" class="btn-press px-3 py-2 rounded-lg border border-neutral-200 text-xs text-neutral-600 hover:bg-white">Cancel</button>
                <button
                  @click="saveJobEdit(job.id)"
                  :disabled="savingJob"
                  class="btn-press px-3 py-2 rounded-lg bg-primary-600 text-white text-xs font-medium hover:bg-primary-700 disabled:opacity-50"
                >
                  {{ savingJob ? 'Saving…' : 'Save changes' }}
                </button>
              </div>
            </div>

            <template v-else>
              <p class="text-sm text-neutral-600 mt-3 leading-relaxed line-clamp-2">{{ job.description }}</p>
              <div v-if="job.skills" class="mt-3 flex flex-wrap gap-1.5">
                <span v-for="skill in job.skills.split(',').slice(0, 5)" :key="skill" class="text-xs px-2 py-0.5 rounded-full bg-neutral-100 text-neutral-600">{{ skill.trim() }}</span>
              </div>
              <div class="mt-3 flex gap-4 text-xs text-neutral-400">
                <span v-if="job.experience"><Clock class="inline w-3 h-3 -mt-0.5" /> {{ job.experience }} yrs</span>
                <span v-if="job.salary">{{ job.salary }}</span>
                <span class="uppercase">{{ job.status || 'active' }}</span>
              </div>
            </template>

            <div class="mt-4">
              <button
                @click="toggleJobApplications(job.id)"
                class="btn-press inline-flex items-center gap-1.5 rounded-xl border border-neutral-200 px-3 py-1.5 text-xs font-medium text-neutral-600 hover:bg-neutral-50"
              >
                <Users class="w-3.5 h-3.5" />
                {{ expandedJobId === job.id ? 'Hide applicants' : 'View applicants' }}
              </button>
            </div>

            <div v-if="expandedJobId === job.id" class="mt-4 rounded-xl border border-neutral-200 bg-neutral-50/70 p-4">
              <p v-if="loadingApplicationsByJob[job.id]" class="text-sm text-neutral-500">Loading applications…</p>
              <p v-else-if="applicationsErrorByJob[job.id]" class="text-sm text-danger-500">{{ applicationsErrorByJob[job.id] }}</p>
              <p v-else-if="!(jobApplicationsById[job.id] || []).length" class="text-sm text-neutral-500">No one has applied yet.</p>
              <div v-else class="space-y-3">
                <article v-for="app in jobApplicationsById[job.id]" :key="app.id" class="rounded-xl border border-white bg-white p-3">
                  <div class="flex items-start justify-between gap-3">
                    <div class="min-w-0">
                      <p class="text-sm font-semibold text-neutral-900">{{ app.candidate_name }}</p>
                      <p class="text-xs text-neutral-500 truncate">{{ app.candidate_email }}</p>
                    </div>
                    <div class="text-right">
                      <p class="text-base font-bold text-neutral-900">{{ app.ats_score }}%</p>
                      <span
                        class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold"
                        :class="app.fit_for_job ? 'bg-success-50 text-success-700' : 'bg-warning-50 text-warning-700'"
                      >
                        <CheckCircle2 class="w-3 h-3" /> {{ app.fit_for_job ? 'Fit' : 'Needs review' }}
                      </span>
                    </div>
                  </div>
                  <div class="mt-2 grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] text-neutral-600">
                    <div class="rounded-lg bg-neutral-50 px-2 py-1">Skill: {{ app.breakdown?.skill_match ?? '-' }}</div>
                    <div class="rounded-lg bg-neutral-50 px-2 py-1">Title: {{ app.breakdown?.title_relevance ?? '-' }}</div>
                    <div class="rounded-lg bg-neutral-50 px-2 py-1">Resume: {{ app.breakdown?.resume_quality ?? '-' }}</div>
                    <div class="rounded-lg bg-neutral-50 px-2 py-1">Keywords: {{ app.breakdown?.keyword_strength ?? '-' }}</div>
                  </div>
                  <p v-if="app.resume_excerpt" class="mt-2 text-xs text-neutral-500 leading-5">{{ app.resume_excerpt }}...</p>
                </article>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <SearchConfigModal
      :open="showSearchModal"
      :initial="modalInitial"
      @close="showSearchModal = false"
      @search="onModalSearch"
    />

    <AppFooter />
  </div>
</template>
