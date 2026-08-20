<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import Navbar from "../components/Navbar.vue";
import AppFooter from "../components/AppFooter.vue";
import {
  ArrowRight, Building2, Code2, Search, UserRound,
} from "lucide-vue-next";

const activeId = ref("startups");

const solutions = [
  {
    id: "startups",
    label: "Small teams",
    icon: Building2,
    headline: "Your first five hires — no spreadsheet circus.",
    body: "One place to post roles, collect applications, and score resumes. Most teams review candidates the afternoon they sign up.",
    fit: [
      "Founders doing recruiting themselves",
      "Teams under ~30 with a few open roles",
      "Anyone who wants scoring before buying Greenhouse or Lever",
    ],
    notFit: "Multi-country payroll, SSO, approval chains — not yet.",
    aside: "Typical week: post Tuesday, shortlist by Thursday.",
  },
  {
    id: "tech",
    label: "Tech & product",
    icon: Code2,
    headline: "Stack in the JD. Depth in the notes.",
    body: "PDF and DOCX parsing, GitHub search for passive candidates, and AI summaries that mention projects — not just keyword hits.",
    fit: [
      "Backend, frontend, full-stack with explicit skill lists",
      "Teams drowning in PDFs per role",
      "Managers who want a paragraph per candidate",
    ],
    notFit: "Live coding tests and ATS integrations — planned.",
    aside: "GitHub search works best when you know the stack already.",
  },
  {
    id: "agencies",
    label: "Recruiters",
    icon: Search,
    headline: "Forty CVs. One brief. Fast scores.",
    body: "Separate employer accounts per client, or one account with clear job titles. Bulk upload when you are working from a shared folder.",
    fit: [
      "Boutique recruiters scoring batches against a brief",
      "Staffing firms prepping a client call",
      "Anyone tired of ctrl-F through identical resumes",
    ],
    notFit: "White-label portals and client billing — roadmap.",
    aside: "We know agencies juggle clients — keep titles obvious.",
  },
  {
    id: "candidates",
    label: "Job seekers",
    icon: UserRound,
    headline: "See your fit before you hit submit.",
    body: "Browse by company, apply with a file or paste, get ATS feedback immediately. Update your resume and resubmit without duplicate applications.",
    fit: [
      "Active applicants who want feedback on fit",
      "Career switchers tailoring per role",
      "People who prefer knowing the score upfront",
    ],
    notFit: "Job alerts and one-click apply to external boards.",
    aside: "Scores reflect the JD you applied to — tailor when you can.",
  },
];

let observer = null;

onMounted(() => {
  const sections = solutions.map((s) => document.getElementById(s.id)).filter(Boolean);
  observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((e) => e.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (visible?.target?.id) activeId.value = visible.target.id;
    },
    { rootMargin: "-30% 0px -55% 0px", threshold: [0, 0.25, 0.5] },
  );
  sections.forEach((el) => observer.observe(el));
});

onUnmounted(() => {
  observer?.disconnect();
});

function scrollTo(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}
</script>

<template>
  <div class="min-h-screen bg-neutral-50">
    <Navbar />

    <!-- Hero -->
    <section class="relative overflow-hidden border-b border-neutral-200 bg-white">
      <div
        class="absolute -left-20 top-0 w-72 h-72 rounded-full bg-primary-100/40 blur-3xl pointer-events-none"
        aria-hidden="true"
      />
      <div class="relative max-w-6xl mx-auto px-5 sm:px-8 py-14 sm:py-20">
        <div class="max-w-2xl">
          <p class="section-eyebrow mb-3">Solutions</p>
          <h1 class="text-3xl sm:text-[2.35rem] font-semibold text-neutral-900 tracking-tight leading-[1.15]">
            Four kinds of people who get value from TalentSync <span class="text-neutral-400">right now</span>.
          </h1>
          <p class="mt-4 text-base text-neutral-600 leading-relaxed">
            Early-stage and honest — each section says what we do well and what we have not built yet.
          </p>
        </div>

        <!-- Quick nav chips -->
        <div class="mt-8 flex flex-wrap gap-2">
          <button
            v-for="sol in solutions"
            :key="sol.id"
            type="button"
            @click="scrollTo(sol.id)"
            class="btn-press inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium border transition-all"
            :class="activeId === sol.id
              ? 'bg-neutral-900 text-white border-neutral-900'
              : 'bg-white text-neutral-600 border-neutral-200 hover:border-neutral-300'"
          >
            <component :is="sol.icon" class="w-3.5 h-3.5" />
            {{ sol.label }}
          </button>
        </div>
      </div>
    </section>

    <div class="max-w-6xl mx-auto px-5 sm:px-8 py-12 sm:py-16">
      <div class="grid lg:grid-cols-[200px_1fr] gap-10 lg:gap-14">
        <!-- Sticky sidebar (desktop) -->
        <aside class="hidden lg:block">
          <nav class="sticky top-24 space-y-1">
            <button
              v-for="(sol, i) in solutions"
              :key="sol.id"
              type="button"
              @click="scrollTo(sol.id)"
              class="w-full text-left px-3 py-2.5 rounded-xl text-sm transition-colors flex items-center gap-3"
              :class="activeId === sol.id
                ? 'bg-white border border-neutral-200 text-neutral-900 font-medium shadow-sm'
                : 'text-neutral-500 hover:text-neutral-800 hover:bg-white/60'"
            >
              <span class="text-[10px] font-mono text-neutral-300 w-4">{{ String(i + 1).padStart(2, '0') }}</span>
              {{ sol.label }}
            </button>
          </nav>
        </aside>

        <!-- Solution blocks -->
        <div class="space-y-12 sm:space-y-16">
          <article
            v-for="(sol, index) in solutions"
            :key="sol.id"
            :id="sol.id"
            class="scroll-mt-24"
          >
            <div class="dashboard-shell overflow-hidden">
              <!-- Header band -->
              <div
                class="px-6 sm:px-8 py-5 border-b border-neutral-100 flex items-center justify-between gap-4"
                :class="index % 2 === 0 ? 'bg-gradient-to-r from-primary-50/80 to-white' : 'bg-neutral-50/80'"
              >
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-xl bg-white border border-neutral-200 flex items-center justify-center shadow-sm">
                    <component :is="sol.icon" class="w-4 h-4 text-primary-700" />
                  </div>
                  <span class="text-sm font-semibold text-neutral-900">{{ sol.label }}</span>
                </div>
                <span class="text-xs font-mono text-neutral-400">{{ String(index + 1).padStart(2, '0') }} / 04</span>
              </div>

              <div class="grid md:grid-cols-5 gap-0">
                <!-- Story -->
                <div class="md:col-span-3 p-6 sm:p-8 border-b md:border-b-0 md:border-r border-neutral-100">
                  <h2 class="text-xl sm:text-2xl font-semibold text-neutral-900 leading-snug">
                    {{ sol.headline }}
                  </h2>
                  <p class="mt-4 text-sm text-neutral-600 leading-relaxed">
                    {{ sol.body }}
                  </p>
                  <p class="mt-6 text-xs text-primary-800/80 bg-primary-50 inline-block px-3 py-1.5 rounded-lg border border-primary-100">
                    {{ sol.aside }}
                  </p>
                </div>

                <!-- Fit list -->
                <div class="md:col-span-2 p-6 sm:p-8 bg-white">
                  <p class="text-xs font-semibold uppercase tracking-wide text-neutral-400 mb-4">
                    Good fit if…
                  </p>
                  <ul class="space-y-3 mb-6">
                    <li
                      v-for="line in sol.fit"
                      :key="line"
                      class="text-sm text-neutral-700 leading-relaxed pl-3 border-l-2 border-lime-400"
                    >
                      {{ line }}
                    </li>
                  </ul>
                  <p class="text-xs text-neutral-500 pt-4 border-t border-neutral-100">
                    <span class="font-medium text-neutral-600">Not yet:</span>
                    {{ sol.notFit }}
                  </p>
                </div>
              </div>
            </div>
          </article>
        </div>
      </div>
    </div>

    <!-- CTA -->
    <section class="max-w-6xl mx-auto px-5 sm:px-8 pb-16 sm:pb-20">
      <div class="grid sm:grid-cols-2 gap-4">
        <div class="employer-hero p-6 sm:p-8 flex flex-col justify-between min-h-[180px]">
          <div>
            <h2 class="text-lg font-semibold text-white">Try the demo</h2>
            <p class="mt-2 text-sm text-neutral-400">Employer login on the sign-in page — post a job and upload a resume.</p>
          </div>
          <router-link
            to="/login"
            class="btn-press mt-6 inline-flex items-center gap-2 text-sm font-semibold text-lime-400 hover:text-lime-300 w-fit"
          >
            Sign in
            <ArrowRight class="w-4 h-4" />
          </router-link>
        </div>
        <div class="dashboard-card p-6 sm:p-8 flex flex-col justify-between min-h-[180px]">
          <div>
            <h2 class="text-lg font-semibold text-neutral-900">Questions?</h2>
            <p class="mt-2 text-sm text-neutral-600">Pricing, pilots, and feedback — we read everything on the contact page.</p>
          </div>
          <router-link
            to="/pricing"
            class="btn-press mt-6 inline-flex items-center gap-2 px-5 py-2.5 rounded-full border border-neutral-300 text-sm font-medium text-neutral-700 hover:border-neutral-400 w-fit"
          >
            Pricing & contact
          </router-link>
        </div>
      </div>
    </section>

    <AppFooter />
  </div>
</template>
