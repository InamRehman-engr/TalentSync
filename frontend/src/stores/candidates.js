import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { fetchCandidates } from "../api/candidates";

export const useCandidateStore = defineStore("candidates", () => {
  const candidates = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const searchQuery = ref("");
  const skillFilter = ref("");
  const statusFilter = ref("");
  const sortBy = ref("matchScore");

  const filteredCandidates = computed(() => candidates.value);

  async function loadCandidates() {
    loading.value = true;
    error.value = null;
    try {
      const params = {};
      if (searchQuery.value) params.q = searchQuery.value;
      if (skillFilter.value) params.skill = skillFilter.value;
      if (statusFilter.value) params.status = statusFilter.value;
      if (sortBy.value) params.sortBy = sortBy.value;

      const data = await fetchCandidates(params);
      candidates.value = data.candidates;
    } catch (err) {
      error.value = "Failed to load candidates. Please try again.";
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  function setSearch(query) {
    searchQuery.value = query;
    loadCandidates();
  }

  function setSkillFilter(skill) {
    skillFilter.value = skill;
    loadCandidates();
  }

  function setStatusFilter(status) {
    statusFilter.value = status;
    loadCandidates();
  }

  function setSortBy(field) {
    sortBy.value = field;
    loadCandidates();
  }

  return {
    candidates,
    loading,
    error,
    searchQuery,
    skillFilter,
    statusFilter,
    sortBy,
    filteredCandidates,
    loadCandidates,
    setSearch,
    setSkillFilter,
    setStatusFilter,
    setSortBy,
  };
});
