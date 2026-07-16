import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { api } from "../api/axios";
import type {
  Movie,
  UserProfile,
  UserUpdateProfile,
  UserHistory,
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

interface UploadImageResponse {
  filename: string;
  content_type: string;
  message: string;
}

// ---- Настройки поллинга ----

const POLL_INTERVAL_MS = 1500;
const POLL_TIMEOUT_MS = 60_000; // если за минуту не готово — считаем сервис недоступным

// ---- Настройки загрузки аватара ----

const MAX_AVATAR_SIZE = 5 * 1024 * 1024; // 5 MB, держим в синхроне с бэком
const ALLOWED_AVATAR_TYPES = ["image/jpeg", "image/png", "image/webp"];

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const extractDetail = (err: unknown): string | undefined =>
  (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;

export const useMovieStore = defineStore("movie", () => {
  const movies = ref<Movie[]>([]);
  const recommendations = ref<Movie[] | null>(null);
  const lastPrompt = ref("");
  const isLoading = ref(false);
  const isFetchingMovies = ref(false);
  const error = ref("");

  // ---- Избранное (пагинация курсором) ----
  const likedMovies = ref<Movie[]>([]);
  const likedNextCursor = ref<number | null>(null);
  const likedHasMore = ref(true);
  const isLoadingLiked = ref(false);

  const catalogMovies = computed(() => movies.value);

  const fetchMovies = async () => {
    isFetchingMovies.value = true;
    error.value = "";
    try {
      const res = await api.get<Movie[]>("/movie");
      movies.value = res.data;
    } catch (err: unknown) {
      error.value = extractDetail(err) || "Ошибка при загрузке фильмов";
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
      const detail = extractDetail(err);
      const message =
        detail || (err instanceof Error ? err.message : "Сервис рекомендаций временно недоступен");
      error.value = message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const getLikedMovies = async (reset = false) => {
    if (isLoadingLiked.value) return;

    if (reset) {
      likedMovies.value = [];
      likedNextCursor.value = null;
      likedHasMore.value = true;
    }

    if (!likedHasMore.value) return;

    isLoadingLiked.value = true;
    try {
      const params: Record<string, number> = { limit: 12 };
      if (likedNextCursor.value !== null) {
        params.cursor = likedNextCursor.value;
      }

      // бэкенд отдаёт поле "movies", а не "items"
      const res = await api.get<{
        movies: Movie[];
        next_cursor: number | null;
        has_more: boolean;
      }>("/actions/like/my", { params });

      likedMovies.value.push(...res.data.movies);
      likedNextCursor.value = res.data.next_cursor;
      likedHasMore.value = res.data.has_more;
    } catch (err: unknown) {
      error.value = extractDetail(err) || "Ошибка при загрузке избранного";
      if (reset) likedMovies.value = [];
    } finally {
      isLoadingLiked.value = false;
    }
  };

  const likeMovie = async (movieId: number) => {
    try {
      await api.post(`/actions/like/${movieId}`);
      await getLikedMovies(true); // перезагружаем список избранного с начала
    } catch (err: unknown) {
      error.value = extractDetail(err) || "Ошибка при добавлении в избранное";
      throw err;
    }
  };

  const unlikeMovie = async (movieId: number) => {
    try {
      await api.delete(`/actions/like/${movieId}`);
      likedMovies.value = likedMovies.value.filter((movie) => movie.id !== movieId);
    } catch (err: unknown) {
      error.value = extractDetail(err) || "Ошибка при удалении из избранного";
      throw err;
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
    likedNextCursor,
    likedHasMore,
    isLoadingLiked,
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
  const isUploadingImage = ref(false);
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
      const detail = extractDetail(err);

      // локализуем известные ошибки бэкенда
      if (detail === "Profile name already exists") {
        error.value = "Это имя уже занято, выберите другое";
      } else {
        error.value = detail || "Ошибка при обновлении профиля";
      }
      throw err;
    }
  };

  const validateAvatarFile = (file: File): string | null => {
    if (!ALLOWED_AVATAR_TYPES.includes(file.type)) {
      return "Допустимые форматы: JPEG, PNG, WEBP";
    }
    if (file.size > MAX_AVATAR_SIZE) {
      return `Файл слишком большой (максимум ${MAX_AVATAR_SIZE / (1024 * 1024)} МБ)`;
    }
    return null;
  };

  const uploadProfileImage = async (file: File) => {
    const validationError = validateAvatarFile(file);
    if (validationError) {
      error.value = validationError;
      throw new Error(validationError);
    }

    isUploadingImage.value = true;
    error.value = "";
    try {
      const formData = new FormData();
      formData.append("file", file);

      await api.post<UploadImageResponse>("/profile/me/upload-profile-image", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      // бэкенд не возвращает обновлённый профиль — перезапрашиваем,
      // чтобы подтянуть свежий image_url
      await getProfile();
    } catch (err: unknown) {
      error.value = extractDetail(err) || "Ошибка при загрузке изображения";
      throw err;
    } finally {
      isUploadingImage.value = false;
    }
  };

  return {
    profile,
    isLoading,
    isUploadingImage,
    error,
    hasName,
    getProfile,
    updateProfile,
    uploadProfileImage,
  };
});

export const useHistoryStore = defineStore("history", () => {
  const history = ref<UserHistory[]>([]);
  const nextCursor = ref<number | null>(null);
  const hasMore = ref(true);
  const isLoading = ref(false);
  const error = ref("");

  const getHistory = async (reset = false) => {
    if (isLoading.value) return;

    if (reset) {
      history.value = [];
      nextCursor.value = null;
      hasMore.value = true;
    }

    if (!hasMore.value) return;

    isLoading.value = true;
    error.value = "";
    try {
      const params: Record<string, number> = { limit: 10 };
      if (nextCursor.value !== null) {
        params.cursor = nextCursor.value;
      }

      const res = await api.get<{
        history: UserHistory[];
        next_cursor: number | null;
        has_more: boolean;
      }>("/actions/history", { params });

      history.value.push(...res.data.history);
      nextCursor.value = res.data.next_cursor;
      hasMore.value = res.data.has_more;
    } catch (err: unknown) {
      error.value = extractDetail(err) || "Ошибка при загрузке истории";
    } finally {
      isLoading.value = false;
    }
  };

  return {
    history,
    nextCursor,
    hasMore,
    isLoading,
    error,
    getHistory,
  };
});