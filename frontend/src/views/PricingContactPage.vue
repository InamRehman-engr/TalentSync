<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import Navbar from "../components/Navbar.vue";
import AppFooter from "../components/AppFooter.vue";
import { pricingContactEmail } from "../runtimeConfig.js";
import { Mail, ArrowLeft, Sparkles } from "lucide-vue-next";

const router = useRouter();

const contactEmail = computed(() => pricingContactEmail || "hello@talentsync.com");
const mailtoLink = computed(() => `mailto:${contactEmail.value}?subject=TalentSync%20Pricing%20Inquiry`);
</script>

<template>
  <div class="min-h-screen bg-white relative overflow-hidden">
    <Navbar />

    <!-- Blurred page content behind the overlay -->
    <div class="pointer-events-none select-none blur-md opacity-60" aria-hidden="true">
      <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <p class="text-sm font-semibold text-primary-600 tracking-wide uppercase mb-4">Pricing</p>
        <h1 class="text-4xl sm:text-5xl font-bold text-neutral-900 leading-tight max-w-3xl">
          Plans that scale with your hiring team
        </h1>
        <p class="mt-5 text-lg text-neutral-500 max-w-2xl">
          From startup hiring to enterprise talent pipelines — flexible options for every stage of growth.
        </p>

        <div class="mt-12 grid md:grid-cols-3 gap-6">
          <div v-for="plan in ['Starter', 'Growth', 'Enterprise']" :key="plan" class="rounded-2xl border border-neutral-200 p-6 bg-white">
            <h2 class="text-xl font-semibold text-neutral-900">{{ plan }}</h2>
            <p class="mt-2 text-3xl font-bold text-neutral-900">—</p>
            <ul class="mt-6 space-y-2 text-sm text-neutral-500">
              <li>AI candidate scoring</li>
              <li>Resume library</li>
              <li>Employer workspace</li>
            </ul>
          </div>
        </div>
      </section>
    </div>

    <!-- Contact overlay -->
    <div class="fixed inset-0 z-40 flex items-center justify-center p-4 bg-neutral-900/35 backdrop-blur-sm">
      <div class="relative w-full max-w-lg rounded-2xl bg-white shadow-2xl border border-neutral-100 p-8 sm:p-10">
        <div class="w-12 h-12 rounded-2xl bg-primary-50 flex items-center justify-center mb-5">
          <Sparkles class="w-6 h-6 text-primary-600" />
        </div>

        <h1 class="text-2xl font-bold text-neutral-900">Pricing tailored to your team</h1>
        <p class="mt-3 text-sm text-neutral-600 leading-relaxed">
          We do not publish fixed pricing online. Every organization has different hiring volume,
          workflows, and integration needs — so we quote based on what you actually use.
        </p>
        <p class="mt-4 text-sm font-medium text-neutral-800">
          For pricing, contact us and we will share the right plan for your team.
        </p>

        <a
          :href="mailtoLink"
          class="btn-press mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-primary-600 px-5 py-3 text-sm font-semibold text-white hover:bg-primary-700 transition-colors"
        >
          <Mail class="w-4 h-4" />
          {{ contactEmail }}
        </a>

        <button
          type="button"
          @click="router.push('/')"
          class="btn-press mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl border border-neutral-200 px-5 py-3 text-sm font-medium text-neutral-700 hover:bg-neutral-50 transition-colors"
        >
          <ArrowLeft class="w-4 h-4" />
          Back to home
        </button>
      </div>
    </div>

    <AppFooter />
  </div>
</template>
