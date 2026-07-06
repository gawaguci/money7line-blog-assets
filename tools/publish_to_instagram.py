#!/usr/bin/env python3
"""Publish the generated card-news carousels to Instagram via the Meta Graph API.

NOTE: This script must be run from an environment that can reach
graph.facebook.com. The Claude Code web environment blocks it by network
policy, so it was NOT run there — run this on your own machine.

Prerequisites
-------------
1. An Instagram *Business* or *Creator* account connected to a Facebook Page.
2. A Meta app with a long-lived access token that has:
     instagram_basic, instagram_content_publish, pages_read_engagement
3. The card PNGs must be reachable at PUBLIC https URLs. After you push this
   repo, they live at raw.githubusercontent.com (see RAW_BASE below).

Usage
-----
    export IG_USER_ID="17841400000000000"          # IG business account id
    export IG_ACCESS_TOKEN="EAAG...."               # long-lived token
    # optional: point at the branch/commit that actually contains the images
    export RAW_BASE="https://raw.githubusercontent.com/gawaguci/money7line-blog-assets/main"

    python3 tools/publish_to_instagram.py            # publish all 15
    python3 tools/publish_to_instagram.py --only 1 3 # publish posts #1 and #3
    python3 tools/publish_to_instagram.py --dry-run  # print URLs, do not post

The Instagram API forbids clickable links in captions, so captions point
readers to the profile link. Update your IG bio link to money7line.blogspot.com.
"""
import os, sys, json, time, urllib.request, urllib.parse, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATE_DIR = "20260705"
GRAPH = "https://graph.facebook.com/v21.0"
RAW_BASE = os.environ.get(
    "RAW_BASE",
    "https://raw.githubusercontent.com/gawaguci/money7line-blog-assets/main")
DOMAIN = "money7line.blogspot.com"
SLIDES = ["01-cover.png", "02-point1.png", "03-point2.png", "04-point3.png"]


def api(path, params, method="POST"):
    url = f"{GRAPH}/{path}"
    data = urllib.parse.urlencode(params).encode()
    if method == "GET":
        url = f"{url}?{data.decode()}"; data = None
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Graph API error {e.code}: {e.read().decode()}")


def caption_for(post):
    pts = " / ".join(p["h"] for p in post["points"])
    return (f"[{post['category']}] {post['title']}\n\n{post['subtitle']}\n\n"
            f"핵심 3가지 → {pts}\n\n"
            f"전문은 블로그에서 확인하세요 (프로필 링크)\n{DOMAIN}\n\n"
            f"#머니세븐라인 #경제뉴스 #카드뉴스 #재테크 #경제상식 "
            f"#{post['slug'].split('-20260705')[0].replace('-','_')}")


def publish_carousel(ig_id, token, folder, caption, dry=False):
    base = f"{RAW_BASE}/instagram-cards/{DATE_DIR}/{folder}"
    urls = [f"{base}/{s}" for s in SLIDES]
    if dry:
        print("  caption:", caption.split(chr(10))[0])
        for u in urls: print("   ", u)
        return None
    children = []
    for u in urls:
        res = api(f"{ig_id}/media", {
            "image_url": u, "is_carousel_item": "true", "access_token": token})
        children.append(res["id"]); time.sleep(1)
    carousel = api(f"{ig_id}/media", {
        "media_type": "CAROUSEL", "children": ",".join(children),
        "caption": caption, "access_token": token})
    time.sleep(3)  # allow container to finish processing
    pub = api(f"{ig_id}/media_publish", {
        "creation_id": carousel["id"], "access_token": token})
    return pub.get("id")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", type=int, help="1-based post numbers")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ig_id = os.environ.get("IG_USER_ID")
    token = os.environ.get("IG_ACCESS_TOKEN")
    if not args.dry_run and not (ig_id and token):
        raise SystemExit("Set IG_USER_ID and IG_ACCESS_TOKEN env vars first.")

    data = json.load(open(os.path.join(ROOT, "tools", "card_content.json"),
                          encoding="utf-8"))
    for n, post in enumerate(data["posts"], start=1):
        if args.only and n not in args.only:
            continue
        folder = f"{n:02d}-{post['slug']}"
        print(f"[{n:02d}/15] {post['title']}")
        mid = publish_carousel(ig_id, token, folder, caption_for(post),
                               dry=args.dry_run)
        if mid:
            print(f"  published media id: {mid}")
        if not args.dry_run:
            time.sleep(5)  # gentle pacing between posts
    print("done.")


if __name__ == "__main__":
    main()
