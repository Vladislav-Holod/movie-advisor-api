import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { api } from "../api/axios";
import type {
  Movie,
  UserProfile,
  UserUpdateProfile,
} from "../types";

// ---- Типы под ответы задачи рекомендаций ----

type TaskStatus = "pending" | "running" | "success" | "failed";

interface CreateTaskResponse {
  task_id: string;
}

interface TaskStatusResponse {
  status: TaskStatus;
  movies?: Movie[];
  error?: string | null;
}

// ---- Настройки поллинга ----

const POLL_INTERVAL_MS = 1500;
const POLL_TIMEOUT_MS = 60_000; // если за минуту не готово — считаем сервис недоступным

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const useMovieStore = defineStore("movie", () => {
  const movies = ref<Movie[]>([]);
  const likedMovies = ref<Movie[]>([]);
  const recommendations = ref<Movie[] | null>(null);
  const lastPrompt = ref("");
  const isLoading = ref(false);
  const isFetchingMovies = ref(false);
  const error = ref("");

  const catalogMovies = computed(() => movies.value);

  const fetchMovies = async () => {
    isFetchingMovies.value = true;
    error.value = "";
    try {
      const res = await api.get<Movie[]>("/movie");
      movies.value = res.data;
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      error.value = detail || "Ошибка при загрузке фильмов";
      movies.value = [];
    } finally {
      isFetchingMovies.value = false;
    }
  };

  const pollTaskStatus = async (taskId: string): Promise<Movie[]> => {
    const startedAt = Date.now();

    while (true) {
      if (Date.now() - startedAt > POLL_TIMEOUT_MS) {
        throw new Error("Превышено время ожидания ответа от сервиса рекомендаций");
      }

      const res = await api.get<TaskStatusResponse>(`/movie/tasks/${taskId}`);
      const { status, movies: resultMovies, error: taskError } = res.data;

      if (status === "success") {
        return resultMovies ?? [];
      }

      if (status === "failed") {
        throw new Error(taskError || "Не удалось получить рекомендации");
      }

      // pending / running — ждём и спрашиваем снова
      await sleep(POLL_INTERVAL_MS);
    }
  };

  const getRecommendations = async (prompt: string) => {
    isLoading.value = true;
    error.value = "";
    lastPrompt.value = prompt;
    try {
      // 1. создаём задачу, получаем task_id
      const createRes = await api.post<CreateTaskResponse>("/movie/recommend", { prompt });
      const { task_id } = createRes.data;

      // 2. опрашиваем статус, пока не готово
      const result = await pollTaskStatus(task_id);

      recommendations.value = result;
      return result;
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      const message =
        detail || (err instanceof Error ? err.message : "Сервис рекомендаций временно недоступен");
      error.value = message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const likeMovie = async (movieId: number) => {
    try {
      await api.post(`/actions/like/${movieId}`);
      await getLikedMovies();
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      error.value = detail || "Ошибка при добавлении в избранное";
      throw err;
    }
  };

  const unlikeMovie = async (movieId: number) => {
    try {
      await api.delete(`/actions/like/${movieId}`);
      likedMovies.value = likedMovies.value.filter((movie) => movie.id !== movieId);
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      error.value = detail || "Ошибка при удалении из избранного";
      throw err;
    }
  };

  const getLikedMovies = async () => {
    try {
      const res = await api.get<Movie[]>("/actions/like/my");
      likedMovies.value = res.data;
    } catch {
      likedMovies.value = [];
    }
  };

  const isLiked = computed(() => {
    return (movieId: number) => likedMovies.value.some((m) => m.id === movieId);
  });

  const clearRecommendations = () => {
    recommendations.value = null;
    error.value = "";
  };

  return {
    movies,
    likedMovies,
    recommendations,
    lastPrompt,
    isLoading,
    isFetchingMovies,
    error,
    catalogMovies,
    fetchMovies,
    getRecommendations,
    likeMovie,
    unlikeMovie,
    getLikedMovies,
    isLiked,
    clearRecommendations,
  };
});

export const useProfileStore = defineStore("profile", () => {
  const profile = ref<UserProfile | null>(null);
  const isLoading = ref(false);
  const error = ref("");

  const hasName = computed(() => !!profile.value?.name?.trim());

  const getProfile = async () => {
    isLoading.value = true;
    error.value = "";
    try {
      const res = await api.get<UserProfile>("/profile/me");
      profile.value = res.data;
    } catch {
      profile.value = null;
      error.value = "Ошибка при загрузке профиля";
    } finally {
      isLoading.value = false;
    }
  };

  const updateProfile = async (data: UserUpdateProfile) => {
    try {
      const res = await api.put<UserProfile>("/profile/me", data);
      profile.value = res.data;
      return res.data;
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      error.value = detail || "Ошибка при обновлении профиля";
      throw err;
    }
  };

  return {
    profile,
    isLoading,
    error,
    hasName,
    getProfile,
    updateProfile,
  };
});