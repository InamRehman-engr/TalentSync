<script setup>
import { ref, computed } from "vue";
import Navbar from "../components/Navbar.vue";
import AppFooter from "../components/AppFooter.vue";
import { Clock, ArrowRight, Tag, User, Search } from "lucide-vue-next";

const searchQuery = ref("");
const activeCategory = ref("All");

const categories = ["All", "Recruiting", "HR Tech", "Product Updates", "Industry Insights", "Guides"];

const posts = [
  {
    id: 1,
    title: "The Future of AI in Recruitment: 2026 Trends",
    excerpt: "AI is reshaping how companies source, screen, and hire talent. Here's what every HR leader needs to know heading into 2026.",
    category: "Industry Insights",
    author: "Inam ul Haq",
    date: "Apr 10, 2026",
    readTime: "8 min read",
    image: "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=600&h=400&fit=crop",
    featured: true,
  },
  {
    id: 2,
    title: "How We Reduced Time-to-Hire by 73% with Smart Filters",
    excerpt: "A deep dive into how our AI scoring engine and automated pipelines help companies hire faster without sacrificing quality.",
    category: "Product Updates",
    author: "Ayesha Khan",
    date: "Apr 7, 2026",
    readTime: "6 min read",
    image: "https://images.unsplash.com/photo-1552664730-d307ca884978?w=600&h=400&fit=crop",
    featured: false,
  },
  {
    id: 3,
    title: "Best Recruiting Software for Startups in 2026",
    excerpt: "We compared 15 ATS platforms across pricing, features, and ease of use. Here's our honest breakdown for growing teams.",
    category: "Guides",
    author: "Omar Farouk",
    date: "Apr 3, 2026",
    readTime: "12 min read",
    image: "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=600&h=400&fit=crop",
    featured: false,
  },
  {
    id: 4,
    title: "Voice Screening: The Async Interview Revolution",
    excerpt: "Why top companies are replacing phone screens with asynchronous voice answers — and how to implement it in your pipeline.",
    category: "Recruiting",
    author: "Priya Sharma",
    date: "Mar 28, 2026",
    readTime: "7 min read",
    image: "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=600&h=400&fit=crop",
    featured: false,
  },
  {
    id: 5,
    title: "HR Software in Pakistan: A Complete Guide",
    excerpt: "The Pakistani HR tech market is booming. We explore the best solutions for local compliance, payroll, and talent management.",
    category: "Industry Insights",
    author: "Inam ul Haq",
    date: "Mar 22, 2026",
    readTime: "10 min read",
    image: "https://images.unsplash.com/photo-1497215842964-222b430dc094?w=600&h=400&fit=crop",
    featured: false,
  },
  {
    id: 6,
    title: "Building Bias-Free AI: Our Approach to Fair Hiring",
    excerpt: "How we designed TalentSync's AI to minimize bias in candidate scoring and promote equitable hiring outcomes.",
    category: "HR Tech",
    author: "Priya Sharma",
    date: "Mar 15, 2026",
    readTime: "9 min read",
    image: "https://images.unsplash.com/photo-1551434678-e076c223a692?w=600&h=400&fit=crop",
    featured: false,
  },
  {
    id: 7,
    title: "Introducing TalentSync CoPilot: Your AI HR Assistant",
    excerpt: "Meet the AI that writes job descriptions, suggests candidates, and automates your hiring workflow — all from natural language.",
    category: "Product Updates",
    author: "Ayesha Khan",
    date: "Mar 8, 2026",
    readTime: "5 min read",
    image: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=400&fit=crop",
    featured: false,
  },
  {
    id: 8,
    title: "5 Onboarding Mistakes That Cost You Great Hires",
    excerpt: "You spent weeks finding the perfect candidate. Don't lose them in the first 30 days with these avoidable onboarding mistakes.",
    category: "Recruiting",
    author: "Elena Vasquez",
    date: "Mar 1, 2026",
    readTime: "6 min read",
    image: "https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=600&h=400&fit=crop",
    featured: false,
  },
  {
    id: 9,
    title: "Remote Hiring Playbook: Lessons from 35 Countries",
    excerpt: "We've helped companies hire across 35 countries. Here's everything we learned about compliance, culture, and scaling remote teams.",
    category: "Guides",
    author: "Omar Farouk",
    date: "Feb 22, 2026",
    readTime: "14 min read",
    image: "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=600&h=400&fit=crop",
    featured: false,
  },
];

const filteredPosts = computed(() => {
  let result = posts;
  if (activeCategory.value !== "All") {
    result = result.filter((p) => p.category === activeCategory.value);
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(
      (p) => p.title.toLowerCase().includes(q) || p.excerpt.toLowerCase().includes(q)
    );
  }
  return result;
});

const featuredPost = computed(() => posts.find((p) => p.featured));
</script>

<template>
  <div class="min-h-screen bg-white">
    <Navbar />

    <!-- Hero — left aligned -->
    <section class="border-b border-neutral-100">
      <div class="max-w-7xl mx-auto px-6 lg:px-8 py-16 sm:py-20">
        <div class="max-w-2xl">
          <p class="text-sm font-semibold text-primary-600 tracking-wide uppercase mb-3">Blog</p>
          <h1 class="text-4xl sm:text-5xl font-bold tracking-tight text-neutral-900 leading-tight">
            Resources &
            <span class="text-primary-600">insights</span>
          </h1>
          <p class="mt-5 text-lg text-neutral-500 leading-relaxed">
            Guides, product updates, and industry insights to help you hire smarter.
          </p>
        </div>
      </div>
    </section>

    <!-- Featured Post -->
    <section class="max-w-6xl mx-auto px-6 lg:px-8 pb-16" v-if="featuredPost">
      <div class="glass rounded-2xl overflow-hidden grid md:grid-cols-2 gap-0 hover:shadow-lg hover:shadow-neutral-200/60 transition-all cursor-pointer group">
        <img :src="featuredPost.image" :alt="featuredPost.title" class="w-full h-64 md:h-full object-cover" />
        <div class="p-8 md:p-10 flex flex-col justify-center">
          <div class="flex items-center gap-3 mb-4">
            <span class="text-xs font-medium px-3 py-1 rounded-full bg-primary-50 text-primary-700">Featured</span>
            <span class="text-xs font-medium px-3 py-1 rounded-full bg-neutral-100 text-neutral-600">{{ featuredPost.category }}</span>
          </div>
          <h2 class="text-2xl font-bold text-neutral-900 mb-3 group-hover:text-primary-700 transition-colors">
            {{ featuredPost.title }}
          </h2>
          <p class="text-sm text-neutral-500 leading-relaxed mb-5">{{ featuredPost.excerpt }}</p>
          <div class="flex items-center gap-4 text-xs text-neutral-400">
            <span class="flex items-center gap-1"><User class="w-3 h-3" /> {{ featuredPost.author }}</span>
            <span>{{ featuredPost.date }}</span>
            <span class="flex items-center gap-1"><Clock class="w-3 h-3" /> {{ featuredPost.readTime }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Search & Filters -->
    <section class="max-w-6xl mx-auto px-6 lg:px-8 pb-8">
      <div class="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
        <!-- Search -->
        <div class="relative w-full md:w-80">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search articles…"
            class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-neutral-200 bg-neutral-50 text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400 transition-all"
          />
        </div>

        <!-- Category Pills -->
        <div class="flex flex-wrap gap-2">
          <button
            v-for="cat in categories"
            :key="cat"
            @click="activeCategory = cat"
            class="btn-press px-4 py-1.5 rounded-full text-xs font-medium transition-all"
            :class="activeCategory === cat
              ? 'bg-primary-600 text-white'
              : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'"
          >
            {{ cat }}
          </button>
        </div>
      </div>
    </section>

    <!-- Posts Grid -->
    <section class="max-w-6xl mx-auto px-6 lg:px-8 pb-24">
      <div v-if="filteredPosts.length === 0" class="text-center py-20">
        <p class="text-neutral-400 text-sm">No articles match your criteria.</p>
      </div>
      <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <article
          v-for="post in filteredPosts.filter(p => !p.featured)"
          :key="post.id"
          class="glass rounded-2xl overflow-hidden hover:shadow-lg hover:shadow-neutral-200/60 transition-all cursor-pointer group"
        >
          <img :src="post.image" :alt="post.title" class="w-full h-44 object-cover" />
          <div class="p-6">
            <div class="flex items-center gap-2 mb-3">
              <span class="text-xs font-medium px-2.5 py-0.5 rounded-full bg-neutral-100 text-neutral-600">
                {{ post.category }}
              </span>
            </div>
            <h3 class="text-base font-semibold text-neutral-900 mb-2 group-hover:text-primary-700 transition-colors leading-snug">
              {{ post.title }}
            </h3>
            <p class="text-sm text-neutral-500 leading-relaxed mb-4 line-clamp-2">{{ post.excerpt }}</p>
            <div class="flex items-center justify-between text-xs text-neutral-400">
              <span>{{ post.author }}</span>
              <span class="flex items-center gap-1"><Clock class="w-3 h-3" /> {{ post.readTime }}</span>
            </div>
          </div>
        </article>
      </div>
    </section>

    <!-- Newsletter — gradient band -->
    <section class="relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-r from-cta-start via-cta-mid to-cta-end"></div>
      <div class="relative max-w-4xl mx-auto px-6 py-14 sm:py-16 flex flex-col md:flex-row items-center justify-between gap-8">
        <div>
          <h2 class="text-2xl font-bold text-white mb-2">Stay ahead in HR tech</h2>
          <p class="text-primary-100 text-sm">Join 5,000+ HR leaders getting weekly insights on recruiting, AI, and team building.</p>
        </div>
        <div class="flex flex-col sm:flex-row gap-3 w-full md:w-auto shrink-0">
          <input
            type="email"
            placeholder="you@company.com"
            class="flex-1 md:w-64 px-4 py-3 rounded-full text-sm bg-white/10 border border-white/20 text-white placeholder-primary-200 focus:outline-none focus:ring-2 focus:ring-white/30"
          />
          <button class="btn-press px-6 py-3 rounded-full bg-white text-primary-700 text-sm font-semibold hover:bg-primary-50 transition-colors shrink-0">
            Subscribe
          </button>
        </div>
      </div>
    </section>

    <AppFooter />
  </div>
</template>
