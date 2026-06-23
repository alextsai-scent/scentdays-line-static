#!/usr/bin/env python3
"""Build qa.html (curated TOP 10 with YouTube Shorts) and wallpapers.html"""
import yaml, json, os, glob, re
from html import escape

BASE = os.path.dirname(os.path.abspath(__file__))
FAQ_DIR = os.path.join(os.path.dirname(BASE), 'faq')

# Load TOP 10 curated order
with open(os.path.join(BASE, 'top10_ids.json')) as f:
    TOP_10_IDS = json.load(f)

# Load all FAQs and index by id
all_faqs = {}
for path in sorted(glob.glob(f'{FAQ_DIR}/*.yml')):
    with open(path) as f:
        items = yaml.safe_load(f)
    if not items: continue
    for item in items:
        all_faqs[item.get('id')] = item

# Build ordered list of TOP 10
ordered = [all_faqs[fid] for fid in TOP_10_IDS if fid in all_faqs]

def linkify(text):
    """Convert URLs in text to clickable links (escape rest)"""
    parts = re.split(r'(https?://\S+)', text)
    out = []
    for p in parts:
        if p.startswith('http'):
            out.append(f'<a href="{escape(p)}" target="_blank" rel="noopener">{escape(p)}</a>')
        else:
            out.append(escape(p))
    return ''.join(out)

def yt_thumbnail(url):
    """Extract YouTube video ID and return thumbnail URL"""
    m = re.search(r'shorts/([\w-]+)', url)
    if m:
        return f'https://img.youtube.com/vi/{m.group(1)}/hqdefault.jpg'
    return ''

# Build qa.html
qa_html = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Scentdays よくあるご質問 (Q&A)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=Noto+Serif+JP:wght@400;500&display=swap" rel="stylesheet">
<style>
* { box-sizing:border-box; margin:0; padding:0; }
body {
    font-family: 'Noto Sans JP', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(180deg, #f6f1e8 0%, #ede4d3 100%);
    color: #3a342d;
    line-height: 1.75;
    -webkit-tap-highlight-color: transparent;
    min-height: 100vh;
}
.header {
    background: linear-gradient(135deg, #c9b496 0%, #b89a78 100%);
    color: #fff;
    padding: 40px 24px 32px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.header h1 {
    font-family: 'Noto Serif JP', serif;
    font-weight: 500;
    font-size: 22px;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
}
.header .sub {
    font-size: 13px;
    opacity: 0.92;
    letter-spacing: 0.06em;
}
.container { max-width: 680px; margin: 0 auto; padding: 24px 16px 80px; }
.intro {
    text-align: center;
    font-size: 13px;
    color: #7a6f60;
    margin-bottom: 24px;
    padding: 0 16px;
    line-height: 1.8;
}
.faq-item {
    margin-bottom: 12px;
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(120,90,60,0.08);
    transition: box-shadow 0.2s;
}
.faq-item.open {
    box-shadow: 0 4px 20px rgba(120,90,60,0.14);
}
.faq-question {
    padding: 18px 22px;
    font-size: 15px;
    font-weight: 500;
    color: #3a342d;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    transition: background 0.2s;
    user-select: none;
}
.faq-question:active { background: #faf5ec; }
.faq-question::after {
    content: '+';
    font-size: 24px;
    color: #b89a78;
    font-weight: 300;
    transition: transform 0.25s;
    line-height: 1;
    flex-shrink: 0;
}
.faq-item.open .faq-question::after {
    transform: rotate(45deg);
}
.faq-q-num {
    font-family: 'Noto Serif JP', serif;
    color: #b89a78;
    font-size: 12px;
    font-weight: 400;
    margin-right: 2px;
    letter-spacing: 0.05em;
}
.faq-answer {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.4s ease-out;
    background: linear-gradient(180deg, #faf6ee 0%, #f6f0e2 100%);
}
.faq-item.open .faq-answer { max-height: 4000px; }
.faq-answer-inner { padding: 16px 22px 22px; }
.faq-answer p {
    font-size: 14px;
    color: #5a5247;
    white-space: pre-wrap;
    word-break: break-word;
    line-height: 1.85;
}
.faq-answer a {
    color: #b8915a;
    text-decoration: underline;
    word-break: break-all;
}

/* YouTube Shorts gallery */
.shorts-section {
    margin-top: 18px;
    padding-top: 16px;
    border-top: 1px solid #e6dcc8;
}
.shorts-label {
    font-family: 'Noto Serif JP', serif;
    font-size: 12px;
    color: #8c7252;
    letter-spacing: 0.1em;
    margin-bottom: 10px;
}
.shorts-grid {
    display: flex;
    gap: 10px;
    overflow-x: auto;
    padding-bottom: 4px;
    -webkit-overflow-scrolling: touch;
}
.shorts-grid::-webkit-scrollbar { height: 4px; }
.shorts-grid::-webkit-scrollbar-thumb { background: #d4c4a8; border-radius:2px; }
.short-card {
    flex: 0 0 140px;
    background: #fff;
    border-radius: 10px;
    overflow: hidden;
    text-decoration: none;
    color: inherit;
    box-shadow: 0 2px 6px rgba(120,90,60,0.1);
    transition: transform 0.15s;
}
.short-card:active { transform: scale(0.97); }
.short-thumb {
    position: relative;
    width: 100%;
    aspect-ratio: 9/16;
    background: #d4c4a8 center/cover no-repeat;
    background-size: cover;
}
.short-thumb::before {
    content: '';
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,0.18);
}
.short-thumb::after {
    content: '▶';
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 38px; height: 38px;
    background: rgba(255,255,255,0.92);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #b89a78;
    font-size: 12px;
    padding-left: 3px;
}
.short-label {
    padding: 8px 10px 10px;
    font-size: 11px;
    color: #3a342d;
    line-height: 1.45;
    font-weight: 500;
}
.footer {
    text-align: center;
    color: #998771;
    font-size: 12px;
    padding: 32px 16px;
    letter-spacing: 0.05em;
}
.footer .brand {
    font-family: 'Noto Serif JP', serif;
    font-size: 16px;
    color: #8c7252;
    margin-bottom: 8px;
    letter-spacing: 0.2em;
}
</style>
</head>
<body>
<div class="header">
    <h1>よくあるご質問</h1>
    <div class="sub">Frequently Asked Questions</div>
</div>
<div class="container">
<div class="intro">お客さまから多くお寄せいただくご質問。<br>気になる項目をタップして、ご確認ください。</div>
"""

for idx, f in enumerate(ordered, 1):
    title = f.get('title') or '質問'
    answer = f.get('answer', '').strip()
    shorts = f.get('shorts', []) or []
    answer_html = linkify(answer)

    qa_html += f'<div class="faq-item">\n'
    qa_html += f'  <div class="faq-question" onclick="this.parentElement.classList.toggle(\'open\')">'
    qa_html += f'<span><span class="faq-q-num">Q{idx:02d}</span>　{escape(title)}</span></div>\n'
    qa_html += '  <div class="faq-answer"><div class="faq-answer-inner">\n'
    qa_html += f'    <p>{answer_html}</p>\n'

    if shorts:
        qa_html += '    <div class="shorts-section">\n'
        qa_html += '      <div class="shorts-label">▶ 関連動画（タップで再生）</div>\n'
        qa_html += '      <div class="shorts-grid">\n'
        for s in shorts:
            thumb = yt_thumbnail(s['url'])
            qa_html += f'        <a class="short-card" href="{escape(s["url"])}" target="_blank" rel="noopener">\n'
            qa_html += f'          <div class="short-thumb" style="background-image:url(\'{thumb}\');"></div>\n'
            qa_html += f'          <div class="short-label">{escape(s["label"])}</div>\n'
            qa_html += '        </a>\n'
        qa_html += '      </div>\n'
        qa_html += '    </div>\n'

    qa_html += '  </div></div>\n'
    qa_html += '</div>\n'

qa_html += """</div>
<div class="footer">
    <div class="brand">Scentdays</div>
    <div>香りで彩る、新しい毎日。</div>
</div>
</body>
</html>
"""

with open(os.path.join(BASE, 'qa.html'), 'w') as f:
    f.write(qa_html)
print(f'✓ qa.html: {len(ordered)} FAQs')

# Wallpapers page (unchanged from previous)
wp_files = sorted(os.listdir(os.path.join(BASE, 'wallpapers')))
wp_html = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Scentdays 壁紙ダウンロード</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500&family=Noto+Serif+JP:wght@500&display=swap" rel="stylesheet">
<style>
* { box-sizing:border-box; margin:0; padding:0; }
body {
    font-family: 'Noto Sans JP', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(180deg, #f6f1e8 0%, #ede4d3 100%);
    color: #3a342d;
    min-height: 100vh;
    padding-bottom: 40px;
}
.header {
    background: linear-gradient(135deg, #c9b496 0%, #b89a78 100%);
    color: #fff;
    padding: 40px 24px 32px;
    text-align: center;
}
.header h1 {
    font-family: 'Noto Serif JP', serif;
    font-weight: 500;
    font-size: 22px;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
}
.header .sub { font-size: 13px; opacity: 0.92; letter-spacing: 0.06em; }
.intro {
    text-align: center;
    padding: 20px 24px 8px;
    color: #5a5247;
    font-size: 14px;
    line-height: 1.8;
}
.howto {
    max-width: 700px;
    margin: 16px auto 0;
    padding: 16px 24px;
    background: linear-gradient(135deg, #faf5ec 0%, #f3ecdf 100%);
    border-left: 4px solid #c9a672;
    border-radius: 8px;
    font-size: 13px;
    color: #6b5d4d;
    line-height: 1.85;
}
.howto strong { color: #8c7252; }
.howto-title {
    font-family: 'Noto Serif JP', serif;
    font-size: 14px;
    color: #8c7252;
    margin-bottom: 8px;
    letter-spacing: 0.05em;
}
.step-num {
    display: inline-block;
    width: 22px;
    height: 22px;
    background: #c9a672;
    color: #fff;
    border-radius: 50%;
    font-size: 12px;
    line-height: 22px;
    text-align: center;
    font-weight: 500;
    margin-right: 6px;
}
.gallery {
    max-width: 700px;
    margin: 0 auto;
    padding: 16px;
    display: grid;
    gap: 20px;
}
.wallpaper {
    background: #fff;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(120,90,60,0.12);
}
.wallpaper img { width: 100%; height: auto; display: block; -webkit-touch-callout: default; }
.wallpaper-actions {
    padding: 14px 20px 16px;
    text-align: center;
}
.wallpaper-title { font-size: 14px; color: #8c7252; font-weight: 500; margin-bottom: 6px; letter-spacing: 0.05em; }
.save-hint {
    font-size: 12px;
    color: #998771;
    line-height: 1.6;
}
.save-hint .icon {
    display: inline-block;
    width: 16px;
    height: 16px;
    background: #c9a672;
    color: #fff;
    border-radius: 50%;
    font-size: 10px;
    line-height: 16px;
    text-align: center;
    margin-right: 4px;
    vertical-align: -2px;
}
.help {
    text-align: center;
    padding: 0 24px 16px;
    font-size: 12px;
    color: #998771;
    line-height: 1.7;
}
.footer {
    text-align: center;
    color: #998771;
    font-size: 12px;
    padding: 24px 16px 8px;
    letter-spacing: 0.05em;
}
.footer .brand {
    font-family: 'Noto Serif JP', serif;
    font-size: 16px;
    color: #8c7252;
    margin-bottom: 8px;
    letter-spacing: 0.2em;
}
</style>
</head>
<body>
<div class="header">
    <h1>壁紙ダウンロード</h1>
    <div class="sub">Wallpaper Collection</div>
</div>
<div class="intro">
    季節に合わせた壁紙をご用意しております。
</div>
<div class="howto">
    <div class="howto-title">📱 携帯の写真に保存する方法</div>
    <span class="step-num">1</span>お好きな壁紙の画像を<strong>長押し</strong><br>
    <span class="step-num">2</span>表示されるメニューから<br>
    　　iPhone：<strong>「"写真"に追加」</strong><br>
    　　Android：<strong>「画像をダウンロード」</strong><br>
    　　を選択<br>
    <span class="step-num">3</span>携帯の写真アプリに保存されます
</div>
<div class="gallery">
"""
wallpaper_labels = {
    'Ajisai_002.png': '初夏 ・ 紫陽花',
    'Ajisai_004.png': '初夏 ・ 紫陽花の小径',
    'Island_Heart_6_7_002B.png': '夏 ・ 想いの島',
    'Windsurfing_6_7_003B.png': '夏 ・ 風と海',
    'Sunset_6_7_004B.png': '夏 ・ 夕暮れの海',
}
for fn in wp_files:
    label = wallpaper_labels.get(fn, fn.rsplit('.',1)[0])
    wp_html += f'''<div class="wallpaper">
    <img src="wallpapers/{fn}" alt="{escape(label)}" loading="lazy">
    <div class="wallpaper-actions">
        <div class="wallpaper-title">{escape(label)}</div>
        <div class="save-hint"><span class="icon">↓</span>画像を長押しして写真に保存</div>
    </div>
</div>
'''
wp_html += """</div>
<div class="help">
    順次新しいデザインを追加してまいります。
</div>
<div class="footer">
    <div class="brand">Scentdays</div>
    <div>香りで彩る、新しい毎日。</div>
</div>
</body>
</html>
"""
with open(os.path.join(BASE, 'wallpapers.html'), 'w') as f:
    f.write(wp_html)
print(f'✓ wallpapers.html: {len(wp_files)} wallpapers')

with open(os.path.join(BASE, 'index.html'), 'w') as f:
    f.write("""<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0;url=qa.html"></head><body></body></html>""")
print('✓ index.html')
