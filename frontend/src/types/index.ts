export interface User {
  id: number;
  email: string;
  is_active: boolean;
}

export interface Movie {
  id?: number;
  id_pois?: number | null;
  name_movie: string;
  year?: number | null;
  genres: string[];
  description: string;
  poster_image: string;
  movieLength?: number | null;
  rating: number;
}

export interface RecommendResponse {
  prompt: string;
  title: string;
  movies: Movie[];
}

export interface UserProfile {
  id: number;
  name: string | null;
  favorite_genres: string | null;
  about_me: string | null;
  user_id: number;
  created_at: string;
}

export interface UserUpdateProfile {
  name?: string | null;
  favorite_genres?: string | null;
  about_me?: string | null;
}
export interface UserHistory {
  id: number;
  prompt: string;
  response: string;
  user_id: number;
  created_at: string;
  movie_list: Movie[];
}

export interface UserGroupHistory {
  history: UserHistory[];
}