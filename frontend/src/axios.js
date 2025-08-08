import axios from "axios";

export const baseURL = "http://localhost:8000";

const axiosInstance = axios.create({
  baseURL: baseURL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",

  },
});

export default axiosInstance;
