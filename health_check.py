import sys
import subprocess
import os
import smtplib
from email.mime.text import MIMEText

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

WARN_THRESHOLD = 3     # 경고: 응답시간 3초 이상
CRITICAL_THRESHOLD = 5  # 긴급: 응답시간 5초 이상


def load_env():
    """~/.vietgil.env 파일에서 환경변수 로드 (없으면 os.environ 그대로 사용)"""
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


def send_alert_email(subject, body):
    """이메일 알림 발송 (Gmail SMTP)"""
    email_from = os.environ.get("ALERT_EMAIL_FROM")
    email_to = os.environ.get("ALERT_EMAIL_TO")
    email_pw = os.environ.get("GMAIL_APP_PASSWORD")

    if not all([email_from, email_to, email_pw]):
        print("  ⚠ 이메일 알림 설정 누락 (ALERT_EMAIL_FROM / ALERT_EMAIL_TO / GMAIL_APP_PASSWORD)")
        return

    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = email_from
        msg["To"] = email_to

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email_from, email_pw)
            smtp.send_message(msg)
        print("  📧 알림 이메일 발송됨")
    except Exception as e:
        print(f"  ⚠ 이메일 발송 실패: {e}")


def build_body(now, status, code, elapsed):
    return (
        f"체크시간: {now}\n"
        f"상태:     {status}\n"
        f"응답코드: {code}\n"
        f"응답시간: {elapsed}초\n"
    )


def check():
    load_env()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] vietgil.com 상태 확인")

    try:
        res = requests.get(URL, timeout=10)
        elapsed = round(res.elapsed.total_seconds(), 2)

        # ── 응답코드 이상 → 긴급
        if res.status_code != 200:
            status = "오류"
            print(f"❌ 오류 | 응답코드: {res.status_code} | 응답시간: {elapsed:.2f}초")
            send_alert_email(
                "[Vietgil 🚨 긴급] vietgil.com 이상 감지",
                build_body(now, status, res.status_code, elapsed),
            )

        # ── 응답코드 200, 응답시간 기준 분기
        elif elapsed > CRITICAL_THRESHOLD:
            status = "느림(긴급)"
            print(f"🚨 긴급 | 응답코드: {res.status_code} | 응답시간: {elapsed:.2f}초 (>{CRITICAL_THRESHOLD}초)")
            send_alert_email(
                "[Vietgil 🚨 긴급] vietgil.com 이상 감지",
                build_body(now, status, res.status_code, elapsed),
            )

        elif elapsed >= WARN_THRESHOLD:
            status = "느림(경고)"
            print(f"⚠️  경고 | 응답코드: {res.status_code} | 응답시간: {elapsed:.2f}초 (>{WARN_THRESHOLD}초)")
            send_alert_email(
                "[Vietgil ⚠️ 경고] vietgil.com 응답 느림",
                build_body(now, status, res.status_code, elapsed),
            )

        else:
            status = "정상"
            print(f"✅ 정상 | 응답코드: {res.status_code} | 응답시간: {elapsed:.2f}초")

        log_to_sheets(now, status, res.status_code, elapsed)

    except requests.exceptions.ConnectionError:
        print("❌ 긴급 | 연결 실패 (사이트에 접근할 수 없습니다)")
        log_to_sheets(now, "연결실패", "-", "-")
        send_alert_email(
            "[Vietgil 🚨 긴급] vietgil.com 이상 감지",
            build_body(now, "연결실패", "-", "-"),
        )

    except requests.exceptions.Timeout:
        print("❌ 긴급 | 타임아웃 (10초 초과)")
        log_to_sheets(now, "타임아웃", "-", "-")
        send_alert_email(
            "[Vietgil 🚨 긴급] vietgil.com 이상 감지",
            build_body(now, "타임아웃 (10초 초과)", "-", "-"),
        )

    except requests.exceptions.RequestException as e:
        print(f"❌ 긴급 | {e}")
        log_to_sheets(now, "오류", "-", "-")
        send_alert_email(
            "[Vietgil 🚨 긴급] vietgil.com 이상 감지",
            build_body(now, f"오류: {e}", "-", "-"),
        )


if __name__ == "__main__":
    check()
