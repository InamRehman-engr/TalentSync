<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { api } from "../stores/auth";
import {
  Upload, Trash2, Sparkles, FileText,
  Briefcase, CheckCircle2, AlertCircle, Loader2, X, Brain, Eraser
} from "lucide-vue-next";

const emit = defineEmits(["updated"]);

const uploadMode = ref("files");
const uploadForm = reactive({
  candidate_name: "",
  location: "",
  skills: "",
  resume_text: "",
  role_title: "",
  role_skills: "",
  role_experience: "",
  role_description: "",
});
const selectedFiles = ref([]);
const fileInputRef = ref(null);
const uploading = ref(false);
const uploadStep = ref("");
const myResumes = ref([]);
const loadingResumes = ref(false);
const uploadResults = ref([]);
const showResultsModal = ref(false);
const expandedResumeId = ref(null);

const roleReady = computed(() => Boolean(uploadForm.role_title.trim()));

function evaluationPayload() {
  return {
    role_title: uploadForm.role_title.trim(),
    role_skills: uploadForm.role_skills.trim(),
    role_experience: uploadForm.role_experience.trim(),
    role_description: uploadForm.role_description.trim(),
  };
}

const avgAiScore = computed(() => {
  const scored = myResumes.value.filter((r) => r.ai_score > 0);
  if (!scored.length) return null;
  return Math.round(scored.reduce((s, r) => s + r.ai_score, 0) / scored.length);
});

const topAiScore = computed(() => {
  const scores = myResumes.value.map((resume) => resume.ai_score).filter((score) => score > 0);
  if (!scores.length) return null;
  return Math.max(...scores);
});

function scoreColor(score) {
  if (score >= 80) return "text-success-600 bg-success-50 border-success-100";
  if (score >= 60) return "text-warning-600 bg-warning-50 border-warning-100";
  return "text-danger-600 bg-danger-50 border-danger-100";
}

async function loadMyResumes() {
  loadingResumes.value = true;
  try {
    const res = await api.get("/resumes/mine");
    myResumes.value = res.data.resumes || [];
    emit("updated", myResumes.value.length);
  } catch {
    myResumes.value = [];
  } finally {
    loadingResumes.value = false;
  }
}

function onFilesSelected(event) {
  selectedFiles.value = Array.from(event.target.files || []);
}

function clearSelectedFiles() {
  selectedFiles.value = [];
  if (fileInputRef.value) fileInputRef.value.value = "";
}

function clearUploadForm() {
  Object.assign(uploadForm, {
    candidate_name: "",
    location: "",
    skills: "",
    resume_text: "",
    role_title: "",
    role_skills: "",
    role_experience: "",
    role_description: "",
  });
  clearSelectedFiles();
  uploadStep.value = "";
}

function clearUploadResults() {
  showResultsModal.value = false;
  uploadResults.value = [];
  clearUploadForm();
}

async function clearLibrary() {
  if (!myResumes.value.length) return;
  if (!window.confirm(`Remove all ${myResumes.value.length} resume(s) from your library?`)) return;
  try {
    await api.delete("/resumes/mine");
    myResumes.value = [];
    expandedResumeId.value = null;
    clearUploadResults();
    emit("updated", 0);
  } catch (err) {
    console.error("Clear library error:", err);
  }
}

function onDrop(event) {
  event.preventDefault();
  const files = Array.from(event.dataTransfer?.files || []);
  if (files.length) selectedFiles.value = files;
}

async function submitResumeUpload() {
  if (!uploadForm.resume_text.trim() || !roleReady.value) return;
  uploading.value = true;
  uploadStep.value = "Running AI evaluation…";
  uploadResults.value = [];
  const payload = {
    candidate_name: uploadForm.candidate_name,
    location: uploadForm.location,
    skills: uploadForm.skills,
    resume_text: uploadForm.resume_text,
    ...evaluationPayload(),
  };
  try {
    const res = await api.post("/resumes/upload", payload);
    uploadResults.value = [res.data.resume];
    showResultsModal.value = true;
    Object.assign(uploadForm, { candidate_name: "", location: "", skills: "", resume_text: "" });
    await loadMyResumes();
  } catch (err) {
    uploadResults.value = [{ error: err.response?.data?.error || "Upload failed" }];
    showResultsModal.value = true;
  } finally {
    uploading.value = false;
    uploadStep.value = "";
  }
}

async function submitBulkUpload() {
  if (!selectedFiles.value.length || !roleReady.value) return;
  uploading.value = true;
  uploadStep.value = "Extracting text and running AI evaluation…";
  uploadResults.value = [];
  try {
    const formData = new FormData();
    selectedFiles.value.forEach((file) => formData.append("files", file));
    if (uploadForm.location) formData.append("location", uploadForm.location);
    if (uploadForm.skills) formData.append("skills", uploadForm.skills);
    const evalFields = evaluationPayload();
    Object.entries(evalFields).forEach(([key, value]) => {
      if (value) formData.append(key, value);
    });

    const res = await api.post("/resumes/upload/bulk", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 600000,
    });
    uploadResults.value = res.data.resumes || [];
    if (res.data.errors?.length) {
      res.data.errors.forEach((e) => uploadResults.value.push({ error: e }));
    }
    showResultsModal.value = true;
    clearSelectedFiles();
    await loadMyResumes();
  } catch (err) {
    const data = err.response?.data || {};
    const detailErrors = Array.isArray(data.errors) ? data.errors : [];
    if (detailErrors.length) {
      uploadResults.value = detailErrors.map((message) => ({ error: message }));
    } else {
      uploadResults.value = [{ error: data.error || "Bulk upload failed" }];
    }
    showResultsModal.value = true;
  } finally {
    uploading.value = false;
    uploadStep.value = "";
  }
}

async function deleteResume(id) {
  try {
    await api.delete(`/resumes/${id}`);
    myResumes.value = myResumes.value.filter((r) => r.id !== id);
    emit("updated", myResumes.value.length);
  } catch (err) {
    console.error("Delete error:", err);
  }
}

function toggleResumeDetails(id) {
  expandedResumeId.value = expandedResumeId.value === id ? null : id;
}

onMounted(() => {
  loadMyResumes();
});
</script>

<template>
  <div class="space-y-6">
    <div class="dashboard-shell p-5 sm:p-6">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-neutral-900 text-white">
            <Brain class="w-5 h-5" />
          </div>
          <div>
            <p class="section-eyebrow">Resume library</p>
            <h3 class="section-title mt-0.5">Upload & evaluate</h3>
          </div>
        </div>

        <div class="flex gap-3">
          <div class="dashboard-stat-card px-4 py-3 text-center min-w-[80px]">
            <p class="text-lg font-semibold text-neutral-900">{{ myResumes.length }}</p>
            <p class="text-[10px] uppercase tracking-wider text-neutral-400">Stored</p>
          </div>
          <div class="dashboard-stat-card px-4 py-3 text-center min-w-[80px]">
            <p class="text-lg font-semibold text-neutral-900">{{ avgAiScore !== null ? `${avgAiScore}%` : '—' }}</p>
            <p class="text-[10px] uppercase tracking-wider text-neutral-400">Avg fit</p>
          </div>
          <div class="dashboard-stat-card px-4 py-3 text-center min-w-[80px]">
            <p class="text-lg font-semibold text-neutral-900">{{ topAiScore !== null ? `${topAiScore}%` : '—' }}</p>
            <p class="text-[10px] uppercase tracking-wider text-neutral-400">Top</p>
          </div>
        </div>
      </div>
    </div>

    <div class="grid gap-5 xl:grid-cols-2 items-start">
      <section class="dashboard-shell p-5 sm:p-6">
        <div class="mb-5">
          <p class="section-eyebrow">Upload</p>
          <h4 class="section-title mt-1 text-lg">Evaluate resumes</h4>
        </div>

        <div class="space-y-4">
          <div class="dashboard-card p-4 sm:p-5">
            <div class="flex items-center gap-2 mb-4">
              <span class="w-6 h-6 rounded-full bg-primary-600 text-white text-xs font-bold flex items-center justify-center">1</span>
              <span class="text-sm font-medium text-neutral-800">Role brief</span>
              <span class="ml-auto text-[10px] uppercase tracking-wider text-neutral-400">Required</span>
            </div>

            <div class="space-y-3">
              <div>
                <label class="block text-xs text-neutral-500 mb-1.5">Role title *</label>
                <input
                  v-model="uploadForm.role_title"
                  placeholder="e.g. Senior Backend Engineer"
                  class="w-full rounded-2xl border border-neutral-200 bg-neutral-50/70 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-200"
                />
              </div>
              <div class="grid sm:grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs text-neutral-500 mb-1.5">Required skills</label>
                  <input
                    v-model="uploadForm.role_skills"
                    placeholder="Python, FastAPI, PostgreSQL"
                    class="w-full rounded-2xl border border-neutral-200 bg-neutral-50/70 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-200"
                  />
                </div>
                <div>
                  <label class="block text-xs text-neutral-500 mb-1.5">Experience level</label>
                  <input
                    v-model="uploadForm.role_experience"
                    placeholder="e.g. 3-5 years"
                    class="w-full rounded-2xl border border-neutral-200 bg-neutral-50/70 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-200"
                  />
                </div>
              </div>
              <div>
                <label class="block text-xs text-neutral-500 mb-1.5">Role description</label>
                <textarea
                  v-model="uploadForm.role_description"
                  rows="4"
                  placeholder="What does this role involve? Key responsibilities, must-haves, nice-to-haves…"
                  class="w-full rounded-2xl border border-neutral-200 bg-neutral-50/70 px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary-200"
                ></textarea>
              </div>
            </div>

            <div v-if="roleReady" class="mt-4 rounded-xl border border-primary-100 bg-primary-50/60 px-3 py-2.5 text-xs text-primary-800 flex items-center gap-2">
              <Briefcase class="w-3.5 h-3.5 shrink-0" />
              <span>Scoring against <strong>{{ uploadForm.role_title }}</strong></span>
            </div>
            <p v-else class="mt-4 text-xs text-warning-600">Enter a role title to enable AI scoring.</p>
          </div>

          <div class="dashboard-card p-4 sm:p-5">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-4">
              <div class="flex items-center gap-2">
                <span class="w-6 h-6 rounded-full bg-primary-600 text-white text-xs font-bold flex items-center justify-center">2</span>
                <span class="text-sm font-medium text-neutral-800">Add resumes</span>
              </div>

              <div class="inline-flex rounded-2xl bg-neutral-100 p-1">
                <button
                  @click="uploadMode = 'files'"
                  :class="uploadMode === 'files' ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-500'"
                  class="btn-press rounded-2xl px-4 py-2 text-xs font-semibold transition-all"
                >Upload files</button>
                <button
                  @click="uploadMode = 'paste'"
                  :class="uploadMode === 'paste' ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-500'"
                  class="btn-press rounded-2xl px-4 py-2 text-xs font-semibold transition-all"
                >Paste text</button>
              </div>
            </div>

            <div v-if="uploadMode === 'files'" class="space-y-4">
              <div
                @dragover.prevent
                @drop="onDrop"
                class="rounded-[24px] border-2 border-dashed px-6 py-10 text-center transition-colors"
                :class="uploading ? 'border-primary-200 bg-primary-50/40' : 'border-neutral-200 bg-neutral-50/70 hover:border-primary-300 hover:bg-primary-50/20'"
              >
                <input
                  ref="fileInputRef"
                  type="file"
                  multiple
                  accept=".zip,.pdf,.docx,.txt,.md"
                  class="hidden"
                  @change="onFilesSelected"
                />
                <div v-if="uploading" class="flex flex-col items-center gap-3">
                  <Loader2 class="w-10 h-10 text-primary-500 animate-spin" />
                  <p class="text-sm font-medium text-primary-700">{{ uploadStep }}</p>
                  <p class="text-xs text-neutral-500">This may take a minute per resume while Ollama analyzes each one.</p>
                </div>
                <template v-else>
                  <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-primary-600 shadow-sm">
                    <Upload class="w-7 h-7" />
                  </div>
                  <p class="text-sm font-medium text-neutral-800 mb-0.5">Drop files or browse</p>
                  <p class="text-xs text-neutral-400 mb-4">PDF, DOCX, TXT, or ZIP</p>
                  <button
                    type="button"
                    @click="fileInputRef?.click()"
                    class="btn-press rounded-2xl border border-neutral-200 bg-white px-5 py-2.5 text-sm font-medium text-neutral-700 hover:bg-neutral-50 shadow-sm"
                  >Choose files</button>
                </template>
              </div>

              <div v-if="selectedFiles.length && !uploading" class="dashboard-muted-card p-4">
                <div class="flex items-center justify-between gap-3 mb-3">
                  <p class="text-sm font-medium text-neutral-800">Selected files</p>
                  <span class="text-xs text-neutral-400">{{ selectedFiles.length }} file{{ selectedFiles.length === 1 ? '' : 's' }}</span>
                </div>
                <div class="space-y-2">
                  <div
                    v-for="file in selectedFiles"
                    :key="file.name + file.size"
                    class="flex items-center gap-3 rounded-2xl border border-white bg-white px-3 py-3 text-sm shadow-sm"
                  >
                    <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-primary-50 text-primary-600">
                      <FileText class="w-4 h-4 shrink-0" />
                    </div>
                    <span class="truncate flex-1 text-neutral-700">{{ file.name }}</span>
                    <span class="text-xs text-neutral-400">{{ Math.round(file.size / 1024) }} KB</span>
                  </div>
                </div>
                <div class="mt-4 flex gap-2">
                  <button
                    @click="submitBulkUpload"
                    :disabled="uploading || !roleReady"
                    class="btn-press flex-1 rounded-2xl bg-primary-600 py-3 text-sm font-medium text-white hover:bg-primary-700 shadow-sm disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    <Sparkles class="w-4 h-4" />
                    Upload &amp; AI evaluate ({{ selectedFiles.length }})
                  </button>
                  <button @click="clearSelectedFiles" class="btn-press rounded-2xl border border-neutral-200 bg-white px-4 py-3 text-sm text-neutral-600 hover:bg-neutral-50">Clear</button>
                </div>
              </div>
            </div>

            <div v-else class="space-y-4">
              <div class="grid sm:grid-cols-3 gap-3">
                <input v-model="uploadForm.candidate_name" placeholder="Candidate name" class="rounded-2xl border border-neutral-200 bg-neutral-50/70 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-200" />
                <input v-model="uploadForm.location" placeholder="Location" class="rounded-2xl border border-neutral-200 bg-neutral-50/70 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-200" />
                <input v-model="uploadForm.skills" placeholder="Skills (optional)" class="rounded-2xl border border-neutral-200 bg-neutral-50/70 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-200" />
              </div>
              <textarea
                v-model="uploadForm.resume_text"
                rows="6"
                placeholder="Paste full resume text here…"
                class="w-full rounded-[24px] border border-neutral-200 bg-neutral-50/70 px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary-200"
              ></textarea>
              <div class="flex gap-2">
                <button
                  @click="submitResumeUpload"
                  :disabled="uploading || !uploadForm.resume_text.trim() || !roleReady"
                  class="btn-press flex-1 rounded-2xl bg-primary-600 py-3 text-sm font-medium text-white disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <Loader2 v-if="uploading" class="w-4 h-4 animate-spin" />
                  <Sparkles v-else class="w-4 h-4" />
                  {{ uploading ? uploadStep || 'Processing…' : 'Add & AI evaluate' }}
                </button>
                <button
                  @click="clearUploadForm"
                  :disabled="uploading"
                  class="btn-press rounded-2xl border border-neutral-200 bg-white px-4 py-3 text-sm text-neutral-600 hover:bg-neutral-50 flex items-center gap-1.5"
                >
                  <Eraser class="w-4 h-4" /> Clear
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="dashboard-shell p-5 sm:p-6">
        <div class="flex items-center justify-between gap-4 mb-5">
          <div>
            <p class="section-eyebrow">Library</p>
            <h4 class="section-title mt-1 text-lg">Saved resumes</h4>
          </div>
          <button
            v-if="myResumes.length"
            @click="clearLibrary"
            class="btn-press inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-neutral-200 text-xs font-medium text-neutral-500 hover:text-danger-600 hover:border-danger-200"
          >
            <Eraser class="w-3.5 h-3.5" /> Clear all
          </button>
        </div>

        <div v-if="loadingResumes" class="py-12 text-center text-sm text-neutral-400">Loading…</div>
        <div
          v-else-if="myResumes.length"
          class="space-y-3"
          :class="myResumes.length > 4 ? 'resume-library-scroll max-h-[min(32rem,70vh)] overflow-y-auto pr-1 -mr-1' : ''"
        >
          <article
            v-for="resume in myResumes"
            :key="resume.id"
            class="dashboard-card dashboard-card-hover p-4 sm:p-5 overflow-hidden"
          >
            <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between min-w-0">
              <button
                type="button"
                @click="toggleResumeDetails(resume.id)"
                class="flex-1 min-w-0 text-left"
              >
                <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between min-w-0">
                  <div class="min-w-0">
                    <div class="flex flex-wrap items-center gap-2">
                      <p class="text-base font-semibold text-neutral-900">{{ resume.candidate_name || 'Unnamed candidate' }}</p>
                      <span class="rounded-full border border-neutral-200 bg-neutral-50 px-2.5 py-1 text-[11px] font-medium text-neutral-500">{{ resume.evaluated_job_title || 'Role not specified' }}</span>
                    </div>
                    <p class="mt-1 truncate text-xs text-neutral-400">{{ resume.source_filename || resume.uploaded_date }}</p>
                  </div>

                  <div class="flex flex-wrap gap-2 md:justify-end max-w-full">
                    <span
                      v-if="resume.ai_score"
                      class="inline-flex items-center gap-1 rounded-full border px-3 py-1.5 text-xs font-bold"
                      :class="scoreColor(resume.ai_score)"
                    >
                      <Brain class="w-3 h-3" /> {{ resume.ai_score }}%
                    </span>
                    <span v-if="resume.ats_score" class="inline-flex items-center gap-1 rounded-full border border-neutral-200 bg-white px-3 py-1.5 text-xs font-medium text-neutral-600">
                      <FileText class="w-3 h-3" /> ATS {{ resume.ats_score }}%
                    </span>
                    <span v-if="!resume.ai_score && !resume.ats_score" class="inline-flex items-center gap-1 rounded-full border border-neutral-200 bg-neutral-50 px-3 py-1.5 text-xs text-neutral-400">
                      Awaiting score
                    </span>
                  </div>
                </div>
              </button>

              <button
                @click.stop="deleteResume(resume.id)"
                class="self-start rounded-2xl border border-neutral-200 bg-white p-2 text-neutral-400 hover:border-danger-200 hover:bg-danger-50 hover:text-danger-500"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>

            <div class="mt-3 flex flex-wrap gap-2 text-xs text-neutral-500">
              <span class="dashboard-muted-card px-2.5 py-1.5 truncate max-w-[140px]">{{ resume.source_filename || 'Upload' }}</span>
              <span class="dashboard-muted-card px-2.5 py-1.5">{{ resume.uploaded_date || 'Recent' }}</span>
              <span class="dashboard-muted-card px-2.5 py-1.5">{{ expandedResumeId === resume.id ? 'Open' : 'Tap for details' }}</span>
            </div>

            <div v-if="expandedResumeId === resume.id" class="mt-4 rounded-[24px] border border-primary-100 bg-primary-50/50 p-4">
              <div class="grid gap-3 sm:grid-cols-2 mb-3 text-xs">
                <div class="rounded-2xl bg-white/80 px-3 py-3">
                  <p class="uppercase tracking-[0.16em] text-[10px] text-neutral-400">Role evaluated</p>
                  <p class="mt-1 text-sm font-medium text-neutral-700">{{ resume.evaluated_job_title || 'Not available' }}</p>
                </div>
                <div class="rounded-2xl bg-white/80 px-3 py-3">
                  <p class="uppercase tracking-[0.16em] text-[10px] text-neutral-400">ATS score</p>
                  <p class="mt-1 text-sm font-medium text-neutral-700">{{ resume.ats_score ? `${resume.ats_score}%` : 'Not available' }}</p>
                </div>
              </div>
              <div v-if="resume.ai_evaluation" class="rounded-2xl bg-white/85 px-4 py-4">
                <p class="text-xs font-medium text-primary-700 mb-1 flex items-center gap-1">
                  <Sparkles class="w-3.5 h-3.5" /> AI evaluation
                </p>
                <p class="text-sm text-neutral-700 leading-relaxed">{{ resume.ai_evaluation }}</p>
              </div>
            </div>
          </article>
        </div>
        <div v-else class="py-10 text-center rounded-xl border border-dashed border-neutral-200">
          <FileText class="w-8 h-8 mx-auto text-neutral-200 mb-2" />
          <p class="text-sm text-neutral-400">No resumes yet</p>
        </div>
      </section>
    </div>

    <!-- Results modal -->
    <Teleport to="body">
      <div v-if="showResultsModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showResultsModal = false"></div>
        <div class="relative w-full max-w-lg bg-white rounded-2xl shadow-2xl max-h-[85vh] overflow-y-auto">
          <div class="p-6">
            <div class="flex items-start justify-between mb-5">
              <div>
                <h3 class="text-lg font-bold text-neutral-900">Upload complete</h3>
                <p class="text-sm text-neutral-500 mt-0.5">AI evaluation results</p>
              </div>
              <button @click="showResultsModal = false" class="p-2 rounded-lg hover:bg-neutral-100 text-neutral-400">
                <X class="w-5 h-5" />
              </button>
            </div>

            <div class="space-y-3">
              <div
                v-for="(item, i) in uploadResults"
                :key="i"
                class="rounded-xl border p-4"
                :class="item.error ? 'border-warning-200 bg-warning-50' : 'border-neutral-100 bg-neutral-50'"
              >
                <div v-if="item.error" class="flex items-start gap-2 text-sm text-warning-700">
                  <AlertCircle class="w-4 h-4 shrink-0 mt-0.5" />
                  {{ item.error }}
                </div>
                <template v-else>
                  <div class="flex items-center justify-between mb-2">
                    <p class="font-semibold text-neutral-900">{{ item.candidate_name || 'Candidate' }}</p>
                    <CheckCircle2 class="w-5 h-5 text-success-500" />
                  </div>
                  <p v-if="item.source_filename" class="text-xs text-neutral-400 mb-3">{{ item.source_filename }}</p>
                  <div class="flex gap-3 mb-3">
                    <div v-if="item.ai_score" class="flex-1 rounded-lg border px-3 py-2 text-center" :class="scoreColor(item.ai_score)">
                      <p class="text-xs opacity-70">AI Fit</p>
                      <p class="text-xl font-bold">{{ item.ai_score }}%</p>
                    </div>
                    <div v-if="item.ats_score" class="flex-1 rounded-lg border border-neutral-200 bg-white px-3 py-2 text-center">
                      <p class="text-xs text-neutral-400">ATS</p>
                      <p class="text-xl font-bold text-neutral-800">{{ item.ats_score }}%</p>
                    </div>
                  </div>
                  <p v-if="item.ai_evaluation" class="text-sm text-neutral-600 leading-relaxed">{{ item.ai_evaluation }}</p>
                </template>
              </div>
            </div>

            <div class="flex gap-3 mt-5">
              <button
                @click="clearUploadResults"
                class="btn-press flex-1 py-3 rounded-xl border border-neutral-200 text-sm font-medium text-neutral-600 hover:bg-neutral-50 flex items-center justify-center gap-2"
              >
                <Eraser class="w-4 h-4" /> Clear
              </button>
              <button
                @click="showResultsModal = false"
                class="btn-press flex-1 py-3 rounded-xl bg-primary-600 text-white text-sm font-medium"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
