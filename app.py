from flask import Flask, render_template_string, request, jsonify, Response
import os, requests as req_lib
from urllib.parse import quote as uq, unquote as uuq

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
  --g: rgba(255,255,255,0.06);
  --gb: rgba(255,255,255,0.13);
  --gh: rgba(255,255,255,0.1);
  --a: #38bdf8; --a2: #818cf8; --a3: #f472b6;
  --t: #f1f5f9; --tm: #94a3b8;
  --bg: #020617; --err: #f87171;
  --blur: blur(18px);
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Vazirmatn',sans-serif;background:var(--bg);color:var(--t);min-height:100vh;overflow-x:hidden}
.orbs{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.orb{position:absolute;border-radius:50%;filter:blur(90px);opacity:.18;animation:fl 14s ease-in-out infinite}
.o1{width:550px;height:550px;background:radial-gradient(circle,#6366f1,transparent);top:-100px;right:-100px}
.o2{width:450px;height:450px;background:radial-gradient(circle,#0ea5e9,transparent);bottom:-100px;left:-100px;animation-delay:-5s}
.o3{width:300px;height:300px;background:radial-gradient(circle,#ec4899,transparent);top:50%;left:50%;transform:translate(-50%,-50%);animation-delay:-10s}
@keyframes fl{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(20px,-20px) scale(1.04)}66%{transform:translate(-15px,15px) scale(.97)}}
body::before{content:'';position:fixed;inset:0;z-index:0;background-image:linear-gradient(rgba(255,255,255,.02) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.02) 1px,transparent 1px);background-size:60px 60px;pointer-events:none}
.page{position:relative;z-index:1;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:36px 18px}

/* هدر */
header{text-align:center;margin-bottom:40px;animation:fdown .7s ease both}
.pill{display:inline-flex;align-items:center;gap:9px;background:var(--g);border:1px solid var(--gb);backdrop-filter:var(--blur);border-radius:100px;padding:9px 20px;margin-bottom:20px}
.pdot{width:7px;height:7px;border-radius:50%;background:var(--a);box-shadow:0 0 8px var(--a)}
.pname{font-size:.8rem;font-weight:600;color:var(--tm);letter-spacing:.12em;text-transform:uppercase}
h1{font-size:clamp(1.8rem,5vw,3rem);font-weight:700;line-height:1.1;margin-bottom:10px;background:linear-gradient(135deg,#fff 0%,var(--a) 55%,var(--a2) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.sub{color:var(--tm);font-size:.9rem;font-weight:300}

/* کارت */
.card{width:100%;max-width:680px;background:var(--g);border:1px solid var(--gb);backdrop-filter:var(--blur);border-radius:22px;padding:28px;margin-bottom:16px;box-shadow:0 25px 60px rgba(0,0,0,.4),inset 0 1px 0 rgba(255,255,255,.07);animation:fup .7s ease .1s both}

/* پلتفرم */
.plats{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:20px}
.pb{display:flex;align-items:center;gap:6px;background:transparent;border:1px solid var(--gb);border-radius:100px;padding:6px 13px;color:var(--tm);font-family:'Vazirmatn',sans-serif;font-size:.78rem;cursor:pointer;transition:all .2s}
.pb:hover,.pb.on{background:var(--gh);border-color:var(--a);color:var(--t)}
.pd{width:7px;height:7px;border-radius:50%}
.dtw{background:#1d9bf0}.dig{background:linear-gradient(135deg,#f09433,#dc2743,#bc1888)}.dtt{background:#ff0050}

/* input */
.ui{width:100%;background:rgba(0,0,0,.35);border:1px solid var(--gb);border-radius:13px;padding:14px 17px;color:var(--t);font-family:'Vazirmatn',sans-serif;font-size:.9rem;direction:ltr;transition:all .2s;outline:none;margin-bottom:15px}
.ui::placeholder{color:#3a4a60}
.ui:focus{border-color:var(--a);background:rgba(56,189,248,.04);box-shadow:0 0 0 3px rgba(56,189,248,.1)}

/* دکمه اصلی */
.bmain{width:100%;position:relative;overflow:hidden;background:linear-gradient(135deg,rgba(14,165,233,.22),rgba(99,102,241,.22));border:1px solid rgba(56,189,248,.38);backdrop-filter:blur(10px);border-radius:13px;padding:14px;color:#fff;font-family:'Vazirmatn',sans-serif;font-size:.95rem;font-weight:600;cursor:pointer;transition:all .3s}
.bmain::before{content:'';position:absolute;top:-50%;left:-60%;width:35%;height:200%;background:linear-gradient(105deg,transparent,rgba(255,255,255,.22),transparent);transform:skewX(-20deg);transition:left .55s ease}
.bmain:hover::before{left:130%}
.bmain:hover{background:linear-gradient(135deg,rgba(14,165,233,.38),rgba(99,102,241,.38));border-color:rgba(56,189,248,.65);box-shadow:0 0 22px rgba(56,189,248,.28),inset 0 1px 0 rgba(255,255,255,.12);transform:translateY(-1px)}
.bmain:disabled{opacity:.4;cursor:not-allowed;transform:none}

/* لودینگ */
.lcard{display:none;width:100%;max-width:680px;background:var(--g);border:1px solid var(--gb);backdrop-filter:var(--blur);border-radius:22px;padding:30px;text-align:center;margin-bottom:16px}
.ring{width:46px;height:46px;margin:0 auto 13px;border:3px solid rgba(255,255,255,.07);border-top-color:var(--a);border-radius:50%;animation:spin .85s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.ltxt{color:var(--tm);font-size:.88rem}

/* خطا */
.ecard{display:none;width:100%;max-width:680px;background:rgba(248,113,113,.07);border:1px solid rgba(248,113,113,.22);backdrop-filter:var(--blur);border-radius:14px;padding:14px 18px;margin-bottom:16px;color:var(--err);font-size:.88rem;text-align:center}

/* نتیجه */
.rcard{display:none;width:100%;max-width:680px;background:var(--g);border:1px solid var(--gb);backdrop-filter:var(--blur);border-radius:22px;padding:24px;margin-bottom:16px;animation:fup .4s ease both;box-shadow:0 25px 60px rgba(0,0,0,.4)}
.vhead{display:flex;gap:13px;align-items:center;margin-bottom:20px}
.vthumb{width:106px;height:60px;object-fit:cover;border-radius:9px;flex-shrink:0;border:1px solid var(--gb)}
.vtitle{font-size:.92rem;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-bottom:3px}
.vplat{font-size:.75rem;color:var(--tm)}
.slabel{font-size:.73rem;color:#334155;margin:10px 0 7px;font-weight:500;text-transform:uppercase;letter-spacing:.06em}

/* دکمه دانلود — شیشه‌ای */
.dlb{display:flex;align-items:center;justify-content:space-between;width:100%;position:relative;overflow:hidden;background:rgba(255,255,255,.04);border:1px solid var(--gb);border-radius:11px;padding:12px 15px;color:var(--t);text-decoration:none;font-family:'Vazirmatn',sans-serif;font-size:.86rem;cursor:pointer;transition:all .25s;margin-bottom:7px}
.dlb::before{content:'';position:absolute;top:-50%;left:-60%;width:33%;height:200%;background:linear-gradient(105deg,transparent,rgba(255,255,255,.16),transparent);transform:skewX(-20deg);transition:left .5s ease}
.dlb:hover::before{left:130%}
.dlb.vbtn:hover{background:rgba(56,189,248,.08);border-color:rgba(56,189,248,.38);box-shadow:0 0 18px rgba(56,189,248,.1),inset 0 1px 0 rgba(255,255,255,.07);transform:translateX(-2px)}
.dlb.abtn:hover{background:rgba(129,140,248,.08);border-color:rgba(129,140,248,.38);box-shadow:0 0 18px rgba(129,140,248,.1),inset 0 1px 0 rgba(255,255,255,.07);transform:translateX(-2px)}
.dlb.pbtn:hover{background:rgba(244,114,182,.08);border-color:rgba(244,114,182,.38);box-shadow:0 0 18px rgba(244,114,182,.1),inset 0 1px 0 rgba(255,255,255,.07);transform:translateX(-2px)}
.dll{display:flex;align-items:center;gap:9px}
.badge{font-size:.68rem;padding:2px 8px;border-radius:20px;font-weight:600}
.bv{background:rgba(56,189,248,.1);color:var(--a);border:1px solid rgba(56,189,248,.22)}
.ba{background:rgba(129,140,248,.1);color:var(--a2);border:1px solid rgba(129,140,248,.22)}
.bp{background:rgba(244,114,182,.1);color:var(--a3);border:1px solid rgba(244,114,182,.22)}
.darr{color:var(--tm);transition:all .2s}
.dlb:hover .darr{transform:translateX(-3px);color:var(--a)}
.dlb.abtn:hover .darr{color:var(--a2)}
.dlb.pbtn:hover .darr{color:var(--a3)}

footer{margin-top:auto;padding-top:40px;text-align:center;animation:fup .7s ease .3s both}
.fb{font-size:.85rem;font-weight:600;color:#334155;margin-bottom:3px}.fb span{color:var(--a)}
.fs{color:#1e293b;font-size:.73rem}

@keyframes fdown{from{opacity:0;transform:translateY(-16px)}to{opacity:1;transform:translateY(0)}}
@keyframes fup{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:480px){.card,.rcard,.lcard{padding:17px}h1{font-size:1.7rem}}
</style>
</head>
<body>
<div class="orbs"><div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div></div>
<div class="page">
<header>
  <div class="pill"><span style="font-size:1.1rem">⬇️</span><div class="pdot"></div><span class="pname">Sam Houston Downloader</span></div>
  <h1>دانلود سریع ویدیو</h1>
  <p class="sub">توییتر • اینستاگرام • تیک‌تاک</p>
</header>

<div class="card">
  <div class="plats">
    <button class="pb on" onclick="setP('instagram',this)"><span class="pd dig"></span>اینستاگرام</button>
    <button class="pb" onclick="setP('twitter',this)"><span class="pd dtw"></span>Twitter / X</button>
    <button class="pb" onclick="setP('tiktok',this)"><span class="pd dtt"></span>تیک‌تاک</button>
  </div>
  <input class="ui" id="url" placeholder="لینک پست یا ویدیو را paste کنید...">
  <button class="bmain" onclick="go()" id="btn">⬇️ دریافت لینک‌های دانلود</button>
</div>

<div class="lcard" id="lcard"><div class="ring"></div><p class="ltxt" id="ltxt">در حال دریافت...</p></div>
<div class="ecard" id="ecard"></div>
<div class="rcard" id="rcard">
  <div class="vhead" id="vhead"></div>
  <div id="vlinks"></div>
  <div id="alinks"></div>
</div>

<footer><div class="fb">Sam <span>Houston</span> Downloader</div><div class="fs">دانلود رایگان و بدون محدودیت</div></footer>
</div>

<script>
let plat = 'instagram';
function setP(p,el){
  plat=p;
  document.querySelectorAll('.pb').forEach(b=>b.classList.remove('on'));
  el.classList.add('on');
}
function load(txt){
  document.getElementById('lcard').style.display='block';
  document.getElementById('ltxt').textContent=txt||'در حال دریافت...';
  document.getElementById('rcard').style.display='none';
  document.getElementById('ecard').style.display='none';
}
function err(msg){
  document.getElementById('lcard').style.display='none';
  document.getElementById('ecard').textContent='⚠️ '+msg;
  document.getElementById('ecard').style.display='block';
  document.getElementById('btn').disabled=false;
}
function makeBtn(link){
  const a=document.createElement('a');
  const cls=link.t==='a'?'abtn':link.t==='p'?'pbtn':'vbtn';
  const bc=link.t==='a'?'ba':link.t==='p'?'bp':'bv';
  a.className='dlb '+cls;
  a.href=link.url;
  a.target='_blank';
  a.innerHTML=`<div class="dll"><span>${link.icon}</span><span>${link.label}</span><span class="badge ${bc}">${link.ext}</span></div><span class="darr">←</span>`;
  return a;
}
function show(data){
  document.getElementById('lcard').style.display='none';
  // هدر
  const h=document.getElementById('vhead');
  h.innerHTML=data.thumb
    ?`<img class="vthumb" src="${data.thumb}" onerror="this.style.display='none'"><div><div class="vtitle">${data.title||'ویدیو'}</div><div class="vplat">${data.platform||''}</div></div>`
    :`<div><div class="vtitle">${data.title||'ویدیو'}</div><div class="vplat">${data.platform||''}</div></div>`;
  // لینک‌های ویدیو
  const vd=document.getElementById('vlinks');
  const ad=document.getElementById('alinks');
  vd.innerHTML=''; ad.innerHTML='';
  const vlinks=data.links.filter(l=>l.t==='v'||l.t==='p');
  const alinks=data.links.filter(l=>l.t==='a');
  if(vlinks.length){
    const s=document.createElement('div');
    s.className='slabel';
    s.textContent='🎬 ویدیو / تصویر';
    vd.appendChild(s);
    vlinks.forEach(l=>vd.appendChild(makeBtn(l)));
  }
  if(alinks.length){
    const s=document.createElement('div');
    s.className='slabel';
    s.textContent='🎵 صدا';
    ad.appendChild(s);
    alinks.forEach(l=>ad.appendChild(makeBtn(l)));
  }
  document.getElementById('rcard').style.display='block';
  document.getElementById('btn').disabled=false;
}
async function go(){
  const url=document.getElementById('url').value.trim();
  if(!url){err('لطفاً لینک را وارد کنید');return;}
  document.getElementById('btn').disabled=true;
  document.getElementById('ecard').style.display='none';
  load('در حال دریافت اطلاعات...');
  try{
    const r=await fetch('/api/get',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({url,platform:plat})
    });
    const d=await r.json();
    if(d.error){err(d.error);return;}
    show(d);
  }catch(e){err('خطا: '+e.message);}
}
document.getElementById('url').addEventListener('keydown',e=>{if(e.key==='Enter')go();});
</script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/get', methods=['POST'])
def get_links():
    import subprocess, json, re

    data = request.get_json()
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'لینک وارد نشده'})

    # اجرای yt-dlp برای گرفتن همه فرمت‌ها
    cmd = [
        'yt-dlp',
        '--no-check-certificates',
        '--no-playlist',
        '-j',
        '--extractor-args', 'twitter:api=legacy',
        url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
        if result.returncode != 0:
            # retry بدون extractor-args
            cmd2 = ['yt-dlp', '--no-check-certificates', '--no-playlist', '-j', url]
            result = subprocess.run(cmd2, capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
            if result.returncode != 0:
                return jsonify({'error': result.stderr[-300:] if result.stderr else 'خطا در دریافت اطلاعات'})

        # parse - ممکنه چند خط JSON باشه
        lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
        if not lines:
            return jsonify({'error': 'اطلاعات دریافت نشد'})
        info = json.loads(lines[0])

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'زمان پردازش تمام شد'})
    except Exception as e:
        return jsonify({'error': str(e)})

    title = info.get('title', '')
    platform = info.get('extractor_key', '')
    thumb = info.get('thumbnail', '')
    formats = info.get('formats', [])

    links = []

    # --- ویدیوها ---
    vfmts = [f for f in formats if f.get('vcodec','none') != 'none' and f.get('url')]
    # مرتب‌سازی از بالاترین کیفیت
    vfmts.sort(key=lambda f: (f.get('height') or 0) * (f.get('tbr') or 1), reverse=True)
    seen_h = set()
    for f in vfmts:
        h = f.get('height')
        key = h or f.get('format_id','')
        if key in seen_h:
            continue
        seen_h.add(key)
        ext = f.get('ext', 'mp4')
        label_h = f"{h}p" if h else f.get('format_note', 'ویدیو')
        fn = uq((title or 'video') + '.' + ext)
        links.append({
            'url': '/dl?u=' + uq(f['url']) + '&f=' + fn + '&r=' + uq(url),
            'label': f'ویدیو — {label_h}',
            'ext': ext.upper(),
            'icon': '🎬',
            't': 'v'
        })
        if len(seen_h) >= 4:
            break

    # --- صداها ---
    afmts = [f for f in formats if f.get('vcodec','none') == 'none' and f.get('acodec','none') != 'none' and f.get('url')]
    afmts.sort(key=lambda f: f.get('abr') or 0, reverse=True)
    seen_a = set()
    for f in afmts[:3]:
        ext = f.get('ext', 'mp3')
        abr = f.get('abr', 0)
        key = f"{ext}_{int(abr or 0)}"
        if key in seen_a:
            continue
        seen_a.add(key)
        label = f"صدا — {int(abr)}kbps" if abr else 'صدا'
        fn = uq((title or 'audio') + '.' + ext)
        links.append({
            'url': '/dl?u=' + uq(f['url']) + '&f=' + fn + '&r=' + uq(url),
            'label': label,
            'ext': ext.upper(),
            'icon': '🎵',
            't': 'a'
        })

    # اگه format جداگانه نبود، از url مستقیم استفاده کن
    if not links and info.get('url'):
        ext = info.get('ext', 'mp4')
        fn = uq((title or 'video') + '.' + ext)
        links.append({
            'url': '/dl?u=' + uq(info['url']) + '&f=' + fn + '&r=' + uq(url),
            'label': 'دانلود ویدیو',
            'ext': ext.upper(),
            'icon': '🎬',
            't': 'v'
        })

    if not links:
        return jsonify({'error': 'هیچ فرمت قابل دانلودی پیدا نشد'})

    return jsonify({
        'title': title,
        'platform': platform,
        'thumb': thumb,
        'links': links
    })


@app.route('/dl')
def download():
    """Proxy دانلود با header درست"""
    file_url = uuq(request.args.get('u', ''))
    filename = uuq(request.args.get('f', 'download'))
    referer_url = uuq(request.args.get('r', ''))

    if not file_url:
        return 'URL missing', 400

    # تنظیم header بر اساس پلتفرم
    if any(x in file_url for x in ['twimg.com', 'video.twimg', 'twvid']):
        ref = 'https://twitter.com/'
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    elif any(x in file_url for x in ['tiktok', 'tiktokcdn', 'muscdn', 'tiktokv']):
        ref = 'https://www.tiktok.com/'
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    elif any(x in file_url for x in ['cdninstagram', 'fbcdn', 'instagram']):
        ref = 'https://www.instagram.com/'
        ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
    else:
        ref = referer_url or 'https://www.google.com/'
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

    headers = {
        'User-Agent': ua,
        'Referer': ref,
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    try:
        r = req_lib.get(file_url, headers=headers, stream=True, timeout=90, allow_redirects=True)

        if r.status_code in (403, 401):
            # retry بدون Referer
            del headers['Referer']
            r = req_lib.get(file_url, headers=headers, stream=True, timeout=90, allow_redirects=True)

        ct = r.headers.get('Content-Type', 'application/octet-stream')
        # اگه content-type عکس یا ویدیو نبود، force کن
        if 'html' in ct or 'text' in ct:
            if filename.endswith('.mp4') or filename.endswith('.ts'):
                ct = 'video/mp4'
            elif filename.endswith('.mp3') or filename.endswith('.m4a'):
                ct = 'audio/mpeg'

        def gen():
            for chunk in r.iter_content(chunk_size=65536):
                if chunk:
                    yield chunk

        resp = Response(gen(), content_type=ct)
        resp.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        if r.headers.get('Content-Length'):
            resp.headers['Content-Length'] = r.headers['Content-Length']
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except Exception as e:
        return str(e), 500


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
