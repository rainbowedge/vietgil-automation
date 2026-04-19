import sys
import subprocess
import os

# requests 없으면 자동 설치
try:
    import requests
except ImportError:
    print("requests 패키지를 설치합니다...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# gspread 없으면 자동 설치
try:
    import gspread
except ImportError:
    print("gspread 패키지를 설치합니다...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gspread"])
    import gspread

from datetime import datetime
from pathlib import Path

URL = "https://vietgil.com"
ENV_PATH = Path.home() / ".vietgil.env"


def load_env():
    """~/.vietgil.env 파일에서 환경변수 로드"""
    if not ENV_PATH.exists():
        return
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


def log_to_sheets(timestamp, status, code, elapsed):
    """Google Sheets '사이트상태' 시트에 결과 기록"""
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
            ws = sh.worksheet("사이트상태")
        except gspread.exceptions.WorksheetNotFound:
            ws = sh.add_worksheet(title="사이트상태", rows=1000, cols=4)
            ws.append_row(["체크시간", "상태", "응답코드", "응답시간(초)"])

        ws.append_row([timestamp, status, code, elapsed])
        print("  📊 Google Sheets 기록 완료")

    except Exception as e:
        print(f"  ⚠ Sheets 기록 실패: {e}")


def check():
    load_env()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] vietgil.com 상태 확인")

    try:
        res = requests.get(URL, timeout=10)
        elapsed = round(res.elapsed.total_seconds(), 2)

        if res.status_code == 200:
            status = "정상"
            print(f"✅ 정상 | 응답코드: {res.status_code} | 응답시간: {elapsed:.2f}초")
        else:
            status = "오류"
            print(f"❌ 오류 | 응답코드: {res.status_code} | 응답시간: {elapsed:.2f}초")

        log_to_sheets(now, status, res.status_code, elapsed)

    except requests.exceptions.ConnectionError:
        print("❌ 오류 | 연결 실패 (사이트에 접근할 수 없습니다)")
        log_to_sheets(now, "연결실패", "-", "-")
    except requests.exceptions.Timeout:
        print("❌ 오류 | 타임아웃 (10초 초과)")
        log_to_sheets(now, "타임아웃", "-", "-")
    except requests.exceptions.RequestException as e:
        print(f"❌ 오류 | {e}")
        log_to_sheets(now, "오류", "-", "-")


if __name__ == "__main__":
    check()
