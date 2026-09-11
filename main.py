import datetime
import requests
import streamlit as st

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(
    page_title="어제 박스오피스 순위", page_icon="🎬", layout="wide"
)


# API 데이터를 불러오고 1시간(3600초)동안 캐싱(기억)하는 함수
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


def main():
    st.title("🎬 어제 박스오피스 순위")

    # 1. Streamlit Secrets에서 API Key 가져오기
    if "KOBIS_KEY" not in st.secrets:
        st.error(
            "🔑 인증키 설정이 필요합니다.\n\n"
            "Streamlit Cloud의 App settings > Secrets에서 `KOBIS_KEY`를 등록해 주세요."
        )
        return

    api_key = st.secrets["KOBIS_KEY"]

    # 2. 한국 시간(UTC+9) 기준 어제 날짜 계산 (YYYYMMDD 형식)
    # 서버 시계 시간대에 관계없이 UTC+9 시차 적용
    korea_tz = datetime.timezone(datetime.timedelta(hours=9))
    yesterday = datetime.datetime.now(korea_tz) - datetime.timedelta(days=1)
    target_date_str = yesterday.strftime("%Y%m%d")
    display_date_str = yesterday.strftime("%Y년 %m월 %d일")

    st.write(f" 기준 날짜: **{display_date_str}**")

    # 3. API 호출
    data = fetch_box_office_data(api_key, target_date_str)

    # 4. 예외 및 오류 처리 (요청 실패 / faultInfo / 빈 목록)
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
        st.warning(
            "⚠️ 해당 날짜의 박스오피스 데이터가 비어 있습니다. 아직 집계가 완료되지 않았거나 데이터가 없을 수 있습니다."
        )
        return

    # 5. 숫자 데이터 형변환 (문자열 -> 정수)
    parsed_list = []
    for item in daily_list:
        parsed_list.append(
            {
                "순위": int(item.get("rank", 0)),
                "영화명": item.get("movieNm", ""),
                "개봉일": item.get("openDt", ""),
                "관객수": int(item.get("audiCnt", 0)),
                "누적관객": int(item.get("audiAcc", 0)),
                "스크린수": int(item.get("scrnCnt", 0)),
                "순위증감": item.get("rankInten", "0"),
            }
        )

    # 순위 기준으로 정렬
    parsed_list.sort(key=lambda x: x["순위"])

    # 6. 1위 영화 지표 카드 3장 표시
    top1 = parsed_list[0]
    st.markdown("### 🏆 1위 영화 상세 정보")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="1위 영화 제목", value=top1["영화명"])
    with col2:
        st.metric(
            label="어제 관객수", value=f"{top1['관객수']:,} 명"
        )
    with col3:
        st.metric(
            label="누적 관객수", value=f"{top1['누적관객']:,} 명"
        )

    st.divider()

    # 7. 상위 5편 관객수 막대그래프
    st.markdown("### 📊 관객수 상위 5개 영화")
    top5_list = parsed_list[:5]

    # Streamlit 기본 차트 사용을 위한 데이터 가공 (영화명: 관객수)
    chart_data = {
        item["영화명"]: item["관객수"] for item in top5_list
    }
    st.bar_chart(chart_data)

    st.divider()

    # 8. 전체 박스오피스 표 출력
    st.markdown("### 📋 박스오피스 전체 순위")

    # 표에 보여줄 열 정리
    table_data = []
    for item in parsed_list:
        table_data.append(
            {
                "순위": item["순위"],
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
