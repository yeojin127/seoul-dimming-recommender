import time
import requests
import pandas as pd

# ====== 경로(지니 PC 기준) ======
CODES_PATH = r"C:\Users\jyj20\Desktop\KW\2_winter\sw경진대회\data\seoul_eupmyeondong_codes.csv"
OUT_PATH   = r"C:\Users\jyj20\Desktop\KW\2_winter\sw경진대회\data\seoul_brtitle_raw.csv"

# ====== API ======
BASE_URL = "https://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo"
SERVICE_KEY = "7f21f4475ba47bf878ab5d330844ffba7f33239d5b0d56d4b4cb946fa97b42fe"

# ====== 수집 설정 ======
NUM_ROWS = 1000          # 페이지당 최대 수(가능하면 크게)
SLEEP_SEC = 0.2          # 과호출 방지
TIMEOUT_SEC = 15         # 요청 타임아웃
RETRY = 3                # 네트워크/일시 오류 재시도 횟수
SAVE_EVERY_DONG = 10     # 동 몇 개마다 중간 저장할지

def safe_get_json(session: requests.Session, url: str, params: dict, timeout: int, retry: int):
    """GET 요청을 안전하게 보내고, 성공(200)일 때만 JSON을 반환한다."""
    last_status = None
    last_text = None

    for attempt in range(1, retry + 1):
        try:
            r = session.get(url, params=params, timeout=timeout)
            last_status = r.status_code
            last_text = r.text

            if r.status_code != 200:
                # 200이 아니면 JSON 파싱하지 말고 텍스트 에러를 반환
                return None, r.status_code, r.text

            # 200인데도 JSON이 아닌 경우가 있어서 보호
            try:
                return r.json(), 200, None
            except Exception:
                return None, 200, r.text

        except requests.exceptions.RequestException as e:
            # 네트워크 오류는 재시도
            if attempt < retry:
                time.sleep(1.0 * attempt)
                continue
            return None, last_status, str(e)

    return None, last_status, last_text

def extract_items(data: dict):
    """response > body > items > item 구조에서 item 리스트를 뽑아온다."""
    items = (
        data.get("response", {})
            .get("body", {})
            .get("items", {})
            .get("item", [])
    )
    if isinstance(items, dict):
        return [items]
    if isinstance(items, list):
        return items
    return []

def load_codes(path: str) -> pd.DataFrame:
    """서울 동 코드 파일 로드 + BOM 컬럼명 정리"""
    codes = pd.read_csv(path, encoding="utf-8-sig")
    # BOM 때문에 첫 컬럼이 '\ufeff시군구명' 이런 식으로 잡힐 수 있어서 정리
    codes.columns = [c.replace("\ufeff", "") for c in codes.columns]
    required = {"sigunguCd", "bjdongCd_5"}
    missing = required - set(codes.columns)
    if missing:
        raise ValueError(f"codes file missing columns: {missing}. columns={list(codes.columns)}")
    return codes

def main():
    print("START")

    codes = load_codes(CODES_PATH)
    print("CODES LOADED:", codes.shape, list(codes.columns))

    session = requests.Session()
    all_rows = []

    for idx, row in codes.iterrows():
        sigunguCd = str(row["sigunguCd"]).zfill(5)
        bjdongCd  = str(row["bjdongCd_5"]).zfill(5)

        print(f"[DONG] {idx+1}/{len(codes)} sigunguCd={sigunguCd}, bjdongCd={bjdongCd}")

        page = 1
        while True:
            params = {
                "serviceKey": SERVICE_KEY,   # 안 되면 "ServiceKey"로 바꿔 테스트
                "sigunguCd": sigunguCd,
                "bjdongCd": bjdongCd,
                "numOfRows": NUM_ROWS,
                "pageNo": page,
                "_type": "json",
            }

            data, status, err_text = safe_get_json(session, BASE_URL, params, TIMEOUT_SEC, RETRY)

            if status != 200:
                print(f"  [ERROR] status={status} page={page}")
                if err_text:
                    print("  [ERROR_TEXT]", err_text[:500])
                break  # 이 동은 여기서 중단(다음 동으로)

            if data is None:
                print(f"  [ERROR] status=200 but non-json response page={page}")
                if err_text:
                    print("  [RAW_TEXT]", err_text[:500])
                break

            items = extract_items(data)
            if not items:
                # 더 이상 데이터 없음
                print(f"  [DONE] pages={page-1}, added=0 (no more items)")
                break

            for it in items:
                it["sigunguCd"] = sigunguCd
                it["bjdongCd"] = bjdongCd
            all_rows.extend(items)

            print(f"  [PAGE] {page} items={len(items)} total_rows={len(all_rows)}")
            page += 1
            time.sleep(SLEEP_SEC)

        # 중간 저장
        if (idx + 1) % SAVE_EVERY_DONG == 0 and all_rows:
            pd.DataFrame(all_rows).to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
            print(f"[SAVE] {idx+1}/{len(codes)} dong done, rows={len(all_rows)} => {OUT_PATH}")

    # 최종 저장
    pd.DataFrame(all_rows).to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print("ALL DONE:", OUT_PATH, "rows:", len(all_rows))

if __name__ == "__main__":
    main()
