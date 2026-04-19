import sys
import subprocess

# requests 없으면 자동 설치
try:
    import requests
except ImportError:
    print("requests 패키지를 설치합니다...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

from datetime import datetime

URL = "https://vietgil.com"

def check():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] vietgil.com 상태 확인")

    try:
        res = requests.get(URL, timeout=10)
        elapsed = res.elapsed.total_seconds()

        if res.status_code == 200:
            print(f"✅ 정상 | 응답코드: {res.status_code} | 응답시간: {elapsed:.2f}초")
        else:
            print(f"❌ 오류 | 응답코드: {res.status_code} | 응답시간: {elapsed:.2f}초")

    except requests.exceptions.ConnectionError:
        print("❌ 오류 | 연결 실패 (사이트에 접근할 수 없습니다)")
    except requests.exceptions.Timeout:
        print("❌ 오류 | 타임아웃 (10초 초과)")
    except requests.exceptions.RequestException as e:
        print(f"❌ 오류 | {e}")

if __name__ == "__main__":
    check()
