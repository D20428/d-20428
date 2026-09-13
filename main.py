import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정 (넓은 레이아웃 적용)
st.set_page_config(
    page_title="영화 관객수 분석 앱",
    page_icon="🎬",
    layout="wide"
)

# [1. 데이터 불러오기]
# @st.cache_data 데코레이터를 사용하여 데이터를 캐싱(저장)합니다.
# 이렇게 하면 앱이 새로고침되어도 매번 CSV를 다시 다운로드하지 않아 속도가 빨라집니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)
    
    # [2. 날짜 전처리]
    # 결측치(값이 없는 데이터)가 하나라도 포함된 행은 삭제합니다.
    df = df.dropna()
    
    # "기준일자" 컬럼을 날짜(datetime) 형식으로 변환합니다.
    df["기준일자"] = pd.to_datetime(df["기준일자"])
    
    # 전체 데이터를 "기준일자" 순서대로 정렬합니다.
    df = df.sort_values(by="기준일자")
    
    return df

# 데이터 로드
df = load_data()

# 앱 제목 설정
st.title("🎬 박스오피스 영화 관객수 분석")
st.markdown("---")

# [3. 영화 선택 기능]
# 누적관객수가 가장 높은 순서대로 영화 목록을 정렬하기 위해 
# 영화명별 최댓값(또는 마지막 누적관객수)을 기준으로 내림차순 정렬합니다.
movie_order = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index
    .tolist()
)

# 영화 선택 드롭다운 생성
selected_movie = st.selectbox(
    "📊 분석할 영화를 선택하세요:",
    options=movie_order
)

# 선택한 영화의 데이터만 필터링
filtered_df = df[df["영화명"] == selected_movie]

# --------------------------------------------------
# [구역 1] 선 그래프 - 일별 관객수 추이
# --------------------------------------------------
st.subheader("1. 일별 관객수 추이")

# Plotly를 사용하여 기준일자별 해당일관객수의 변화를 선 그래프로 생성합니다.
fig1 = px.line(
    filtered_df,
    x="기준일자",
    y="해당일관객수",
    title=f"'{selected_movie}'의 일별 관객수 변화",
    markers=True, # 데이터 지점에 점 표시
    labels={"기준일자": "날짜", "해당일관객수": "해당일 관객수(명)"}
)

# 그래프 화면 출력
st.plotly_chart(fig1, use_container_width=True)

# 알 수 있는 것 문구
st.info(f"💡 **이 그래프로 알 수 있는 것:** 개봉 후 시간 경과에 따른 '{selected_movie}'의 일별 관객수 증감 추세 및 관객 집중 시기를 확인할 수 있습니다.")

st.markdown("---")

# --------------------------------------------------
# [구역 2] 영역 차트 - 누적 관객수 추이
# --------------------------------------------------
st.subheader("2. 누적 관객수 추이")

# Plotly를 사용하여 기준일자별 누적관객수의 변화를 영역 차트(area chart)로 생성합니다.
fig2 = px.area(
    filtered_df,
    x="기준일자",
    y="누적관객수",
    title=f"'{selected_movie}'의 누적 관객수 성장 추이",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)"}
)

# 그래프 선 및 영역 스타일 조정 (선명한 표현)
fig2.update_traces(mode="lines+markers")

# 그래프 화면 출력
st.plotly_chart(fig2, use_container_width=True)

# 알 수 있는 것 문구
st.info(f"💡 **이 그래프로 알 수 있는 것:** 시간 경과에 따른 '{selected_movie}'의 전체 누적 관객수 증가 속도와 최종 누적 성과를 직관적으로 파악할 수 있습니다.")
