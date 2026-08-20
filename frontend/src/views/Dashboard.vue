<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useCandidateStore } from "../stores/candidates";
import CandidateCard from "../components/CandidateCard.vue";
import SkeletonCard from "../components/SkeletonCard.vue";
import {
  Zap,
  Search,
  LayoutDashboard,
  Users,
  Filter,
  ArrowUpDown,
  Home,
  ChevronDown,
} from "lucide-vue-next";

const router = useRouter();
const store = useCandidateStore();

const searchInput = ref("");
const sidebarOpen = ref(true);

let debounceTimer = null;

function onSearch() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    store.setSearch(searchInput.value);
  }, 300);
}

onMounted(() => {
  store.loadCandidates();
});
</script>

<template>
  <div class="flex min-h-screen bg-neutral-50">
    <!-- Mobile Sidebar Overlay -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/40 z-40 lg:hidden"
      @click="sidebarOpen = false"
    ></div>

    <!-- Sidebar -->
    <aside
      class="w-64 bg-white border-r border-neutral-100 flex flex-col shrink-0 transition-all duration-300 z-50 fixed lg:static inset-y-0 left-0"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
    >
      <div class="flex items-center gap-2 px-6 py-6 border-b border-neutral-50">
        <Zap class="w-6 h-6 text-primary-600" :stroke-width="2.2" />
        <span class="text-lg font-semibold tracking-tight text-neutral-900"
          >TalentSync</span
        >
      </div>

      <nav class="flex-1 px-4 py-6 space-y-1">
        <button
          @click="router.push('/')"
          class="btn-press flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm text-neutral-500 hover:bg-neutral-50 transition-colors"
        >
          <Home class="w-4 h-4" />
          Home
        </button>
        <button
          class="btn-press flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium text-primary-700 bg-primary-50"
        >
          <LayoutDashboard class="w-4 h-4" />
          Dashboard
        </button>
        <button
          class="btn-press flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm text-neutral-500 hover:bg-neutral-50 transition-colors"
        >
          <Users class="w-4 h-4" />
          Candidates
        </button>
      </nav>

      <div class="px-6 py-4 border-t border-neutral-50 text-xs text-neutral-400">
        v1.0.0 &middot; Mocked Backend
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Top Bar -->
      <header class="bg-white border-b border-neutral-100 px-4 sm:px-8 py-4 flex items-center gap-3 sm:gap-4">
        <button
          @click="sidebarOpen = !sidebarOpen"
          class="btn-press p-2 rounded-lg hover:bg-neutral-50 lg:hidden shrink-0"
        >
          <Filter class="w-4 h-4 text-neutral-500" />
        </button>

        <!-- Search Bar -->
        <div class="relative flex-1 min-w-0">
          <Search
            class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400"
          />
          <input
            v-model="searchInput"
            @input="onSearch"
            type="text"
            placeholder="Search candidates…"
            class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-neutral-200 bg-neutral-50 text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400 transition-all"
          />
        </div>

        <!-- Filter Controls -->
        <div class="hidden sm:flex items-center gap-3">
          <div class="relative">
            <select
              :value="store.statusFilter"
              @change="store.setStatusFilter($event.target.value)"
              class="btn-press appearance-none text-sm bg-white border border-neutral-200 rounded-lg pl-3 pr-8 py-2 focus:outline-none focus:ring-2 focus:ring-primary-200 cursor-pointer"
            >
              <option value="">All Status</option>
              <option value="available">Available</option>
              <option value="interviewing">Interviewing</option>
            </select>
            <ChevronDown
              class="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-neutral-400 pointer-events-none"
            />
          </div>

          <div class="relative">
            <select
              :value="store.sortBy"
              @change="store.setSortBy($event.target.value)"
              class="btn-press appearance-none text-sm bg-white border border-neutral-200 rounded-lg pl-3 pr-8 py-2 focus:outline-none focus:ring-2 focus:ring-primary-200 cursor-pointer"
            >
              <option value="matchScore">Sort: Match Score</option>
              <option value="experience">Sort: Experience</option>
            </select>
            <ChevronDown
              class="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-neutral-400 pointer-events-none"
            />
          </div>
        </div>
      </header>

      <!-- Mobile Filters (shown below header on small screens) -->
      <div class="sm:hidden bg-white border-b border-neutral-100 px-4 py-3 flex gap-2">
        <div class="relative flex-1">
          <select
            :value="store.statusFilter"
            @change="store.setStatusFilter($event.target.value)"
            class="btn-press w-full appearance-none text-xs bg-white border border-neutral-200 rounded-lg pl-3 pr-7 py-2 focus:outline-none focus:ring-2 focus:ring-primary-200 cursor-pointer"
          >
            <option value="">All Status</option>
            <option value="available">Available</option>
            <option value="interviewing">Interviewing</option>
          </select>
          <ChevronDown class="absolute right-2 top-1/2 -translate-y-1/2 w-3 h-3 text-neutral-400 pointer-events-none" />
        </div>
        <div class="relative flex-1">
          <select
            :value="store.sortBy"
            @change="store.setSortBy($event.target.value)"
            class="btn-press w-full appearance-none text-xs bg-white border border-neutral-200 rounded-lg pl-3 pr-7 py-2 focus:outline-none focus:ring-2 focus:ring-primary-200 cursor-pointer"
          >
            <option value="matchScore">Match Score</option>
            <option value="experience">Experience</option>
          </select>
          <ChevronDown class="absolute right-2 top-1/2 -translate-y-1/2 w-3 h-3 text-neutral-400 pointer-events-none" />
        </div>
      </div>

      <!-- Candidate Grid -->
      <main class="flex-1 p-4 sm:p-8 overflow-y-auto">
        <!-- Error state -->
        <div
          v-if="store.error"
          class="text-center py-20 text-danger-500 text-sm"
        >
          {{ store.error }}
        </div>

        <!-- Loading state -->
        <div
          v-else-if="store.loading"
          class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
        >
          <SkeletonCard v-for="n in 6" :key="n" />
        </div>

        <!-- Empty state -->
        <div
          v-else-if="store.candidates.length === 0"
          class="text-center py-20"
        >
          <Users class="w-12 h-12 text-neutral-300 mx-auto mb-4" />
          <p class="text-neutral-400 text-sm">No candidates match your filters.</p>
        </div>

        <!-- Candidate Feed -->
        <div
          v-else
          class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
        >
          <CandidateCard
            v-for="candidate in store.candidates"
            :key="candidate.id"
            :candidate="candidate"
          />
        </div>
      </main>
    </div>
  </div>
</template>
