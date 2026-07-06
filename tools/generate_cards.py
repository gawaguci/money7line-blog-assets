#!/usr/bin/env python3
"""Generate clean, Claude-style Instagram card-news images from blog post metadata.

Reads card_content.json, renders each slide as a 1080x1350 PNG using headless
Chromium, and writes an Instagram caption file per date batch.
"""
import json, os, subprocess, html, sys, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
BUILD = os.path.join(TOOLS, "_build")
DATE_DIR_NAME = "20260705"
OUT_DIR = os.path.join(ROOT, "instagram-cards", DATE_DIR_NAME)
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

data = json.load(open(os.path.join(TOOLS, "card_content.json"), encoding="utf-8"))
BRAND = data["brand"]; DATE = data["date_label"]; DOMAIN = data["domain"]

CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
:root{
  --cream:#F0EEE6; --paper:#FAF9F6; --ink:#1A1915; --sub:#73706A;
  --coral:#CC785C; --coral-deep:#B5613F; --line:#E2DECF;
}
html,body{ width:1080px; height:1350px; }
.slide{
  width:1080px; height:1350px; background:var(--cream);
  font-family:'Pretendard', sans-serif; color:var(--ink);
  position:relative; overflow:hidden;
  padding:84px 84px 106px 84px; display:flex; flex-direction:column;
}
.edge{ position:absolute; left:0; top:0; bottom:0; width:12px; background:var(--coral); }
.header{ display:flex; align-items:center; justify-content:space-between; }
.brand{ display:flex; align-items:center; gap:14px; font-weight:700; font-size:30px; letter-spacing:-.5px; }
.brand .dot{ width:16px; height:16px; border-radius:50%; background:var(--coral); display:inline-block; }
.brand .slash{ color:var(--coral); font-weight:800; }
.date{ font-size:24px; color:var(--sub); font-weight:500; letter-spacing:.5px; }

/* cover */
.cover .cat{ display:inline-flex; align-self:flex-start; margin-top:86px;
  background:rgba(204,120,92,.12); color:var(--coral-deep); font-weight:700;
  font-size:26px; padding:14px 26px; border-radius:100px; letter-spacing:.5px; }
.cover .bar{ width:96px; height:10px; background:var(--coral); border-radius:8px; margin:44px 0 34px; }
.cover .title{ font-weight:800; font-size:82px; line-height:1.2; letter-spacing:-1.5px; }
.cover .subtitle{ margin-top:34px; font-size:36px; line-height:1.5; color:var(--sub); font-weight:500; }
.cover .spacer{ flex:1; }
.cover .swipe{ display:flex; align-items:center; gap:16px; font-size:28px; color:var(--coral-deep); font-weight:700; }
.cover .swipe .arrow{ font-size:34px; }

/* point */
.point .ghost{ position:absolute; right:40px; top:150px; font-size:440px; font-weight:800;
  color:rgba(204,120,92,.08); line-height:1; letter-spacing:-10px; }
.point .idx{ margin-top:96px; display:flex; align-items:center; gap:26px; }
.point .idx .badge{ width:96px; height:96px; border-radius:24px; background:var(--coral);
  color:#fff; font-weight:800; font-size:46px; display:flex; align-items:center; justify-content:center; }
.point .idx .of{ font-size:28px; color:var(--sub); font-weight:600; letter-spacing:1px; }
.point .h{ margin-top:52px; font-weight:800; font-size:62px; line-height:1.28; letter-spacing:-1px; }
.point .rule{ width:72px; height:8px; background:var(--coral); border-radius:6px; margin:40px 0 40px; }
.point .lines{ display:flex; flex-direction:column; gap:26px; }
.point .lines .l{ position:relative; padding-left:40px; font-size:36px; line-height:1.55; color:#3B3934; font-weight:500; }
.point .lines .l::before{ content:''; position:absolute; left:0; top:18px; width:18px; height:18px;
  border-radius:50%; border:5px solid var(--coral); }
.point .spacer{ flex:1; }

/* footer */
.footer{ display:flex; align-items:center; justify-content:space-between;
  border-top:2px solid var(--line); padding-top:30px; font-size:24px; color:var(--sub); font-weight:500; }
.footer .dom{ font-weight:600; color:#4A4843; }
.dots{ display:flex; gap:12px; align-items:center; }
.dots i{ width:14px; height:14px; border-radius:50%; background:var(--line); display:inline-block; }
.dots i.on{ background:var(--coral); width:34px; border-radius:8px; }
"""

def esc(s): return html.escape(s)

def dots(active, total):
    return '<div class="dots">' + ''.join(
        f'<i class="{"on" if i==active else ""}"></i>' for i in range(total)) + '</div>'

def brand_html():
    return (f'<div class="brand"><span class="dot"></span>money'
            f'<span class="slash">7</span>line</div>')

def cover_html(post, total):
    return f"""<div class="slide cover"><div class="edge"></div>
  <div class="header">{brand_html()}<div class="date">{DATE}</div></div>
  <div class="cat">{esc(post['category'])}</div>
  <div class="bar"></div>
  <div class="title">{esc(post['title'])}</div>
  <div class="subtitle">{esc(post['subtitle'])}</div>
  <div class="spacer"></div>
  <div class="swipe"><span>넘겨서 핵심 정리 보기</span><span class="arrow">→</span></div>
  <div class="footer"><span class="dom">{DOMAIN}</span>{dots(0,total)}</div>
</div>"""

def point_html(post, i, total):
    p = post["points"][i]
    num = f"{i+1:02d}"
    lines = ''.join(f'<div class="l">{esc(l)}</div>' for l in p["lines"])
    return f"""<div class="slide point"><div class="edge"></div>
  <div class="ghost">{num}</div>
  <div class="header">{brand_html()}<div class="date">{esc(post['category'])}</div></div>
  <div class="idx"><div class="badge">{num}</div><div class="of">POINT {i+1} / 3</div></div>
  <div class="h">{esc(p['h'])}</div>
  <div class="rule"></div>
  <div class="lines">{lines}</div>
  <div class="spacer"></div>
  <div class="footer"><span class="dom">{DOMAIN}</span>{dots(i+1,total)}</div>
</div>"""

def page(inner):
    return (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<style>{CSS}</style></head><body>{inner}</body></html>")

def render(html_path, png_path):
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--hide-scrollbars",
        "--force-device-scale-factor=1", "--default-background-color=00000000",
        "--window-size=1080,1350", f"--screenshot={png_path}", f"file://{html_path}"],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    if os.path.isdir(BUILD): shutil.rmtree(BUILD)
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    total = 4
    captions = []
    made = 0
    for n, post in enumerate(data["posts"], start=1):
        folder = f"{n:02d}-{post['slug']}"
        pdir = os.path.join(OUT_DIR, folder)
        os.makedirs(pdir, exist_ok=True)
        slides = [("01-cover", cover_html(post, total))]
        for i in range(3):
            slides.append((f"0{i+2}-point{i+1}", point_html(post, i, total)))
        for name, inner in slides:
            hp = os.path.join(BUILD, f"{folder}-{name}.html")
            open(hp, "w", encoding="utf-8").write(page(inner))
            render(hp, os.path.join(pdir, f"{name}.png"))
            made += 1
        # caption
        pts = " / ".join(p["h"] for p in post["points"])
        cap = (f"[{post['category']}] {post['title']}\n\n{post['subtitle']}\n\n"
               f"핵심 3가지 → {pts}\n\n"
               f"전문은 블로그에서 확인하세요 (프로필 링크)\n{DOMAIN}\n\n"
               f"#머니세븐라인 #경제뉴스 #카드뉴스 #재테크 #경제상식 "
               f"#{post['slug'].split('-20260705')[0].replace('-','_')}")
        captions.append(f"### {n:02d}. {post['title']}\n\n```\n{cap}\n```\n")
    open(os.path.join(OUT_DIR, "captions.md"), "w", encoding="utf-8").write(
        f"# Instagram 카드뉴스 캡션 — {DATE}\n\n" + "\n".join(captions))
    print(f"Rendered {made} PNGs across {len(data['posts'])} posts into {OUT_DIR}")

if __name__ == "__main__":
    main()
