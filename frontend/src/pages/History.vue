<script setup lang="ts">
import { onMounted } from "vue";
import { useHistoryStore } from "../stores/movie";
import MovieCard from "../components/MovieCard.vue";

const historyStore = useHistoryStore();

onMounted(() => {
  historyStore.getHistory(true);
});

const loadMore = () => {
  historyStore.getHistory();
};

const formatDate = (iso: string) =>
  new Date(iso).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
</script>

<template>
  <div class="history-container">
    <div class="page-header">
      <h1>🕓 История запросов</h1>
      <p class="subtitle">Все ваши промты и подборки к ним</p>
    </div>

    <div v-if="historyStore.isLoading && historyStore.history.length === 0" class="loading-state">
      <div class="spinner"></div>
      <p>Загружаем историю...</p>
    </div>

    <div v-else-if="historyStore.error && historyStore.history.length === 0" class="error-state">
      <p>{{ historyStore.error }}</p>
      <button @click="historyStore.getHistory(true)" class="btn-secondary">Повторить</button>
    </div>

    <div v-else-if="historyStore.history.length > 0" class="history-list">
      <div v-for="item in historyStore.history" :key="item.id" class="history-item">
        <div class="history-item-header">
          <p class="history-prompt">«{{ item.prompt }}»</p>
          <span class="history-date">{{ formatDate(item.created_at) }}</span>
        </div>

        <div v-if="item.movie_list.length > 0" class="movies-grid">
          <MovieCard
            v-for="movie in item.movie_list"
            :key="movie.id"
            :movie="movie"
          />
        </div>
        <p v-else class="no-movies">Фильмы не найдены для этого запроса</p>
      </div>

      <div v-if="historyStore.error" class="alert alert-error">
        ⚠️ {{ historyStore.error }}
      </div>

      <div v-if="historyStore.hasMore" class="load-more-wrapper">
        <button
          @click="loadMore"
          class="btn-load-more"
          :disabled="historyStore.isLoading"
        >
          {{ historyStore.isLoading ? "Загрузка..." : "Показать ещё" }}
        </button>
      </div>
    </div>

    <div v-else class="empty-state">
      <div class="empty-icon">🕓</div>
      <h2>История пуста</h2>
      <p>Здесь появятся ваши прошлые запросы к AI-рекомендациям.</p>
      <router-link to="/recommend" class="btn-primary">✨ Получить рекомендации</router-link>
    </div>
  </div>
</template>

<style scoped>
.history-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}
.page-header { margin-bottom: 2rem; }
.page-header h1 { font-size: 2rem; font-weight: 800; color: #1a202c; margin: 0 0 0.4rem; }
.subtitle { color: #718096; margin: 0; }

.loading-state, .error-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #718096;
}
.error-state p { color: #c53030; margin-bottom: 1rem; }
.spinner {
  width: 40px; height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}
@keyframes spin { to { transform: rotate(360deg); } }

.history-list {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}
.history-item {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  border: 1px solid #e2e8f0;
}
.history-item-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f0f4f8;
}
.history-prompt {
  font-weight: 700;
  color: #2d3748;
  font-style: italic;
  margin: 0;
}
.history-date {
  font-size: 0.8rem;
  color: #a0aec0;
}
.no-movies { color: #a0aec0; font-size: 0.9rem; }

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.5rem;
}

.alert {
  padding: 1rem 1.25rem;
  border-radius: 10px;
  font-weight: 500;
  background: #fff5f5;
  color: #c53030;
  border-left: 4px solid #fc8181;
}

.load-more-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 0.5rem;
}
.btn-load-more {
  padding: 0.75rem 2rem;
  background: white;
  color: #667eea;
  border: 2px solid #c7d2fe;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
}
.btn-load-more:hover:not(:disabled) {
  background: #eef2ff;
  transform: translateY(-2px);
}
.btn-load-more:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06);
  border: 1px solid #e2e8f0;
}
.empty-icon { font-size: 4rem; margin-bottom: 1rem; }
.empty-state h2 { font-size: 1.5rem; font-weight: 800; color: #1a202c; margin: 0 0 0.75rem; }
.empty-state p { color: #4a5568; margin: 0 0 2rem; }

.btn-primary, .btn-secondary {
  display: inline-block;
  padding: 0.8rem 1.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
}

@media (max-width: 768px) {
  .history-container { padding: 1rem; }
  .movies-grid { grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; }
}
</style>