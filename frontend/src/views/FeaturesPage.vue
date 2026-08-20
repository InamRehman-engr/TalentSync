<script setup>
import Navbar from "../components/Navbar.vue";
import AppFooter from "../components/AppFooter.vue";
import {
  ArrowRight, Briefcase, FileSearch, Sparkles, Upload, Users,
} from "lucide-vue-next";

const workflow = [
  {
    step: "01",
    title: "Post the role",
    body: "Skills, experience range, and location feed straight into scoring.",
    icon: Briefcase,
  },
  {
    step: "02",
    title: "Collect resumes",
    body: "Applications, bulk PDF upload, talent pool, or GitHub search.",
    icon: Upload,
  },
  {
    step: "03",
    title: "Review matches",
    body: "ATS score plus a short AI write-up for each person on that role.",
    icon: FileSearch,
  },
];

const groups = [
  {
    name: "Hiring workflow",
    icon: Briefcase,
    tint: "from-lime-50 to-white",
    items: [
      { title: "Job postings", detail: "Create and edit listings, track applicants per role, close when filled." },
      { title: "Application inbox", detail: "See who applied, read excerpts, sort by fit without leaving the dashboard." },
      { title: "Resume library", detail: "Single files or ZIP batches — parsed text and history stay attached." },
    ],
  },
  {
    name: "Scoring & search",
    icon: Sparkles,
    tint: "from-neutral-50 to-white",
    items: [
      { title: "ATS scoring", detail: "Keyword, skills, and title match — same logic candidates see when applying." },
      { title: "AI resume review", detail: "A short paragraph on strengths and gaps, not just a number." },
      { title: "Talent pool search", detail: "Filter by skills, experience, and location across pool and uploads." },
      { title: "GitHub discovery", detail: "Public profiles by language and location for technical roles." },
    ],
  },
  {
    name: "For candidates",
    icon: Users,
    tint: "from-lime-50/60 to-white",
    items: [
      { title: "Browse open roles", detail: "Jobs grouped by company. Search by title, skills, or location." },
      { title: "Apply with file or paste", detail: "PDF upload or pasted text — instant ATS feedback before submit." },
      { title: "Application history", detail: "Track applications and the score you got at submission time." },
    ],
  },
];

const snapshots = [
  { label: "Avg. time to first score", value: "< 1 min" },
  { label: "Resume formats", value: "PDF · DOCX · TXT" },
  { label: "Accounts", value: "Employer + Employee" },
];
</script>

<template>
  <div class="min-h-screen bg-neutral-50">
    <Navbar />

    <!-- Hero -->
    <section class="relative overflow-hidden border-b border-neutral-200 bg-white">
      <div
        class="absolute inset-0 opacity-60 pointer-events-none"
        style="background: radial-gradient(ellipse 70% 60% at 100% 0%, rgba(190,242,100,0.25), transparent 55%);"
      />
      <div class="relative max-w-6xl mx-auto px-5 sm:px-8 py-14 sm:py-20">
        <div class="grid lg:grid-cols-[1fr_280px] gap-10 lg:gap-14 items-end">
          <div>
            <p class="section-eyebrow mb-3">Features</p>
            <h1 class="text-3xl sm:text-[2.35rem] font-semibold text-neutral-900 tracking-tight max-w-xl leading-[1.15]">
              What you can actually do in TalentSync today.
            </h1>
            <p class="mt-4 text-base text-neutral-600 max-w-lg leading-relaxed">
              Built for hiring managers who want scores and notes on real resumes — not a slide deck of future integrations.
            </p>
            <router-link
              to="/login"
              class="btn-press mt-7 inline-flex items-center gap-2 text-sm font-semibold text-primary-700 hover:text-primary-800"
            >
              Try the employer dashboard
              <ArrowRight class="w-4 h-4" />
            </router-link>
          </div>

          <!-- Mini stat stack -->
          <div class="hidden sm:flex flex-col gap-2">
            <div
              v-for="snap in snapshots"
              :key="snap.label"
              class="dashboard-card px-4 py-3 flex items-baseline justify-between gap-4"
            >
              <span class="text-xs text-neutral-500">{{ snap.label }}</span>
              <span class="text-sm font-semibold text-neutral-900 tabular-nums">{{ snap.value }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Workflow -->
    <section class="max-w-6xl mx-auto px-5 sm:px-8 py-14 sm:py-16">
      <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-10">
        <div>
          <h2 class="section-title">How employers use it</h2>
          <p class="mt-1 text-sm text-neutral-500">Most teams are reviewing candidates the same day they post.</p>
        </div>
        <span class="text-xs font-mono text-neutral-400 hidden sm:block">3 steps</span>
      </div>

      <div class="relative grid md:grid-cols-3 gap-5">
        <div
          class="hidden md:block absolute top-12 left-[16%] right-[16%] h-px bg-gradient-to-r from-transparent via-lime-300 to-transparent"
          aria-hidden="true"
        />
        <div
          v-for="item in workflow"
          :key="item.step"
          class="dashboard-card-hover dashboard-card relative p-6 sm:p-7 group"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="w-10 h-10 rounded-xl bg-primary-50 border border-primary-100 flex items-center justify-center">
              <component :is="item.icon" class="w-5 h-5 text-primary-700" />
            </div>
            <span class="text-4xl font-bold text-neutral-100 group-hover:text-primary-100 transition-colors tabular-nums">
              {{ item.step }}
            </span>
          </div>
          <h3 class="mt-5 text-lg font-semibold text-neutral-900">{{ item.title }}</h3>
          <p class="mt-2 text-sm text-neutral-600 leading-relaxed">{{ item.body }}</p>
        </div>
      </div>
    </section>

    <!-- Product peek -->
    <section class="border-y border-neutral-200 bg-white">
      <div class="max-w-6xl mx-auto px-5 sm:px-8 py-12 sm:py-14">
        <div class="grid lg:grid-cols-2 gap-10 items-center">
          <div class="employer-hero p-6 sm:p-8 font-mono text-[11px] sm:text-xs leading-relaxed text-neutral-300 overflow-hidden">
            <div class="flex items-center gap-2 mb-4">
              <span class="w-2 h-2 rounded-full bg-lime-400" />
              <span class="w-2 h-2 rounded-full bg-neutral-600" />
              <span class="w-2 h-2 rounded-full bg-neutral-600" />
              <span class="ml-2 text-neutral-500">employer · candidates</span>
            </div>
            <p class="text-lime-300/90">Senior Backend Engineer</p>
            <p class="mt-3 text-neutral-500"># applications · sorted by fit</p>
            <div class="mt-4 space-y-2">
              <div class="flex justify-between py-2 border-b border-white/5">
                <span>Sara K.</span>
                <span class="text-lime-400">87</span>
              </div>
              <div class="flex justify-between py-2 border-b border-white/5">
                <span>James O.</span>
                <span class="text-lime-400">74</span>
              </div>
              <div class="flex justify-between py-2 opacity-60">
                <span>… 12 more</span>
                <span>—</span>
              </div>
            </div>
          </div>
          <div>
            <p class="text-sm text-neutral-600 leading-relaxed">
              The dashboard is plain on purpose: job on the left, ranked people on the right, AI notes when you expand a row.
              No configuration wizard before you see your first score.
            </p>
            <p class="mt-4 text-sm text-neutral-500 italic border-l-2 border-lime-400 pl-4">
              “We built this because we were tired of opening forty PDFs and still not knowing who to call first.”
              <span class="not-italic block mt-1 text-xs text-neutral-400">— TalentSync team</span>
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Feature groups -->
    <section class="max-w-6xl mx-auto px-5 sm:px-8 py-14 sm:py-16 space-y-8">
      <h2 class="section-title">By area</h2>
      <div
        v-for="group in groups"
        :key="group.name"
        class="dashboard-shell overflow-hidden"
      >
        <div
          class="grid lg:grid-cols-[220px_1fr] bg-gradient-to-br"
          :class="group.tint"
        >
          <div class="p-6 sm:p-8 border-b lg:border-b-0 lg:border-r border-neutral-100 flex flex-col justify-between gap-6">
            <div>
              <div class="w-11 h-11 rounded-2xl bg-white border border-neutral-200 shadow-sm flex items-center justify-center mb-4">
                <component :is="group.icon" class="w-5 h-5 text-primary-700" />
              </div>
              <h3 class="text-lg font-semibold text-neutral-900">{{ group.name }}</h3>
            </div>
            <span class="text-xs text-neutral-400">{{ group.items.length }} items</span>
          </div>
          <dl class="divide-y divide-neutral-100">
            <div
              v-for="(item, idx) in group.items"
              :key="item.title"
              class="grid sm:grid-cols-[10rem_1fr] gap-2 sm:gap-6 px-6 sm:px-8 py-5 hover:bg-white/80 transition-colors"
            >
              <dt class="text-sm font-medium text-neutral-900 flex items-start gap-2">
                <span class="text-[10px] font-mono text-neutral-300 mt-0.5">{{ String(idx + 1).padStart(2, '0') }}</span>
                {{ item.title }}
              </dt>
              <dd class="text-sm text-neutral-600 leading-relaxed">{{ item.detail }}</dd>
            </div>
          </dl>
        </div>
      </div>
    </section>

    <!-- Scope note -->
    <section class="max-w-6xl mx-auto px-5 sm:px-8 pb-8">
      <div class="rounded-2xl border border-dashed border-neutral-300 bg-white/80 px-6 py-5 sm:px-8">
        <p class="text-sm font-medium text-neutral-800">Still on the roadmap</p>
        <p class="mt-1 text-sm text-neutral-600 leading-relaxed">
          Voice screening, calendar sync, and onboarding checklists. We would rather ship one workflow well than pretend everything is live.
        </p>
      </div>
    </section>

    <!-- CTA -->
    <section class="max-w-6xl mx-auto px-5 sm:px-8 pb-16 sm:pb-20">
      <div class="employer-hero px-6 sm:px-10 py-10 sm:py-12 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
        <div>
          <h2 class="text-xl sm:text-2xl font-semibold text-white">Post a role. Upload three resumes.</h2>
          <p class="mt-2 text-sm text-neutral-400 max-w-md">
            You will know within a minute if the scoring is useful for your hiring — no sales call required.
          </p>
        </div>
        <router-link
          to="/login"
          class="btn-press inline-flex items-center justify-center gap-2 px-6 py-3 rounded-full bg-lime-500 text-neutral-900 text-sm font-semibold hover:bg-lime-400 transition-colors shrink-0"
        >
          Open the dashboard
          <ArrowRight class="w-4 h-4" />
        </router-link>
      </div>
    </section>

    <AppFooter />
  </div>
</template>
