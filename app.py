from flask import Flask, render_template_string, request, jsonify
import os

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
  --glass: rgba(255,255,255,0.07);
  --glass-border: rgba(255,255,255,0.15);
  --glass-hover: rgba(255,255,255,0.12);
  --accent: #38bdf8;
  --accent2: #818cf8;
  --accent3: #f472b6;
  --text: #f1f5f9;
  --text-muted: #94a3b8;
  --bg1: #020617;
  --bg2: #0f172a;
  --success: #34d399;
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
  position: relative;
}

/* پس‌زمینه متحرک */
.bg-orbs {
  position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden;
}
.orb {
  position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.25; animation: float 12s ease-in-out infinite;
}
.orb1 { width: 500px; height: 500px; background: radial-gradient(circle, #6366f1, transparent); top: -100px; right: -100px; animation-delay: 0s; }
.orb2 { width: 400px; height: 400px; background: radial-gradient(circle, #0ea5e9, transparent); bottom: -100px; left: -100px; animation-delay: -4s; }
.orb3 { width: 300px; height: 300px; background: radial-gradient(circle, #ec4899, transparent); top: 40%; left: 40%; animation-delay: -8s; }

@keyframes float {
  0%, 100% { transform: translate(0,0) scale(1); }
  33% { transform: translate(30px,-30px) scale(1.05); }
  66% { transform: translate(-20px,20px) scale(0.95); }
}

/* grid pattern */
body::before {
  content: '';
  position: fixed; inset: 0; z-index: 0;
  background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  pointer-events: none;
}

.page { position: relative; z-index: 1; min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 40px 20px; }

/* هدر */
header {
  text-align: center; margin-bottom: 48px; animation: fadeDown 0.8s ease both;
}
.logo-wrap {
  display: inline-flex; align-items: center; gap: 12px;
  background: var(--glass); border: 1px solid var(--glass-border);
  backdrop-filter: var(--blur); border-radius: 100px;
  padding: 10px 24px; margin-bottom: 24px;
}
.logo-icon { font-size: 1.4rem; }
.logo-text { font-size: 0.9rem; font-weight: 600; color: var(--text-muted); letter-spacing: 0.1em; text-transform: uppercase; }
.logo-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }

h1 {
  font-size: clamp(2rem, 6vw, 3.5rem); font-weight: 700; line-height: 1.1; margin-bottom: 12px;
  background: linear-gradient(135deg, #fff 0%, var(--accent) 50%, var(--accent2) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.tagline { color: var(--text-muted); font-size: 1rem; font-weight: 300; }

/* کارت اصلی */
.main-card {
  width: 100%; max-width: 680px;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  backdrop-filter: var(--blur);
  border-radius: 24px;
  padding: 32px;
  margin-bottom: 20px;
  animation: fadeUp 0.8s ease 0.2s both;
  box-shadow: 0 25px 50px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1);
}

/* پلتفرم‌ها */
.platforms {
  display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 24px;
}
.plat-btn {
  display: flex; align-items: center; gap: 6px;
  background: transparent; border: 1px solid var(--glass-border);
  border-radius: 100px; padding: 6px 14px;
  color: var(--text-muted); font-family: 'Vazirmatn', sans-serif;
  font-size: 0.8rem; cursor: pointer; transition: all 0.2s;
}
.plat-btn:hover, .plat-btn.active {
  background: var(--glass-hover); border-color: var(--accent); color: var(--text);
}
.plat-btn .dot { width: 8px; height: 8px; border-radius: 50%; }
.dot-tw { background: #1d9bf0; }
.dot-ig { background: linear-gradient(135deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); }
.dot-tt { background: #ff0050; }

/* input */
.input-wrap {
  position: relative; margin-bottom: 16px;
}
.url-input {
  width: 100%;
  background: rgba(0,0,0,0.3);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  padding: 16px 20px;
  color: var(--text);
  font-family: 'Vazirmatn', sans-serif;
  font-size: 0.95rem;
  direction: ltr;
  transition: all 0.2s;
  outline: none;
}
.url-input::placeholder { color: #475569; }
.url-input:focus {
  border-color: var(--accent);
  background: rgba(56,189,248,0.05);
  box-shadow: 0 0 0 3px rgba(56,189,248,0.1);
}

/* گزینه‌ها */
.options-row {
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;
}
.option-group label {
  display: block; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 8px; font-weight: 500;
}
.seg-control {
  display: flex;
  background: rgba(0,0,0,0.3);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  padding: 3px;
  gap: 3px;
}
.seg-btn {
  flex: 1; padding: 8px; border: none; background: transparent;
  color: var(--text-muted); font-family: 'Vazirmatn', sans-serif;
  font-size: 0.8rem; border-radius: 8px; cursor: pointer; transition: all 0.2s;
}
.seg-btn.active {
  background: var(--glass-hover);
  color: var(--text);
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.quality-select {
  width: 100%;
  background: rgba(0,0,0,0.3);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  padding: 9px 14px;
  color: var(--text);
  font-family: 'Vazirmatn', sans-serif;
  font-size: 0.85rem;
  outline: none;
  cursor: pointer;
  transition: all 0.2s;
}
.quality-select:focus { border-color: var(--accent); }
.quality-select option { background: #0f172a; }

/* دکمه */
.btn-download {
  width: 100%;
  background: linear-gradient(135deg, #0ea5e9, #6366f1);
  border: none; border-radius: 14px;
  padding: 16px;
  color: white;
  font-family: 'Vazirmatn', sans-serif;
  font-size: 1rem; font-weight: 600;
  cursor: pointer; transition: all 0.3s;
  position: relative; overflow: hidden;
}
.btn-download::before {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.2), transparent);
  opacity: 0; transition: opacity 0.3s;
}
.btn-download:hover::before { opacity: 1; }
.btn-download:hover { transform: translateY(-1px); box-shadow: 0 8px 25px rgba(14,165,233,0.4); }
.btn-download:disabled { opacity: 0.5; cursor: not-allowed; transform: none; box-shadow: none; }

/* حالت لودینگ */
.loading-card {
  display: none; width: 100%; max-width: 680px;
  background: var(--glass); border: 1px solid var(--glass-border);
  backdrop-filter: var(--blur); border-radius: 24px; padding: 32px;
  text-align: center; margin-bottom: 20px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.4);
}
.loader-ring {
  width: 50px; height: 50px; margin: 0 auto 16px;
  border: 3px solid rgba(255,255,255,0.1);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { color: var(--text-muted); font-size: 0.9rem; }

/* نتایج */
.result-card {
  display: none; width: 100%; max-width: 680px;
  background: var(--glass); border: 1px solid var(--glass-border);
  backdrop-filter: var(--blur); border-radius: 24px; padding: 28px;
  margin-bottom: 20px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.4);
  animation: fadeUp 0.4s ease both;
}
.vid-header { display: flex; gap: 16px; align-items: center; margin-bottom: 24px; }
.vid-thumb {
  width: 110px; height: 62px; object-fit: cover;
  border-radius: 10px; flex-shrink: 0;
  border: 1px solid var(--glass-border);
}
.vid-meta { flex: 1; min-width: 0; }
.vid-title-text {
  font-size: 0.95rem; font-weight: 600; margin-bottom: 4px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.vid-platform { font-size: 0.78rem; color: var(--text-muted); }

.dl-btn {
  display: flex; align-items: center; justify-content: space-between;
  width: 100%;
  background: rgba(0,0,0,0.2);
  border: 1px solid var(--glass-border);
  border-radius: 12px; padding: 14px 18px;
  color: var(--text);
  text-decoration: none;
  font-family: 'Vazirmatn', sans-serif;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s; margin-bottom: 8px;
}
.dl-btn:hover {
  background: var(--glass-hover);
  border-color: var(--accent);
  transform: translateX(-2px);
}
.dl-btn-left { display: flex; align-items: center; gap: 10px; }
.dl-badge {
  font-size: 0.72rem; padding: 3px 10px; border-radius: 20px;
  font-weight: 600;
}
.badge-video { background: rgba(56,189,248,0.15); color: var(--accent); border: 1px solid rgba(56,189,248,0.3); }
.badge-audio { background: rgba(129,140,248,0.15); color: var(--accent2); border: 1px solid rgba(129,140,248,0.3); }
.dl-size { font-size: 0.78rem; color: var(--text-muted); }
.dl-arrow { color: var(--text-muted); font-size: 1rem; transition: transform 0.2s; }
.dl-btn:hover .dl-arrow { transform: translateX(-4px); color: var(--accent); }

/* خطا */
.error-card {
  display: none; width: 100%; max-width: 680px;
  background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.3);
  backdrop-filter: var(--blur); border-radius: 16px; padding: 16px 20px;
  margin-bottom: 20px; color: var(--error); font-size: 0.9rem; text-align: center;
}

/* فوتر */
footer {
  margin-top: auto; padding-top: 48px; text-align: center;
  color: #334155; font-size: 0.78rem; animation: fadeUp 0.8s ease 0.4s both;
}
.footer-brand {
  font-size: 0.9rem; font-weight: 600; color: #475569; margin-bottom: 4px;
  letter-spacing: 0.05em;
}
.footer-brand span { color: var(--accent); }

@keyframes fadeDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 480px) {
  .main-card, .result-card, .loading-card { padding: 20px; }
  .options-row { grid-template-columns: 1fr; }
  h1 { font-size: 1.8rem; }
}
</style>
</head>
<body>
<div class="bg-orbs">
  <div class="orb orb1"></div>
  <div class="orb orb2"></div>
  <div class="orb orb3"></div>
</div>

<div class="page">

  <header>
    <div class="logo-wrap">
      <span class="logo-icon">⬇️</span>
      <span class="logo-dot"></span>
      <span class="logo-text">Sam Houston Downloader</span>
    </div>
    <h1>دانلود سریع ویدیو</h1>
    <p class="tagline">توییتر • اینستاگرام • تیک‌تاک — بدون تبلیغ، بدون ثبت‌نام</p>
  </header>

  <div class="main-card">
    <div class="platforms">
      <button class="plat-btn active" onclick="setPlatform('twitter',this)">
        <span class="dot dot-tw"></span> Twitter / X
      </button>
      <button class="plat-btn" onclick="setPlatform('instagram',this)">
        <span class="dot dot-ig"></span> اینستاگرام
      </button>
      <button class="plat-btn" onclick="setPlatform('tiktok',this)">
        <span class="dot dot-tt"></span> تیک‌تاک
      </button>
    </div>

    <div class="input-wrap">
      <input class="url-input" type="text" id="url"
        placeholder="لینک ویدیو را اینجا paste کنید...">
    </div>

    <div class="options-row">
      <div class="option-group">
        <label>نوع فایل</label>
        <div class="seg-control">
          <button class="seg-btn active" onclick="setType('video',this)">🎬 ویدیو</button>
          <button class="seg-btn" onclick="setType('audio',this)">🎵 صدا</button>
        </div>
      </div>
      <div class="option-group" id="quality-group">
        <label>کیفیت</label>
        <select class="quality-select" id="quality">
          <option value="best">بهترین کیفیت</option>
          <option value="1080">1080p</option>
          <option value="720" selected>720p</option>
          <option value="480">480p</option>
          <option value="360">360p</option>
        </select>
      </div>
    </div>

    <button class="btn-download" onclick="startDownload()" id="dl-btn">
      ⬇️ دریافت لینک دانلود
    </button>
  </div>

  <div class="loading-card" id="loading-card">
    <div class="loader-ring"></div>
    <p class="loading-text" id="loading-text">در حال دریافت اطلاعات...</p>
  </div>

  <div class="error-card" id="error-card"></div>

  <div class="result-card" id="result-card">
    <div class="vid-header">
      <img class="vid-thumb" id="vid-thumb" src="" alt="">
      <div class="vid-meta">
        <div class="vid-title-text" id="vid-title">ویدیو آماده دانلود</div>
        <div class="vid-platform" id="vid-platform"></div>
      </div>
    </div>
    <div id="dl-links"></div>
  </div>

  <footer>
    <div class="footer-brand">Sam <span>Houston</span> Downloader</div>
    <div>ساخته شده با ❤️ — دانلود رایگان و بدون محدودیت</div>
  </footer>

</div>

<script>
let selectedType = 'video';
let selectedPlatform = 'twitter';

function setPlatform(p, el) {
  selectedPlatform = p;
  document.querySelectorAll('.plat-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  const placeholders = {
    twitter: 'https://twitter.com/user/status/...',
    instagram: 'https://www.instagram.com/p/...',
    tiktok: 'https://www.tiktok.com/@user/video/...'
  };
  document.getElementById('url').placeholder = placeholders[p] + ' را paste کنید';
}

function setType(t, el) {
  selectedType = t;
  document.querySelectorAll('.seg-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('quality-group').style.opacity = t === 'audio' ? '0.4' : '1';
}

function showLoading(text) {
  document.getElementById('loading-card').style.display = 'block';
  document.getElementById('loading-text').textContent = text || 'در حال دریافت اطلاعات...';
  document.getElementById('result-card').style.display = 'none';
  document.getElementById('error-card').style.display = 'none';
}

function showError(msg) {
  document.getElementById('loading-card').style.display = 'none';
  document.getElementById('error-card').textContent = '⚠️ ' + msg;
  document.getElementById('error-card').style.display = 'block';
  document.getElementById('dl-btn').disabled = false;
}

function showResults(links, title, platform, thumb) {
  document.getElementById('loading-card').style.display = 'none';
  document.getElementById('vid-title').textContent = title || 'ویدیو';
  document.getElementById('vid-platform').textContent = platform;
  if (thumb) document.getElementById('vid-thumb').src = thumb;
  else document.getElementById('vid-thumb').style.display = 'none';

  const container = document.getElementById('dl-links');
  container.innerHTML = '';
  links.forEach(link => {
    const a = document.createElement('a');
    a.className = 'dl-btn';
    a.href = link.url;
    a.target = '_blank';
    a.rel = 'noopener';
    a.innerHTML = `
      <div class="dl-btn-left">
        <span>${link.icon}</span>
        <span>${link.label}</span>
        <span class="dl-badge ${link.type === 'audio' ? 'badge-audio' : 'badge-video'}">${link.ext}</span>
      </div>
      <span class="dl-arrow">←</span>
    `;
    container.appendChild(a);
  });

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
    const quality = document.getElementById('quality').value;
    const resp = await fetch('/api/info', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, type: selectedType, quality, platform: selectedPlatform })
    });
    const data = await resp.json();
    if (data.error) { showError(data.error); return; }
    showResults(data.links, data.title, data.platform, data.thumb);
  } catch(e) {
    showError('خطا در اتصال به سرور: ' + e.message);
  }
}

document.getElementById('url').addEventListener('keydown', e => {
  if (e.key === 'Enter') startDownload();
});
</script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/info', methods=['POST'])
def get_info():
    import subprocess, json, re, uuid, tempfile, os

    data = request.get_json()
    url = data.get('url', '').strip()
    dl_type = data.get('type', 'video')
    quality = data.get('quality', '720')

    if not url:
        return jsonify({'error': 'لینک وارد نشده'})

    # استخراج اطلاعات با yt-dlp
    cmd = [
        'yt-dlp',
        '--no-check-certificates',
        '--no-playlist',
        '-j',
        url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
        if result.returncode != 0:
            err = result.stderr[-300:]
            return jsonify({'error': 'خطا در دریافت اطلاعات: ' + err})

        info = json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'زمان پردازش تمام شد'})
    except Exception as e:
        return jsonify({'error': str(e)})

    title = info.get('title', 'ویدیو')
    platform = info.get('extractor_key', '')
    thumb = info.get('thumbnail', '')

    links = []
    formats = info.get('formats', [])

    if dl_type == 'audio':
        # بهترین فرمت صوتی
        audio_fmts = [f for f in formats if f.get('vcodec') == 'none' and f.get('acodec') != 'none' and f.get('url')]
        if audio_fmts:
            best = max(audio_fmts, key=lambda f: f.get('abr', 0) or 0)
            links.append({
                'url': best['url'],
                'label': f"صدا — {int(best.get('abr',0))}kbps" if best.get('abr') else 'بهترین کیفیت صدا',
                'ext': best.get('ext', 'mp3').upper(),
                'icon': '🎵',
                'type': 'audio'
            })
        # fallback
        if not links and info.get('url'):
            links.append({'url': info['url'], 'label': 'دانلود صدا', 'ext': 'MP3', 'icon': '🎵', 'type': 'audio'})
    else:
        # فرمت‌های ویدیو
        target_heights = {'1080': 1080, '720': 720, '480': 480, '360': 360, 'best': 9999}
        max_h = target_heights.get(quality, 720)

        video_fmts = [
            f for f in formats
            if f.get('vcodec') != 'none' and f.get('url')
            and (f.get('height') or 0) <= max_h
        ]

        # مرتب‌سازی بر اساس کیفیت
        video_fmts.sort(key=lambda f: (f.get('height') or 0) * (f.get('tbr') or 0), reverse=True)

        seen_heights = set()
        for f in video_fmts[:4]:
            h = f.get('height')
            label_h = f"{h}p" if h else 'بهترین کیفیت'
            if h in seen_heights:
                continue
            seen_heights.add(h)
            links.append({
                'url': f['url'],
                'label': f"ویدیو — {label_h}",
                'ext': f.get('ext', 'mp4').upper(),
                'icon': '🎬',
                'type': 'video'
            })

        # اگه format stream مستقیم داشت
        if not links and info.get('url'):
            links.append({'url': info['url'], 'label': 'دانلود ویدیو', 'ext': 'MP4', 'icon': '🎬', 'type': 'video'})

    if not links:
        return jsonify({'error': 'فرمت دانلود پیدا نشد'})

    return jsonify({
        'title': title,
        'platform': platform,
        'thumb': thumb,
        'links': links
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
