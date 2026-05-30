from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>دانلودر ویدیو</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700&display=swap');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Vazirmatn', sans-serif; background: #0a0a0f; color: #e0e0e0; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
  .container { width: 100%; max-width: 620px; }
  h1 { text-align: center; font-size: 2rem; font-weight: 700; margin-bottom: 8px; background: linear-gradient(135deg, #a78bfa, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .subtitle { text-align: center; color: #666; font-size: 0.85rem; margin-bottom: 32px; }
  .card { background: #111118; border: 1px solid #222230; border-radius: 16px; padding: 28px; margin-bottom: 16px; }
  label { display: block; font-size: 0.85rem; color: #888; margin-bottom: 8px; }
  input[type="text"] { width: 100%; background: #0a0a0f; border: 1px solid #2a2a3a; border-radius: 10px; padding: 12px 16px; color: #e0e0e0; font-family: 'Vazirmatn', sans-serif; font-size: 0.9rem; direction: ltr; margin-bottom: 20px; transition: border-color 0.2s; }
  input[type="text"]:focus { outline: none; border-color: #a78bfa; }
  .btn-main { width: 100%; background: linear-gradient(135deg, #7c3aed, #2563eb); border: none; border-radius: 10px; padding: 14px; color: white; font-family: 'Vazirmatn', sans-serif; font-size: 1rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
  .btn-main:hover { opacity: 0.9; }
  .btn-main:disabled { opacity: 0.5; cursor: not-allowed; }
  .loading { display: none; text-align: center; padding: 20px; color: #a78bfa; }
  .spinner { display: inline-block; width: 30px; height: 30px; border: 3px solid #2a2a3a; border-top-color: #a78bfa; border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 10px; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .results { display: none; }
  .result-title { font-size: 1rem; font-weight: 600; margin-bottom: 16px; color: #e0e0e0; text-align: center; }
  .thumb { width: 100%; border-radius: 10px; margin-bottom: 16px; }
  .formats { display: flex; flex-direction: column; gap: 10px; }
  .fmt-btn { display: flex; align-items: center; justify-content: space-between; background: #0a0a0f; border: 2px solid #2a2a3a; border-radius: 10px; padding: 12px 16px; cursor: pointer; text-decoration: none; color: #e0e0e0; transition: all 0.2s; font-family: 'Vazirmatn', sans-serif; font-size: 0.9rem; }
  .fmt-btn:hover { border-color: #a78bfa; color: #a78bfa; }
  .fmt-btn.mp4 { border-color: #2563eb33; }
  .fmt-btn.mp4:hover { border-color: #2563eb; color: #60a5fa; }
  .fmt-btn.mp3 { border-color: #7c3aed33; }
  .fmt-btn.mp3:hover { border-color: #7c3aed; color: #a78bfa; }
  .fmt-label { font-weight: 600; }
  .fmt-size { font-size: 0.8rem; color: #666; }
  .error-msg { color: #f87171; font-size: 0.9rem; text-align: center; display: none; margin-top: 12px; padding: 12px; background: #1a0a0a; border-radius: 10px; border: 1px solid #3a1a1a; }
  .divider { text-align: center; color: #444; font-size: 0.8rem; margin: 8px 0; }
  .invidious-links { display: none; }
  .inv-link { display: block; text-align: center; color: #60a5fa; font-size: 0.85rem; margin-top: 8px; text-decoration: none; }
  .inv-link:hover { text-decoration: underline; }
</style>
</head>
<body>
<div class="container">
  <h1>🎬 دانلودر</h1>
  <p class="subtitle">یوتیوب • اینستاگرام • تیک‌تاک • توییتر و بیشتر</p>

  <div class="card">
    <label>لینک ویدیو را وارد کنید</label>
    <input type="text" id="url" placeholder="https://youtube.com/watch?v=...">
    <button class="btn-main" onclick="analyze()" id="btn">🔍 دریافت لینک‌های دانلود</button>
    <p class="error-msg" id="error"></p>
  </div>

  <div class="loading" id="loading">
    <div class="spinner"></div>
    <p>در حال دریافت اطلاعات...</p>
  </div>

  <div class="card results" id="results">
    <p class="result-title" id="vid-title"></p>
    <img class="thumb" id="vid-thumb" src="" alt="">
    <div class="formats" id="formats"></div>
    <div class="divider">─── یا دانلود مستقیم از ─── </div>
    <div class="invidious-links" id="inv-links"></div>
  </div>
</div>

<script>
function extractId(url) {
  const patterns = [
    /youtu\.be\/([^?&]+)/,
    /youtube\.com\/watch\?v=([^&]+)/,
    /youtube\.com\/shorts\/([^?&]+)/,
    /youtube\.com\/embed\/([^?&]+)/,
  ];
  for (const p of patterns) {
    const m = url.match(p);
    if (m) return m[1];
  }
  return null;
}

async function analyze() {
  const url = document.getElementById('url').value.trim();
  if (!url) { showError('لطفاً لینک را وارد کنید'); return; }

  const videoId = extractId(url);
  if (!videoId) { showError('لینک یوتیوب معتبر نیست'); return; }

  document.getElementById('btn').disabled = true;
  document.getElementById('error').style.display = 'none';
  document.getElementById('results').style.display = 'none';
  document.getElementById('loading').style.display = 'block';

  // لیست Invidious instances که از مرورگر کاربر accessible هستن
  const instances = [
    'https://inv.nadeko.net',
    'https://invidious.nerdvpn.de',
    'https://invidious.fdn.fr',
    'https://invidious.io.lol',
    'https://iv.melmac.space',
    'https://invidious.perennialte.ch',
    'https://invidious.dhusch.de',
  ];

  let data = null;
  let workingInstance = null;

  for (const inst of instances) {
    try {
      const r = await fetch(`${inst}/api/v1/videos/${videoId}`, {
        signal: AbortSignal.timeout(6000)
      });
      if (r.ok) {
        data = await r.json();
        workingInstance = inst;
        break;
      }
    } catch(e) { continue; }
  }

  document.getElementById('loading').style.display = 'none';
  document.getElementById('btn').disabled = false;

  if (!data) {
    // اگه همه instance ها کار نکردن، لینک مستقیم Invidious بده
    showInvidiousLinks(videoId, instances);
    return;
  }

  showResults(data, videoId, workingInstance);
}

function showResults(data, videoId, instance) {
  document.getElementById('vid-title').textContent = data.title || 'ویدیو';
  
  const thumb = data.videoThumbnails?.find(t => t.quality === 'high') || data.videoThumbnails?.[0];
  if (thumb) document.getElementById('vid-thumb').src = thumb.url;

  const formatsDiv = document.getElementById('formats');
  formatsDiv.innerHTML = '';

  // فرمت‌های MP4
  const streams = data.formatStreams || [];
  const qualities = ['1080p', '720p', '480p', '360p', '240p', '144p'];
  
  streams
    .filter(f => f.container === 'mp4')
    .sort((a, b) => {
      const ai = qualities.indexOf(a.qualityLabel);
      const bi = qualities.indexOf(b.qualityLabel);
      return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
    })
    .forEach(f => {
      const a = document.createElement('a');
      a.className = 'fmt-btn mp4';
      a.href = f.url;
      a.target = '_blank';
      a.download = '';
      a.innerHTML = `<span class="fmt-label">🎬 ویدیو MP4 — ${f.qualityLabel}</span><span class="fmt-size">دانلود مستقیم ↓</span>`;
      formatsDiv.appendChild(a);
    });

  // لینک MP3 از instance
  const mp3Link = `${instance}/latest_version?id=${videoId}&itag=140`;
  const mp3Btn = document.createElement('a');
  mp3Btn.className = 'fmt-btn mp3';
  mp3Btn.href = mp3Link;
  mp3Btn.target = '_blank';
  mp3Btn.innerHTML = `<span class="fmt-label">🎵 فقط صدا MP3/M4A</span><span class="fmt-size">دانلود مستقیم ↓</span>`;
  formatsDiv.appendChild(mp3Btn);

  // لینک مستقیم به صفحه Invidious
  const invDiv = document.getElementById('inv-links');
  invDiv.innerHTML = '';
  const invLink = document.createElement('a');
  invLink.className = 'inv-link';
  invLink.href = `${instance}/watch?v=${videoId}`;
  invLink.target = '_blank';
  invLink.textContent = `🔗 باز کردن در ${instance.replace('https://','')}`;
  invDiv.appendChild(invLink);
  invDiv.style.display = 'block';

  document.getElementById('results').style.display = 'block';
}

function showInvidiousLinks(videoId, instances) {
  // اگه API کار نکرد، مستقیم لینک صفحه Invidious بده
  document.getElementById('vid-title').textContent = 'برای دانلود از یکی از لینک‌های زیر استفاده کنید:';
  document.getElementById('vid-thumb').style.display = 'none';
  document.getElementById('formats').innerHTML = '';
  
  const invDiv = document.getElementById('inv-links');
  invDiv.innerHTML = '';
  instances.forEach(inst => {
    const a = document.createElement('a');
    a.className = 'inv-link';
    a.href = `${inst}/watch?v=${videoId}`;
    a.target = '_blank';
    a.textContent = `🔗 ${inst.replace('https://','')}`;
    invDiv.appendChild(a);
  });
  invDiv.style.display = 'block';

  document.getElementById('results').style.display = 'block';
}

function showError(msg) {
  const e = document.getElementById('error');
  e.textContent = msg;
  e.style.display = 'block';
}
</script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
