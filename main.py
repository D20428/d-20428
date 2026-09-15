import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
# 전체 영화 목록을 누적관객수 내림차순으로 정렬합니다.
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
# [구역 1] 선 그래프 - 개별 영화 일별 관객수 추이
# --------------------------------------------------
st.subheader("1. 개별 영화 일별 관객수 추이")

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
# [구역 2] 영역 차트 - 개별 영화 누적 관객수 추이
# --------------------------------------------------
st.subheader("2. 개별 영화 누적 관객수 추이")

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

st.markdown("---")

# --------------------------------------------------
# [구역 3] 다중 선그래프 - 20일 이상 상위권 자리를 지킨 TOP 5 영화 비교
# --------------------------------------------------
st.subheader("3. 장기 흥행 TOP 5 영화 누적 관객수 비교")

# 1. TOP 10에 등장한 일수 세기
days_in_top10 = df["영화명"].value_counts()

# 2. 20일 이상 등장한 영화들만 필터링
movies_over_20days = days_in_top10[days_in_top10 >= 20].index

# 3. 20일 이상 등장한 영화 중 누적관객수 기준 내림차순 상위 5개 추출
top5_long_run_movies = (
    df[df["영화명"].isin(movies_over_20days)]
    .groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .head(5)
    .index
    .tolist()
)

# 4. 필터링된 TOP 5 영화의 전체 데이터 추출
top5_df = df[df["영화명"].isin(top5_long_run_movies)]

# 5. Plotly 다중 선그래프 생성
fig3 = px.line(
    top5_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",
    title="TOP 10 차트에 20일 이상 진입한 주요 흥행작 TOP 5 누적 관객수 비교",
    markers=True,
    labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)", "영화명": "영화 제목"}
)

# 그래프 화면 출력
st.plotly_chart(fig3, use_container_width=True)

# 알 수 있는 것 문구
st.info("💡 **이 그래프로 알 수 있는 것:** 박스오피스 TOP 10에 최소 20일 이상 장기 상주하며 꾸준한 인기를 유지한 대표 흥행작 5편의 누적 관객수 증가 추이를 비교하여 볼 수 있습니다.")

st.markdown("---")

# --------------------------------------------------
# [구역 4] 이동평균선 - 전체 박스오피스 관객수 7일 이동평균
# --------------------------------------------------
st.subheader("4. 전체 박스오피스 일별 총 관객수 및 7일 이동평균")

# 1. 기준일자별 TOP10 영화의 해당일관객수 총합 계산
daily_total = df.groupby("기준일자")["해당일관객수"].sum().reset_index()

# 2. 7일 이동평균(Rolling Mean) 계산
daily_total["7일이동평균"] = daily_total["해당일관객수"].rolling(window=7, min_periods=1).mean()

# 3. Plotly graph_objects를 이용해 원본 선과 이동평균 선 시각화
fig4 = go.Figure()

fig4.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["해당일관객수"],
        mode="lines",
        name="일별 총 관객수 (일간 변동)",
        line=dict(color="rgba(180, 180, 180, 0.6)", width=1.5)
    )
)

fig4.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["7일이동평균"],
        mode="lines",
        name="7일 이동평균",
        line=dict(color="royalblue", width=3)
    )
)

fig4.update_layout(
    title="전체 박스오피스 일별 총 관객수 추이 및 7일 이동평균선",
    xaxis_title="날짜",
    yaxis_title="관객수(명)",
    legend=dict(x=0, y=1.1, orientation="h")
)

st.plotly_chart(fig4, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 주말/평일 간의 격차로 인한 단기적인 일별 관객수 변동(연한 선)을 완화하고, 7일 이동평균선(진한 선)을 통해 극장가 전체 관객수 흐름의 중장기적인 상승 및 하락 트렌드를 명확하게 파악할 수 있습니다.")

st.markdown("---")

# --------------------------------------------------
# [구역 5] 막대그래프 - 월별 전체 관객수 합계
# --------------------------------------------------
st.subheader("5. 월별 전체 박스오피스 관객수 합계")

# 1. 기준일자에서 '연-월(YYYY-MM)' 형식의 컬럼 생성
daily_total["연월"] = daily_total["기준일자"].dt.strftime("%Y-%m")

# 2. 월 단위로 그룹화하여 해당일관객수의 총합 계산
monthly_total = daily_total.groupby("연월")["해당일관객수"].sum().reset_index()

# 3. Plotly 막대그래프 생성
fig5 = px.bar(
    monthly_total,
    x="연월",
    y="해당일관객수",
    title="월별 극장가 전체 관객수 합계",
    text_auto=".2s", # 막대 위에 숫자를 간략하게 표시 (예: 1.2M)
    labels={"연월": "월(연-월)", "해당일관객수": "총 관객수(명)"}
)

# 막대 색상 및 레이아웃 설정
fig5.update_traces(marker_color="teal")
fig5.update_layout(xaxis_type="category") # 연월 라벨이 뭉개지지 않도록 범주형 축으로 설정

# 그래프 화면 출력
st.plotly_chart(fig5, use_container_width=True)

# 알 수 있는 것 문구
st.info("💡 **이 그래프로 알 수 있는 것:** 월별 총 관객 수의 변화를 통해 극장가의 계절적 성수기(방학, 연말연시, 추석 등)와 비수기 시즌을 한눈에 비교 및 파악할 수 있습니다.")
