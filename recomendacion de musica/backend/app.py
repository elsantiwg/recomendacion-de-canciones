from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import csv
import math
import random
from collections import defaultdict, Counter
import os
import json

app = Flask(__name__)
CORS(app)  # Permitir todas las conexiones del frontend

# Cargar dataset
def load_dataset():
    user_item = defaultdict(dict)
    song_ids = set()
    user_ids = set()
    favorite_genre = {}
    
    with open('/app/data/full_music_dataset.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                user_id = int(row['user_id'])
                song_id = int(row['song_id'])
                rating = int(row['rating'])
                genre = row['genre']
                
                user_ids.add(user_id)
                song_ids.add(song_id)
                
                if rating > 0:
                    user_item[user_id][song_id] = rating
                    
            except:
                continue
    
    # Calcular géneros favoritos (simplificado)
    user_genre_sum = defaultdict(lambda: defaultdict(int))
    for user_id, ratings in user_item.items():
        for song_id, rating in ratings.items():
            user_genre_sum[user_id]['Pop'] += rating  # Simplificación
    
    for user_id in user_genre_sum:
        favorite_genre[user_id] = 'Pop'  # Simplificado
    
    return user_item, sorted(list(song_ids)), sorted(list(user_ids)), favorite_genre

# Cargar datos al iniciar
print("🔄 Cargando dataset...")
user_item, song_ids, user_ids, favorite_genre = load_dataset()
train_users = user_ids[:int(0.8 * len(user_ids))]  # 80% para entrenamiento
print("✅ Dataset cargado!")

# Funciones KNN (simplificadas)
def dict_to_vector(ratings_dict, song_ids):
    return [float(ratings_dict.get(s, 0)) for s in song_ids]

def cosine_distance(u, v):
    dot = sum(a*b for a,b in zip(u,v))
    norm_u = math.sqrt(sum(a*a for a in u))
    norm_v = math.sqrt(sum(b*b for b in v))
    if norm_u * norm_v == 0:
        return 1.0
    return 1.0 - dot / (norm_u * norm_v)

def get_k_neighbors(query_vector, k=5):
    neighbors = []
    for user_id in train_users:
        user_vec = dict_to_vector(user_item[user_id], song_ids)
        distance = cosine_distance(user_vec, query_vector)
        neighbors.append((user_id, distance))
    neighbors.sort(key=lambda x: x[1])
    return neighbors[:k]

# Rutas del API
@app.route('/')
def home():
    return jsonify({"message": "Music Recommendation API", "status": "active"})

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "users": len(user_ids), 
        "songs": len(song_ids)
    })

@app.route('/songs')
def get_songs():
    return jsonify({"songs": song_ids[:100]})  # Solo 100 canciones para simplificar

@app.route('/classify', methods=['POST'])
def classify():
    data = request.json
    user_ratings = {int(r['song_id']): int(r['rating']) for r in data['ratings']}
    
    query_vector = dict_to_vector(user_ratings, song_ids)
    neighbors = get_k_neighbors(query_vector, k=data.get('k', 5))
    
    # Predicción simple
    predicted_genre = "Pop"  # Simplificado
    return jsonify({
        "predicted_genre": predicted_genre,
        "neighbors_used": len(neighbors)
    })

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_ratings = {int(r['song_id']): int(r['rating']) for r in data['ratings']}
    
    query_vector = dict_to_vector(user_ratings, song_ids)
    neighbors = get_k_neighbors(query_vector, k=data.get('k', 10))
    
    # Recomendaciones simples
    recommendations = []
    for song_id in song_ids[:20]:  # Solo primeras 20 canciones
        if song_id not in user_ratings:
            score = random.uniform(3.0, 5.0)  # Score aleatorio simplificado
            recommendations.append({
                "song_id": song_id,
                "predicted_rating": round(score, 2)
            })
    
    return jsonify({
        "recommendations": recommendations[:data.get('n_recommendations', 10)]
    })

# Servir archivos estáticos del frontend
@app.route('/<path:path>')
def serve_frontend(path):
    return send_from_directory('../frontend', path)

@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)