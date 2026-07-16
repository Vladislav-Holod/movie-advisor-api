<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useProfileStore } from "../stores/movie";
import { useMovieStore } from "../stores/movie";

const profileStore = useProfileStore();
const movieStore = useMovieStore();
const isEditing = ref(false);
const editData = ref({
  name: "",
  favorite_genres: "",
  about_me: "",
});

const avatarInput = ref<HTMLInputElement | null>(null);
const avatarError = ref("");

onMounted(async () => {
  await profileStore.getProfile();
  await movieStore.getLikedMovies();
});

const startEdit = () => {
  if (profileStore.profile) {
    editData.value = {
      name: profileStore.profile.name || "",
      favorite_genres: profileStore.profile.favorite_genres || "",
      about_me: profileStore.profile.about_me || "",
    };
  }
  profileStore.error = "";
  isEditing.value = true;
};

const cancelEdit = () => {
  profileStore.error = "";
  isEditing.value = false;
};

const clearError = () => {
  if (profileStore.error) {
    profileStore.error = "";
  }
};

const saveEdit = async () => {
  profileStore.error = "";
  try {
    await profileStore.updateProfile(editData.value);
    isEditing.value = false;
  } catch {
    // ошибка отображается в profileStore.error, остаёмся в режиме редактирования
  }
};

const triggerAvatarPicker = () => {
  avatarError.value = "";
  avatarInput.value?.click();
};

const onAvatarSelected = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  avatarError.value = "";
  try {
    await profileStore.uploadProfileImage(file);
  } catch {
    avatarError.value = profileStore.error || "Не удалось загрузить фото";
  } finally {
    // сбрасываем input, чтобы можно было выбрать тот же файл повторно
    target.value = "";
  }
};
</script>

<template>
  <div class="profile-container">
    <div class="profile-card">
      <h1>👤 Личный кабинет</h1>

      <div v-if="profileStore.isLoading" class="loading">
        Загрузка профиля...
      </div>

      <template v-else-if="profileStore.profile">
        <div class="avatar-block">
          <div class="avatar-wrapper" @click="triggerAvatarPicker">
            <img
              v-if="profileStore.profile.image_url"
              :src="profileStore.profile.image_url"
              alt="Аватар"
              class="avatar-image"
            />
            <div v-else class="avatar-placeholder">
              {{ (profileStore.profile.name || "?").charAt(0).toUpperCase() }}
            </div>
            <div v-if="profileStore.isUploadingImage" class="avatar-overlay">
              Загрузка...
            </div>
            <div v-else class="avatar-overlay avatar-overlay-hover">
              Изменить фото
            </div>
          </div>
          <input
            ref="avatarInput"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            class="avatar-input-hidden"
            @change="onAvatarSelected"
          />
          <span v-if="avatarError" class="field-error">{{ avatarError }}</span>
        </div>

        <div v-if="!isEditing" class="profile-view">
          <div v-if="!profileStore.hasName" class="name-warning">
            ⚠️ Укажите имя в профиле — без него нельзя добавлять фильмы в избранное
          </div>

          <div class="profile-field">
            <label>Имя</label>
            <p>{{ profileStore.profile.name || "Не указано" }}</p>
          </div>

          <div class="profile-field">
            <label>Любимые жанры</label>
            <p>{{ profileStore.profile.favorite_genres || "Не указаны" }}</p>
          </div>

          <div class="profile-field">
            <label>О себе</label>
            <p>{{ profileStore.profile.about_me || "Не указано" }}</p>
          </div>

          <div class="profile-field">
            <label>Дата регистрации</label>
            <p>{{ new Date(profileStore.profile.created_at).toLocaleDateString("ru-RU") }}</p>
          </div>

          <div class="stats-row">
            <div class="stat-box">
              <span class="stat-value">{{ movieStore.likedMovies.length }}</span>
              <span class="stat-label">Фильмов в избранном</span>
            </div>
          </div>

          <button @click="startEdit" class="btn-edit">Редактировать профиль</button>
        </div>

        <div v-else class="profile-edit">
          <div class="form-group">
            <label for="name">Имя *</label>
            <input
              id="name"
              v-model="editData.name"
              type="text"
              maxlength="80"
              placeholder="Как к вам обращаться"
              :class="{ 'input-error': profileStore.error.includes('занято') }"
              @input="clearError"
            />
            <span class="field-hint">Обязательно для добавления фильмов в избранное</span>
            <span v-if="profileStore.error.includes('занято')" class="field-error">
              {{ profileStore.error }}
            </span>
          </div>

          <div class="form-group">
            <label for="genres">Любимые жанры</label>
            <input
              id="genres"
              v-model="editData.favorite_genres"
              type="text"
              maxlength="200"
              placeholder="Например: Sci-Fi, Триллер, Комедия"
            />
          </div>

          <div class="form-group">
            <label for="about">О себе</label>
            <textarea
              id="about"
              v-model="editData.about_me"
              maxlength="300"
              rows="4"
              placeholder="Расскажите о своих кинопредпочтениях"
            ></textarea>
          </div>

          <div v-if="profileStore.error && !profileStore.error.includes('занято')" class="error-message">
            {{ profileStore.error }}
          </div>

          <div class="button-group">
            <button @click="saveEdit" class="btn-save" :disabled="profileStore.isLoading">
              {{ profileStore.isLoading ? "Сохранение..." : "Сохранить" }}
            </button>
            <button @click="cancelEdit" class="btn-cancel">Отменить</button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.profile-container {
  max-width: 700px;
  margin: 2rem auto;
  padding: 2rem;
}

.profile-card {
  background: white;
  padding: 3rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.profile-card h1 {
  margin-bottom: 2rem;
  color: #2d3748;
  font-size: 2rem;
  font-weight: 700;
}

.loading {
  text-align: center;
  color: #a0aec0;
  padding: 3rem 2rem;
}

.avatar-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.avatar-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  cursor: pointer;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
  background: rgba(0, 0, 0, 0.55);
}

.avatar-overlay-hover {
  opacity: 0;
  transition: opacity 0.2s;
}

.avatar-wrapper:hover .avatar-overlay-hover {
  opacity: 1;
}

.avatar-input-hidden {
  display: none;
}

.name-warning {
  background: #fefcbf;
  color: #744210;
  padding: 1rem 1.25rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border-left: 4px solid #ecc94b;
  font-size: 0.95rem;
}

.profile-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.profile-field label {
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: block;
}

.profile-field p {
  color: #4a5568;
  padding: 1rem;
  background: #f7fafc;
  border-radius: 8px;
  border-left: 3px solid #667eea;
  margin: 0;
}

.stats-row {
  display: flex;
  gap: 1rem;
}

.stat-box {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 2rem;
  font-weight: 700;
}

.stat-label {
  font-size: 0.85rem;
  opacity: 0.9;
}

.profile-edit {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group label {
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.5rem;
  display: block;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
}

.input-error {
  border-color: #f56565 !important;
}

.field-hint {
  font-size: 0.8rem;
  color: #a0aec0;
  margin-top: 0.35rem;
  display: block;
}

.field-error {
  font-size: 0.85rem;
  color: #e53e3e;
  margin-top: 0.35rem;
  display: block;
  font-weight: 600;
}

.error-message {
  background: #fed7d7;
  color: #742a2a;
  padding: 1rem;
  border-radius: 8px;
}

.button-group {
  display: flex;
  gap: 1rem;
}

.btn-edit,
.btn-save,
.btn-cancel {
  padding: 0.9rem 1.8rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-edit,
.btn-save {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  flex: 1;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  background: #f7fafc;
  color: #667eea;
  border: 2px solid #cbd5e0;
  flex: 1;
}

@media (max-width: 768px) {
  .profile-container {
    padding: 1rem;
  }

  .profile-card {
    padding: 1.5rem;
  }

  .button-group {
    flex-direction: column;
  }
}
</style>