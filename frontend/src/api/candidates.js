import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 50000,
});

export async function fetchCandidates(params = {}) {
  const { data } = await api.get("/candidates/search", { params });
  return data;
}

export async function fetchCandidateById(id) {
  const { data } = await api.get(`/candidates/${id}`);
  return data;
}

export default api;
