<script setup>
import { useRouter } from "vue-router";
import Navbar from "../components/Navbar.vue";
import AppFooter from "../components/AppFooter.vue";
import {
  Zap, Users, Filter, ArrowRight, Brain, Mic, CalendarCheck,
  BarChart3, Shield, CheckCircle2, Play, Sparkles, ArrowUpRight
} from "lucide-vue-next";

const router = useRouter();

function goToDashboard() {
  router.push("/dashboard");
}

const features = [
  { icon: Brain, title: "AI CoPilot", desc: "Intelligent assistant that writes JDs, screens resumes, and recommends candidates.", color: "indigo" },
  { icon: Users, title: "People Management", desc: "Centralized directory with org charts, document vault, and employee profiles.", color: "emerald" },
  { icon: Filter, title: "Smart Scoring", desc: "AI-powered candidate ranking based on skills, experience, and cultural fit.", color: "violet" },
  { icon: Mic, title: "Voice Answers", desc: "Async audio screening — evaluate candidates before the first interview.", color: "amber" },
  { icon: CalendarCheck, title: "Auto Scheduling", desc: "Candidates self-book interviews synced with your calendar. Zero back-and-forth.", color: "cyan" },
  { icon: Zap, title: "n8n Automation", desc: "Connect any workflow via webhooks to auto-ingest and process candidates.", color: "rose" },
];

const colorMap = {
  indigo: { bg: "bg-primary-50", icon: "text-primary-600" },
  emerald: { bg: "bg-success-50", icon: "text-success-600" },
  violet: { bg: "bg-violet-50", icon: "text-violet-600" },
  amber: { bg: "bg-warning-50", icon: "text-warning-600" },
  cyan: { bg: "bg-cyan-50", icon: "text-cyan-600" },
  rose: { bg: "bg-rose-50", icon: "text-rose-600" },
};

const stats = [
  { value: "73%", label: "Faster time-to-hire" },
  { value: "12+", label: "Candidates screened" },
  { value: "98.2%", label: "Uptime SLA" },
  { value: "100+", label: "Employers supported" },
];
</script>

<template>
  <div class="min-h-screen bg-white">
    <Navbar />

    <!-- Hero — left-aligned with decorative right column -->
    <section class="relative overflow-hidden bg-hero">
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-hero-glow/30 via-transparent to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28 lg:py-32">
        <div class="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-primary-300 text-xs font-medium mb-6 backdrop-blur-sm border border-white/10">
              <Sparkles class="w-3.5 h-3.5" />
              AI-Powered Recruitment Platform
            </div>

            <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-white leading-[1.1]">
              Hire smarter.
              <br />
              <span class="bg-gradient-to-r from-primary-400 to-cyan-400 bg-clip-text text-transparent">Grow faster.</span>
            </h1>

            <p class="mt-6 text-lg text-neutral-400 max-w-lg leading-relaxed">
              TalentSync connects employers with pre-screened candidates using
              AI scoring, smart filters, and workflow automation.
            </p>

            <div class="mt-8 flex flex-col sm:flex-row gap-3">
              <router-link
                to="/demo"
                class="btn-press inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-full bg-primary-600 text-white font-semibold hover:bg-primary-500 transition-colors"
              >
                Get Started Free
                <ArrowRight class="w-4 h-4" />
              </router-link>
              <button
                @click="goToDashboard"
                class="btn-press inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-full text-white font-medium border border-white/20 hover:bg-white/10 transition-colors"
              >
                <Play class="w-4 h-4" />
                Live Demo
              </button>
            </div>

            <p class="mt-4 text-xs text-neutral-500">Free for up to 25 employees · No credit card required</p>
          </div>

          <!-- Right side — stats grid -->
          <div class="hidden lg:grid grid-cols-2 gap-4">
            <div
              v-for="stat in stats"
              :key="stat.label"
              class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 text-center hover:bg-white/10 transition-colors"
            >
              <div class="text-3xl font-bold text-white mb-1">{{ stat.value }}</div>
              <div class="text-sm text-neutral-400">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Mobile stats bar -->
    <div class="lg:hidden bg-neutral-900 border-t border-neutral-800">
      <div class="max-w-7xl mx-auto px-4 py-6 grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div v-for="stat in stats" :key="stat.label" class="text-center">
          <div class="text-xl font-bold text-white">{{ stat.value }}</div>
          <div class="text-xs text-neutral-400">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- Features — alternating 2-col bento -->
    <section id="features" class="py-16 sm:py-24">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-2xl mb-14">
          <p class="text-sm font-semibold text-primary-600 tracking-wide uppercase mb-3">Platform</p>
          <h2 class="text-3xl sm:text-4xl font-bold text-neutral-900 mb-4">Everything you need to hire smarter</h2>
          <p class="text-neutral-500 leading-relaxed">From sourcing to onboarding — a complete toolkit powered by AI.</p>
        </div>

        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="(f, idx) in features"
            :key="f.title"
            class="group rounded-2xl border border-neutral-100 p-6 hover:border-primary-200 hover:shadow-lg hover:shadow-primary-50 transition-all duration-300"
            :class="idx === 0 ? 'sm:col-span-2 lg:col-span-1' : ''"
          >
            <div class="w-10 h-10 rounded-xl flex items-center justify-center mb-4" :class="colorMap[f.color].bg">
              <component :is="f.icon" class="w-5 h-5" :class="colorMap[f.color].icon" />
            </div>
            <h3 class="text-base font-semibold text-neutral-900 mb-2 group-hover:text-primary-700 transition-colors">{{ f.title }}</h3>
            <p class="text-sm text-neutral-500 leading-relaxed">{{ f.desc }}</p>
          </div>
        </div>

        <div class="mt-10">
          <router-link
            to="/features"
            class="btn-press inline-flex items-center gap-2 text-sm font-semibold text-primary-600 hover:text-primary-800 transition-colors"
          >
            Explore all features
            <ArrowUpRight class="w-4 h-4" />
          </router-link>
        </div>
      </div>
    </section>

    <!-- How It Works — horizontal numbered steps -->
    <section class="bg-neutral-50 border-y border-neutral-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div class="text-center mb-14">
          <p class="text-sm font-semibold text-primary-600 tracking-wide uppercase mb-3">Process</p>
          <h2 class="text-3xl font-bold text-neutral-900 mb-4">Three steps to smarter hiring</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-0">
          <div v-for="(step, idx) in [
            { n: '01', title: 'Post & Source', desc: 'Create AI-generated job descriptions and publish to your branded career page in one click.' },
            { n: '02', title: 'Screen & Score', desc: 'AI automatically scores and ranks candidates. Use voice screening before live interviews.' },
            { n: '03', title: 'Hire & Onboard', desc: 'Send offers, run automated onboarding checklists, and welcome new hires from TalentSync.' }
          ]" :key="idx"
            class="relative px-8 py-10 text-center md:text-left"
            :class="idx < 2 ? 'md:border-r border-b md:border-b-0 border-neutral-200' : ''"
          >
            <div class="text-5xl font-black text-neutral-100 mb-4">{{ step.n }}</div>
            <h3 class="text-lg font-semibold text-neutral-900 mb-2">{{ step.title }}</h3>
            <p class="text-sm text-neutral-500 leading-relaxed">{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Final CTA — gradient band -->
    <section class="relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-r from-cta-start via-cta-mid to-cta-end"></div>
      <div class="relative max-w-4xl mx-auto px-4 sm:px-6 py-16 sm:py-20 flex flex-col md:flex-row items-center justify-between gap-8">
        <div>
          <h2 class="text-2xl sm:text-3xl font-bold text-white mb-2">Ready to transform your hiring?</h2>
          <p class="text-primary-100 text-sm sm:text-base">Start using TalentSync to find, screen, and hire top talent faster.</p>
        </div>
        <div class="flex flex-col sm:flex-row gap-3 shrink-0">
          <router-link
            to="/demo"
            class="btn-press inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-full bg-white text-primary-700 font-semibold hover:bg-primary-50 transition-colors"
          >
            Get Started
            <ArrowRight class="w-4 h-4" />
          </router-link>
          <router-link
            to="/pricing"
            class="btn-press inline-flex items-center justify-center px-7 py-3.5 rounded-full text-white font-medium border border-white/30 hover:bg-white/10 transition-colors"
          >
            View Pricing
          </router-link>
        </div>
      </div>
    </section>

    <AppFooter />
  </div>
</template>
