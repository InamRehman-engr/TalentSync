<script setup>
import { ref } from "vue";
import Navbar from "../components/Navbar.vue";
import AppFooter from "../components/AppFooter.vue";
import {
  CheckCircle2, ArrowRight, CalendarCheck, Users,
  Zap, Shield, Clock, Headphones
} from "lucide-vue-next";

const form = ref({
  firstName: "",
  lastName: "",
  email: "",
  company: "",
  companySize: "",
  role: "",
  message: "",
});

const submitted = ref(false);

function handleSubmit() {
  // Mock submission
  submitted.value = true;
}

const benefits = [
  { icon: CalendarCheck, text: "30-minute personalized walkthrough" },
  { icon: Users, text: "See how it works for your team size" },
  { icon: Zap, text: "Live AI CoPilot demonstration" },
  { icon: Shield, text: "Security & compliance Q&A" },
  { icon: Clock, text: "No commitment — cancel anytime" },
  { icon: Headphones, text: "Dedicated onboarding support" },
];

const companySizes = [
  "1–10 employees",
  "11–50 employees",
  "51–200 employees",
  "201–500 employees",
  "500+ employees",
];
</script>

<template>
  <div class="min-h-screen bg-white">
    <Navbar />

    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-20">
      <div class="grid lg:grid-cols-5 gap-10 sm:gap-16 items-start">
        <!-- Left: Form (wider) -->
        <div class="lg:col-span-3 order-2 lg:order-1">
          <div class="rounded-2xl border border-neutral-100 p-5 sm:p-8 lg:p-10">
          <!-- Success state -->
          <div v-if="submitted" class="text-center py-12">
            <div class="w-16 h-16 rounded-2xl bg-success-50 flex items-center justify-center mx-auto mb-5">
              <CheckCircle2 class="w-8 h-8 text-success-600" />
            </div>
            <h3 class="text-xl font-semibold text-neutral-900 mb-2">Demo booked!</h3>
            <p class="text-sm text-neutral-500 leading-relaxed">
              We'll reach out within 24 hours to confirm your time slot.
              Check your inbox for a confirmation email.
            </p>
            <button @click="submitted = false" class="btn-press mt-6 text-sm text-primary-600 font-medium hover:text-primary-800">
              Submit another request
            </button>
          </div>

          <!-- Form -->
          <form v-else @submit.prevent="handleSubmit" class="space-y-5">
            <div>
              <h3 class="text-lg font-semibold text-neutral-900 mb-1">Book your demo</h3>
              <p class="text-sm text-neutral-500">Fill in your details and we'll get back to you within 24 hours.</p>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-neutral-700 mb-1.5">First name *</label>
                <input v-model="form.firstName" required type="text" class="w-full px-3.5 py-2.5 rounded-xl border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400" />
              </div>
              <div>
                <label class="block text-xs font-medium text-neutral-700 mb-1.5">Last name *</label>
                <input v-model="form.lastName" required type="text" class="w-full px-3.5 py-2.5 rounded-xl border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400" />
              </div>
            </div>

            <div>
              <label class="block text-xs font-medium text-neutral-700 mb-1.5">Work email *</label>
              <input v-model="form.email" required type="email" class="w-full px-3.5 py-2.5 rounded-xl border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400" />
            </div>

            <div>
              <label class="block text-xs font-medium text-neutral-700 mb-1.5">Company name *</label>
              <input v-model="form.company" required type="text" class="w-full px-3.5 py-2.5 rounded-xl border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400" />
            </div>

            <div>
              <label class="block text-xs font-medium text-neutral-700 mb-1.5">Company size *</label>
              <select v-model="form.companySize" required class="w-full px-3.5 py-2.5 rounded-xl border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400 appearance-none">
                <option value="" disabled>Select size</option>
                <option v-for="s in companySizes" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-medium text-neutral-700 mb-1.5">Your role</label>
              <input v-model="form.role" type="text" placeholder="e.g. Head of HR, CTO" class="w-full px-3.5 py-2.5 rounded-xl border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400" />
            </div>

            <div>
              <label class="block text-xs font-medium text-neutral-700 mb-1.5">Anything else?</label>
              <textarea v-model="form.message" rows="3" placeholder="Tell us about your hiring challenges…" class="w-full px-3.5 py-2.5 rounded-xl border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400 resize-none"></textarea>
            </div>

            <button
              type="submit"
              class="btn-press w-full flex items-center justify-center gap-2 py-3 rounded-full bg-primary-600 text-white text-sm font-semibold hover:bg-primary-700 transition-colors"
            >
              Book My Demo
              <ArrowRight class="w-4 h-4" />
            </button>

            <p class="text-xs text-neutral-400 text-center">
              By submitting, you agree to our Privacy Policy. No spam, ever.
            </p>
          </form>
          </div>
        </div>

        <!-- Right: Info sidebar -->
        <div class="lg:col-span-2 order-1 lg:order-2">
          <p class="text-sm font-semibold text-primary-600 tracking-wide uppercase mb-3">Free Demo</p>
          <h1 class="text-3xl sm:text-4xl font-bold tracking-tight text-neutral-900 leading-tight mb-5">
            See TalentSync
            <span class="text-primary-600">in action</span>
          </h1>
          <p class="text-neutral-500 leading-relaxed mb-10">
            Book a free 30-minute demo with our team. We'll show you how TalentSync
            can streamline your hiring workflow.
          </p>

          <!-- Benefits — compact list -->
          <div class="space-y-4">
            <div v-for="b in benefits" :key="b.text" class="flex items-start gap-3">
              <div class="w-8 h-8 rounded-lg bg-neutral-50 border border-neutral-100 flex items-center justify-center shrink-0 mt-0.5">
                <component :is="b.icon" class="w-3.5 h-3.5 text-primary-600" />
              </div>
              <span class="text-sm text-neutral-600">{{ b.text }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <AppFooter />
  </div>
</template>
