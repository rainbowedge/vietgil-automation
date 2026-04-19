#!/usr/bin/env python3
"""
Vietgil WordPress Auto-Uploader
사용법: python upload_to_wp.py posts/파일명.md
"""

import sys
import os
import requests
import frontmatter
import markdown
from base64 import b64encode
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.vietgil.env"))

WP_URL = os.getenv("WP_URL", "").rstrip("/")
WP_USER = os.getenv("WP_USER", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")


# ─────────────────────────────────────────
# 인증
# ─────────────────────────────────────────

def get_headers():
    credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
    token = b64encode(credentials.encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    }


def check_credentials():
    if not WP_URL or not WP_USER or not WP_APP_PASSWORD:
        print("❌ .env 파일을 확인하세요: WP_URL, WP_USER, WP_APP_PASSWORD 필요")
        sys.exit(1)

    headers = get_headers()
    headers.pop("Content-Type", None)  # GET 요청에는 불필요

    r = requests.get(f"{WP_URL}/wp-json/wp/v2/users/me", headers=headers)
    if r.status_code == 200:
        user = r.json()
        print(f"✅ 연결 성공: {user.get('name', WP_USER)} ({WP_URL})")
    else:
        print(f"❌ WordPress 인증 실패 (HTTP {r.status_code})")
        print("   Application Password 확인: WordPress 관리자 → 사용자 → 프로필")
        sys.exit(1)


# ─────────────────────────────────────────
# 카테고리 / 태그
# ─────────────────────────────────────────

def get_or_create_taxonomy(name, taxonomy, headers):
    """카테고리 또는 태그를 이름으로 검색하고, 없으면 생성합니다."""
    endpoint = f"{WP_URL}/wp-json/wp/v2/{taxonomy}"
    auth_headers = {k: v for k, v in headers.items() if k != "Content-Type"}

    r = requests.get(endpoint, params={"search": name, "per_page": 20}, headers=auth_headers)
    for item in r.json():
        if item["name"] == name:
            return item["id"]

    # 없으면 생성
    r = requests.post(endpoint, json={"name": name}, headers=headers)
    result = r.json()
    if "id" in result:
        label = "카테고리" if taxonomy == "categories" else "태그"
        print(f"   + 새 {label} 생성: {name} (ID: {result['id']})")
        return result["id"]

    print(f"   ⚠️  {name} 생성 실패: {result.get('message', str(result))}")
    return None


# ─────────────────────────────────────────
# 메인 업로드
# ─────────────────────────────────────────

def upload_post(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {filepath}")
        sys.exit(1)

    check_credentials()
    headers = get_headers()

    # ── 파일 파싱 ──
    post = frontmatter.load(str(path))
    title = post.get("title", path.stem)
    print(f"\n📄 {title}")
    print(f"   파일: {path.name}")

    # ── 마크다운 → HTML ──
    md = markdown.Markdown(extensions=["extra", "nl2br", "sane_lists"])
    content_html = md.convert(post.content)

    # ── 카테고리 ──
    category_ids = []
    for name in post.get("categories", []):
        cid = get_or_create_taxonomy(name, "categories", headers)
        if cid:
            category_ids.append(cid)
    if category_ids:
        print(f"   📁 카테고리 {len(category_ids)}개")

    # ── 태그 ──
    tag_ids = []
    for name in post.get("tags", []):
        tid = get_or_create_taxonomy(name, "tags", headers)
        if tid:
            tag_ids.append(tid)
    if tag_ids:
        print(f"   🏷️  태그 {len(tag_ids)}개")

    # ── 페이로드 ──
    payload = {
        "title": title,
        "slug": post.get("slug", path.stem),
        "content": content_html,
        "excerpt": post.get("excerpt", ""),
        "status": "draft",  # 항상 초안 — 발행은 수동으로
        "categories": category_ids,
        "tags": tag_ids,
        "meta": {
            "rank_math_focus_keyword": post.get("focus_keyword", ""),
            "rank_math_description": post.get("meta_description", ""),
            "rank_math_title": post.get("meta_title", ""),
        },
    }

    # ── 업로드 ──
    print("\n🚀 WordPress에 업로드 중...")
    r = requests.post(f"{WP_URL}/wp-json/wp/v2/posts", json=payload, headers=headers)

    if r.status_code == 201:
        data = r.json()
        post_id = data["id"]
        print(f"\n✅ 업로드 완료!")
        print(f"   상태: 초안 (draft)")
        print(f"   슬러그: /{data['slug']}/")
        print(f"\n🔗 지금 편집하기:")
        print(f"   {WP_URL}/wp-admin/post.php?post={post_id}&action=edit")
        print(f"\n📋 발행 전 체크리스트:")
        print(f"   □ 대표 이미지 업로드 (1200×675)")
        print(f"   □ 본문 이미지 업로드 및 삽입")
        print(f"   □ Rank Math SEO 점수 확인 (80점 이상)")
        print(f"   □ 미리보기로 모바일 확인")
        print(f"   □ 발행")
    else:
        print(f"\n❌ 업로드 실패 (HTTP {r.status_code})")
        try:
            err = r.json()
            print(f"   오류: {err.get('message', str(err))}")
            if "meta" in str(err):
                print("\n   💡 Rank Math 메타 필드 오류인 경우:")
                print("   WordPress 관리자 → Rank Math → 일반 설정 → REST API 활성화 확인")
        except Exception:
            print(f"   응답: {r.text[:300]}")
        sys.exit(1)


# ─────────────────────────────────────────
# 엔트리포인트
# ─────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--check":
        check_credentials()
    elif len(sys.argv) == 2:
        upload_post(sys.argv[1])
    else:
        print("사용법:")
        print("  python upload_to_wp.py posts/파일명.md   # 업로드")
        print("  python upload_to_wp.py --check           # 연결 확인")
        sys.exit(1)
