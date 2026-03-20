// services/api.js – centralised Axios client for all backend calls

import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30_000,
  headers: { "Content-Type": "application/json" },
});

// Request interceptor: attach auth token if present
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("auth_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: normalise errors
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg =
      err.response?.data?.detail ||
      err.response?.data?.message ||
      err.message ||
      "An unknown error occurred";
    return Promise.reject(new Error(msg));
  }
);

// Health
export const fetchHealth = () => api.get("/").then((r) => r.data);

// Products
export const fetchProducts = ({ page = 1, size = 20, category } = {}) =>
  api.get("/products", { params: { page, size, ...(category ? { category } : {}) } }).then((r) => r.data);

export const fetchProduct = (id) => api.get(`/products/${id}`).then((r) => r.data);
export const fetchSimilarProducts = (id, n = 6) =>
  api.get(`/products/${id}/similar`, { params: { n } }).then((r) => r.data);
export const fetchTrendingProducts = (n = 8) =>
  api.get("/products/trending", { params: { n } }).then((r) => r.data);
export const fetchCategories = () => api.get("/products/categories").then((r) => r.data);

// Recommendations
export const fetchRecommendations = (userId, { n = 10, strategy = "hybrid", abTest = false } = {}) =>
  api.get(`/recommend/${userId}`, { params: { n, strategy, ab_test: abTest } }).then((r) => r.data);

// Interactions
export const postInteraction = ({ user_id, product_id, rating, interaction_type = "view" }) =>
  api.post("/interact", { user_id, product_id, rating, interaction_type }).then((r) => r.data);
export const fetchUserInteractions = (userId, limit = 20) =>
  api.get(`/interact/user/${userId}`, { params: { limit } }).then((r) => r.data);

// Users
export const fetchUser = (id) => api.get(`/users/${id}`).then((r) => r.data);

// Analytics
export const fetchDashboard = () => api.get("/analytics/dashboard").then((r) => r.data);

export default api;
