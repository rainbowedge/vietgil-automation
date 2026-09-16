import sys
import subprocess
import os

# google-auth, google-api-python-client 없으면 자동 설치
try:
    from google.oauth2 import service_account
except ImportError:
    print("google-auth 패키지를 설치합니다...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-auth"])
    from google.oauth2 import service_account

try:
    from googleapiclient.discovery import build
except ImportError:
    print("google-api-python-client 패키지를 설치합니다...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-api-python-client"])
    from googleapiclient.discovery import build

# gspread 없으면 자동 설치
try:
    import gspread
except ImportError:
    print("gspread 패키지를 설치합니다...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gspread"])
    import gspread

from datetime import datetime, timedelta
from pathlib import Path

ENV_PATH = Path.home() / ".vietgil.env"

KEYWORDS = [
    "사파 여행",
    "판시판",
    "하롱베이 크루즈",
    "베트남 북부 여행",
]

GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def load_env():
    if not ENV_PATH.exists():
        return
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


def build_gsc_service(creds_path):
    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=GSC_SCOPES
    )
    return build("webmasters", "v3", credentials=creds, cache_discovery=False)


def fetch_keyword_data(service, site_url, keyword, start_date, end_date):
    """GSC API로 단일 키워드 데이터 조회. 없으면 None 반환."""
    try:
        resp = service.searchanalytics().query(
            siteUrl=site_url,
            body={
                "startDate": start_date,
                "endDate": end_date,
                "dimensions": ["query"],
                "dimensionFilterGroups": [
                    {
                        "filters": [
                            {
                                "dimension": "query",
                                "operator": "equals",
                                "expression": keyword,
                            }
                        ]
                    }
                ],
                "rowLimit": 1,
            },
        ).execute()
    except Exception as e:
        print(f"  ⚠ GSC API 오류 [{keyword}]: {e}")
        return None

    rows = resp.get("rows", [])
    if not rows:
        return None

    row = rows[0]
    return {
        "clicks": int(row.get("clicks", 0)),
        "impressions": int(row.get("impressions", 0)),
        "ctr": round(row.get("ctr", 0.0) * 100, 2),   # % 변환
        "position": round(row.get("position", 0.0), 1),
    }


def log_to_sheets(rows):
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
            ws = sh.worksheet("구글순위")
        except gspread.exceptions.WorksheetNotFound:
            ws = sh.add_worksheet(title="구글순위", rows=1000, cols=6)
            ws.append_row(["체크시간", "키워드", "평균순위", "클릭수", "노출수", "CTR(%)"])

        ws.append_rows(rows)
        print("  📊 Google Sheets 기록 완료")

    except Exception as e:
        print(f"  ⚠ Sheets 기록 실패: {e}")


def run():
    load_env()

    sheets_id = os.environ.get("SHEETS_ID")
    creds_path = os.environ.get("GOOGLE_CREDENTIALS_PATH")
    site_url = os.environ.get("GSC_SITE_URL", "https://vietgil.com/")

    if not creds_path or not Path(creds_path).exists():
        print(f"❌ GOOGLE_CREDENTIALS_PATH가 없거나 파일이 존재하지 않습니다: {creds_path}")
        sys.exit(1)

    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=7)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{now}] GSC 검색 순위 확인 — {site_url} ({start_str} ~ {end_str})\n")

    try:
        service = build_gsc_service(creds_path)
    except Exception as e:
        print(f"❌ GSC 서비스 초기화 실패: {e}")
        sys.exit(1)

    sheet_rows = []

    for keyword in KEYWORDS:
        data = fetch_keyword_data(service, site_url, keyword, start_str, end_str)

        if data:
            position_str = f"평균 {data['position']}위"
            print(
                f"  [{keyword}] → {position_str} "
                f"(클릭 {data['clicks']}, 노출 {data['impressions']}, CTR {data['ctr']}%)"
            )
            sheet_rows.append([
                now,
                keyword,
                data["position"],
                data["clicks"],
                data["impressions"],
                data["ctr"],
            ])
        else:
            print(f"  [{keyword}] → 데이터 없음 (노출 없음 또는 해당 기간 데이터 미수집)")
            sheet_rows.append([now, keyword, "-", 0, 0, 0])

    print()
    log_to_sheets(sheet_rows)
    print()


if __name__ == "__main__":
    run()
