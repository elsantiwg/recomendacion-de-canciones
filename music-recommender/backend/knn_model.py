import csv, math, random
from collections import defaultdict

class KNNRecommender:
    def __init__(self, path):
        self.user_ratings = defaultdict(dict)
        self.song_info = {}
        self._load_data(path)

    def _load_data(self, path):
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                u = int(row['user_id'])
                s = int(row['song_id'])
                r = int(row['rating'])
                self.user_ratings[u][s] = r
                self.song_info[s] = {
                    "song_id": s,
                    "song_name": row["song_name"],
                    "artist": row["artist"],
                    "genre": row["genre"]
                }

    def _similarity(self, user1, user2):
        common = set(user1) & set(user2)
        if not common:
            return 0
        num = sum(user1[s] * user2[s] for s in common)
        den1 = math.sqrt(sum(v**2 for v in user1.values()))
        den2 = math.sqrt(sum(v**2 for v in user2.values()))
        return num / (den1 * den2) if den1 and den2 else 0

    def recommend(self, new_user):
        sims = {}
        for uid in self.user_ratings:
            sims[uid] = self._similarity(new_user, self.user_ratings[uid])

        top_users = sorted(sims.items(), key=lambda x: x[1], reverse=True)[:5]
        scores = defaultdict(float)

        for uid, sim in top_users:
            for song, rating in self.user_ratings[uid].items():
                if song not in new_user:
                    scores[song] += sim * rating

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        return [self.song_info[s] for s, _ in ranked]

    def get_random_songs(self, n=10):
        """Devuelve canciones aleatorias"""
        return random.sample(list(self.song_info.values()), n)
