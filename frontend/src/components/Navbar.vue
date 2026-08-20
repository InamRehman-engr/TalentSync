<script setup>
import { ref, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { Menu, X, LogOut, User } from "lucide-vue-next";
import { useAuthStore } from "../stores/auth";
import { showEmployeeDashboard, showQuickDemo } from "../router/index";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const mobileOpen = ref(false);

const navLinks = [
  { label: "Features", to: "/features" },
  { label: "Solutions", to: "/solutions" },
  { label: "Pricing", to: "/pricing" },
  { label: "Hiring Guide", to: "/guide" },
  { label: "About", to: "/about" },
];

function isActive(path) {
  return route.path === path;
}

const dashboardLink = computed(() => {
  if (!auth.isLoggedIn) return null;
  if (auth.isEmployer) return "/employer";
  if (auth.isEmployee && showEmployeeDashboard) return "/employee";
  return null;
});

function handleLogout() {
  auth.logout();
  router.push("/");
}
</script>

<template>
  <nav class="sticky top-0 z-50 bg-white/70 backdrop-blur-xl border-b border-neutral-100/80">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-2.5 shrink-0">
          <img src="/favicon.svg" alt="TalentSync" class="w-8 h-8 rounded-lg" />
          <span class="text-lg font-bold tracking-tight text-neutral-900">TalentSync</span>
        </router-link>

        <!-- Desktop Links — centered pill bar -->
        <div class="hidden lg:flex items-center bg-neutral-50 rounded-full px-1.5 py-1">
          <router-link
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="px-4 py-1.5 rounded-full text-[13px] font-medium transition-all"
            :class="isActive(link.to) ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-500 hover:text-neutral-800'"
          >
            {{ link.label }}
          </router-link>
        </div>

        <!-- Desktop CTA -->
        <div class="hidden lg:flex items-center gap-2">
          <template v-if="auth.isLoggedIn">
            <router-link
              :to="dashboardLink"
              class="inline-flex items-center gap-1.5 text-sm font-medium text-neutral-600 hover:text-neutral-900 px-3 py-2 rounded-lg hover:bg-neutral-50 transition-colors"
            >
              <User class="w-4 h-4" />
              {{ auth.user?.name || 'Dashboard' }}
            </router-link>
            <button
              @click="handleLogout"
              class="btn-press inline-flex items-center gap-1.5 text-sm font-medium px-3 py-2 rounded-lg text-neutral-500 hover:text-neutral-700 hover:bg-neutral-50 transition-colors"
            >
              <LogOut class="w-4 h-4" /> Logout
            </button>
          </template>
          <template v-else>
            <router-link
              to="/login"
              class="text-sm font-medium text-neutral-600 hover:text-neutral-900 px-4 py-2 rounded-lg transition-colors"
            >
              Sign in
            </router-link>
            <router-link
              v-if="showQuickDemo"
              to="/demo"
              class="btn-press text-sm font-semibold px-5 py-2 rounded-full bg-primary-600 text-white hover:bg-primary-700 transition-colors"
            >
              Get Started
            </router-link>
          </template>
        </div>

        <!-- Mobile Toggle -->
        <button
          @click="mobileOpen = !mobileOpen"
          class="btn-press lg:hidden p-2 rounded-lg hover:bg-neutral-50"
        >
          <X v-if="mobileOpen" class="w-5 h-5 text-neutral-600" />
          <Menu v-else class="w-5 h-5 text-neutral-600" />
        </button>
      </div>
    </div>

    <!-- Mobile Menu -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
    <div v-if="mobileOpen" class="lg:hidden bg-white border-t border-neutral-100 px-4 sm:px-6 py-3 space-y-1">
      <router-link
        v-for="link in navLinks"
        :key="link.to"
        :to="link.to"
        @click="mobileOpen = false"
        class="block px-4 py-3 rounded-xl text-sm font-medium transition-colors"
        :class="isActive(link.to) ? 'text-primary-700 bg-primary-50' : 'text-neutral-600 hover:bg-neutral-50'"
      >
        {{ link.label }}
      </router-link>
      <div class="pt-3 border-t border-neutral-100 space-y-1">
        <template v-if="auth.isLoggedIn">
          <router-link :to="dashboardLink" @click="mobileOpen = false" class="block px-4 py-3 rounded-xl text-sm font-medium text-neutral-600 hover:bg-neutral-50">{{ auth.user?.name || 'Dashboard' }}</router-link>
          <button @click="handleLogout(); mobileOpen = false" class="block w-full text-left px-4 py-3 rounded-xl text-sm font-medium text-danger-600 hover:bg-danger-50">Logout</button>
        </template>
        <template v-else>
          <router-link to="/login" @click="mobileOpen = false" class="block px-4 py-3 rounded-xl text-sm font-medium text-neutral-600 hover:bg-neutral-50">Sign in</router-link>
          <router-link v-if="showQuickDemo" to="/demo" @click="mobileOpen = false" class="block px-4 py-3 rounded-full text-sm font-semibold text-center bg-primary-600 text-white mt-2">Get Started</router-link>
        </template>
      </div>
    </div>
    </transition>
  </nav>
</template>
