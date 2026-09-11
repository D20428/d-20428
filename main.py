import datetime
import requests
import streamlit as st

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(
    page_title="박스오피스 순위 조회", page_icon="🎬", layout="wide"
)


# API 데이터를 불러오고 1시간(3600초)동안 캐싱(기억)하는 함수
# 선택한 target_date마다 별도로 결과가 기억됩니다.
@st.cache_data(ttl=3600)
def fetch_box_office_data(api_key, target_date):
    """KOBIS API를 호출하여 dailyBoxOfficeList 데이터를 반환합니다."""
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_date}

    try:
        response = requests.get(url, params=params, timeout=10)
        # 네트워크 응답 코드가 200이 아닌 경우 예외 발생
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # 요청 도중 에러가 발생하면 None을 반환
        return None


def format_rank_change(rank_inten):
    """순위 증감 수치를 화살표 기호가 붙은 문자열로 변환합니다."""
    try:
        change = int(rank_inten)
    except ValueError:
        return "-"

    if change > 0:
        return f"🔺 {change}"  # 순위 상승 (빨간 위 화살표)
    elif change < 0:
        return f"🔹 {abs(change)}"  # 순위 하강 (파란 아래 화살표)
    else:
        return "-"  # 변동 없음


def main():
    st.title("🎬 박스오피스 순위 조회")

    # 1. Streamlit Secrets에서 API Key 가져오기
    if "KOBIS_KEY" not in st.secrets:
        st.error(
            "🔑 인증키 설정이 필요합니다.\n\n"
            "Streamlit Cloud의 App settings > Secrets에서 `KOBIS_KEY`를 등록해 주세요."
        )
        return

    api_key = st.secrets["KOBIS_KEY"]

    # 2. 한국 시간(UTC+9) 기준 어제 날짜 계산 (달력의 최대 선택 가능 날짜)
    korea_tz = datetime.timezone(datetime.timedelta(hours=9))
    today_korea = datetime.datetime.now(korea_tz).date()
    yesterday = today_korea - datetime.timedelta(days=1)

    # 3. 달력을 통해 조회할 날짜 선택
    selected_date = st.date_input(
        label="📅 조회할 날짜를 선택해 주세요",
        value=yesterday,
        max_value=yesterday,  # 오늘 이후 날짜는 선택 불가능
        help="오늘 날짜는 아직 데이터 집계 전이므로 어제 날짜까지만 선택 가능합니다."
    )

    # API에 전달할 YYYYMMDD 형태 문자열 생성
    target_date_str = selected_date.strftime("%Y%m%d")
    display_date_str = selected_date.strftime("%Y년 %m월 %d일")

    st.write(f" 기준 날짜: **{display_date_str}**")

    # 4. API 호출
    data = fetch_box_office_data(api_key, target_date_str)

    # 5. 예외 및 오류 처리 (요청 실패 / faultInfo / 빈 목록)
    if data is None:
        st.error(
            "❌ 네트워크 연결에 실패했거나 KOBIS 서버 응답을 받지 못했습니다. 잠시 후 다시 시도해 주세요."
        )
        return

    # KOBIS API는 인증키가 틀렸을 때 faultInfo 응답을 전달함
    if "faultInfo" in data:
        message = data["faultInfo"].get("message", "알 수 없는 오류")
        st.error(
            f"❌ API 오류가 발생했습니다.\n\n"
            f"- 메시지: {message}\n"
            f"- 확인 사항: `.streamlit/secrets.toml` 또는 Cloud Secrets의 `KOBIS_KEY` 값이 올바른지 확인해 주세요."
        )
        return

    # 결과 데이터 구조 파싱
    box_office_result = data.get("boxOfficeResult", {})
    daily_list = box_office_result.get("dailyBoxOfficeList", [])

    if not daily_list:
        st.warning("⚠️ 그날은 아직 집계 전입니다.")
        return

    # 6. 숫자 데이터 형변환 및 영화명/순위증감 가공
    parsed_list = []
    for item in daily_list:
        movie_name = item.get("movieNm", "")
        audi_acc = int(item.get("audiAcc", 0))

        # 누적 관객 100만 명 이상일 경우 영화명에 트로피 이모지 붙이기
        if audi_acc >= 1000000:
            movie_name = f"🏆 {movie_name}"

        parsed_list.append(
            {
                "순위": int(item.get("rank", 0)),
                "영화명": movie_name,
                "개봉일": item.get("openDt", ""),
                "관객수": int(item.get("audiCnt", 0)),
                "누적관객": audi_acc,
                "스크린수": int(item.get("scrnCnt", 0)),
                "순위증감": format_rank_change(item.get("rankInten", "0")),
            }
        )

    # 순위 기준으로 정렬
    parsed_list.sort(key=lambda x: x["순위"])

    # 7. 1위 영화 지표 카드 3장 표시
    top1 = parsed_list[0]
    st.markdown("### 🏆 1위 영화 상세 정보")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="1위 영화 제목", value=top1["영화명"])
    with col2:
        st.metric(
            label="당일 관객수", value=f"{top1['관객수']:,} 명"
        )
    with col3:
        st.metric(
            label="누적 관객수", value=f"{top1['누적관객']:,} 명"
        )

    st.divider()

    # 8. 상위 5편 관객수 막대그래프
    st.markdown("### 📊 관객수 상위 5개 영화")
    top5_list = parsed_list[:5]

    chart_data = {
        item["영화명"]: item["관객수"] for item in top5_list
    }
    st.bar_chart(chart_data)

    st.divider()

    # 9. 전체 박스오피스 표 출력
    st.markdown("### 📋 박스오피스 전체 순위")

    table_data = []
    for item in parsed_list:
        table_data.append(
            {
                "순위": item["순위"],
                "순위 변동": item["순위증감"],
                "영화명": item["영화명"],
                "개봉일": item["개봉일"],
                "일일 관객수": f"{item['관객수']:,}명",
                "누적 관객수": f"{item['누적관객']:,}명",
                "스크린수": f"{item['스크린수']:,}개",
            }
        )

    st.dataframe(table_data, use_container_width=True)


if __name__ == "__main__":
    main()
