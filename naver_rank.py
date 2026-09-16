import sys
import subprocess
import os
import time
import random

# requests 없으면 자동 설치
try:
    import requests
except ImportError:
    print("requests 패키지를 설치합니다...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# beautifulsoup4 없으면 자동 설치
try:
    from bs4 import BeautifulSoup
except ImportError:
    print("beautifulsoup4 패키지를 설치합니다...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
    from bs4 import BeautifulSoup

# gspread 없으면 자동 설치
try:
    import gspread
except ImportError:
    print("gspread 패키지를 설치합니다...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gspread"])
    import gspread

from datetime import datetime
from pathlib import Path

TARGET_DOMAIN = "vietgil.com"
ENV_PATH = Path.home() / ".vietgil.env"
RESULTS_PER_PAGE = 10
MAX_RESULTS = 50  # 최대 5페이지

KEYWORDS = [
    "사파 여행",
    "판시판",
    "하롱베이 크루즈",
    "베트남 북부 여행",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.naver.com/",
}


def load_env():
    if not ENV_PATH.exists():
        return
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


def search_naver(keyword):
    """네이버 검색 결과 상위 50개 URL 수집. (URL, 순위) 리스트 반환"""
    results = []
    pages = MAX_RESULTS // RESULTS_PER_PAGE  # 5페이지

    for page in range(pages):
        start = page * RESULTS_PER_PAGE + 1
        url = (
            f"https://search.naver.com/search.naver"
            f"?where=web&query={requests.utils.quote(keyword)}&start={start}"
        )

        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"  ⚠ 요청 실패 (page {page + 1}): {e}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")

        # 네이버 웹 검색 결과 링크 추출
        links = []

        # 일반 검색 결과 (.total_tit a, .link_tit, li.bx a.link_tit 등)
        for selector in [
            "a.link_tit",
            "a.total_tit",
            ".lst_total .bx a[href]",
            ".web-results .g_b_n a[href]",
            "ul.lst_total li a[href]",
        ]:
            for tag in soup.select(selector):
                href = tag.get("href", "")
                if href.startswith("http") and href not in links:
                    links.append(href)

        # 위 셀렉터로 못 찾으면 data-* 속성 시도
        if not links:
            for tag in soup.find_all("a", href=True):
                href = tag["href"]
                if (
                    href.startswith("http")
                    and "naver.com" not in href
                    and "javascript" not in href
                ):
                    links.append(href)

        for link in links:
            rank = len(results) + 1
            results.append((link, rank))
            if len(results) >= MAX_RESULTS:
                break

        if len(results) >= MAX_RESULTS:
            break

        # 페이지 사이 딜레이 (1~2초)
        if page < pages - 1:
            time.sleep(random.uniform(1.0, 2.0))

    return results


def find_rank(results, domain):
    """결과 리스트에서 domain이 포함된 첫 번째 항목 반환"""
    for url, rank in results:
        if domain in url:
            return rank, url
    return None, None


def log_to_sheets(rows):
    """Google Sheets '네이버순위' 시트에 결과 기록"""
    sheets_id = os.environ.get("SHEETS_ID")
    creds_path = os.environ.get("GOOGLE_CREDENTIALS_PATH")

    if not sheets_id or not creds_path:
        print("  ⚠ SHEETS_ID 또는 GOOGLE_CREDENTIALS_PATH가 설정되지 않아 Sheets 기록을 건너뜁니다.")
        return

    if not Path(creds_path).exists():
        print(f"  ⚠ 인증 파일을 찾을 수 없습니다: {creds_path}")
        return

    try:
        gc = gspread.service_account(filename=creds_path)
        sh = gc.open_by_key(sheets_id)

        try:
            ws = sh.worksheet("네이버순위")
        except gspread.exceptions.WorksheetNotFound:
            ws = sh.add_worksheet(title="네이버순위", rows=1000, cols=4)
            ws.append_row(["체크시간", "키워드", "순위", "URL"])

        ws.append_rows(rows)
        print("  📊 Google Sheets 기록 완료")

    except Exception as e:
        print(f"  ⚠ Sheets 기록 실패: {e}")


def run():
    load_env()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{now}] 네이버 검색 순위 확인 — {TARGET_DOMAIN}\n")

    sheet_rows = []

    for i, keyword in enumerate(KEYWORDS):
        results = search_naver(keyword)
        rank, found_url = find_rank(results, TARGET_DOMAIN)

        if rank:
            rank_str = f"{rank}위"
            display_url = found_url
            print(f"  [{keyword}] → {rank_str} ({found_url})")
        else:
            rank_str = "50위 밖"
            display_url = "-"
            print(f"  [{keyword}] → 50위 밖")

        sheet_rows.append([now, keyword, rank_str, display_url])

        # 키워드 사이 딜레이 (1~2초), 마지막은 생략
        if i < len(KEYWORDS) - 1:
            time.sleep(random.uniform(1.0, 2.0))

    print()
    log_to_sheets(sheet_rows)
    print()


if __name__ == "__main__":
    run()
