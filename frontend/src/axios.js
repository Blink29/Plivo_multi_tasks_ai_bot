import axios from "axios";

// Use environment variable for API base URL, fallback to localhost for development
export const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

console.log("🔍 Frontend API Base URL:", baseURL); // Debug log

const axiosInstance = axios.create({
  baseURL: baseURL,
  // withCredentials: true, // Temporarily commented out
  headers: {
    "Content-Type": "application/json",
  },
});

export default axiosInstance;
