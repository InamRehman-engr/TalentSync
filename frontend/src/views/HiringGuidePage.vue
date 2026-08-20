<script setup>
import Navbar from "../components/Navbar.vue";
import AppFooter from "../components/AppFooter.vue";
import { showQuickDemo } from "../router/index";
import {
  FileText, Target, Search, CheckCircle2, ArrowRight, Briefcase, Sparkles,
} from "lucide-vue-next";

const employerTips = [
  {
    title: "Write job posts for humans and ATS",
    body: "Use a clear title, must-have skills up front, and separate nice-to-haves. TalentSync scores applicants against the role you publish.",
  },
  {
    title: "Search across every talent source",
    body: "Combine your talent pool, applications, uploaded resumes, and GitHub in one search instead of checking each channel manually.",
  },
  {
    title: "Review fit with context",
    body: "Use ATS breakdowns for skill match, title relevance, resume quality, and keyword strength before shortlisting candidates.",
  },
];

const candidateTips = [
  {
    title: "Mirror the job description",
    body: "Reuse the employer's language for skills, tools, and outcomes. Generic resumes score lower against role-specific postings.",
  },
  {
    title: "Quantify impact",
    body: "Replace vague bullets with metrics — time saved, revenue influenced, users supported, or delivery milestones.",
  },
  {
    title: "Apply once, then improve",
    body: "Submit your best resume first. You can update your application later to refresh your ATS score for the same role.",
  },
];

const workflow = [
  { step: "1", title: "Employer posts a role", detail: "Define skills, experience, and requirements in TalentSync." },
  { step: "2", title: "Candidates apply", detail: "Resumes are parsed and scored automatically against the posting." },
  { step: "3", title: "AI-assisted review", detail: "Employers search, rank, and shortlist from one workspace." },
  { step: "4", title: "Move to interview", detail: "Focus time on high-fit candidates instead of manual screening." },
];
</script>

<template>
  <div class="min-h-screen bg-white">
    <Navbar />

    <section class="bg-neutral-950 text-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
        <p class="text-sm font-semibold text-primary-300 tracking-wide uppercase mb-3">Hiring Guide</p>
        <h1 class="text-3xl sm:text-4xl font-bold leading-tight max-w-3xl">
          Practical tips to hire faster and apply smarter
        </h1>
        <p class="mt-4 text-neutral-400 max-w-2xl leading-relaxed">
          Short, actionable guidance for employers and candidates using AI-assisted recruiting on TalentSync.
        </p>
      </div>
    </section>

    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
      <div class="flex items-center gap-3 mb-8">
        <div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
          <Briefcase class="w-5 h-5 text-primary-600" />
        </div>
        <div>
          <h2 class="text-xl font-semibold text-neutral-900">For employers</h2>
          <p class="text-sm text-neutral-500">Get better applicants and faster shortlists.</p>
        </div>
      </div>

      <div class="grid md:grid-cols-3 gap-5">
        <article
          v-for="tip in employerTips"
          :key="tip.title"
          class="rounded-2xl border border-neutral-100 bg-neutral-50/60 p-6"
        >
          <CheckCircle2 class="w-5 h-5 text-primary-600 mb-3" />
          <h3 class="font-semibold text-neutral-900">{{ tip.title }}</h3>
          <p class="mt-2 text-sm text-neutral-600 leading-relaxed">{{ tip.body }}</p>
        </article>
      </div>
    </section>

    <section class="bg-neutral-50 border-y border-neutral-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
        <div class="flex items-center gap-3 mb-8">
          <div class="w-10 h-10 rounded-xl bg-lime-100 flex items-center justify-center">
            <FileText class="w-5 h-5 text-lime-700" />
          </div>
          <div>
            <h2 class="text-xl font-semibold text-neutral-900">For candidates</h2>
            <p class="text-sm text-neutral-500">Improve your resume before you apply.</p>
          </div>
        </div>

        <div class="grid md:grid-cols-3 gap-5">
          <article
            v-for="tip in candidateTips"
            :key="tip.title"
            class="rounded-2xl border border-white bg-white p-6 shadow-sm"
          >
            <Target class="w-5 h-5 text-lime-600 mb-3" />
            <h3 class="font-semibold text-neutral-900">{{ tip.title }}</h3>
            <p class="mt-2 text-sm text-neutral-600 leading-relaxed">{{ tip.body }}</p>
          </article>
        </div>
      </div>
    </section>

    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
      <div class="flex items-center gap-3 mb-8">
        <div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
          <Search class="w-5 h-5 text-primary-600" />
        </div>
        <div>
          <h2 class="text-xl font-semibold text-neutral-900">How TalentSync fits in</h2>
          <p class="text-sm text-neutral-500">A simple hiring loop from posting to shortlist.</p>
        </div>
      </div>

      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          v-for="item in workflow"
          :key="item.step"
          class="rounded-2xl border border-neutral-100 p-5"
        >
          <span class="inline-flex h-8 w-8 items-center justify-center rounded-full bg-neutral-900 text-white text-sm font-semibold">
            {{ item.step }}
          </span>
          <h3 class="mt-4 font-semibold text-neutral-900">{{ item.title }}</h3>
          <p class="mt-2 text-sm text-neutral-600 leading-relaxed">{{ item.detail }}</p>
        </div>
      </div>

      <div class="mt-10 flex flex-col sm:flex-row gap-3">
        <router-link
          to="/features"
          class="btn-press inline-flex items-center justify-center gap-2 rounded-full bg-primary-600 px-6 py-3 text-sm font-semibold text-white hover:bg-primary-700"
        >
          Explore features <ArrowRight class="w-4 h-4" />
        </router-link>
        <router-link
          v-if="showQuickDemo"
          to="/demo"
          class="btn-press inline-flex items-center justify-center gap-2 rounded-full border border-neutral-200 px-6 py-3 text-sm font-semibold text-neutral-700 hover:bg-neutral-50"
        >
          <Sparkles class="w-4 h-4" /> Book a demo
        </router-link>
      </div>
    </section>

    <AppFooter />
  </div>
</template>
