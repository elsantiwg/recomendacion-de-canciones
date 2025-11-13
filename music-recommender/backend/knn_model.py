"""
- Lee un dataset CSV con usuarios, canciones y géneros.
- Calcula la similitud entre usuarios por sus calificaciones.
- Identifica el género predominante en las canciones calificadas por el usuario.
- Recomienda canciones del mismo género (para coherencia musical).

"""

import csv
import math
import random
from collections import Counter


class KNNRecommender:
    """Sistema de recomendación musical usando KNN """

    def __init__(self, dataset_path: str, k: int = 5):
        """
        Inicializa el modelo con los datos del CSV y el valor de K.
        """
        self.k = k
        self.data = self._load_data(dataset_path)
        self.songs_info = self._build_song_info()

    # CARGA Y PROCESAMIENTO DE DATOS
    def _load_data(self, path: str):
        """Carga los datos del CSV en memoria."""
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def _build_song_info(self):
        """Crea un diccionario auxiliar con información de canciones."""
        songs = {}
        for row in self.data:
            songs[row['song_id']] = {
                "name": row['song_name'],
                "artist": row['artist'],
                "genre": row['genre']
            }
        return songs

    # FUNCIONES DE SIMILITUD
    def _distance(self, user1: dict, user2: dict) -> float:
        """Calcula distancia euclidiana entre dos usuarios."""
        sum_sq = 0
        for song in user1:
            if song in user2:
                sum_sq += (user1[song] - user2[song]) ** 2
        return math.sqrt(sum_sq)

    def _get_neighbors(self, user_ratings: dict):
        """Encuentra los K vecinos más cercanos."""
        distances = []
        users = set(row['user_id'] for row in self.data)

        for uid in users:
            u_ratings = {row['song_id']: float(row['rating'])
                         for row in self.data if row['user_id'] == uid}
            dist = self._distance(user_ratings, u_ratings)
            distances.append((uid, dist))

        distances.sort(key=lambda x: x[1])
        return distances[:self.k]

    # LÓGICA DE RECOMENDACIÓN
    def _get_dominant_genre(self, user_ratings: dict):
        """
        Identifica el género predominante ponderando por la calificación del usuario.
        """
        genre_scores = {}
        for song_id, rating in user_ratings.items():
            if song_id in self.songs_info:
                genre = self.songs_info[song_id]["genre"]
                genre_scores[genre] = genre_scores.get(genre, 0) + rating

        if not genre_scores:
            return None

        # Retorna el género con mayor puntuación total ponderada
        return max(genre_scores, key=genre_scores.get)

    def recommend(self, user_ratings: dict):
        """Genera recomendaciones filtradas por género dominante."""
        neighbors = self._get_neighbors(user_ratings)
        genre_filter = self._get_dominant_genre(user_ratings)
        scores = {}

        for uid, _ in neighbors:
            for row in self.data:
                if row['user_id'] == uid and row['song_id'] not in user_ratings:
                    song_id = row['song_id']
                    rating = float(row['rating'])
                    song_genre = self.songs_info[song_id]["genre"]

                    if rating > 3 and (genre_filter is None or song_genre == genre_filter):
                        scores[song_id] = scores.get(song_id, 0) + rating

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        recs = []
        for song_id, _ in ranked[:5]:
            info = self.songs_info[song_id]
            recs.append({
                "id": song_id,
                "title": info["name"],
                "artist": info["artist"],
                "genre": info["genre"]
            })
        return recs
    # FUNCIÓN AUXILIAR
    def get_random_songs(self, n: int = 10):
        """Devuelve una muestra aleatoria de canciones."""
        all_songs = list(self.songs_info.items())
        sample = random.sample(all_songs, min(n, len(all_songs)))
        return [
            {"id": sid, "title": info["name"], "artist": info["artist"], "genre": info["genre"]}
            for sid, info in sample
        ]
