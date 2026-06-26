<script setup lang="ts">
import { onMounted } from "vue";
import { useMovieStore } from "../stores/movie";
import MovieCard from "../components/MovieCard.vue";

const movieStore = useMovieStore();

onMounted(() => {
  movieStore.getLikedMovies();
});
</script>

<template>
  <div class="favorites-container">
    <div class="page-header">
      <h1>❤️ Избранное</h1>
      <p class="subtitle">Фильмы, которые вы сохранили</p>
    </div>

    <div v-if="movieStore.isLoading" class="skeleton-grid">
      <div class="skeleton-card" v-for="i in 8" :key="i">
        <div class="skeleton-poster"></div>
        <div class="skeleton-title"></div>
        <div class="skeleton-meta"></div>
      </div>
    </div>

    <div v-else-if="movieStore.likedMovies.length > 0">
      <p class="count-label">{{ movieStore.likedMovies.length }} фильмов</p>
      <div class="movies-grid">
        <MovieCard
          v-for="movie in movieStore.likedMovies"
          :key="movie.id"
          :movie="movie"
          class="card-appear"
        />
      </div>
    </div>

    <div v-else class="no-favorites">
      <div class="empty-icon">🎬</div>
      <h2>Пока пусто</h2>
      <p>Получите рекомендации и добавьте понравившиеся фильмы в избранное.</p>
      <p class="hint">Не забудьте указать имя в профиле — без него лайки не сохраняются.</p>
      <div class="actions">
        <router-link to="/recommend" class="btn-primary">✨ Получить рекомендации</router-link>
        <router-link to="/profile" class="btn-secondary">👤 Заполнить профиль</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.favorites-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}
.page-header { margin-bottom: 2rem; }
.page-header h1 { font-size: 2rem; font-weight: 800; color: #1a202c; margin: 0 0 0.4rem; }
.subtitle { color: #718096; margin: 0; }

.count-label { font-size: 0.85rem; color: #a0aec0; margin-bottom: 1.25rem; }

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 2rem;
}
.card-appear { animation: cardIn 0.4s ease-out both; }
.movies-grid > *:nth-child(1) { animation-delay: 0.05s; }
.movies-grid > *:nth-child(2) { animation-delay: 0.1s; }
.movies-grid > *:nth-child(3) { animation-delay: 0.15s; }
.movies-grid > *:nth-child(4) { animation-delay: 0.2s; }
.movies-grid > *:nth-child(5) { animation-delay: 0.25s; }
.movies-grid > *:nth-child(6) { animation-delay: 0.3s; }
@keyframes cardIn {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}
.skeleton-card { display: flex; flex-direction: column; gap: 8px; }
.skeleton-poster {
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
  height: 10px; width: 55%;
  background: linear-gradient(90deg, #e2e8f0 25%, #edf2f7 50%, #e2e8f0 75%);
  background-size: 200% 100%;
  border-radius: 6px;
  animation: shimmer 1.5s ease-in-out infinite 0.2s;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.no-favorites {
  text-align: center;
  padding: 5rem 2rem;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06);
  border: 1px solid #e2e8f0;
}
.empty-icon { font-size: 4rem; margin-bottom: 1rem; }
.no-favorites h2 { font-size: 1.5rem; font-weight: 800; color: #1a202c; margin: 0 0 0.75rem; }
.no-favorites p { color: #4a5568; margin: 0 0 0.5rem; }
.no-favorites .hint { color: #a0aec0; font-size: 0.9rem; max-width: 420px; margin: 0 auto 2rem; line-height: 1.6; }

.actions { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }
.btn-primary {
  display: inline-block;
  padding: 0.8rem 1.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 10px;
  font-weight: 700;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 6px 20px rgba(102,126,234,0.3);
}
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(102,126,234,0.4); }
.btn-secondary {
  display: inline-block;
  padding: 0.8rem 1.75rem;
  background: white;
  color: #667eea;
  border: 2px solid #c7d2fe;
  text-decoration: none;
  border-radius: 10px;
  font-weight: 700;
  transition: all 0.2s;
}
.btn-secondary:hover { background: #eef2ff; }

@media (max-width: 768px) {
  .favorites-container { padding: 1rem; }
  .movies-grid { grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
  .skeleton-grid { grid-template-columns: repeat(3, 1fr); gap: 1rem; }
}
</style>