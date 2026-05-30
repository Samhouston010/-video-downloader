from flask import Flask, render_template_string, request, jsonify, Response
import os
import requests as req_lib
from urllib.parse import quote as url_quote, unquote as url_unquote
import subprocess
import json

app = Flask(__name__)

HTML = r'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sam Houston Downloader</title>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --glass: rgba(255,255,255,0.06);
  --glass-border: rgba(255,255,255,0.13);
  --glass-hover: rgba(255,255,255,0.11);
  --accent: #38bdf8;
  --accent2: #818cf8;
  --accent3: #f472b6;
  --text: #f1f5f9;
  --text-muted: #94a3b8;
  --bg1: #020617;
  --error: #f87171;
  --blur: blur(20px);
}
* { margin:0; padding:0; box-sizing:border-box; }
body {
  font-family: 'Vazirmatn', sans-serif;
  background: var(--bg1);
  color: var(--text);
  min-height: 100vh;
  overflow-x: hidden;
}
.bg-orbs { position:fixed; inset:0; z-index:0; pointer-events:none; overflow:hidden; }
.orb { position:absolute; border-radius:50%; filter:blur(90px); opacity:0.2; animation:float 14s ease-in-out infinite; }
.orb1 { width:550px; height:550px; background:radial-gradient(circle,#6366f1,transparent); top:-120px; right:-120px; }
.orb2 { width:450px; height:450px; background:radial-gradient(circle,#0ea5e9,transparent); bottom:-120px; left:-120px; animation-delay:-5s; }
.orb3 { width:350px; height:350px; background:radial-gradient(circle,#ec4899,transparent); top:50%; left:50%; transform:translate(-50%,-50%); animation-delay:-10s; }
@keyframes float {
  0%,100% { transform:translate(0,0) scale(1); }
  33% { transform:translate(25px,-25px) scale(1.04); }
  66% { transform:translate(-18px,18px) scale(0.96); }
}
body::before {
  content:''; position:fixed; inset:0; z-index:0;
  background-image: linear-gradient(rgba(255,255,255,0.025) 1px,transparent 1px),
                    linear-gradient(90deg,rgba(255,255,255,0.025) 1px,transparent 1px);
  background-size:60px 60px; pointer-events:none;
}
.page { position:relative; z-index:1; min-height:100vh; display:flex; flex-direction:column; align-items:center; padding:40px 20px; }

/* هدر */
header { text-align:center; margin-bottom:44px; animation:fadeDown 0.7s ease both; }
.logo-pill {
  display:inline-flex; align-items:center; gap:10px;
  background:var(--glass); border:1px solid var(--glass-border);
  backdrop-filter:var(--blur); border-radius:100px;
  padding:10px 22px; margin-bottom:22px;
}
.logo-dot { width:7px; height:7px; border-radius:50%; background:var(--accent); box-shadow:0 0 8px var(--accent); }
.logo-name { font-size:0.82rem; font-weight:600; color:var(--text-muted); letter-spacing:0.12em; text-transform:uppercase; }
h1 { font-size:clamp(1.9rem,5.5vw,3.2rem); font-weight:700; line-height:1.1; margin-bottom:10px;
  background:linear-gradient(135deg,#fff 0%,var(--accent) 55%,var(--accent2) 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.tagline { color:var(--text-muted); font-size:0.95rem; font-weight:300; }

/* کارت اصلی */
.main-card {
  width:100%; max-width:680px;
  background:var(--glass); border:1px solid var(--glass-border);
  backdrop-filter:var(--blur); border-radius:24px; padding:30px;
  margin-bottom:18px; animation:fadeUp 0.7s ease 0.15s both;
  box-shadow:0 25px 60px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.08);
}

/* پلتفرم */
.platforms { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:22px; }
.plat-btn {
  display:flex; align-items:center; gap:6px;
  background:transparent; border:1px solid var(--glass-border);
  border-radius:100px; padding:6px 14px;
  color:var(--text-muted); font-family:'Vazirmatn',sans-serif;
  font-size:0.8rem; cursor:pointer; transition:all 0.25s;
}
.plat-btn:hover, .plat-btn.active {
  background:var(--glass-hover); border-color:var(--accent); color:var(--text);
}
.plat-dot { width:8px; height:8px; border-radius:50%; }
.dot-tw { background:#1d9bf0; }
.dot-ig { background:linear-gradient(135deg,#f09433,#dc2743,#bc1888); }
.dot-tt { background:#ff0050; }

/* input */
.url-input {
  width:100%; background:rgba(0,0,0,0.35); border:1px solid var(--glass-border);
  border-radius:14px; padding:15px 18px; color:var(--text);
  font-family:'Vazirmatn',sans-serif; font-size:0.95rem; direction:ltr;
  transition:all 0.2s; outline:none; margin-bottom:16px;
}
.url-input::placeholder { color:#3f4f65; }
.url-input:focus { border-color:var(--accent); background:rgba(56,189,248,0.04); box-shadow:0 0 0 3px rgba(56,189,248,0.1); }

/* گزینه‌ها */
.options-row { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:18px; }
.opt-label { font-size:0.75rem; color:var(--text-muted); margin-bottom:7px; font-weight:500; }
.seg { display:flex; background:rgba(0,0,0,0.3); border:1px solid var(--glass-border); border-radius:10px; padding:3px; gap:3px; }
.seg-btn {
  flex:1; padding:8px; border:none; background:transparent;
  color:var(--text-muted); font-family:'Vazirmatn',sans-serif;
  font-size:0.8rem; border-radius:7px; cursor:pointer; transition:all 0.2s;
}
.seg-btn.active { background:rgba(255,255,255,0.1); color:var(--text); box-shadow:0 1px 3px rgba(0,0,0,0.3); }
.q-select {
  width:100%; background:rgba(0,0,0,0.3); border:1px solid var(--glass-border);
  border-radius:10px; padding:9px 13px; color:var(--text);
  font-family:'Vazirmatn',sans-serif; font-size:0.85rem; outline:none; cursor:pointer;
}
.q-select option { background:#0f172a; }

/* دکمه اصلی — شیشه‌ای درخشان */
.btn-main {
  width:100%; position:relative; overflow:hidden;
  background:linear-gradient(135deg,rgba(14,165,233,0.25),rgba(99,102,241,0.25));
  border:1px solid rgba(56,189,248,0.4);
  backdrop-filter:blur(10px);
  border-radius:14px; padding:15px;
  color:white; font-family:'Vazirmatn',sans-serif;
  font-size:1rem; font-weight:600; cursor:pointer; transition:all 0.3s;
}
.btn-main::before {
  content:''; position:absolute; top:-50%; left:-60%; width:40%; height:200%;
  background:linear-gradient(105deg,transparent,rgba(255,255,255,0.25),transparent);
  transform:skewX(-20deg); transition:left 0.6s ease;
}
.btn-main:hover::before { left:130%; }
.btn-main:hover {
  background:linear-gradient(135deg,rgba(14,165,233,0.4),rgba(99,102,241,0.4));
  border-color:rgba(56,189,248,0.7);
  box-shadow:0 0 25px rgba(56,189,248,0.3), inset 0 1px 0 rgba(255,255,255,0.15);
  transform:translateY(-1px);
}
.btn-main:disabled { opacity:0.45; cursor:not-allowed; transform:none; }

/* لودینگ */
.loading-card {
  display:none; width:100%; max-width:680px;
  background:var(--glass); border:1px solid var(--glass-border);
  backdrop-filter:var(--blur); border-radius:24px; padding:32px;
  text-align:center; margin-bottom:18px;
}
.ring { width:48px; height:48px; margin:0 auto 14px; border:3px solid rgba(255,255,255,0.08); border-top-color:var(--accent); border-radius:50%; animation:spin 0.85s linear infinite; }
@keyframes spin { to { transform:rotate(360deg); } }
.loading-txt { color:var(--text-muted); font-size:0.9rem; }

/* خطا */
.error-card {
  display:none; width:100%; max-width:680px;
  background:rgba(248,113,113,0.07); border:1px solid rgba(248,113,113,0.25);
  backdrop-filter:var(--blur); border-radius:16px; padding:15px 20px;
  margin-bottom:18px; color:var(--error); font-size:0.9rem; text-align:center;
}

/* نتایج */
.result-card {
  display:none; width:100%; max-width:680px;
  background:var(--glass); border:1px solid var(--glass-border);
  backdrop-filter:var(--blur); border-radius:24px; padding:26px;
  margin-bottom:18px; animation:fadeUp 0.4s ease both;
  box-shadow:0 25px 60px rgba(0,0,0,0.4);
}
.vid-head { display:flex; gap:14px; align-items:center; margin-bottom:20px; }
.vid-thumb { width:110px; height:62px; object-fit:cover; border-radius:10px; flex-shrink:0; border:1px solid var(--glass-border); }
.vid-thumb-sq { width:72px; height:72px; object-fit:cover; border-radius:50%; flex-shrink:0; border:2px solid var(--glass-border); }
.vid-meta { flex:1; min-width:0; }
.vid-t { font-size:0.95rem; font-weight:600; margin-bottom:4px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.vid-p { font-size:0.78rem; color:var(--text-muted); }

/* بخش موزیک */
.music-card {
  background:rgba(129,140,248,0.08); border:1px solid rgba(129,140,248,0.2);
  border-radius:14px; padding:14px 16px; margin-bottom:14px;
  display:flex; align-items:center; gap:12px;
}
.music-cover { width:44px; height:44px; border-radius:8px; object-fit:cover; flex-shrink:0; background:#1a1a3a; }
.music-info { flex:1; min-width:0; }
.music-name { font-size:0.88rem; font-weight:600; margin-bottom:2px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.music-artist { font-size:0.76rem; color:var(--text-muted); }
.music-btns { display:flex; gap:6px; flex-shrink:0; }
.music-btn {
  position:relative; overflow:hidden;
  background:rgba(129,140,248,0.15); border:1px solid rgba(129,140,248,0.3);
  border-radius:8px; padding:6px 12px; color:#a5b4fc;
  font-family:'Vazirmatn',sans-serif; font-size:0.78rem; cursor:pointer;
  text-decoration:none; transition:all 0.25s;
}
.music-btn::before {
  content:''; position:absolute; top:-50%; left:-60%; width:40%; height:200%;
  background:linear-gradient(105deg,transparent,rgba(255,255,255,0.2),transparent);
  transform:skewX(-20deg); transition:left 0.5s ease;
}
.music-btn:hover::before { left:130%; }
.music-btn:hover { background:rgba(129,140,248,0.3); border-color:rgba(129,140,248,0.6); box-shadow:0 0 15px rgba(129,140,248,0.25); }

/* دکمه‌های دانلود — شیشه‌ای درخشان */
.dl-btn {
  display:flex; align-items:center; justify-content:space-between;
  width:100%; position:relative; overflow:hidden;
  background:rgba(255,255,255,0.04); border:1px solid var(--glass-border);
  border-radius:12px; padding:13px 16px; color:var(--text);
  text-decoration:none; font-family:'Vazirmatn',sans-serif;
  font-size:0.88rem; cursor:pointer; transition:all 0.25s; margin-bottom:8px;
}
.dl-btn::before {
  content:''; position:absolute; top:-50%; left:-60%; width:35%; height:200%;
  background:linear-gradient(105deg,transparent,rgba(255,255,255,0.18),transparent);
  transform:skewX(-20deg); transition:left 0.55s ease;
}
.dl-btn:hover::before { left:130%; }
.dl-btn:hover {
  background:rgba(56,189,248,0.08);
  border-color:rgba(56,189,248,0.4);
  box-shadow:0 0 20px rgba(56,189,248,0.12), inset 0 1px 0 rgba(255,255,255,0.08);
  transform:translateX(-2px);
}
.dl-btn.audio-btn:hover {
  background:rgba(129,140,248,0.08);
  border-color:rgba(129,140,248,0.4);
  box-shadow:0 0 20px rgba(129,140,248,0.12), inset 0 1px 0 rgba(255,255,255,0.08);
}
.dl-btn.photo-btn:hover {
  background:rgba(244,114,182,0.08);
  border-color:rgba(244,114,182,0.4);
  box-shadow:0 0 20px rgba(244,114,182,0.12), inset 0 1px 0 rgba(255,255,255,0.08);
}
.dl-left { display:flex; align-items:center; gap:10px; }
.badge {
  font-size:0.7rem; padding:2px 9px; border-radius:20px; font-weight:600;
}
.badge-v { background:rgba(56,189,248,0.12); color:var(--accent); border:1px solid rgba(56,189,248,0.25); }
.badge-a { background:rgba(129,140,248,0.12); color:var(--accent2); border:1px solid rgba(129,140,248,0.25); }
.badge-p { background:rgba(244,114,182,0.12); color:var(--accent3); border:1px solid rgba(244,114,182,0.25); }
.dl-arrow { color:var(--text-muted); transition:all 0.2s; }
.dl-btn:hover .dl-arrow { color:var(--accent); transform:translateX(-3px); }
.dl-btn.audio-btn:hover .dl-arrow { color:var(--accent2); }
.dl-btn.photo-btn:hover .dl-arrow { color:var(--accent3); }

.section-sep { font-size:0.75rem; color:#334155; margin:12px 0 8px; font-weight:500; }

/* فوتر */
footer { margin-top:auto; padding-top:44px; text-align:center; animation:fadeUp 0.7s ease 0.3s both; }
.footer-brand { font-size:0.88rem; font-weight:600; color:#334155; margin-bottom:4px; }
.footer-brand span { color:var(--accent); }

@keyframes fadeDown { from{opacity:0;transform:translateY(-18px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeUp { from{opacity:0;transform:translateY(18px)} to{opacity:1;transform:translateY(0)} }

@media(max-width:480px) {
  .main-card,.result-card,.loading-card{padding:18px}
  .options-row{grid-template-columns:1fr}
  h1{font-size:1.75rem}
  .music-btns{flex-direction:column}
}
</style>
</head>
<body>
<div class="bg-orbs">
  <div class="orb orb1"></div><div class="orb orb2"></div><div class="orb orb3"></div>
</div>
<div class="page">

  <header>
    <div class="logo-pill">
      <span style="font-size:1.1rem">⬇️</span>
      <div class="logo-dot"></div>
      <span class="logo-name">Sam Houston Downloader</span>
    </div>
    <h1>دانلود سریع ویدیو</h1>
    <p class="tagline">توییتر • اینستاگرام • تیک‌تاک</p>
  </header>

  <div class="main-card">
    <div class="platforms">
      <button class="plat-btn active" onclick="setPlatform('instagram',this)">
        <span class="plat-dot dot-ig"></span> اینستاگرام
      </button>
      <button class="plat-btn" onclick="setPlatform('twitter',this)">
        <span class="plat-dot dot-tw"></span> Twitter / X
      </button>
      <button class="plat-btn" onclick="setPlatform('tiktok',this)">
        <span class="plat-dot dot-tt"></span> تیک‌تاک
      </button>
    </div>

    <input class="url-input" type="text" id="url"
      placeholder="لینک پست، ریل، استوری یا پروفایل را paste کنید...">

    <div class="options-row">
      <div>
        <div class="opt-label">نوع فایل</div>
        <div class="seg">
          <button class="seg-btn active" onclick="setType('video',this)">🎬 ویدیو</button>
          <button class="seg-btn" onclick="setType('audio',this)">🎵 صدا</button>
          <button class="seg-btn" onclick="setType('photo',this)">🖼 عکس</button>
        </div>
      </div>
      <div id="qg">
        <div class="opt-label">کیفیت</div>
        <select class="q-select" id="quality">
          <option value="best">بهترین کیفیت</option>
          <option value="1080">1080p</option>
          <option value="720" selected>720p</option>
          <option value="480">480p</option>
          <option value="360">360p</option>
        </select>
      </div>
    </div>

    <button class="btn-main" onclick="startDownload()" id="dl-btn">
      ⬇️ دریافت لینک دانلود
    </button>
  </div>

  <div class="loading-card" id="loading-card">
    <div class="ring"></div>
    <p class="loading-txt" id="loading-txt">در حال دریافت اطلاعات...</p>
  </div>

  <div class="error-card" id="error-card"></div>

  <div class="result-card" id="result-card">
    <div class="vid-head" id="vid-head"></div>
    <div id="music-section"></div>
    <div id="dl-links"></div>
  </div>

  <footer>
    <div class="footer-brand">Sam <span>Houston</span> Downloader</div>
    <div style="color:#1e293b;font-size:0.75rem;margin-top:3px">دانلود رایگان و بدون محدودیت</div>
  </footer>
</div>

<script>
let selType = 'video', selPlatform = 'instagram';

function setPlatform(p, el) {
  selPlatform = p;
  document.querySelectorAll('.plat-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
}

function setType(t, el) {
  selType = t;
  document.querySelectorAll('.seg-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('qg').style.opacity = t === 'audio' || t === 'photo' ? '0.4' : '1';
}

function showLoading(txt) {
  document.getElementById('loading-card').style.display = 'block';
  document.getElementById('loading-txt').textContent = txt || 'در حال دریافت اطلاعات...';
  document.getElementById('result-card').style.display = 'none';
  document.getElementById('error-card').style.display = 'none';
}

function showError(msg) {
  document.getElementById('loading-card').style.display = 'none';
  document.getElementById('error-card').textContent = '⚠️ ' + msg;
  document.getElementById('error-card').style.display = 'block';
  document.getElementById('dl-btn').disabled = false;
}

function showResults(data) {
  document.getElementById('loading-card').style.display = 'none';

  // هدر
  const head = document.getElementById('vid-head');
  const isProfile = data.is_profile;
  if (data.thumb) {
    head.innerHTML = `
      <img class="${isProfile ? 'vid-thumb-sq' : 'vid-thumb'}" src="${data.thumb}" onerror="this.style.display='none'">
      <div class="vid-meta">
        <div class="vid-t">${data.title || 'محتوا'}</div>
        <div class="vid-p">${data.platform || ''}</div>
      </div>`;
  } else {
    head.innerHTML = `<div class="vid-meta"><div class="vid-t">${data.title || 'محتوا'}</div><div class="vid-p">${data.platform || ''}</div></div>`;
  }

  // بخش موزیک
  const musicSec = document.getElementById('music-section');
  musicSec.innerHTML = '';
  if (data.music) {
    const m = data.music;
    musicSec.innerHTML = `
      <div class="music-card">
        ${m.cover ? `<img class="music-cover" src="${m.cover}" onerror="this.style.display='none'">` : '<div class="music-cover" style="display:flex;align-items:center;justify-content:center;font-size:1.3rem">🎵</div>'}
        <div class="music-info">
          <div class="music-name">${m.name || 'موزیک اصلی'}</div>
          <div class="music-artist">${m.artist || ''}</div>
        </div>
        <div class="music-btns">
          ${m.spotify ? `<a class="music-btn" href="${m.spotify}" target="_blank">🎧 Spotify</a>` : ''}
          ${m.apple ? `<a class="music-btn" href="${m.apple}" target="_blank">🍎 Apple</a>` : ''}
          ${m.youtube ? `<a class="music-btn" href="${m.youtube}" target="_blank">▶ YouTube</a>` : ''}
          ${!m.spotify && !m.apple && !m.youtube ? `<a class="music-btn" href="https://open.spotify.com/search/${encodeURIComponent((m.name||'') + ' ' + (m.artist||''))}" target="_blank">🔍 جستجو</a>` : ''}
        </div>
      </div>`;
  }

  // لینک‌های دانلود
  const dlDiv = document.getElementById('dl-links');
  dlDiv.innerHTML = '';

  if (data.links && data.links.length > 0) {
    data.links.forEach(link => {
      const a = document.createElement('a');
      const cls = link.type === 'audio' ? 'audio-btn' : link.type === 'photo' ? 'photo-btn' : '';
      const badge = link.type === 'audio' ? 'badge-a' : link.type === 'photo' ? 'badge-p' : 'badge-v';
      a.className = `dl-btn ${cls}`;
      a.href = link.url;
      a.target = '_blank';
      a.innerHTML = `
        <div class="dl-left">
          <span>${link.icon}</span>
          <span>${link.label}</span>
          <span class="badge ${badge}">${link.ext}</span>
        </div>
        <span class="dl-arrow">←</span>`;
      dlDiv.appendChild(a);
    });
  }

  document.getElementById('result-card').style.display = 'block';
  document.getElementById('dl-btn').disabled = false;
}

async function startDownload() {
  const url = document.getElementById('url').value.trim();
  if (!url) { showError('لطفاً لینک را وارد کنید'); return; }
  document.getElementById('dl-btn').disabled = true;
  document.getElementById('error-card').style.display = 'none';
  showLoading('در حال دریافت اطلاعات...');
  try {
    const r = await fetch('/api/info', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({url, type: selType, quality: document.getElementById('quality').value, platform: selPlatform})
    });
    const data = await r.json();
    if (data.error) { showError(data.error); return; }
    showResults(data);
  } catch(e) { showError('خطا: ' + e.message); }
}

document.getElementById('url').addEventListener('keydown', e => { if (e.key === 'Enter') startDownload(); });
</script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get('url', '').strip()
    dl_type = data.get('type', 'video')
    quality = data.get('quality', '720')

    if not url:
        return jsonify({'error': 'لینک وارد نشده'})

    # تشخیص پروفایل اینستاگرام
    is_profile = False
    import re
    if re.match(r'https?://(www\.)?instagram\.com/[^/]+/?$', url.rstrip('/')):
        is_profile = True
        return handle_instagram_profile(url)

    # yt-dlp برای استخراج اطلاعات
    cmd = ['yt-dlp', '--no-check-certificates', '--no-playlist', '-j', url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
        if result.returncode != 0:
            return jsonify({'error': 'خطا: ' + result.stderr[-250:]})
        info = json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'زمان پردازش تمام شد'})
    except Exception as e:
        return jsonify({'error': str(e)})

    title = info.get('title', '')
    platform = info.get('extractor_key', '')
    thumb = info.get('thumbnail', '')
    formats = info.get('formats', [])

    links = []

    # اطلاعات موزیک از اینستاگرام
    music_info = None
    if 'instagram' in platform.lower() or 'instagram' in url.lower():
        music_data = info.get('music_metadata') or info.get('music') or {}
        music_title = music_data.get('music_name') or info.get('music_title', '')
        music_artist = music_data.get('artist_name') or info.get('music_author', '')
        if music_title or music_artist:
            music_info = {
                'name': music_title,
                'artist': music_artist,
                'cover': music_data.get('album_cover_url', ''),
                'spotify': None,
                'apple': None,
                'youtube': f"https://www.youtube.com/results?search_query={url_quote((music_title or '') + ' ' + (music_artist or ''))}" if music_title else None
            }

    if dl_type == 'photo':
        # عکس‌های پست
        images = info.get('thumbnails', [])
        if images:
            best_img = max(images, key=lambda x: (x.get('width', 0) or 0) * (x.get('height', 0) or 0))
            img_url = best_img.get('url', '')
            if img_url:
                fn = url_quote((title or 'photo') + '.jpg')
                links.append({
                    'url': '/proxy?url=' + url_quote(img_url) + '&fn=' + fn,
                    'label': 'عکس با بهترین کیفیت',
                    'ext': 'JPG', 'icon': '🖼', 'type': 'photo'
                })
        if not links and thumb:
            fn = url_quote((title or 'photo') + '.jpg')
            links.append({
                'url': '/proxy?url=' + url_quote(thumb) + '&fn=' + fn,
                'label': 'عکس', 'ext': 'JPG', 'icon': '🖼', 'type': 'photo'
            })

    elif dl_type == 'audio':
        audio_fmts = [f for f in formats if f.get('vcodec') == 'none' and f.get('acodec') != 'none' and f.get('url')]
        if audio_fmts:
            best = max(audio_fmts, key=lambda f: f.get('abr', 0) or 0)
            ext = best.get('ext', 'mp3')
            fn = url_quote((title or 'audio') + '.' + ext)
            links.append({
                'url': '/proxy?url=' + url_quote(best['url']) + '&fn=' + fn,
                'label': f"صدا — {int(best.get('abr',0))}kbps" if best.get('abr') else 'بهترین کیفیت صدا',
                'ext': ext.upper(), 'icon': '🎵', 'type': 'audio'
            })
        if not links and info.get('url'):
            fn = url_quote((title or 'audio') + '.mp3')
            links.append({'url': '/proxy?url=' + url_quote(info['url']) + '&fn=' + fn, 'label': 'دانلود صدا', 'ext': 'MP3', 'icon': '🎵', 'type': 'audio'})

    else:
        target_h = {'1080': 1080, '720': 720, '480': 480, '360': 360, 'best': 9999}
        max_h = target_h.get(quality, 720)
        vfmts = [f for f in formats if f.get('vcodec') != 'none' and f.get('url') and (f.get('height') or 0) <= max_h]
        vfmts.sort(key=lambda f: (f.get('height') or 0) * (f.get('tbr') or 1), reverse=True)
        seen = set()
        for f in vfmts[:4]:
            h = f.get('height')
            if h in seen: continue
            seen.add(h)
            ext = f.get('ext', 'mp4')
            fn = url_quote((title or 'video') + '.' + ext)
            links.append({
                'url': '/proxy?url=' + url_quote(f['url']) + '&fn=' + fn,
                'label': f"ویدیو — {h}p" if h else 'بهترین کیفیت',
                'ext': ext.upper(), 'icon': '🎬', 'type': 'video'
            })
        if not links and info.get('url'):
            fn = url_quote((title or 'video') + '.mp4')
            links.append({'url': '/proxy?url=' + url_quote(info['url']) + '&fn=' + fn, 'label': 'دانلود ویدیو', 'ext': 'MP4', 'icon': '🎬', 'type': 'video'})

    if not links:
        return jsonify({'error': 'فرمت دانلود پیدا نشد'})

    return jsonify({
        'title': title, 'platform': platform,
        'thumb': thumb, 'links': links,
        'music': music_info, 'is_profile': False
    })


def handle_instagram_profile(url):
    """دانلود عکس پروفایل اینستاگرام"""
    import re
    m = re.search(r'instagram\.com/([^/?#]+)', url)
    if not m:
        return jsonify({'error': 'نام کاربری پیدا نشد'})
    username = m.group(1).strip('/')

    # استفاده از yt-dlp برای گرفتن اطلاعات
    cmd = ['yt-dlp', '--no-check-certificates', '-j',
           f'https://www.instagram.com/{username}/']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20, stdin=subprocess.DEVNULL)
        lines = [l for l in result.stdout.strip().split('\n') if l]
        if lines:
            info = json.loads(lines[0])
            thumb = info.get('thumbnail') or info.get('uploader_url', '')
            uploader = info.get('uploader', username)
        else:
            thumb = ''
            uploader = username
    except:
        thumb = ''
        uploader = username

    # لینک مستقیم عکس پروفایل
    profile_pic_url = f'https://unavatar.io/instagram/{username}'
    fn = url_quote(f'{username}_profile.jpg')

    links = [{
        'url': '/proxy?url=' + url_quote(profile_pic_url) + '&fn=' + fn,
        'label': f'عکس پروفایل @{username}',
        'ext': 'JPG', 'icon': '👤', 'type': 'photo'
    }]

    return jsonify({
        'title': f'@{username}',
        'platform': 'Instagram',
        'thumb': profile_pic_url,
        'links': links,
        'music': None,
        'is_profile': True
    })


@app.route('/proxy')
def proxy_download():
    file_url = url_unquote(request.args.get('url', ''))
    filename = url_unquote(request.args.get('fn', 'download'))
    if not file_url:
        return 'URL missing', 400
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
            'Referer': 'https://www.instagram.com/',
            'Accept': '*/*',
        }
        r = req_lib.get(file_url, headers=headers, stream=True, timeout=60)
        content_type = r.headers.get('Content-Type', 'application/octet-stream')
        def generate():
            for chunk in r.iter_content(chunk_size=8192):
                if chunk: yield chunk
        resp = Response(generate(), content_type=content_type)
        resp.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        if r.headers.get('Content-Length'):
            resp.headers['Content-Length'] = r.headers['Content-Length']
        return resp
    except Exception as e:
        return str(e), 500


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
