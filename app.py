from flask import Flask, request, jsonify, send_file, render_template_string
import subprocess
import os
import shutil
import tempfile
import threading
import uuid

app = Flask(__name__)
downloads = {}

COOKIES_PATH = '/etc/secrets/cookies.txt'
COOKIES_COPY = '/tmp/cookies.txt'

def base_cmd():
    cmd = [
        'yt-dlp',
        '--no-check-certificates',
        '--extractor-args', 'youtube:player_client=web',
        '--add-header', 'Accept-Language:en-US,en;q=0.9',
        '--no-playlist',
    ]
    if os.path.exists(COOKIES_PATH):
        shutil.copy2(COOKIES_PATH, COOKIES_COPY)
    if os.path.exists(COOKIES_COPY):
        cmd += ['--cookies', COOKIES_COPY]
    return cmd

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
  .container { width: 100%; max-width: 600px; }
  h1 { text-align: center; font-size: 2rem; font-weight: 700; margin-bottom: 8px; background: linear-gradient(135deg, #a78bfa, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .subtitle { text-align: center; color: #666; font-size: 0.85rem; margin-bottom: 32px; }
  .card { background: #111118; border: 1px solid #222230; border-radius: 16px; padding: 28px; margin-bottom: 20px; }
  label { display: block; font-size: 0.85rem; color: #888; margin-bottom: 8px; }
  input[type="text"] { width: 100%; background: #0a0a0f; border: 1px solid #2a2a3a; border-radius: 10px; padding: 12px 16px; color: #e0e0e0; font-family: 'Vazirmatn', sans-serif; font-size: 0.9rem; direction: ltr; margin-bottom: 20px; transition: border-color 0.2s; }
  input[type="text"]:focus { outline: none; border-color: #a78bfa; }
  .options { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
  .option-btn { background: #0a0a0f; border: 2px solid #2a2a3a; border-radius: 10px; padding: 14px; cursor: pointer; text-align: center; transition: all 0.2s; color: #888; font-family: 'Vazirmatn', sans-serif; font-size: 0.85rem; }
  .option-btn:hover { border-color: #a78bfa; color: #a78bfa; }
  .option-btn.active { border-color: #a78bfa; background: #1a1030; color: #a78bfa; }
  .option-btn .icon { font-size: 1.5rem; display: block; margin-bottom: 6px; }
  .quality-section { margin-bottom: 20px; }
  .quality-options { display: flex; gap: 8px; flex-wrap: wrap; }
  .quality-btn { background: #0a0a0f; border: 2px solid #2a2a3a; border-radius: 8px; padding: 8px 16px; cursor: pointer; color: #888; font-family: 'Vazirmatn', sans-serif; font-size: 0.8rem; transition: all 0.2s; }
  .quality-btn:hover { border-color: #60a5fa; color: #60a5fa; }
  .quality-btn.active { border-color: #60a5fa; background: #0a1a30; color: #60a5fa; }
  .download-btn { width: 100%; background: linear-gradient(135deg, #7c3aed, #2563eb); border: none; border-radius: 10px; padding: 14px; color: white; font-family: 'Vazirmatn', sans-serif; font-size: 1rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
  .download-btn:hover { opacity: 0.9; }
  .download-btn:disabled { opacity: 0.5; cursor: not-allowed; }
  .progress-card { display: none; background: #111118; border: 1px solid #222230; border-radius: 16px; padding: 24px; margin-bottom: 20px; }
  .progress-bar-bg { background: #1a1a2a; border-radius: 100px; height: 8px; margin: 12px 0; overflow: hidden; }
  .progress-bar { height: 100%; background: linear-gradient(135deg, #7c3aed, #2563eb); border-radius: 100px; width: 0%; transition: width 0.3s; }
  .progress-text { font-size: 0.85rem; color: #888; text-align: center; }
  .result-card { display: none; background: #111118; border: 1px solid #1a3a1a; border-radius: 16px; padding: 24px; text-align: center; }
  .result-title { font-size: 1rem; font-weight: 600; margin-bottom: 16px; color: #4ade80; }
  .action-btns { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .action-btn { padding: 12px; border-radius: 10px; border: none; cursor: pointer; font-family: 'Vazirmatn', sans-serif; font-size: 0.9rem; font-weight: 600; transition: opacity 0.2s; }
  .btn-download { background: #4ade80; color: #0a0a0f; }
  .btn-share { background: #25d366; color: white; }
  .action-btn:hover { opacity: 0.9; }
  .supported { text-align: center; color: #444; font-size: 0.75rem; margin-top: 16px; }
  .error-msg { color: #f87171; font-size: 0.85rem; margin-top: 8px; text-align: center; display: none; white-space: pre-wrap; word-break: break-word; }
</style>
</head>
<body>
<div class="container">
  <h1>🎬 دانلودر</h1>
  <p class="subtitle">یوتیوب • اینستاگرام • تیک‌تاک • توییتر و بیشتر</p>
  <div class="card">
    <label>لینک ویدیو یا آهنگ را وارد کنید</label>
    <input type="text" id="url" placeholder="https://youtube.com/watch?v=...">
    <label>نوع فایل</label>
    <div class="options">
      <button class="option-btn active" onclick="setType('video')" id="btn-video">
        <span class="icon">🎬</span>ویدیو (MP4)
      </button>
      <button class="option-btn" onclick="setType('audio')" id="btn-audio">
        <span class="icon">🎵</span>فقط صدا (MP3)
      </button>
    </div>
    <div class="quality-section" id="quality-section">
      <label>کیفیت</label>
      <div class="quality-options">
        <button class="quality-btn" onclick="setQuality('1080')" id="q-1080">1080p</button>
        <button class="quality-btn active" onclick="setQuality('720')" id="q-720">720p</button>
        <button class="quality-btn" onclick="setQuality('480')" id="q-480">480p</button>
        <button class="quality-btn" onclick="setQuality('360')" id="q-360">360p</button>
      </div>
    </div>
    <button class="download-btn" onclick="startDownload()" id="dl-btn">⬇️ دانلود</button>
    <p class="error-msg" id="error-msg"></p>
  </div>
  <div class="progress-card" id="progress-card">
    <p style="text-align:center; margin-bottom:8px;">در حال دانلود...</p>
    <div class="progress-bar-bg"><div class="progress-bar" id="progress-bar"></div></div>
    <p class="progress-text" id="progress-text">لطفاً صبر کنید...</p>
  </div>
  <div class="result-card" id="result-card">
    <p class="result-title">✅ دانلود آماده شد!</p>
    <div class="action-btns">
      <button class="action-btn btn-download" onclick="saveFile()">💾 ذخیره فایل</button>
      <button class="action-btn btn-share" onclick="shareWhatsApp()">📲 ارسال واتساپ</button>
    </div>
  </div>
  <p class="supported">پشتیبانی از: YouTube • Instagram • TikTok • Twitter/X • Facebook و ۱۰۰۰+ سایت دیگر</p>
</div>
<script>
let selectedType = 'video', selectedQuality = '720', downloadId = null, downloadUrl = null;
function setType(type) {
  selectedType = type;
  document.getElementById('btn-video').classList.toggle('active', type==='video');
  document.getElementById('btn-audio').classList.toggle('active', type==='audio');
  document.getElementById('quality-section').style.display = type==='video' ? 'block' : 'none';
}
function setQuality(q) {
  selectedQuality = q;
  document.querySelectorAll('.quality-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('q-'+q).classList.add('active');
}
async function startDownload() {
  const url = document.getElementById('url').value.trim();
  if (!url) { showError('لطفاً لینک را وارد کنید'); return; }
  document.getElementById('dl-btn').disabled = true;
  document.getElementById('error-msg').style.display = 'none';
  document.getElementById('progress-card').style.display = 'block';
  document.getElementById('result-card').style.display = 'none';
  document.getElementById('progress-bar').style.width = '10%';
  document.getElementById('progress-text').textContent = 'در حال شروع...';
  try {
    const res = await fetch('/download', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({url, type: selectedType, quality: selectedQuality})
    });
    const data = await res.json();
    if (data.error) { showError(data.error); return; }
    downloadId = data.id;
    checkProgress();
  } catch(e) { showError('خطا در اتصال به سرور'); }
}
function checkProgress() {
  const interval = setInterval(async () => {
    const res = await fetch('/progress/'+downloadId);
    const data = await res.json();
    if (data.progress) {
      document.getElementById('progress-bar').style.width = data.progress+'%';
      document.getElementById('progress-text').textContent = data.status || 'در حال دانلود...';
    }
    if (data.done) {
      clearInterval(interval);
      document.getElementById('progress-bar').style.width = '100%';
      setTimeout(() => {
        document.getElementById('progress-card').style.display = 'none';
        document.getElementById('result-card').style.display = 'block';
        downloadUrl = '/file/'+downloadId;
        document.getElementById('dl-btn').disabled = false;
      }, 500);
    }
    if (data.error) { clearInterval(interval); showError(data.error); }
  }, 1500);
}
function saveFile() { if (downloadUrl) window.location.href = downloadUrl; }
function shareWhatsApp() {
  window.open('https://wa.me/?text='+encodeURIComponent('فایل: '+window.location.origin+'/file/'+downloadId));
}
function showError(msg) {
  document.getElementById('error-msg').textContent = msg;
  document.getElementById('error-msg').style.display = 'block';
  document.getElementById('progress-card').style.display = 'none';
  document.getElementById('dl-btn').disabled = false;
}
</script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    dl_type = data.get('type', 'video')
    quality = data.get('quality', '720')
    if not url:
        return jsonify({'error': 'لینک وارد نشده'})
    dl_id = str(uuid.uuid4())
    downloads[dl_id] = {'progress': 0, 'done': False, 'error': None, 'file': None, 'status': 'شروع...'}
    thread = threading.Thread(target=do_download, args=(dl_id, url, dl_type, quality))
    thread.daemon = True
    thread.start()
    return jsonify({'id': dl_id})

def do_download(dl_id, url, dl_type, quality):
    try:
        tmp_dir = tempfile.mkdtemp()
        downloads[dl_id]['progress'] = 20
        downloads[dl_id]['status'] = 'در حال دریافت اطلاعات...'

        cmd = base_cmd()

        if dl_type == 'audio':
            cmd += [
                '-x', '--audio-format', 'mp3', '--audio-quality', '0',
                '-o', os.path.join(tmp_dir, '%(title)s.%(ext)s'),
                url
            ]
        else:
            # فرمت انعطاف‌پذیر — از بهترین به پایین‌ترین fallback می‌کنه
            fmt = (
                f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/'
                f'bestvideo[height<={quality}]+bestaudio/'
                f'best[height<={quality}]/'
                f'bestvideo+bestaudio/'
                f'best'
            )
            cmd += [
                '-f', fmt,
                '--merge-output-format', 'mp4',
                '-o', os.path.join(tmp_dir, '%(title)s.%(ext)s'),
                url
            ]

        downloads[dl_id]['progress'] = 40
        downloads[dl_id]['status'] = 'در حال دانلود...'

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180, stdin=subprocess.DEVNULL)

        if result.returncode != 0:
            err = result.stderr[-400:] if result.stderr else 'خطای ناشناخته'
            downloads[dl_id]['error'] = err
            return

        downloads[dl_id]['progress'] = 90
        downloads[dl_id]['status'] = 'در حال آماده‌سازی...'

        files = os.listdir(tmp_dir)
        if files:
            downloads[dl_id]['file'] = os.path.join(tmp_dir, files[0])
            downloads[dl_id]['filename'] = files[0]
            downloads[dl_id]['progress'] = 100
            downloads[dl_id]['done'] = True
            downloads[dl_id]['status'] = 'تمام!'
        else:
            downloads[dl_id]['error'] = 'فایلی پیدا نشد'
    except subprocess.TimeoutExpired:
        downloads[dl_id]['error'] = 'زمان دانلود تمام شد (timeout)'
    except Exception as e:
        downloads[dl_id]['error'] = str(e)

@app.route('/progress/<dl_id>')
def progress(dl_id):
    if dl_id not in downloads:
        return jsonify({'error': 'شناسه نامعتبر'})
    return jsonify(downloads[dl_id])

@app.route('/file/<dl_id>')
def get_file(dl_id):
    if dl_id not in downloads or not downloads[dl_id].get('file'):
        return 'فایل یافت نشد', 404
    return send_file(downloads[dl_id]['file'], as_attachment=True,
                     download_name=downloads[dl_id].get('filename', 'download'))

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'cookies_secret': os.path.exists(COOKIES_PATH),
        'cookies_tmp': os.path.exists(COOKIES_COPY)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
