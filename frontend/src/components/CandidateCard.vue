<script setup>
import { computed } from "vue";
import { MapPin, Briefcase, Calendar } from "lucide-vue-next";

const props = defineProps({
  candidate: { type: Object, required: true },
});

const score = computed(() => {
  return (
    props.candidate.matchScore ??
    props.candidate.fit_score ??
    props.candidate.vector_score ??
    0
  );
});

const skills = computed(() => {
  if (!props.candidate.skills) return [];
  if (Array.isArray(props.candidate.skills)) return props.candidate.skills;
  return props.candidate.skills
    .split(",")
    .map((skill) => skill.trim())
    .filter(Boolean);
});

function scoreColor(value) {
  if (value >= 85) return "text-success-600 bg-success-50";
  if (value >= 70) return "text-warning-600 bg-warning-50";
  return "text-neutral-600 bg-neutral-100";
}

function statusBadge(status) {
  return status === "available"
    ? "bg-success-50 text-success-700"
    : "bg-primary-50 text-primary-700";
}
</script>

<template>
  <div
    class="glass rounded-2xl p-6 hover:shadow-lg hover:shadow-neutral-200/50 transition-all duration-200 cursor-pointer group"
  >
    <!-- Header -->
    <div class="flex items-start justify-between mb-4">
      <div class="flex items-center gap-3">
        <img
          :src="candidate.avatar"
          :alt="candidate.name"
          class="w-11 h-11 rounded-full bg-neutral-100"
        />
        <div>
          <h3 class="text-sm font-semibold text-neutral-900 group-hover:text-primary-700 transition-colors">
            {{ candidate.name }}
          </h3>
          <p class="text-xs text-neutral-500">{{ candidate.title }}</p>
        </div>
      </div>
      <span
        :class="scoreColor(score)"
        class="text-xs font-bold px-2.5 py-1 rounded-lg"
      >
        {{ score }}%
      </span>
    </div>

    <!-- Meta -->
    <div class="flex flex-wrap gap-3 text-xs text-neutral-500 mb-4">
      <span class="inline-flex items-center gap-1">
        <MapPin class="w-3 h-3" />
        {{ candidate.location }}
      </span>
      <span class="inline-flex items-center gap-1">
        <Briefcase class="w-3 h-3" />
        {{ candidate.experience }}y exp
      </span>
      <span class="inline-flex items-center gap-1">
        <Calendar class="w-3 h-3" />
        {{ candidate.appliedDate }}
      </span>
    </div>

    <!-- Skills -->
    <div class="flex flex-wrap gap-1.5 mb-4">
      <span
        v-for="skill in skills"
        :key="skill"
        class="px-2 py-0.5 rounded-md bg-neutral-100 text-neutral-600 text-xs"
      >
        {{ skill }}
      </span>
    </div>

    <!-- Footer -->
    <div class="flex items-center justify-between pt-3 border-t border-neutral-100">
      <span
        :class="statusBadge(candidate.status)"
        class="text-xs font-medium px-2.5 py-1 rounded-full capitalize"
      >
        {{ candidate.status }}
      </span>
      <button
        class="btn-press text-xs font-medium text-primary-600 hover:text-primary-800 transition-colors"
      >
        View Profile →
      </button>
    </div>
  </div>
</template>
