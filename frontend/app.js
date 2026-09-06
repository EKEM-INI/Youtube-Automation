// AutoShorts AI — Frontend Logic

let currentJobId = null;
let pollInterval = null;

// Tab Switching
function switchTab(tabId) {
  document.getElementById('tab-wizard').classList.add('hidden');
  document.getElementById('tab-gallery').classList.add('hidden');
  document.getElementById('tab-settings').classList.add('hidden');

  document.getElementById('tab-btn-wizard').className = "px-3.5 py-1.5 rounded-lg text-sm font-semibold transition text-gray-400 hover:text-white hover:bg-gray-800/60";
  document.getElementById('tab-btn-gallery').className = "px-3.5 py-1.5 rounded-lg text-sm font-semibold transition text-gray-400 hover:text-white hover:bg-gray-800/60";
  document.getElementById('tab-btn-settings').className = "px-3.5 py-1.5 rounded-lg text-sm font-semibold transition text-gray-400 hover:text-white hover:bg-gray-800/60";

  document.getElementById(`tab-${tabId}`).classList.remove('hidden');
  document.getElementById(`tab-btn-${tabId}`).className = "px-3.5 py-1.5 rounded-lg text-sm font-semibold transition bg-purple-600/20 text-purple-300 border border-purple-500/30";

  if (tabId === 'gallery') {
    fetchVideoList();
  }
}

// Preset Topic Setter
function setTopic(text) {
  document.getElementById('input-topic').value = text;
}

// Tone Selector
function selectTone(tone) {
  document.getElementById('input-tone').value = tone;
  document.querySelectorAll('.tone-card').forEach(card => {
    card.classList.remove('border-purple-500', 'bg-purple-950/30');
    card.classList.add('border-gray-800', 'bg-black/40');
  });
  event.currentTarget.classList.remove('border-gray-800', 'bg-black/40');
  event.currentTarget.classList.add('border-purple-500', 'bg-purple-950/30');
}

// Voice Selector
function selectVoice(voice) {
  document.getElementById('input-voice').value = voice;
  document.querySelectorAll('.voice-card').forEach(card => {
    card.classList.remove('border-purple-500', 'bg-purple-950/30');
    card.classList.add('border-gray-800', 'bg-black/40');
  });
  event.currentTarget.classList.remove('border-gray-800', 'bg-black/40');
  event.currentTarget.classList.add('border-purple-500', 'bg-purple-950/30');
}

// Start Video Generation
async function startVideoGeneration() {
  const topic = document.getElementById('input-topic').value.trim();
  const tone = document.getElementById('input-tone').value;
  const voice = document.getElementById('input-voice').value;
  const publishMode = document.querySelector('input[name="publish_mode"]:checked').value;
  const pexelsKey = localStorage.getItem('pexels_api_key') || "";

  if (!topic) {
    alert("Please enter or pick a video topic.");
    return;
  }

  // Open Modal
  document.getElementById('generation-modal').classList.remove('hidden');
  document.getElementById('modal-title').innerText = "Generating Your Viral Short...";
  document.getElementById('modal-status-text').innerText = "🧠 Crafting viral hook & script...";
  document.getElementById('modal-progress-bar').style.width = "15%";
  document.getElementById('modal-progress-percent').innerText = "15%";
  document.getElementById('modal-success-box').classList.add('hidden');

  try {
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topic,
        tone: tone,
        voice: voice,
        publish_mode: publishMode,
        pexels_key: pexelsKey
      })
    });

    if (!res.ok) {
      throw new Error("Failed to start generation.");
    }

    const data = await res.json();
    currentJobId = data.job_id;
    startPolling(currentJobId);

  } catch (err) {
    alert("Error: " + err.message);
    closeModal();
  }
}

// Poll Job Status
function startPolling(jobId) {
  if (pollInterval) clearInterval(pollInterval);

  pollInterval = setInterval(async () => {
    try {
      const res = await fetch(`/api/job/${jobId}`);
      if (!res.ok) return;

      const job = await res.json();
      document.getElementById('modal-status-text').innerText = job.step || "Processing...";
      document.getElementById('modal-progress-bar').style.width = `${job.progress || 10}%`;
      document.getElementById('modal-progress-percent').innerText = `${job.progress || 10}%`;

      if (job.status === 'completed') {
        clearInterval(pollInterval);
        document.getElementById('modal-title').innerText = "🎉 Your Short Is Ready!";
        document.getElementById('modal-status-text').innerText = "Rendered in 1080x1920 Full HD with animated captions.";
        document.getElementById('modal-success-box').classList.remove('hidden');

        const videoUrl = job.result.video_url;
        const videoEl = document.getElementById('modal-video-preview');
        videoEl.src = videoUrl;
        videoEl.load();

        document.getElementById('modal-download-btn').href = videoUrl;
        fetchVideoList(); // update gallery counter
      } else if (job.status === 'failed') {
        clearInterval(pollInterval);
        alert("Generation failed: " + job.error);
        closeModal();
      }

    } catch (e) {
      console.error("Polling error:", e);
    }
  }, 1500);
}

function closeModal() {
  document.getElementById('generation-modal').classList.add('hidden');
}

// Fetch Video Gallery
async function fetchVideoList() {
  try {
    const res = await fetch('/api/videos');
    if (!res.ok) return;

    const data = await res.json();
    const videos = data.videos || [];
    document.getElementById('video-count').innerText = videos.length;

    const grid = document.getElementById('video-grid');
    grid.innerHTML = '';

    if (videos.length === 0) {
      grid.innerHTML = `
        <div class="col-span-full py-12 text-center text-gray-500">
          <i class="fa-solid fa-film text-4xl mb-3"></i>
          <p class="text-sm">No videos generated yet. Go to the Generator tab to create your first Short!</p>
        </div>
      `;
      return;
    }

    videos.forEach(v => {
      const card = document.createElement('div');
      card.className = "glass-panel p-4 rounded-2xl space-y-3 flex flex-col justify-between";
      card.innerHTML = `
        <div class="space-y-2">
          <video src="${v.url}" controls class="w-full aspect-[9/16] bg-black rounded-xl object-cover border border-gray-800"></video>
          <div class="font-bold text-xs text-white truncate">${v.filename}</div>
          <div class="text-[10px] text-gray-400">${v.size_mb} MB • 1080x1920 HD</div>
        </div>
        <div class="flex gap-2 pt-2">
          <a href="${v.url}" download class="flex-1 py-2 rounded-lg bg-purple-600/30 hover:bg-purple-600 text-purple-200 hover:text-white text-xs font-bold text-center transition">
            <i class="fa-solid fa-download"></i> Save
          </a>
        </div>
      `;
      grid.appendChild(card);
    });

  } catch (err) {
    console.error("Failed to load videos:", err);
  }
}

// Save Settings
function saveSettings() {
  const pexelsKey = document.getElementById('setting-pexels').value.trim();
  localStorage.setItem('pexels_api_key', pexelsKey);
  alert("Settings saved successfully!");
}

// Init on load
document.addEventListener('DOMContentLoaded', () => {
  const savedKey = localStorage.getItem('pexels_api_key');
  if (savedKey) {
    document.getElementById('setting-pexels').value = savedKey;
  }
  fetchVideoList();
});
