<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore, api } from "../stores/auth";
import { showEmployeeDashboard } from "../router/index";
import Navbar from "../components/Navbar.vue";
import AppFooter from "../components/AppFooter.vue";
import {
  Search, Briefcase, MapPin, Clock, Building2, FileText,
  XCircle, LogOut, Send, Sparkles, Target, BookOpen, Hash,
  Layers, Filter, Upload,
} from "lucide-vue-next";

const router = useRouter();
const auth = useAuthStore();

if (!showEmployeeDashboard || !auth.isLoggedIn || !auth.isEmployee) {
  router.push(showEmployeeDashboard ? "/login" : "/");
}

const tab = ref("browse");

// Browse jobs grouped by tenant/company
const tenants = ref([]);
const loadingJobs = ref(false);
const searchQ = ref("");
const selectedTenant = ref("all");

async function loadJobs() {
  loadingJobs.value = true;
  try {
    const res = await api.get("/tenants/jobs");
    tenants.value = res.data.tenants || [];
  } catch (err) {
    console.error("Load tenant jobs error:", err);
    tenants.value = [];
  } finally {
    loadingJobs.value = false;
  }
}

const tenantOptions = computed(() => {
  return tenants.value.map((tenant) => ({
    key: tenant.tenant_key,
    company: tenant.company,
  }));
});

const allJobs = computed(() => {
  return tenants.value.flatMap((tenant) => tenant.jobs || []);
});

const filteredTenants = computed(() => {
  const terms = searchQ.value.toLowerCase().split(/\s+/).filter(Boolean);
  return tenants.value
    .map((tenant) => {
      if (selectedTenant.value !== "all" && tenant.tenant_key !== selectedTenant.value) {
        return { ...tenant, jobs: [] };
      }
      const jobs = (tenant.jobs || []).filter((job) => {
        if (!terms.length) return true;
        const searchable = `${job.title || ""} ${job.company || ""} ${job.skills || ""} ${job.description || ""} ${job.location || ""} ${job.type || ""} ${job.salary || ""}`.toLowerCase();
        return terms.some((term) => searchable.includes(term));
      });
      return { ...tenant, jobs };
    })
    .filter((tenant) => tenant.jobs.length > 0);
});

const totalVisibleJobs = computed(() => {
  return filteredTenants.value.reduce((acc, tenant) => acc + tenant.jobs.length, 0);
});

// My applications
const myApps = ref([]);
const loadingApps = ref(false);

async function loadMyApps() {
  loadingApps.value = true;
  try {
    const res = await api.get("/applications/my");
    myApps.value = res.data.applications || [];
  } catch {
    myApps.value = [];
  } finally {
    loadingApps.value = false;
  }
}

const dashboardStats = computed(() => {
  return {
    tenants: tenants.value.length,
    jobs: allJobs.value.length,
    applications: myApps.value.length,
  };
});

const appliedJobIds = computed(() => new Set(myApps.value.map((app) => app.job_id).filter(Boolean)));

function hasApplied(jobId) {
  return appliedJobIds.value.has(jobId);
}

function formatTenantName(name) {
  return name || "Unknown Company";
}

function clearBrowseFilters() {
  searchQ.value = "";
  selectedTenant.value = "all";
}

function getTenantInitials(name) {
  const trimmed = formatTenantName(name).trim();
  const parts = trimmed.split(/\s+/).filter(Boolean);
  if (!parts.length) return "TC";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
}

// Apply modal
const applyModal = ref(false);
const applyingJobId = ref(null);
const applyingJobTitle = ref("");
const applyingCompany = ref("");
const resumeText = ref("");
const applyMode = ref("text");
const resumeFile = ref(null);
const applying = ref(false);
const atsResult = ref(null);
const applyError = ref("");

function openApply(job) {
  applyingJobId.value = job.id;
  applyingJobTitle.value = job.title;
  applyingCompany.value = job.company || "";
  resumeText.value = "";
  applyMode.value = "text";
  resumeFile.value = null;
  atsResult.value = null;
  applyError.value = "";
  applyModal.value = true;
}

function onResumeFileSelected(event) {
  const files = Array.from(event.target.files || []);
  resumeFile.value = files.length ? files[0] : null;
}

async function submitApplication() {
  if (applying.value) return;
  if (applyMode.value === "text" && !resumeText.value.trim()) return;
  if (applyMode.value === "upload" && !resumeFile.value) return;
  applying.value = true;
  applyError.value = "";
  try {
    const jobId = applyingJobId.value;
    const usePut = hasApplied(jobId);
    const endpoint = usePut ? `/applications/job/${jobId}` : "/applications";
    const method = usePut ? "put" : "post";
    let res;
    if (applyMode.value === "upload") {
      const formData = new FormData();
      if (!usePut) formData.append("job_id", String(jobId));
      formData.append("resume_file", resumeFile.value);
      res = await api[method](endpoint, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    } else {
      const payload = { resume_text: resumeText.value };
      if (!usePut) payload.job_id = jobId;
      res = await api[method](endpoint, payload);
    }
    atsResult.value = res.data;
    await loadMyApps();
  } catch (err) {
    if (err.response?.status === 409) {
      try {
        let res;
        if (applyMode.value === "upload") {
          const formData = new FormData();
          formData.append("resume_file", resumeFile.value);
          res = await api.put(`/applications/job/${applyingJobId.value}`, formData, {
            headers: { "Content-Type": "multipart/form-data" },
          });
        } else {
          res = await api.put(`/applications/job/${applyingJobId.value}`, {
            resume_text: resumeText.value,
          });
        }
        atsResult.value = res.data;
        await loadMyApps();
        return;
      } catch (retryErr) {
        applyError.value = retryErr.response?.data?.error || "Could not update your application. Please try again.";
        atsResult.value = { error: true };
        return;
      }
    }
    applyError.value = err.response?.data?.error || "Could not submit your application. Please try again.";
    atsResult.value = { error: true };
  } finally {
    applying.value = false;
  }
}

function closeApplyModal() {
  applyModal.value = false;
  atsResult.value = null;
  applyError.value = "";
  resumeFile.value = null;
}

function retryApplication() {
  atsResult.value = null;
  applyError.value = "";
}

function switchTab(nextTab) {
  tab.value = nextTab;
  if (nextTab === "applications") loadMyApps();
  if (nextTab === "browse") loadJobs();
}

function getScoreColor(score) {
  if (score >= 80) return "text-success-600";
  if (score >= 60) return "text-warning-600";
  return "text-danger-500";
}

function getScoreBg(score) {
  if (score >= 80) return "bg-success-500";
  if (score >= 60) return "bg-warning-500";
  return "bg-danger-400";
}

function getScoreLabel(score) {
  if (score >= 90) return "Excellent";
  if (score >= 75) return "Strong";
  if (score >= 60) return "Good";
  if (score >= 40) return "Fair";
  return "Needs Improvement";
}

function getScoreAdvice(score) {
  if (score >= 80) return "Your resume is a great match for this role. Consider applying with confidence.";
  if (score >= 60) return "Decent match. Highlight more relevant skills and quantify your achievements.";
  return "Consider tailoring your resume to better match the role and add specific keywords from the posting.";
}

onMounted(async () => {
  await Promise.all([loadJobs(), loadMyApps()]);
});
</script>

<template>
  <div class="min-h-screen employer-page">
    <Navbar />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10">
      <section class="employer-hero p-6 sm:p-8 mb-8 text-white">
        <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-5">
          <div>
            <p class="text-xs uppercase tracking-[0.18em] text-lime-300/90 mb-2">Employee Workspace</p>
            <h1 class="text-2xl sm:text-3xl font-semibold tracking-tight">
              Welcome, {{ auth.user?.name || "Job Seeker" }}
            </h1>
            <p class="text-sm text-neutral-200 mt-2">
              Browse active tenants, explore current openings, and submit tenant-scoped applications.
            </p>
          </div>
          <button
            @click="auth.logout(); router.push('/')"
            class="btn-press inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border border-white/20 bg-white/10 text-sm font-medium hover:bg-white/20"
          >
            <LogOut class="w-4 h-4" /> Sign out
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-6">
          <div class="hero-metric-card p-4">
            <p class="text-xs text-neutral-300 uppercase tracking-wide">Tenants Hiring</p>
            <p class="text-2xl font-semibold mt-1">{{ dashboardStats.tenants }}</p>
          </div>
          <div class="hero-metric-card p-4">
            <p class="text-xs text-neutral-300 uppercase tracking-wide">Open Roles</p>
            <p class="text-2xl font-semibold mt-1">{{ dashboardStats.jobs }}</p>
          </div>
          <div class="hero-metric-card p-4">
            <p class="text-xs text-neutral-300 uppercase tracking-wide">My Applications</p>
            <p class="text-2xl font-semibold mt-1">{{ dashboardStats.applications }}</p>
          </div>
        </div>
      </section>

      <div class="employer-tabs mb-6">
        <button
          @click="switchTab('browse')"
          :class="tab === 'browse' ? 'employer-tab employer-tab-active' : 'employer-tab'"
        >
          <Search class="w-4 h-4" /> Browse Jobs
        </button>
        <button
          @click="switchTab('applications')"
          :class="tab === 'applications' ? 'employer-tab employer-tab-active' : 'employer-tab'"
        >
          <FileText class="w-4 h-4" /> My Applications
        </button>
      </div>

      <div v-if="tab === 'browse'" class="space-y-6">
        <div class="dashboard-shell p-4 sm:p-5">
          <div class="grid grid-cols-1 md:grid-cols-[1fr,240px,120px] gap-3">
            <div class="relative">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
              <input
                v-model="searchQ"
                type="text"
                placeholder="Search by title, skills, company, or location"
                class="w-full pl-10 pr-3 py-2.5 rounded-xl border border-neutral-200 text-sm focus:ring-2 focus:ring-lime-200 focus:border-lime-400 focus:outline-none"
              />
            </div>
            <div class="relative">
              <Filter class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
              <select
                v-model="selectedTenant"
                class="w-full pl-10 pr-3 py-2.5 rounded-xl border border-neutral-200 text-sm bg-white focus:ring-2 focus:ring-lime-200 focus:border-lime-400 focus:outline-none"
              >
                <option value="all">All Tenants</option>
                <option v-for="tenant in tenantOptions" :key="tenant.key" :value="tenant.key">
                  {{ tenant.company }}
                </option>
              </select>
            </div>
            <button
              @click="clearBrowseFilters"
              class="btn-press px-3 py-2.5 rounded-xl border border-neutral-200 text-sm text-neutral-700 hover:bg-neutral-50"
            >
              Reset
            </button>
          </div>

          <div class="mt-4 flex items-center gap-4 text-sm text-neutral-500">
            <span class="inline-flex items-center gap-1.5"><Layers class="w-4 h-4" /> {{ filteredTenants.length }} tenants</span>
            <span class="inline-flex items-center gap-1.5"><Briefcase class="w-4 h-4" /> {{ totalVisibleJobs }} visible jobs</span>
          </div>
        </div>

        <div v-if="loadingJobs" class="space-y-3">
          <div v-for="i in 4" :key="i" class="dashboard-card p-6 animate-pulse">
            <div class="h-4 bg-neutral-200 rounded w-1/3 mb-3"></div>
            <div class="h-3 bg-neutral-100 rounded w-2/3 mb-2"></div>
            <div class="h-3 bg-neutral-100 rounded w-1/2"></div>
          </div>
        </div>

        <div v-else-if="filteredTenants.length === 0" class="dashboard-shell text-center py-14 px-6">
          <Briefcase class="w-12 h-12 text-neutral-300 mx-auto mb-3" />
          <h3 class="text-lg font-semibold text-neutral-700 mb-1">No matching jobs</h3>
          <p class="text-sm text-neutral-500">Try a broader search or select a different tenant.</p>
        </div>

        <div v-else class="space-y-5">
          <section
            v-for="tenant in filteredTenants"
            :key="tenant.tenant_key"
            class="dashboard-shell p-4 sm:p-5"
          >
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
              <div class="flex items-center gap-3 min-w-0">
                <div class="w-11 h-11 rounded-xl bg-lime-100 text-lime-700 flex items-center justify-center font-semibold text-sm">
                  {{ getTenantInitials(tenant.company) }}
                </div>
                <div class="min-w-0">
                  <h2 class="text-lg font-semibold text-neutral-900 truncate">{{ formatTenantName(tenant.company) }}</h2>
                  <p class="text-xs text-neutral-500">Tenant key: {{ tenant.tenant_key }}</p>
                </div>
              </div>
              <span class="text-xs font-medium text-neutral-600 bg-neutral-100 rounded-full px-3 py-1.5">
                {{ tenant.jobs.length }} open roles
              </span>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
              <article
                v-for="job in tenant.jobs"
                :key="job.id"
                class="dashboard-card dashboard-card-hover p-4 flex flex-col"
              >
                <div class="min-w-0">
                  <h3 class="text-base font-semibold text-neutral-900 line-clamp-2">{{ job.title }}</h3>
                  <div class="mt-1 text-sm text-neutral-500 flex flex-wrap items-center gap-x-3 gap-y-1">
                    <span class="inline-flex items-center gap-1 min-w-0"><Building2 class="w-3.5 h-3.5 shrink-0" /> <span class="truncate">{{ job.company }}</span></span>
                    <span v-if="job.location" class="inline-flex items-center gap-1"><MapPin class="w-3.5 h-3.5 shrink-0" /> {{ job.location }}</span>
                    <span v-if="job.type" class="inline-flex items-center gap-1"><Clock class="w-3.5 h-3.5 shrink-0" /> {{ job.type }}</span>
                  </div>
                </div>

                <p class="mt-3 text-sm text-neutral-600 line-clamp-2">{{ job.description }}</p>

                <div class="mt-3 flex flex-wrap gap-1.5">
                  <span
                    v-for="skill in (job.skills || '').split(',').slice(0, 6)"
                    :key="skill"
                    class="text-xs px-2.5 py-0.5 rounded-full bg-neutral-100 text-neutral-600"
                  >
                    {{ skill.trim() }}
                  </span>
                </div>

                <div class="mt-3 flex flex-wrap gap-4 text-xs text-neutral-500">
                  <span v-if="job.experience" class="inline-flex items-center gap-1">
                    <Clock class="w-3.5 h-3.5" /> {{ job.experience }} yrs exp
                  </span>
                  <span v-if="job.salary">{{ job.salary }}</span>
                </div>

                <div class="mt-4 pt-3 border-t border-neutral-100 flex justify-end">
                  <button
                    @click="openApply(job)"
                    class="btn-press whitespace-nowrap px-4 py-2 rounded-xl text-sm font-medium inline-flex items-center gap-2"
                    :class="hasApplied(job.id)
                      ? 'border border-lime-200 bg-lime-50 text-lime-800 hover:bg-lime-100'
                      : 'bg-lime-600 text-white hover:bg-lime-700'"
                  >
                    <Send class="w-4 h-4 shrink-0" /> {{ hasApplied(job.id) ? "Update resume" : "Apply" }}
                  </button>
                </div>
              </article>
            </div>
          </section>
        </div>
      </div>

      <div v-if="tab === 'applications'" class="space-y-4">
        <div v-if="loadingApps" class="space-y-3">
          <div v-for="i in 3" :key="i" class="dashboard-card p-6 animate-pulse">
            <div class="h-4 bg-neutral-200 rounded w-1/4 mb-3"></div>
            <div class="h-3 bg-neutral-100 rounded w-1/2"></div>
          </div>
        </div>

        <div v-else-if="myApps.length === 0" class="dashboard-shell text-center py-16">
          <FileText class="w-12 h-12 text-neutral-300 mx-auto mb-3" />
          <h3 class="text-lg font-semibold text-neutral-700 mb-1">No applications yet</h3>
          <p class="text-sm text-neutral-500 mb-4">Browse tenant jobs and submit your first application.</p>
          <button
            @click="switchTab('browse')"
            class="btn-press px-6 py-2.5 bg-lime-600 text-white text-sm rounded-xl font-medium inline-flex items-center gap-2"
          >
            <Search class="w-4 h-4" /> Browse Jobs
          </button>
        </div>

        <div v-else class="space-y-4">
          <p class="text-sm text-neutral-500">
            <span class="font-semibold text-neutral-900">{{ myApps.length }}</span> applications submitted
          </p>
          <div v-for="app in myApps" :key="app.id" class="dashboard-shell p-4 sm:p-6">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0 flex-1">
                <h3 class="text-base font-semibold text-neutral-900 truncate">{{ app.job_title }}</h3>
                <p class="text-sm text-neutral-500">{{ app.company || "Unknown Company" }} - Applied {{ app.applied_at }}</p>
              </div>
              <div class="text-right">
                <div class="text-2xl font-bold" :class="getScoreColor(app.ats_score)">
                  {{ app.ats_score }}
                </div>
                <div class="text-xs text-neutral-400">ATS Score</div>
              </div>
            </div>

            <div class="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div class="dashboard-muted-card p-3 text-center">
                <Target class="w-4 h-4 mx-auto text-lime-600 mb-1" />
                <div class="text-sm font-bold text-neutral-900">{{ app.breakdown?.skill_match || '-' }}</div>
                <div class="text-xs text-neutral-500">Skill Match</div>
              </div>
              <div class="dashboard-muted-card p-3 text-center">
                <Briefcase class="w-4 h-4 mx-auto text-lime-600 mb-1" />
                <div class="text-sm font-bold text-neutral-900">{{ app.breakdown?.title_relevance || '-' }}</div>
                <div class="text-xs text-neutral-500">Title Fit</div>
              </div>
              <div class="dashboard-muted-card p-3 text-center">
                <BookOpen class="w-4 h-4 mx-auto text-lime-600 mb-1" />
                <div class="text-sm font-bold text-neutral-900">{{ app.breakdown?.resume_quality || '-' }}</div>
                <div class="text-xs text-neutral-500">Resume Quality</div>
              </div>
              <div class="dashboard-muted-card p-3 text-center">
                <Hash class="w-4 h-4 mx-auto text-lime-600 mb-1" />
                <div class="text-sm font-bold text-neutral-900">{{ app.breakdown?.keyword_strength || '-' }}</div>
                <div class="text-xs text-neutral-500">Keywords</div>
              </div>
            </div>

            <p class="mt-3 text-xs text-neutral-500">{{ getScoreAdvice(app.ats_score) }}</p>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="applyModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/30 backdrop-blur-sm" @click="closeApplyModal"></div>
        <div class="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl max-h-[90vh] overflow-y-auto">
          <div class="p-5 sm:p-8">
            <div v-if="!atsResult">
              <h2 class="text-xl font-bold text-neutral-900 mb-1">
                {{ hasApplied(applyingJobId) ? "Update application for" : "Apply for" }} {{ applyingJobTitle }}
              </h2>
              <p class="text-sm text-neutral-500 mb-6">
                Company: <span class="font-medium text-neutral-700">{{ applyingCompany || "Unknown Company" }}</span>
                <span v-if="hasApplied(applyingJobId)" class="block mt-1 text-lime-700">
                  You already applied. Submit a new resume to refresh your ATS score.
                </span>
              </p>

              <div class="mb-4">
                <label class="text-xs font-medium text-neutral-700 mb-2 block">Resume / CV *</label>
                <div class="inline-flex rounded-xl bg-neutral-100 p-1 mb-3">
                  <button
                    @click="applyMode = 'text'"
                    :class="applyMode === 'text' ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-500'"
                    class="btn-press rounded-lg px-3 py-1.5 text-xs font-medium"
                  >Paste text</button>
                  <button
                    @click="applyMode = 'upload'"
                    :class="applyMode === 'upload' ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-500'"
                    class="btn-press rounded-lg px-3 py-1.5 text-xs font-medium"
                  >Upload file</button>
                </div>

                <div v-if="applyMode === 'text'">
                  <textarea
                    v-model="resumeText"
                    rows="12"
                    placeholder="Paste your full resume here including your experience, skills, education, and certifications"
                    class="w-full px-4 py-3 rounded-xl border border-neutral-200 text-sm focus:ring-2 focus:ring-lime-200 focus:border-lime-400 focus:outline-none resize-none"
                  ></textarea>
                  <p class="text-xs text-neutral-400 mt-1">{{ resumeText.split(/\s+/).filter((w) => w).length }} words</p>
                </div>

                <div v-else class="rounded-xl border border-dashed border-neutral-300 bg-neutral-50 p-4">
                  <input type="file" accept=".pdf,.docx,.txt,.md,.rtf" @change="onResumeFileSelected" class="block w-full text-sm text-neutral-600" />
                  <p class="text-xs text-neutral-400 mt-2">Upload a single resume file (PDF, DOCX, TXT, MD, RTF).</p>
                  <p v-if="resumeFile" class="text-xs text-neutral-600 mt-1">Selected: {{ resumeFile.name }}</p>
                </div>
              </div>

              <div class="flex gap-3">
                <button @click="closeApplyModal" class="btn-press flex-1 py-3 rounded-xl border border-neutral-200 text-sm font-medium text-neutral-600 hover:bg-neutral-50">Cancel</button>
                <button
                  @click="submitApplication"
                  :disabled="applying || (applyMode === 'text' ? !resumeText.trim() : !resumeFile)"
                  class="btn-press flex-1 py-3 rounded-xl bg-lime-600 text-white text-sm font-medium hover:bg-lime-700 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <Upload v-if="applyMode === 'upload'" class="w-4 h-4" />
                  <Sparkles v-else class="w-4 h-4" />
                  {{ applying ? "Analyzing..." : (hasApplied(applyingJobId) ? "Update & Re-score" : "Submit & Get ATS Score") }}
                </button>
              </div>
            </div>

            <div v-else-if="!atsResult.error">
              <div class="text-center mb-8">
                <div class="w-20 h-20 mx-auto mb-4 rounded-full flex items-center justify-center" :class="getScoreBg(atsResult.ats_score) + ' bg-opacity-10'">
                  <span class="text-3xl font-black" :class="getScoreColor(atsResult.ats_score)">{{ atsResult.ats_score }}</span>
                </div>
                <h2 class="text-xl font-bold text-neutral-900 mb-1">
                  {{ getScoreLabel(atsResult.ats_score) }} Match
                </h2>
                <p class="text-sm text-neutral-500">
                  {{ atsResult.updated ? "Application updated with a new ATS score for" : "ATS compatibility score for" }}
                  <strong>{{ applyingJobTitle }}</strong>
                </p>
              </div>

              <div class="grid grid-cols-2 gap-3 mb-6">
                <div class="dashboard-muted-card p-4">
                  <div class="flex items-center gap-2 mb-2">
                    <Target class="w-4 h-4 text-lime-600" />
                    <span class="text-xs font-medium text-neutral-600">Skill Match</span>
                  </div>
                  <div class="flex items-end gap-1">
                    <span class="text-2xl font-bold text-neutral-900">{{ atsResult.breakdown?.skill_match || 0 }}</span>
                    <span class="text-xs text-neutral-400 mb-1">/ 50</span>
                  </div>
                </div>
                <div class="dashboard-muted-card p-4">
                  <div class="flex items-center gap-2 mb-2">
                    <Briefcase class="w-4 h-4 text-lime-600" />
                    <span class="text-xs font-medium text-neutral-600">Title Relevance</span>
                  </div>
                  <div class="flex items-end gap-1">
                    <span class="text-2xl font-bold text-neutral-900">{{ atsResult.breakdown?.title_relevance || 0 }}</span>
                    <span class="text-xs text-neutral-400 mb-1">/ 20</span>
                  </div>
                </div>
                <div class="dashboard-muted-card p-4">
                  <div class="flex items-center gap-2 mb-2">
                    <BookOpen class="w-4 h-4 text-lime-600" />
                    <span class="text-xs font-medium text-neutral-600">Resume Quality</span>
                  </div>
                  <div class="flex items-end gap-1">
                    <span class="text-2xl font-bold text-neutral-900">{{ atsResult.breakdown?.resume_quality || 0 }}</span>
                    <span class="text-xs text-neutral-400 mb-1">/ 15</span>
                  </div>
                </div>
                <div class="dashboard-muted-card p-4">
                  <div class="flex items-center gap-2 mb-2">
                    <Hash class="w-4 h-4 text-lime-600" />
                    <span class="text-xs font-medium text-neutral-600">Keyword Strength</span>
                  </div>
                  <div class="flex items-end gap-1">
                    <span class="text-2xl font-bold text-neutral-900">{{ atsResult.breakdown?.keyword_strength || 0 }}</span>
                    <span class="text-xs text-neutral-400 mb-1">/ 15</span>
                  </div>
                </div>
              </div>

              <div class="bg-lime-50 rounded-xl p-4 mb-6">
                <div class="flex items-start gap-3">
                  <Sparkles class="w-5 h-5 text-lime-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <p class="text-sm font-medium text-lime-900">AI Recommendation</p>
                    <p class="text-sm text-lime-700 mt-1">{{ getScoreAdvice(atsResult.ats_score) }}</p>
                  </div>
                </div>
              </div>

              <div class="flex gap-3">
                <button @click="closeApplyModal" class="btn-press flex-1 py-3 rounded-xl border border-neutral-200 text-sm font-medium text-neutral-600 hover:bg-neutral-50">
                  Close
                </button>
                <button @click="switchTab('applications'); closeApplyModal()" class="btn-press flex-1 py-3 rounded-xl bg-lime-600 text-white text-sm font-medium hover:bg-lime-700 flex items-center justify-center gap-2">
                  <FileText class="w-4 h-4" /> View My Applications
                </button>
              </div>
            </div>

            <div v-else class="text-center py-8">
              <XCircle class="w-12 h-12 text-danger-400 mx-auto mb-3" />
              <h3 class="text-lg font-semibold text-neutral-700 mb-1">Something went wrong</h3>
              <p class="text-sm text-neutral-500 mb-4">{{ applyError }}</p>
              <button @click="retryApplication" class="btn-press px-6 py-2.5 bg-lime-600 text-white text-sm rounded-xl font-medium">Try again</button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <AppFooter />
  </div>
</template>
