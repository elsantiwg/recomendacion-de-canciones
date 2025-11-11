from flask import Flask, request, jsonify
from flask_cors import CORS
from knn_model import KNNRecommender

app = Flask(__name__)
CORS(app)
model = KNNRecommender("colombia_music_dataset.csv")

@app.route('/')
def index():
    return "🎵 API del Recomendador Musical activa"

@app.route('/songs', methods=['GET'])
def get_songs():
    """Devuelve canciones aleatorias para que el usuario las califique"""
    songs = model.get_random_songs(15)
    return jsonify(songs)

@app.route('/recommend', methods=['POST'])
def recommend():
    """Recibe calificaciones y devuelve recomendaciones"""
    data = request.json
    ratings = data.get("ratings", {})
    if not ratings:
        return jsonify({"error": "No se enviaron calificaciones"}), 400
    recs = model.recommend(ratings)
    return jsonify(recs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
