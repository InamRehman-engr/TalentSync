<script setup>
import { ref, computed } from "vue";
import Navbar from "../components/Navbar.vue";
import AppFooter from "../components/AppFooter.vue";
import {
  CheckCircle2, X, ArrowRight, Zap, HelpCircle,
  ChevronDown, Shield, CreditCard, Clock, Sparkles
} from "lucide-vue-next";

const billingCycle = ref("monthly");

const plans = [
  {
    name: "Basic",
    description: "For small teams getting started",
    monthlyPrice: 99,
    yearlyPrice: 1050,
    cta: "Start Basic Plan",
    ctaStyle: "border border-neutral-200 text-neutral-900 hover:bg-neutral-50",
    highlighted: false,
    features: [
      { text: "Up to 25 employees", included: true },
      { text: "20 active job postings", included: true },
      { text: "Basic candidate scoring", included: true },
      { text: "Career page (TalentSync branded)", included: true },
      { text: "Email support", included: true },
      { text: "AI CoPilot", included: false },
      { text: "Voice Answers", included: false },
      { text: "Custom pipeline stages", included: false },
      { text: "People analytics", included: false },
      { text: "API access", included: false },
    ],
  },
  {
    name: "Pro",
    description: "For growing companies",
    monthlyPrice: 299,
    yearlyPrice: 3450,
    cta: "Start Free Trial",
    ctaStyle: "bg-primary-600 text-white hover:bg-primary-700 shadow-lg shadow-primary-200",
    highlighted: true,
    badge: "Most Popular",
    features: [
      { text: "Up to 200 employees", included: true },
      { text: "Unlimited job postings", included: true },
      { text: "AI candidate scoring & ranking", included: true },
      { text: "Custom career page (your domain)", included: true },
      { text: "Priority email & chat support", included: true },
      { text: "AI CoPilot (full access)", included: true },
      { text: "Voice Answers screening", included: true },
      { text: "Basic analytics dashboard", included: true },
      { text: "Custom pipeline stages", included: false },
      { text: "API access", included: false },
    ],
  },
  {
    name: "Enterprise",
    description: "For large organizations",
    monthlyPrice: null,
    yearlyPrice: null,
    cta: "Contact Sales",
    ctaStyle: "border border-neutral-200 text-neutral-900 hover:bg-neutral-50",
    highlighted: false,
    features: [
      { text: "Unlimited employees", included: true },
      { text: "Unlimited job postings", included: true },
      { text: "AI scoring + custom models", included: true },
      { text: "White-label career pages", included: true },
      { text: "Dedicated account manager", included: true },
      { text: "AI CoPilot (custom trained)", included: true },
      { text: "Voice Answers + transcription", included: true },
      { text: "Advanced custom workflows", included: true },
      { text: "Advanced analytics & exports", included: true },
      { text: "Full API & webhook access", included: true },
    ],
  },
];

// Full feature comparison table
const comparisonCategories = [
  {
    name: "Hiring & Sourcing",
    features: [
      { label: "Active job postings", basic: "3", pro: "Unlimited", enterprise: "Unlimited" },
      { label: "Career page", basic: "Branded", pro: "Custom domain", enterprise: "White-label" },
      { label: "AI job description generator", basic: false, pro: true, enterprise: true },
      { label: "Job board distribution", basic: false, pro: "5 boards", enterprise: "Unlimited" },
    ],
  },
  {
    name: "Screening & Assessment",
    features: [
      { label: "Candidate scoring", basic: "Basic", pro: "AI-powered", enterprise: "Custom models" },
      { label: "Resume parsing", basic: true, pro: true, enterprise: true },
      { label: "Voice Answers", basic: false, pro: true, enterprise: true },
      { label: "Custom screening questions", basic: false, pro: true, enterprise: true },
    ],
  },
  {
    name: "Workflow & Automation",
    features: [
      { label: "Pipeline stages", basic: "Default", pro: "Custom", enterprise: "Advanced" },
      { label: "AI CoPilot", basic: false, pro: true, enterprise: "Custom trained" },
      { label: "Automated scheduling", basic: false, pro: true, enterprise: true },
      { label: "API & webhooks", basic: false, pro: false, enterprise: true },
    ],
  },
  {
    name: "Analytics & Support",
    features: [
      { label: "Analytics dashboard", basic: false, pro: "Basic", enterprise: "Advanced + export" },
      { label: "Team members", basic: "Up to 25", pro: "Up to 200", enterprise: "Unlimited" },
      { label: "Support", basic: "Email", pro: "Email & chat", enterprise: "Dedicated manager" },
      { label: "SLA guarantee", basic: false, pro: false, enterprise: true },
    ],
  },
];

const showComparison = ref(false);

const faqs = computed(() => {
  const basicSavings = savingsPercent(plans[0]);
  const proSavings = savingsPercent(plans[1]);
  return [
    { q: "Is there a free trial?", a: "Yes — the Pro plan comes with a 14-day free trial with full access. No credit card required to start." },
    { q: "Can I switch plans at any time?", a: "Absolutely. You can upgrade or downgrade your plan at any time. Changes take effect on your next billing cycle, and you'll only be charged the prorated difference." },
    { q: "What payment methods do you accept?", a: "We accept all major credit cards (Visa, Mastercard, Amex), as well as wire transfer for Enterprise plans." },
    { q: "Do you offer discounts for nonprofits?", a: "Yes, we offer discounts for registered nonprofits and educational institutions. Contact us to apply." },
    { q: "What happens if I exceed my plan limits?", a: "You'll receive a notification and can upgrade seamlessly. We'll never cut off your access unexpectedly — your data is always safe." },
    { q: "Can I cancel anytime?", a: "Yes, you can cancel your subscription at any point with no penalties. You'll retain full access until the end of your current billing period." },
    { q: "Do you offer annual billing?", a: `Yes — switch to yearly billing and save up to ${basicSavings}% on Basic and ${proSavings}% on Pro. Enterprise pricing is always custom.` },
  ];
});

const openFaq = ref(null);
function toggleFaq(idx) {
  openFaq.value = openFaq.value === idx ? null : idx;
}

function savingsPercent(plan) {
  if (!plan.monthlyPrice || !plan.yearlyPrice) return 0;
  const monthlyTotal = plan.monthlyPrice * 12;
  return Math.round(((monthlyTotal - plan.yearlyPrice) / monthlyTotal) * 100);
}

function yearlyPerMonth(plan) {
  if (!plan.yearlyPrice) return 0;
  // return Math.round(plan.yearlyPrice / 12);
  return Math.round(plan.yearlyPrice);
}
</script>

<template>
  <div class="min-h-screen bg-white">
    <Navbar />

    <!-- Hero — dark with floating toggle -->
    <section class="relative overflow-hidden bg-hero">
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-hero-glow/40 via-transparent to-transparent"></div>
      <div class="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 sm:pt-24 pb-32 sm:pb-40 text-center">
        <p class="text-sm font-semibold text-primary-400 tracking-wide uppercase mb-4">Pricing</p>
        <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight text-white leading-tight">
          Plans that grow
          <br class="hidden sm:block" />
          with your team
        </h1>
        <p class="mt-5 text-base sm:text-lg text-neutral-400 max-w-xl mx-auto leading-relaxed">
          No hidden fees, no surprises. Start with a 14-day free trial on Pro.
        </p>

        <!-- Billing Toggle — floating pill -->
        <div class="mt-8 inline-flex items-center gap-1 bg-white/10 backdrop-blur-sm rounded-full p-1 border border-white/10">
          <button
            @click="billingCycle = 'monthly'"
            class="btn-press px-5 py-2 rounded-full text-sm font-medium transition-all"
            :class="billingCycle === 'monthly' ? 'bg-white text-neutral-900 shadow-md' : 'text-neutral-300 hover:text-white'"
          >Monthly</button>
          <button
            @click="billingCycle = 'yearly'"
            class="btn-press px-5 py-2 rounded-full text-sm font-medium transition-all"
            :class="billingCycle === 'yearly' ? 'bg-white text-neutral-900 shadow-md' : 'text-neutral-300 hover:text-white'"
          >
            Yearly
            <span class="ml-1.5 text-xs text-success-400 font-semibold">Save {{ savingsPercent(plans[0]) }}%</span>
          </button>
        </div>
      </div>
    </section>

    <!-- Pricing Cards — pulled up to overlap hero -->
    <section class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 -mt-20 sm:-mt-24 relative z-10 pb-16 sm:pb-20">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5 items-start">
        <div
          v-for="plan in plans"
          :key="plan.name"
          class="rounded-2xl p-6 sm:p-8 transition-all duration-300 bg-white"
          :class="[
            plan.highlighted
              ? 'ring-2 ring-primary-600 shadow-2xl shadow-primary-200/40 relative md:-mt-4 md:pb-10 order-first md:order-none'
              : 'border border-neutral-200 shadow-lg shadow-neutral-100/60 hover:shadow-xl hover:border-primary-200'
          ]"
        >
          <!-- Badge -->
          <div v-if="plan.badge" class="absolute -top-3.5 left-1/2 -translate-x-1/2">
            <span class="inline-flex items-center gap-1.5 bg-primary-600 text-white text-xs font-semibold px-4 py-1.5 rounded-full shadow-lg shadow-primary-300/40">
              <Sparkles class="w-3 h-3" />
              {{ plan.badge }}
            </span>
          </div>

          <h3 class="text-lg font-bold text-neutral-900">{{ plan.name }}</h3>
          <p class="text-sm text-neutral-500 mt-1">{{ plan.description }}</p>

          <!-- Price -->
          <div class="mt-6 mb-2">
            <template v-if="plan.monthlyPrice !== null">
              <div class="flex items-baseline gap-1">
                <span class="text-4xl sm:text-5xl font-extrabold text-neutral-900">
                  ${{ billingCycle === 'monthly' ? plan.monthlyPrice : yearlyPerMonth(plan) }}
                </span>
                <span class="text-neutral-400 text-sm font-medium">{{ billingCycle === 'monthly' ? '/user/mo' : '/user/yr' }}</span>
              </div>
            </template>
            <template v-else>
              <span class="text-4xl sm:text-5xl font-extrabold text-neutral-900">Custom</span>
              <p class="text-sm text-neutral-500 mt-1">Tailored to your needs</p>
            </template>
          </div>

          <!-- Savings Tag -->
          <div class="mb-6 h-5">
            <span
              v-if="billingCycle === 'yearly' && savingsPercent(plan) > 0"
              class="text-xs font-semibold text-success-700 bg-success-50 px-2.5 py-0.5 rounded-full"
            >
              Save {{ savingsPercent(plan) }}% vs monthly
            </span>
            <span
              v-else-if="plan.monthlyPrice !== null && billingCycle === 'monthly'"
              class="text-xs text-neutral-400"
            >
              Billed monthly
            </span>
          </div>

          <!-- CTA -->
          <router-link
            to="/demo"
            class="btn-press block w-full text-center py-3.5 rounded-full text-sm font-semibold transition-colors"
            :class="plan.ctaStyle"
          >
            {{ plan.cta }}
          </router-link>

          <!-- Divider -->
          <div class="my-6 border-t border-neutral-100"></div>

          <!-- Features -->
          <p class="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-4">What's included</p>
          <ul class="space-y-3">
            <li
              v-for="f in plan.features"
              :key="f.text"
              class="flex items-center gap-2.5 text-[13px]"
              :class="f.included ? 'text-neutral-700' : 'text-neutral-400'"
            >
              <CheckCircle2 v-if="f.included" class="w-4 h-4 text-success-500 shrink-0" />
              <X v-else class="w-4 h-4 text-neutral-300 shrink-0" />
              {{ f.text }}
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Compare Plans Toggle -->
    <section class="max-w-6xl mx-auto px-6 lg:px-8 pb-6">
      <div class="text-center">
        <button
          @click="showComparison = !showComparison"
          class="btn-press inline-flex items-center gap-2 text-sm font-semibold text-primary-600 hover:text-primary-800 transition-colors"
        >
          {{ showComparison ? 'Hide comparison' : 'Compare all features' }}
          <ChevronDown class="w-4 h-4 transition-transform" :class="showComparison ? 'rotate-180' : ''" />
        </button>
      </div>
    </section>

    <!-- Feature Comparison Table - Desktop -->
    <section v-if="showComparison" class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 sm:pb-24">
      <!-- Desktop table -->
      <div class="hidden sm:block rounded-2xl border border-neutral-200 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-neutral-200 bg-neutral-50">
                <th class="text-left py-4 px-6 font-semibold text-neutral-900 w-2/5">Feature</th>
                <th class="text-center py-4 px-4 font-semibold text-neutral-900">Basic</th>
                <th class="text-center py-4 px-4 font-semibold text-primary-700 bg-primary-50/50">Pro</th>
                <th class="text-center py-4 px-4 font-semibold text-neutral-900">Enterprise</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="category in comparisonCategories" :key="category.name">
                <tr class="bg-neutral-50/50">
                  <td colspan="4" class="px-6 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">
                    {{ category.name }}
                  </td>
                </tr>
                <tr v-for="feature in category.features" :key="feature.label" class="border-b border-neutral-100 last:border-0">
                  <td class="py-3.5 px-6 text-neutral-700">{{ feature.label }}</td>
                  <td class="py-3.5 px-4 text-center" v-for="tier in ['basic', 'pro', 'enterprise']" :key="tier" :class="tier === 'pro' ? 'bg-primary-50/30' : ''">
                    <template v-if="feature[tier] === true">
                      <CheckCircle2 class="w-4 h-4 text-success-500 mx-auto" />
                    </template>
                    <template v-else-if="feature[tier] === false">
                      <X class="w-4 h-4 text-neutral-300 mx-auto" />
                    </template>
                    <template v-else>
                      <span class="text-neutral-600 font-medium">{{ feature[tier] }}</span>
                    </template>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Mobile comparison cards -->
      <div class="sm:hidden space-y-4">
        <div v-for="category in comparisonCategories" :key="category.name" class="rounded-xl border border-neutral-200 overflow-hidden">
          <div class="bg-neutral-50 px-4 py-2.5">
            <h4 class="text-xs font-semibold text-neutral-500 uppercase tracking-wider">{{ category.name }}</h4>
          </div>
          <div class="divide-y divide-neutral-100">
            <div v-for="feature in category.features" :key="feature.label" class="px-4 py-3">
              <p class="text-sm font-medium text-neutral-800 mb-2">{{ feature.label }}</p>
              <div class="grid grid-cols-3 gap-2 text-center">
                <div v-for="tier in ['basic', 'pro', 'enterprise']" :key="tier">
                  <p class="text-[10px] uppercase tracking-wide font-semibold mb-1" :class="tier === 'pro' ? 'text-primary-600' : 'text-neutral-400'">{{ tier }}</p>
                  <div v-if="feature[tier] === true" class="flex justify-center">
                    <CheckCircle2 class="w-4 h-4 text-success-500" />
                  </div>
                  <div v-else-if="feature[tier] === false" class="flex justify-center">
                    <X class="w-4 h-4 text-neutral-300" />
                  </div>
                  <span v-else class="text-xs text-neutral-600 font-medium">{{ feature[tier] }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Trust Signals — inline row -->
    <section class="border-y border-neutral-100">
      <div class="max-w-5xl mx-auto px-6 lg:px-8 py-10">
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-xl bg-success-50 flex items-center justify-center shrink-0">
              <Shield class="w-5 h-5 text-success-600" />
            </div>
            <div>
              <h4 class="text-sm font-semibold text-neutral-900">14-Day Free Trial</h4>
              <p class="text-xs text-neutral-500">Full Pro access, no card needed</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center shrink-0">
              <CreditCard class="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h4 class="text-sm font-semibold text-neutral-900">No Hidden Fees</h4>
              <p class="text-xs text-neutral-500">Cancel anytime, keep your data</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-xl bg-violet-50 flex items-center justify-center shrink-0">
              <Clock class="w-5 h-5 text-violet-600" />
            </div>
            <div>
              <h4 class="text-sm font-semibold text-neutral-900">Setup in 5 Minutes</h4>
              <p class="text-xs text-neutral-500">Start hiring right away</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQs — two column on desktop -->
    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
      <div class="grid lg:grid-cols-5 gap-10">
        <div class="lg:col-span-2">
          <p class="text-sm font-semibold text-primary-600 tracking-wide uppercase mb-3">FAQ</p>
          <h2 class="text-2xl sm:text-3xl font-bold text-neutral-900 mb-4">Common questions</h2>
          <p class="text-neutral-500 text-sm leading-relaxed">
            Can't find what you need?
            <router-link to="/demo" class="text-primary-600 hover:text-primary-800 font-medium">Talk to our team</router-link>.
          </p>
        </div>
        <div class="lg:col-span-3 space-y-3">
          <div
            v-for="(faq, idx) in faqs"
            :key="idx"
            class="rounded-xl border border-neutral-100 overflow-hidden hover:border-primary-200 transition-colors"
          >
            <button
              @click="toggleFaq(idx)"
              class="btn-press w-full flex items-center justify-between px-5 py-4 text-left"
            >
              <span class="text-sm font-medium text-neutral-900">{{ faq.q }}</span>
              <ChevronDown
                class="w-4 h-4 text-neutral-400 shrink-0 transition-transform duration-200"
                :class="openFaq === idx ? 'rotate-180' : ''"
              />
            </button>
            <div v-if="openFaq === idx" class="px-5 pb-4">
              <p class="text-sm text-neutral-500 leading-relaxed">{{ faq.a }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Bottom CTA — gradient band -->
    <section class="relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-r from-cta-start via-cta-mid to-cta-end"></div>
      <div class="relative max-w-4xl mx-auto px-6 py-14 sm:py-20 flex flex-col md:flex-row items-center justify-between gap-8">
        <div>
          <h2 class="text-2xl sm:text-3xl font-bold text-white mb-2">Still deciding?</h2>
          <p class="text-primary-100 text-sm sm:text-base">Book a free demo and we'll help you pick the right plan.</p>
        </div>
        <div class="flex flex-col sm:flex-row gap-3 shrink-0">
          <router-link
            to="/demo"
            class="btn-press inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-full bg-white text-primary-700 font-semibold hover:bg-primary-50 transition-colors"
          >
            Book a Demo
            <ArrowRight class="w-4 h-4" />
          </router-link>
          <router-link
            to="/features"
            class="btn-press inline-flex items-center justify-center px-7 py-3.5 rounded-full text-white font-medium border border-white/30 hover:bg-white/10 transition-colors"
          >
            Explore Features
          </router-link>
        </div>
      </div>
    </section>

    <AppFooter />
  </div>
</template>
