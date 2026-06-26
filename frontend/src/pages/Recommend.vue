<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useMovieStore } from "../stores/movie";
import { useProfileStore } from "../stores/movie";
import { useAuthStore } from "../stores/auth";
import MovieCard from "../components/MovieCard.vue";

const movieStore = useMovieStore();
const profileStore = useProfileStore();
const authStore = useAuthStore();

const prompt = ref("");
const serviceUnavailable = ref(false);
const currentPhrase = ref(0);

const SUGGESTIONS = [
  "Фильмы про космос и будущее человечества",
  "Лёгкая комедия для вечера с друзьями",
  "Детективы с неожиданной развязкой",
  "Классика советского кино",
  "Драмы про настоящую дружбу",
  "Боевики с харизматичным героем",
];

const LOADING_PHRASES = [
  "🔍 Анализируем ваш запрос...",
  "🤖 AI подбирает фильмы...",
  "🎬 Ищем лучшие совпадения...",
  "⭐ Оцениваем рейтинги...",
  "🎯 Финальный отбор подборки...",
  "✨ Почти готово!",
];

let phraseInterval: ReturnType<typeof setInterval> | null = null;

const startPhraseLoop = () => {
  currentPhrase.value = 0;
  phraseInterval = setInterval(() => {
    if (currentPhrase.value < LOADING_PHRASES.length - 1) {
      currentPhrase.value++;
    }
  }, 2200);
};

const stopPhraseLoop = () => {
  if (phraseInterval) {
    clearInterval(phraseInterval);
    phraseInterval = null;
  }
};

onMounted(() => {
  if (authStore.isAuthenticated()) {
    profileStore.getProfile();
    movieStore.getLikedMovies();
  }
});

const handleSubmit = async () => {
  if (prompt.value.trim().length < 10) {
    movieStore.error = "Запрос должен содержать минимум 10 символов";
    return;
  }
  serviceUnavailable.value = false;
  movieStore.clearRecommendations();
  startPhraseLoop();
  try {
    await movieStore.getRecommendations(prompt.value.trim());
  } catch {
    serviceUnavailable.value = true;
  } finally {
    stopPhraseLoop();
  }
};

const useSuggestion = (text: string) => {
  prompt.value = text;
};

const reset = () => {
  prompt.value = "";
  serviceUnavailable.value = false;
  movieStore.clearRecommendations();
  stopPhraseLoop();
};
</script>

<template>
  <div class="recommend-container">
    <div class="page-header">
      <h1>🤖 AI Рекомендации</h1>
      <p>Опишите, какие фильмы хотите найти — система подберёт подборку</p>
    </div>

    <div v-if="!authStore.isAuthenticated()" class="auth-banner">
      <div class="lock-icon">🔒</div>
      <h2>AI рекомендации доступны после входа</h2>
      <p>Войдите или зарегистрируйтесь, чтобы получить персональный подбор фильмов</p>
      <router-link to="/auth" class="btn-auth">Войти или зарегистрироваться</router-link>
    </div>

    <template v-else>
      <div class="prompt-section">
        <textarea
          v-model="prompt"
          rows="4"
          maxlength="300"
          placeholder="Например: атмосферный sci-fi про время..."
          class="prompt-textarea"
          :disabled="movieStore.isLoading"
        />

        <div class="prompt-footer">
          <span class="char-count">{{ prompt.length }}/300</span>
          <div class="prompt-actions">
            <button
              v-if="movieStore.recommendations || serviceUnavailable"
              type="button"
              class="btn-reset"
              @click="reset"
            >
              Сбросить
            </button>
            <button
              type="button"
              class="btn-submit"
              :disabled="movieStore.isLoading || prompt.trim().length < 10"
              @click="handleSubmit"
            >
              <span v-if="!movieStore.isLoading">✨ Найти фильмы</span>
              <span v-else class="btn-loading">
                <span class="btn-dot"></span>
                <span class="btn-dot"></span>
                <span class="btn-dot"></span>
              </span>
            </button>
          </div>
        </div>

        <div class="suggestions">
          <button
            v-for="s in SUGGESTIONS"
            :key="s"
            class="suggestion-chip"
            :disabled="movieStore.isLoading"
            @click="useSuggestion(s)"
          >
            {{ s }}
          </button>
        </div>
      </div>

      <div v-if="movieStore.error && !movieStore.isLoading" class="alert alert-error">
        ⚠️ {{ movieStore.error }}
      </div>

      <div v-if="serviceUnavailable" class="alert alert-warning">
        🚧 Сервис временно недоступен. Попробуйте позже.
      </div>

      <div v-if="movieStore.isLoading" class="loading-state">
        <div class="ai-loader">
          <div class="ai-ring"></div>
          <div class="ai-ring ai-ring--2"></div>
          <div class="ai-ring ai-ring--3"></div>
          <div class="ai-icon">✨</div>
        </div>

        <div class="loading-phrase-wrapper">
          <transition name="phrase-fade" mode="out-in">
            <p :key="currentPhrase" class="loading-phrase">
              {{ LOADING_PHRASES[currentPhrase] }}
            </p>
          </transition>
        </div>

        <div class="skeleton-grid">
          <div class="skeleton-card" v-for="i in 6" :key="i">
            <div class="skeleton-poster"></div>
            <div class="skeleton-title"></div>
            <div class="skeleton-meta"></div>
          </div>
        </div>
      </div>

      <div v-else-if="movieStore.recommendations && movieStore.recommendations.length > 0" class="results">
        <div class="results-header">
          <h2>🎬 Подборка для вас</h2>
          <p class="results-prompt">Запрос: «{{ prompt || movieStore.lastPrompt }}»</p>
          <span class="results-count">{{ movieStore.recommendations.length }} фильмов</span>
        </div>
        <div class="movies-grid">
          <MovieCard
            v-for="m in movieStore.recommendations"
            :key="m.id"
            :movie="m"
            class="movie-card-appear"
          />
        </div>
      </div>

      <div v-else-if="!movieStore.isLoading && !movieStore.error" class="empty-hint">
        <div class="empty-icon">✨</div>
        <p>Введите запрос и нажмите «Найти фильмы»</p>
        <p class="empty-sub">AI проанализирует запрос и подберёт лучшие варианты из базы Кинопоиска</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.recommend-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header { margin-bottom: 2rem; }
.page-header h1 { font-size: 2rem; font-weight: 800; color: #1a202c; margin: 0 0 0.5rem; }
.page-header p { color: #718096; margin: 0; }

.auth-banner {
  background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 100%);
  border: 2px solid #c7d2fe;
  border-radius: 20px;
  padding: 4rem 2rem;
  text-align: center;
}
.lock-icon { font-size: 3rem; margin-bottom: 1rem; }
.auth-banner h2 { color: #1a202c; font-size: 1.5rem; font-weight: 800; margin: 0 0 0.75rem; }
.auth-banner p { color: #718096; margin: 0 0 2rem; max-width: 420px; margin-left: auto; margin-right: auto; }
.btn-auth {
  display: inline-block;
  padding: 0.9rem 2.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 1rem;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.3);
}
.btn-auth:hover { transform: translateY(-3px); box-shadow: 0 14px 40px rgba(102, 126, 234, 0.45); }

.prompt-section {
  background: #fff;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}
.prompt-textarea {
  width: 100%;
  border: none;
  outline: none;
  resize: vertical;
  font-size: 1rem;
  font-family: inherit;
  color: #2d3748;
  line-height: 1.6;
  padding: 0;
  min-height: 90px;
  background: transparent;
  box-sizing: border-box;
}
.prompt-textarea:disabled { opacity: 0.6; cursor: not-allowed; }

.prompt-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f0f4f8;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.char-count { font-size: 12px; color: #a0aec0; }
.prompt-actions { display: flex; gap: 0.75rem; }

.btn-reset {
  padding: 0.65rem 1.2rem;
  background: #f7fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background 0.2s;
}
.btn-reset:hover { background: #edf2f7; }

.btn-submit {
  padding: 0.65rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 700;
  min-width: 160px;
  transition: opacity 0.2s, transform 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-submit:hover:not(:disabled) { transform: translateY(-2px); }
.btn-submit:disabled { opacity: 0.45; cursor: not-allowed; }

.btn-loading { display: flex; gap: 5px; align-items: center; }
.btn-dot {
  width: 7px; height: 7px;
  background: white;
  border-radius: 50%;
  animation: dotBounce 1.2s ease-in-out infinite;
}
.btn-dot:nth-child(2) { animation-delay: 0.2s; }
.btn-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 1rem;
}
.suggestion-chip {
  background: #f0f4ff;
  color: #4f46e5;
  border: 1px solid #c7d2fe;
  border-radius: 20px;
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;
}
.suggestion-chip:hover:not(:disabled) { background: #e0e7ff; transform: translateY(-1px); }
.suggestion-chip:disabled { opacity: 0.5; cursor: not-allowed; }

.alert {
  padding: 1rem 1.25rem;
  border-radius: 10px;
  margin-bottom: 1.5rem;
  font-weight: 500;
}
.alert-error { background: #fff5f5; color: #c53030; border-left: 4px solid #fc8181; }
.alert-warning { background: #fffbeb; color: #92400e; border-left: 4px solid #fbbf24; }

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  padding: 2.5rem 0;
}

.ai-loader {
  position: relative;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.ai-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 3px solid transparent;
  border-top-color: #667eea;
  animation: ringSpin 1.2s linear infinite;
}
.ai-ring--2 {
  inset: 10px;
  border-top-color: #764ba2;
  border-right-color: #764ba2;
  animation-duration: 1.8s;
  animation-direction: reverse;
}
.ai-ring--3 {
  inset: 20px;
  border-top-color: #a78bfa;
  animation-duration: 2.4s;
}
@keyframes ringSpin { to { transform: rotate(360deg); } }

.ai-icon {
  font-size: 1.4rem;
  animation: iconPulse 2s ease-in-out infinite;
  position: relative;
  z-index: 1;
}
@keyframes iconPulse {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.2); opacity: 1; }
}

.loading-phrase-wrapper { height: 28px; }
.loading-phrase {
  font-size: 1rem;
  color: #4a5568;
  font-weight: 600;
  text-align: center;
  margin: 0;
}
.phrase-fade-enter-active,
.phrase-fade-leave-active { transition: opacity 0.4s, transform 0.4s; }
.phrase-fade-enter-from { opacity: 0; transform: translateY(8px); }
.phrase-fade-leave-to { opacity: 0; transform: translateY(-8px); }

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 1.25rem;
  width: 100%;
}
.skeleton-card { display: flex; flex-direction: column; gap: 8px; }
.skeleton-poster {
  width: 100%;
  aspect-ratio: 2/3;
  background: linear-gradient(90deg, #e2e8f0 25%, #edf2f7 50%, #e2e8f0 75%);
  background-size: 200% 100%;
  border-radius: 10px;
  animation: shimmer 1.5s ease-in-out infinite;
}
.skeleton-title {
  height: 14px;
  background: linear-gradient(90deg, #e2e8f0 25%, #edf2f7 50%, #e2e8f0 75%);
  background-size: 200% 100%;
  border-radius: 6px;
  animation: shimmer 1.5s ease-in-out infinite 0.1s;
}
.skeleton-meta {
  height: 10px;
  width: 60%;
  background: linear-gradient(90deg, #e2e8f0 25%, #edf2f7 50%, #e2e8f0 75%);
  background-size: 200% 100%;
  border-radius: 6px;
  animation: shimmer 1.5s ease-in-out infinite 0.2s;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.results-header {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}
.results-header h2 { font-size: 1.4rem; font-weight: 800; color: #1a202c; margin: 0; }
.results-prompt { font-size: 0.9rem; color: #a0aec0; font-style: italic; margin: 0; }
.results-count {
  margin-left: auto;
  font-size: 0.85rem;
  background: #eef2ff;
  color: #4f46e5;
  padding: 3px 10px;
  border-radius: 20px;
  font-weight: 600;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.75rem;
}
.movie-card-appear { animation: cardAppear 0.4s ease-out both; }
.movies-grid > *:nth-child(1) { animation-delay: 0.05s; }
.movies-grid > *:nth-child(2) { animation-delay: 0.1s; }
.movies-grid > *:nth-child(3) { animation-delay: 0.15s; }
.movies-grid > *:nth-child(4) { animation-delay: 0.2s; }
.movies-grid > *:nth-child(5) { animation-delay: 0.25s; }
.movies-grid > *:nth-child(6) { animation-delay: 0.3s; }
@keyframes cardAppear {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.empty-hint { text-align: center; padding: 3rem 2rem; color: #a0aec0; }
.empty-icon { font-size: 2.5rem; margin-bottom: 0.75rem; }
.empty-sub {
  font-size: 0.9rem;
  margin-top: 0.5rem;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

@media (max-width: 768px) {
  .recommend-container { padding: 1rem; }
  .movies-grid { grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
  .skeleton-grid { grid-template-columns: repeat(3, 1fr); }
  .prompt-footer { flex-direction: column; align-items: stretch; }
  .prompt-actions { justify-content: flex-end; }
  .results-header { flex-direction: column; }
  .results-count { margin-left: 0; }
}
</style>