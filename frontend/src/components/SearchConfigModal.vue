<script setup>
import { reactive, computed, watch } from "vue";
import { X, Github, Database, FileText, Upload } from "lucide-vue-next";

const props = defineProps({
  open: { type: Boolean, default: false },
  initial: { type: Object, default: () => ({}) },
});

const emit = defineEmits(["close", "search"]);

const form = reactive({
  sources: {
    pool: true,
    applications: true,
    uploads: true,
  },
  includeGithub: false,
});

const sourceOptions = [
  { key: "pool", label: "Talent Pool", icon: Database, desc: "Profiles in your database" },
  { key: "applications", label: "Applications", icon: FileText, desc: "Resumes from your job posts" },
  { key: "uploads", label: "Resume Library", icon: Upload, desc: "Your uploaded resumes" },
];

const hasSource = computed(() => Object.values(form.sources).some(Boolean) || form.includeGithub);

function resetFromInitial() {
  const init = props.initial || {};
  form.sources.pool = init.sources?.pool !== false;
  form.sources.applications = init.sources?.applications !== false;
  form.sources.uploads = init.sources?.uploads !== false;
  form.includeGithub = !!init.includeGithub;
}

function handleApply() {
  if (!hasSource.value) return;
  const sources = Object.entries(form.sources)
    .filter(([, value]) => value)
    .map(([key]) => key);
  emit("search", { sources, includeGithub: form.includeGithub });
  emit("close");
}

watch(() => props.open, (isOpen) => {
  if (isOpen) resetFromInitial();
});
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/30 backdrop-blur-sm" @click="emit('close')"></div>
      <div class="relative w-full max-w-xl bg-white rounded-[28px] shadow-2xl max-h-[90vh] overflow-y-auto">
        <div class="p-5 sm:p-8">
          <div class="flex items-start justify-between mb-6">
            <div>
              <h2 class="text-lg font-semibold text-neutral-900">Search sources</h2>
              <p class="text-sm text-neutral-500 mt-0.5">Choose where to look for candidates.</p>
            </div>
            <button @click="emit('close')" class="p-2 rounded-lg hover:bg-neutral-100 text-neutral-400">
              <X class="w-5 h-5" />
            </button>
          </div>

          <div class="space-y-2">
            <label
              v-for="opt in sourceOptions"
              :key="opt.key"
              class="flex items-start gap-3 p-4 rounded-2xl border border-neutral-200 cursor-pointer hover:bg-neutral-50 transition-colors"
              :class="form.sources[opt.key] ? 'border-primary-300 bg-primary-50/50' : ''"
            >
              <input
                v-model="form.sources[opt.key]"
                type="checkbox"
                class="mt-1 rounded border-neutral-300 text-primary-600 focus:ring-primary-200"
              />
              <component :is="opt.icon" class="w-5 h-5 text-primary-500 mt-0.5 shrink-0" />
              <div>
                  <span class="text-sm font-medium text-neutral-900">{{ opt.label }}</span>
                  <p class="text-xs text-neutral-500 mt-0.5">{{ opt.desc }}</p>
              </div>
            </label>
          </div>

          <div class="mt-4 p-4 rounded-2xl border border-neutral-200 bg-neutral-50">
            <label class="flex items-center justify-between cursor-pointer gap-4">
              <div class="flex items-center gap-3">
                <Github class="w-5 h-5 text-neutral-700" />
                <div>
                  <span class="text-sm font-medium text-neutral-900">Include GitHub</span>
                  <p class="text-xs text-neutral-500 mt-0.5">Search public GitHub profiles too.</p>
                </div>
              </div>
              <input
                v-model="form.includeGithub"
                type="checkbox"
                class="w-5 h-5 rounded border-neutral-300 text-primary-600 focus:ring-primary-200"
              />
            </label>
          </div>

          <p v-if="!hasSource" class="text-xs text-danger-500 mt-3">Select at least one source or enable GitHub.</p>

          <div class="flex gap-3 mt-6">
            <button @click="emit('close')" class="btn-press flex-1 py-3 rounded-xl border border-neutral-200 text-sm font-medium text-neutral-600 hover:bg-neutral-50">
              Cancel
            </button>
            <button
              @click="handleApply"
              :disabled="!hasSource"
              class="btn-press flex-1 py-3 rounded-xl bg-primary-600 text-white text-sm font-medium hover:bg-primary-700 shadow-lg shadow-primary-200 disabled:opacity-50"
            >
              Apply sources
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
