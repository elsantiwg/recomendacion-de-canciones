let songs = [];
let ratings = {};

async function loadSongs() {
  const btn = document.getElementById("loadBtn");
  btn.textContent = "🎵 Cargando...";
  btn.disabled = true;

  const res = await fetch("http://localhost:8000/songs");
  songs = await res.json();

  const container = document.getElementById("songs");
  container.innerHTML = songs.map(song => `
    <div class="song-card">
      <div class="text-center">
        <h3 class="text-xl font-semibold mb-1">${song.song_name}</h3>
        <p class="text-sm text-gray-300">${song.artist}</p>
        <span class="text-xs bg-pink-600 px-2 py-1 rounded">${song.genre}</span>
      </div>
      <div class="stars mt-3" id="stars-${song.song_id}">
        ${[1,2,3,4,5].map(r => `<span class="star" onclick="rateSong(${song.song_id}, ${r})">★</span>`).join('')}
      </div>
    </div>
  `).join("");

  document.getElementById("recommendBtn").disabled = false;
  btn.textContent = "✅ Canciones Cargadas";
}

function rateSong(id, value) {
  ratings[id] = value;
  const stars = document.querySelectorAll(`#stars-${id} .star`);
  stars.forEach((s, i) => s.classList.toggle("active", i < value));
}

async function getRecommendations() {
  if (Object.keys(ratings).length === 0) {
    alert("Por favor califica al menos una canción 🎵");
    return;
  }

  const res = await fetch("http://localhost:8000/recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ratings })
  });

  const recs = await res.json();
  const result = document.getElementById("result");
  const section = document.getElementById("resultSection");

  result.innerHTML = recs.map(r => `
    <div class="recommend-card">
      <h4 class="text-lg font-semibold">${r.song_name}</h4>
      <p class="text-sm text-gray-300">${r.artist}</p>
      <span class="text-xs bg-green-500 px-2 py-1 rounded">${r.genre}</span>
    </div>
  `).join("");

  section.classList.remove("hidden");
  window.scrollTo({ top: section.offsetTop, behavior: "smooth" });
}
