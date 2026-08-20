<script setup>
import Navbar from "../components/Navbar.vue";
import AppFooter from "../components/AppFooter.vue";
import {
  Zap, Target, Heart, Globe2, ArrowRight,
  MapPin, Quote, Star
} from "lucide-vue-next";

const testimonials = [
  {
    name: "Zainab Rida",
    role: "Data Analyst",
    quote: "The ATS resume review by TalentSync was very helpful. The report provided clear suggestions and highlighted important keywords needed for data analyst roles. Highly recommended for job seekers looking to improve their resumes.",
    image: "/img1.jpg",
    rating: 5,
  },
  {
    name: "Hasnain Raza",
    role: "Ethically Professional",
    quote: "I highly recommend the services provided by TalentSync to anyone who wants to improve their resume and increase their chances of getting noticed by recruiters. This is where the expertise of TalentSync truly makes a difference.",
    image: "/img2.jpg",
    rating: 5,
  },
  {
    name: "Muhammed Umer Sajid",
    role: "Embedded System Engineer @ RISETech",
    quote: "I had a very great experience, especially with the review report which was excellent. TalentSync did an outstanding job and the response was very effective, so I would love to use TalentSync's services again.",
    image: "/img3.jpg",
    rating: 5,
  },
];



const values = [
  {
    icon: Target,
    title: "Mission-Driven",
    description: "We believe every company deserves access to world-class recruiting tools, not just enterprises with massive budgets.",
  },
  {
    icon: Heart,
    title: "People-First",
    description: "Hiring is fundamentally human. Our AI enhances — never replaces — the personal connections that make great hires.",
  },
  {
    icon: Zap,
    title: "Relentlessly Simple",
    description: "We obsess over removing complexity. Every feature is designed to save time, not add cognitive load.",
  },
  {
    icon: Globe2,
    title: "Globally Inclusive",
    description: "Built for distributed teams across every timezone, culture, and industry. Hiring should have no borders.",
  },
];

const team = [
  {
    name: "Nija Asif",
    role: "Founder, Business",
    bio: "Nija Asif is Founder of TalentSync and leads the business division — covering growth, partnerships, and operations. With experience in technical support and business management, she bridges product insight with go-to-market strategy. She conceived the idea behind TalentSync and developed the initial n8n automation pipeline to streamline candidate matching.",
    avatar: "https://api.dicebear.com/9.x/notionists/svg?seed=NijaAsif&backgroundColor=e0e7ff",
    location: "Islamabad, Pakistan",
  },
  {
    name: "Inam ur Rehman",
    role: "Founder & CTO",
    bio: "Inam ur Rehman is Founder and CTO of TalentSync, and led the majority of the platform’s technical build — from system architecture and the web app to AI-powered screening, resume intelligence, and production infrastructure. A Mechatronics Engineer with deep experience at the intersection of hardware and software, he turns complex hiring workflows into scalable, reliable product systems.",
    avatar: "https://api.dicebear.com/9.x/notionists/svg?seed=InamRehman&backgroundColor=ddd6fe",
    location: "Islamabad, Pakistan",
  },
];

const timeline = [
  { year: "Dec 2025", title: "The Idea", description: "The TalentSync vision took shape: fix the broken hiring pipeline with an AI-powered platform built for real recruiting workflows." },
  { year: "Jan 2026", title: "Core Platform", description: "Inam ur Rehman designed the system architecture and began building the core TalentSync platform — laying the foundation for AI-driven candidate screening and matching." },
  { year: "Feb 2026", title: "MVP Launch", description: "Inam delivered the full MVP: web platform, backend services, and intelligent resume evaluation — turning the concept into a working product." },
  { year: "Apr 2026", title: "Hatch 8 Incubator", description: "Accepted into the Hatch 8 program in April 2026 — validating the vision and accelerating our path to market." },
  { year: "2026", title: "What's Next", description: "Scaling the platform for production, launching publicly, and building advanced AI features including predictive hiring analytics and a mobile app." },
];


</script>

<template>
  <div class="min-h-screen bg-white">
    <Navbar />

    <!-- Hero — left aligned, no gradient blob -->
    <section class="border-b border-neutral-100">
      <div class="max-w-7xl mx-auto px-6 lg:px-8 py-16 sm:py-24">
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <p class="text-sm font-semibold text-primary-600 tracking-wide uppercase mb-3">Our Story</p>
            <h1 class="text-4xl sm:text-5xl font-bold tracking-tight text-neutral-900 leading-tight">
              We're building the future of
              <span class="text-primary-600">hiring</span>
            </h1>
            <p class="mt-5 text-lg text-neutral-500 leading-relaxed">
              TalentSync was born from a simple frustration: hiring is broken. Too many tools, too much manual work,
              and too many great candidates falling through the cracks. We're here to fix that.
            </p>
          </div>
          <!-- Values grid replaces right side -->
          <div class="grid grid-cols-2 gap-4">
            <div v-for="v in values" :key="v.title" class="rounded-2xl border border-neutral-100 p-5 hover:border-primary-200 hover:shadow-md transition-all">
              <component :is="v.icon" class="w-5 h-5 text-primary-600 mb-3" />
              <h3 class="text-sm font-semibold text-neutral-900 mb-1">{{ v.title }}</h3>
              <p class="text-xs text-neutral-500 leading-relaxed">{{ v.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonials -->
    <section class="py-16 sm:py-20">
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <div class="text-center mb-12">
          <p class="text-sm font-semibold text-primary-600 tracking-wide uppercase mb-3">Testimonials</p>
          <h2 class="text-3xl font-bold text-neutral-900">Trusted by hiring teams everywhere</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div
            v-for="t in testimonials"
            :key="t.name"
            class="rounded-2xl border border-neutral-100 overflow-hidden hover:border-primary-200 hover:shadow-lg transition-all relative group"
          >
            <!-- Screenshot -->
            <div class="relative">
              <img
                :src="t.image"
                :alt="t.name + ' review'"
                class="w-full object-contain bg-white p-2"
              />
            </div>
            <!-- Content -->
            <div class="p-6">
              <div class="flex items-center gap-0.5 mb-3">
                <Star
                  v-for="s in 5"
                  :key="s"
                  class="w-4 h-4"
                  :class="s <= t.rating ? 'text-warning-400 fill-warning-400' : 'text-neutral-200'"
                />
              </div>
              <p class="text-sm text-neutral-600 leading-relaxed mb-4">"{{ t.quote }}"</p>
              <div class="flex items-center gap-3">
                <div>
                  <h4 class="text-sm font-semibold text-neutral-900">{{ t.name }}</h4>
                  <p class="text-xs text-neutral-500">{{ t.role }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Timeline — horizontal on desktop -->
    <section class="bg-neutral-50 border-b border-neutral-100">
      <div class="max-w-7xl mx-auto px-6 lg:px-8 py-16 sm:py-20">
        <p class="text-sm font-semibold text-primary-600 tracking-wide uppercase mb-3">Milestones</p>
        <h2 class="text-3xl font-bold text-neutral-900 mb-12">Our journey</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-0">
          <div
            v-for="(item, idx) in timeline"
            :key="idx"
            class="relative px-6 py-8"
            :class="idx < timeline.length - 1 ? 'lg:border-r border-b lg:border-b-0 border-neutral-200' : ''"
          >
            <span class="text-xs font-bold text-primary-600 uppercase tracking-wider">{{ item.year }}</span>
            <h3 class="text-base font-semibold text-neutral-900 mt-2 mb-1">{{ item.title }}</h3>
            <p class="text-sm text-neutral-500 leading-relaxed">{{ item.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Team — card layout -->
    <section class="py-16 sm:py-20">
      <div class="max-w-5xl mx-auto px-6 lg:px-8">
        <div class="mb-12">
          <p class="text-sm font-semibold text-primary-600 tracking-wide uppercase mb-3">Team</p>
          <h2 class="text-3xl font-bold text-neutral-900">Meet the founders</h2>
        </div>
        <div class="grid md:grid-cols-2 gap-6">
          <div
            v-for="member in team"
            :key="member.name"
            class="rounded-2xl border border-neutral-100 p-7 hover:border-primary-200 hover:shadow-lg transition-all group"
          >
            <div class="flex items-center gap-4 mb-5">
              <img :src="member.avatar" :alt="member.name" class="w-14 h-14 rounded-xl bg-neutral-100" />
              <div>
                <h3 class="text-base font-semibold text-neutral-900 group-hover:text-primary-700 transition-colors">{{ member.name }}</h3>
                <p class="text-sm text-primary-600 font-medium">{{ member.role }}</p>
              </div>
            </div>
            <p class="text-sm text-neutral-500 leading-relaxed mb-4">{{ member.bio }}</p>
            <div class="flex items-center gap-1.5 text-xs text-neutral-400">
              <MapPin class="w-3 h-3" />
              {{ member.location }}
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA — gradient band -->
    <section class="relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-r from-cta-start via-cta-mid to-cta-end"></div>
      <div class="relative max-w-4xl mx-auto px-6 py-16 sm:py-20 flex flex-col md:flex-row items-center justify-between gap-8">
        <div>
          <h2 class="text-2xl sm:text-3xl font-bold text-white mb-2">Want to join our mission?</h2>
          <p class="text-neutral-400">We're always looking for talented people who want to reshape recruitment.</p>
        </div>
        <div class="flex flex-col sm:flex-row gap-3 shrink-0">
          <router-link
            to="/demo"
            class="btn-press inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-full bg-primary-600 text-white font-semibold hover:bg-primary-500 transition-colors"
          >
            Book a Demo
            <ArrowRight class="w-4 h-4" />
          </router-link>
          <a
            href="#"
            class="btn-press inline-flex items-center justify-center px-7 py-3.5 rounded-full text-neutral-300 font-medium border border-neutral-600 hover:bg-neutral-700 transition-colors"
          >
            View Open Roles
          </a>
        </div>
      </div>
    </section>

    <AppFooter />
  </div>
</template>
