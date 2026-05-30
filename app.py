from flask import Flask, render_template_string
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
  .vid-info { display: flex; gap: 12px; align-items: center; margin-bottom: 16px; }
  .thumb { width: 120px; height: 68px; object-fit: cover; border-radius: 8px; flex-shrink: 0; }
  .vid-title { font-size: 0.9rem; font-weight: 600; }
  .section-label { font-size: 0.8rem; color: #666; margin: 12px 0 8px; }
  .formats { display: flex; flex-direction: column; gap: 8px; }
  .fmt-btn { display: flex; align-items: center; justify-content: space-between; background: #0a0a0f; border: 2px solid #2a2a3a; border-radius: 10px; padding: 12px 16px; cursor: pointer; text-decoration: none; color: #e0e0e0; transition: all 0.2s; font-family: 'Vazirmatn', sans-serif; font-size: 0.9rem; }
  .fmt-btn:hover { border-color: #a78bfa; background: #1a1030; }
  .fmt-btn.audio:hover { border-color: #7c3aed; }
  .badge { font-size: 0.75rem; padding: 2px 8px; border-radius: 20px; background: #2a2a3a; color: #888; }
  .error-msg { color: #f87171; font-size: 0.9rem; text-align: center; display: none; margin-top: 12px; padding: 12px; background: #1a0a0a; border-radius: 10px; }
</style>
</head>
<body>
<div class="container">
  <h1>🎬 دانلودر</h1>
  <p class="subtitle">یوتیوب • اینستاگرام • تیک‌تاک • توییتر</p>

  <div class="card">
    <label>لینک ویدیو را وارد کنید</label>
    <input type="text" id="url" placeholder="https://youtube.com/watch?v=...">
    <button class="btn-main" onclick="analyze()" id="btn">🔍 دریافت لینک‌های دانلود</button>
    <p class="error-msg" id="error"></p>
  </div>

  <div class="loading" id="loading">
    <div class="spinner"></div>
    <p id="loading-text">در حال دریافت اطلاعات...</p>
  </div>

  <div class="card results" id="results">
    <div class="vid-info">
      <img class="thumb" id="vid-thumb" src="" alt="">
      <div class="vid-title" id="vid-title"></div>
    </div>
    <div class="section-label">🎬 ویدیو MP4</div>
    <div class="formats" id="video-formats"></div>
    <div class="section-label" style="margin-top:16px">🎵 فقط صدا</div>
    <div class="formats" id="audio-formats"></div>
  </div>
</div>

<script>
function extractId(url) {
  const p = [/youtu\.be\/([^?&\s]+)/, /[?&]v=([^&\s]+)/, /shorts\/([^?&\s]+)/, /embed\/([^?&\s]+)/];
  for (const r of p) { const m = url.match(r); if (m) return m[1]; }
  return null;
}

async function analyze() {
  const rawUrl = document.getElementById('url').value.trim();
  if (!rawUrl) { showError('لطفاً لینک را وارد کنید'); return; }

  const videoId = extractId(rawUrl);
  if (!videoId) { showError('لینک یوتیوب معتبر نیست'); return; }

  document.getElementById('btn').disabled = true;
  document.getElementById('error').style.display = 'none';
  document.getElementById('results').style.display = 'none';
  document.getElementById('loading').style.display = 'block';
  document.getElementById('loading-text').textContent = 'در حال دریافت اطلاعات...';

  try {
    // مرحله ۱: analyze
    const analyzeResp = await fetch('https://www.y2mate.com/mates/analyzeV2/ajax', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        k_query: `https://www.youtube.com/watch?v=${videoId}`,
        k_page: 'home',
        hl: 'en',
        q_auto: '1'
      })
    });
    const analyzeData = await analyzeResp.json();

    if (!analyzeData || analyzeData.status !== 'ok') {
      throw new Error('خطا در دریافت اطلاعات ویدیو');
    }

    document.getElementById('vid-title').textContent = analyzeData.title || 'ویدیو';
    document.getElementById('vid-thumb').src = `https://i.ytimg.com/vi/${videoId}/mqdefault.jpg`;

    // نمایش فرمت‌های MP4
    const videoDiv = document.getElementById('video-formats');
    const audioDiv = document.getElementById('audio-formats');
    videoDiv.innerHTML = '';
    audioDiv.innerHTML = '';

    const links = analyzeData.links || {};

    // MP4 ویدیو
    const mp4Links = links.mp4 || {};
    const qualities = ['1080p', '720p', '480p', '360p', '240p', '144p'];
    qualities.forEach(q => {
      if (mp4Links[q]) {
        const btn = document.createElement('button');
        btn.className = 'fmt-btn';
        btn.innerHTML = `<span>🎬 ${q}</span><span class="badge">MP4</span>`;
        btn.onclick = () => convert(analyzeData.vid, mp4Links[q].k, q, 'mp4', analyzeData.title);
        videoDiv.appendChild(btn);
      }
    });

    // MP3 صدا
    const mp3Links = links.mp3 || {};
    ['128kbps', '192kbps', '320kbps'].forEach(q => {
      if (mp3Links[q]) {
        const btn = document.createElement('button');
        btn.className = 'fmt-btn audio';
        btn.innerHTML = `<span>🎵 ${q}</span><span class="badge">MP3</span>`;
        btn.onclick = () => convert(analyzeData.vid, mp3Links[q].k, q, 'mp3', analyzeData.title);
        audioDiv.appendChild(btn);
      }
    });

    if (videoDiv.children.length === 0) {
      videoDiv.innerHTML = '<p style="color:#666;font-size:0.85rem">فرمت ویدیو پیدا نشد</p>';
    }
    if (audioDiv.children.length === 0) {
      audioDiv.innerHTML = '<p style="color:#666;font-size:0.85rem">فرمت صدا پیدا نشد</p>';
    }

    document.getElementById('loading').style.display = 'none';
    document.getElementById('results').style.display = 'block';

  } catch(e) {
    document.getElementById('loading').style.display = 'none';
    showError('خطا: ' + e.message);
  }

  document.getElementById('btn').disabled = false;
}

async function convert(vid, k, quality, type, title) {
  document.getElementById('loading').style.display = 'block';
  document.getElementById('loading-text').textContent = 'در حال آماده‌سازی فایل...';
  document.getElementById('results').style.display = 'none';

  try {
    const resp = await fetch('https://www.y2mate.com/mates/convertV2/index', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ vid, k })
    });
    const data = await resp.json();

    document.getElementById('loading').style.display = 'none';
    document.getElementById('results').style.display = 'block';

    if (data.status === 'ok' && data.dlink) {
      // دانلود مستقیم
      const a = document.createElement('a');
      a.href = data.dlink;
      a.download = (title || 'download') + '.' + type;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } else {
      showError('خطا در دریافت لینک دانلود');
    }
  } catch(e) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('results').style.display = 'block';
    showError('خطا: ' + e.message);
  }
}

function showError(msg) {
  const e = document.getElementById('error');
  e.textContent = msg;
  e.style.display = 'block';
  document.getElementById('btn').disabled = false;
  document.getElementById('loading').style.display = 'none';
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
