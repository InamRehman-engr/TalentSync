import { defineStore } from "pinia";
import { ref, computed } from "vue";
import axios from "axios";

export const api = axios.create({ baseURL: "/api", timeout: 10000 });

export const useAuthStore = defineStore("auth", () => {
  const token = ref(localStorage.getItem("ts_token") || "");
  const user = ref(JSON.parse(localStorage.getItem("ts_user") || "null"));
  const loading = ref(false);
  const error = ref(null);

  const isLoggedIn = computed(() => !!token.value && !!user.value);
  const isEmployer = computed(() => user.value?.role === "employer");
  const isEmployee = computed(() => user.value?.role === "employee");

  function setSession(t, u) {
    token.value = t;
    user.value = u;
    localStorage.setItem("ts_token", t);
    localStorage.setItem("ts_user", JSON.stringify(u));
    api.defaults.headers.common["Authorization"] = `Bearer ${t}`;
  }

  function clearSession() {
    token.value = "";
    user.value = null;
    localStorage.removeItem("ts_token");
    localStorage.removeItem("ts_user");
    delete api.defaults.headers.common["Authorization"];
  }

  // Restore token on load
  if (token.value) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token.value}`;
  }

  // Auto-handle 401 responses — redirect to login
  api.interceptors.response.use(
    (res) => res,
    (err) => {
      if (err.response?.status === 401 && token.value) {
        clearSession();
        window.location.href = "/login";
      }
      return Promise.reject(err);
    }
  );

  async function login(email, password) {
    loading.value = true;
    error.value = null;
    try {
      const { data } = await api.post("/auth/login", { email, password });
      setSession(data.token, data.user);
      return data.user;
    } catch (err) {
      error.value = err.response?.data?.error || "Login failed";
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function register(payload) {
    loading.value = true;
    error.value = null;
    try {
      const { data } = await api.post("/auth/register", payload);
      setSession(data.token, data.user);
      return data.user;
    } catch (err) {
      const body = err.response?.data;
      error.value = body?.error || "Registration failed";
      if (err.response?.status === 409) {
        error.value = body?.error || "An account with this email already exists.";
      }
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function resetPassword(email, newPassword) {
    loading.value = true;
    error.value = null;
    try {
      const { data } = await api.post("/auth/reset-password", {
        email,
        new_password: newPassword,
      });
      return data;
    } catch (err) {
      error.value = err.response?.data?.error || "Could not reset password";
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function logout() {
    try {
      await api.post("/auth/logout");
    } catch (_) {
      // Ignore logout errors
    }
    clearSession();
  }

  return {
    token, user, loading, error,
    isLoggedIn, isEmployer, isEmployee,
    login, register, resetPassword, logout,
  };
});
