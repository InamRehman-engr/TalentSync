<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { showEmployeeDashboard, showQuickDemo } from "../router/index";
import Navbar from "../components/Navbar.vue";
import AppFooter from "../components/AppFooter.vue";
import { Mail, Lock, User, Building2, Briefcase, ArrowRight, Eye, EyeOff } from "lucide-vue-next";

const router = useRouter();
const auth = useAuthStore();

const mode = ref("login"); // login | register | reset
const role = ref("employer"); // employer | employee

const form = ref({
  email: "",
  password: "",
  confirmPassword: "",
  name: "",
  company: "",
  title: "",
});

const showPassword = ref(false);
const localError = ref("");
const successMessage = ref("");

async function handleSubmit() {
  localError.value = "";
  successMessage.value = "";

  if (!form.value.email) {
    localError.value = "Email is required";
    return;
  }

  if (mode.value === "reset") {
    if (!form.value.password || !form.value.confirmPassword) {
      localError.value = "Enter and confirm your new password";
      return;
    }
    if (form.value.password !== form.value.confirmPassword) {
      localError.value = "Passwords do not match";
      return;
    }
    if (form.value.password.length < 6) {
      localError.value = "Password must be at least 6 characters";
      return;
    }
    try {
      await auth.resetPassword(form.value.email, form.value.password);
      successMessage.value = "Password updated. Sign in with your new password.";
      form.value.password = "";
      form.value.confirmPassword = "";
      mode.value = "login";
    } catch {
      localError.value = auth.error || "Could not reset password";
    }
    return;
  }

  if (!form.value.password) {
    localError.value = "Password is required";
    return;
  }

  try {
    if (mode.value === "login") {
      const user = await auth.login(form.value.email, form.value.password);
      redirectByRole(user.role);
    } else {
      if (!form.value.name) {
        localError.value = "Name is required";
        return;
      }
      const user = await auth.register({
        email: form.value.email,
        password: form.value.password,
        name: form.value.name,
        role: role.value,
        company: form.value.company,
        title: form.value.title,
      });
      redirectByRole(user.role);
    }
  } catch (err) {
    if (mode.value === "register" && err.response?.status === 409) {
      localError.value = auth.error || "This email is already registered.";
    } else {
      localError.value = auth.error || "Something went wrong";
    }
  }
}

function switchMode(nextMode) {
  mode.value = nextMode;
  localError.value = "";
  successMessage.value = "";
  if (nextMode !== "reset") {
    form.value.confirmPassword = "";
  }
}

function redirectByRole(r) {
  if (r === "employer") {
    router.push("/employer");
  } else if (r === "employee" && showEmployeeDashboard) {
    router.push("/employee");
  } else {
    router.push("/");
  }
}

const errorMessage = computed(() => localError.value || auth.error || "");

// Demo credentials
const demoCredentials = {
  employer: { email: "employer1@talentsync.com", password: "Employer@123" },
  employee: { email: "employee1@talentsync.com", password: "Employee@123" },
};

function selectRole(type) {
  role.value = type;
  if (!showQuickDemo) return;

  const creds = demoCredentials[type];
  form.value.email = creds.email;
  form.value.password = creds.password;
  mode.value = "login";
}
</script>

<template>
  <div class="min-h-screen bg-white">
    <Navbar />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-16">
      <div class="grid lg:grid-cols-2 gap-10 sm:gap-16 items-center">
        <!-- Left: Info Panel -->
        <div class="hidden lg:block">
          <div class="mb-8">
            <p class="text-sm font-semibold text-primary-600 tracking-wide uppercase mb-3">
              {{ role === 'employer' ? 'Employer Portal' : 'Employee Portal' }}
            </p>
            <h1 class="text-3xl font-bold text-neutral-900 leading-tight mb-4">
              {{ role === 'employer' ? 'Find your next great hire' : 'Land your dream job' }}
            </h1>
            <p class="text-neutral-500 leading-relaxed">
              {{ role === 'employer'
                ? 'Post job descriptions, search candidates with AI-powered scoring, and build your dream team — all from one dashboard.'
                : 'Browse open positions, submit your resume, get instant ATS feedback, and track your applications in real time.'
              }}
            </p>
          </div>

        </div>

        <!-- Right: Login/Register Form -->
        <div class="w-full max-w-md mx-auto lg:mx-0">
          <div class="rounded-2xl border border-neutral-100 p-8 lg:p-10">
            <!-- Role selector (also fills demo credentials when quick demo is enabled) -->
            <div v-if="showEmployeeDashboard && mode !== 'reset'" class="space-y-3 mb-6">
              <p class="text-xs text-neutral-500 uppercase tracking-wider font-medium">
                {{ showQuickDemo ? 'Quick demo — I am a' : 'I am a' }}
              </p>
              <div class="flex gap-3">
                <button
                  type="button"
                  @click="selectRole('employer')"
                  class="btn-press flex-1 flex items-center gap-3 px-4 py-3.5 rounded-xl border-2 transition-all"
                  :class="role === 'employer'
                    ? 'border-primary-600 bg-primary-50 text-primary-700'
                    : 'border-neutral-200 text-neutral-600 hover:border-neutral-300'"
                >
                  <Building2 class="w-5 h-5 shrink-0" />
                  <div class="text-left min-w-0">
                    <div class="text-sm font-semibold">Employer</div>
                    <div class="text-xs opacity-70 truncate">Post jobs & find talent</div>
                  </div>
                </button>
                <button
                  type="button"
                  @click="selectRole('employee')"
                  class="btn-press flex-1 flex items-center gap-3 px-4 py-3.5 rounded-xl border-2 transition-all"
                  :class="role === 'employee'
                    ? 'border-primary-600 bg-primary-50 text-primary-700'
                    : 'border-neutral-200 text-neutral-600 hover:border-neutral-300'"
                >
                  <Briefcase class="w-5 h-5 shrink-0" />
                  <div class="text-left min-w-0">
                    <div class="text-sm font-semibold">Employee</div>
                    <div class="text-xs opacity-70 truncate">Apply & track jobs</div>
                  </div>
                </button>
              </div>
            </div>

            <!-- Mode Tabs -->
            <div v-if="mode !== 'reset'" class="flex gap-1 bg-neutral-100 rounded-lg p-1 mb-6">
              <button
                type="button"
                @click="switchMode('login')"
                class="flex-1 text-sm font-medium py-2 rounded-md transition-all"
                :class="mode === 'login' ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-500'"
              >Sign In</button>
              <button
                type="button"
                @click="switchMode('register')"
                class="flex-1 text-sm font-medium py-2 rounded-md transition-all"
                :class="mode === 'register' ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-500'"
              >Create Account</button>
            </div>

            <div v-else class="mb-6">
              <button
                type="button"
                @click="switchMode('login')"
                class="text-sm text-primary-600 hover:text-primary-800 font-medium"
              >← Back to sign in</button>
              <h2 class="text-lg font-semibold text-neutral-900 mt-3">Reset password</h2>
              <p class="text-sm text-neutral-500 mt-1">Enter your registered email and choose a new password.</p>
            </div>

            <!-- Success -->
            <div v-if="successMessage" class="mb-4 px-4 py-3 rounded-xl bg-success-50 text-success-700 text-sm">
              {{ successMessage }}
            </div>

            <!-- Error -->
            <div v-if="errorMessage" class="mb-4 px-4 py-3 rounded-xl bg-danger-50 text-danger-700 text-sm">
              {{ errorMessage }}
              <button
                v-if="mode === 'register' && errorMessage.includes('already exists')"
                type="button"
                @click="switchMode('reset')"
                class="block mt-2 text-primary-700 font-medium hover:underline"
              >Reset password instead</button>
            </div>

            <form @submit.prevent="handleSubmit" class="space-y-4">
              <!-- Name (register only) -->
              <div v-if="mode === 'register'">
                <label class="block text-xs font-medium text-neutral-700 mb-1.5">Full name</label>
                <div class="relative">
                  <User class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                  <input
                    v-model="form.name"
                    type="text"
                    placeholder="Ahmed Raza"
                    class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400"
                  />
                </div>
              </div>

              <!-- Email -->
              <div>
                <label class="block text-xs font-medium text-neutral-700 mb-1.5">Email</label>
                <div class="relative">
                  <Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                  <input
                    v-model="form.email"
                    type="email"
                    placeholder="you@company.com"
                    class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400"
                  />
                </div>
              </div>

              <!-- Password -->
              <div>
                <label class="block text-xs font-medium text-neutral-700 mb-1.5">
                  {{ mode === 'reset' ? 'New password' : 'Password' }}
                </label>
                <div class="relative">
                  <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                  <input
                    v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="••••••••"
                    class="w-full pl-10 pr-10 py-2.5 rounded-xl border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400"
                  />
                  <button type="button" @click="showPassword = !showPassword" class="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600">
                    <EyeOff v-if="showPassword" class="w-4 h-4" />
                    <Eye v-else class="w-4 h-4" />
                  </button>
                </div>
              </div>

              <!-- Confirm password (reset) -->
              <div v-if="mode === 'reset'">
                <label class="block text-xs font-medium text-neutral-700 mb-1.5">Confirm new password</label>
                <div class="relative">
                  <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                  <input
                    v-model="form.confirmPassword"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="••••••••"
                    class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400"
                  />
                </div>
              </div>

              <p v-if="mode === 'login'" class="text-right">
                <button
                  type="button"
                  @click="switchMode('reset')"
                  class="text-xs text-primary-600 hover:text-primary-800 font-medium"
                >Forgot password?</button>
              </p>

              <!-- Company (employer register) -->
              <div v-if="mode === 'register' && role === 'employer'">
                <label class="block text-xs font-medium text-neutral-700 mb-1.5">Company name</label>
                <div class="relative">
                  <Building2 class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                  <input
                    v-model="form.company"
                    type="text"
                    placeholder="Your Company"
                    class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400"
                  />
                </div>
              </div>

              <!-- Title (register) -->
              <div v-if="mode === 'register'">
                <label class="block text-xs font-medium text-neutral-700 mb-1.5">
                  {{ role === 'employer' ? 'Your role' : 'Job title' }}
                </label>
                <div class="relative">
                  <Briefcase class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                  <input
                    v-model="form.title"
                    type="text"
                    :placeholder="role === 'employer' ? 'e.g. HR Director' : 'e.g. Frontend Engineer'"
                    class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400"
                  />
                </div>
              </div>

              <!-- Submit -->
              <button
                type="submit"
                :disabled="auth.loading"
                class="btn-press w-full flex items-center justify-center gap-2 py-3 rounded-full bg-primary-600 text-white text-sm font-semibold hover:bg-primary-700 transition-colors disabled:opacity-50"
              >
                <span v-if="auth.loading">{{ mode === 'reset' ? 'Updating…' : 'Signing in…' }}</span>
                <span v-else-if="mode === 'login'">Sign In</span>
                <span v-else-if="mode === 'register'">Create Account</span>
                <span v-else>Update Password</span>
                <ArrowRight v-if="!auth.loading" class="w-4 h-4" />
              </button>
            </form>

            <!-- Employer-only quick demo when employee dashboard is disabled -->
            <div v-if="showQuickDemo && !showEmployeeDashboard" class="mt-6 pt-4 border-t border-neutral-100">
              <p class="text-xs font-semibold text-neutral-700 mb-3">Quick demo access</p>
              <button
                type="button"
                @click="selectRole('employer')"
                class="btn-press w-full text-xs font-medium px-4 py-2.5 rounded-full bg-neutral-900 text-white hover:bg-neutral-800 transition-colors"
              >
                Try employer demo
              </button>
            </div>

            <p class="mt-6 text-xs text-neutral-400 text-center">
              By continuing, you agree to our
              <router-link to="/terms" class="text-primary-600 hover:text-primary-800">Terms</router-link>
              and
              <router-link to="/privacy" class="text-primary-600 hover:text-primary-800">Privacy Policy</router-link>.
            </p>
          </div>
        </div>
      </div>
    </div>

    <AppFooter />
  </div>
</template>
