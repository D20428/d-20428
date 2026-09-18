# main.py
import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 설정
st.set_page_config(page_title="영화 데이터 - 분포와 관계", layout="wide")

st.title("영화 데이터 - 분포와 관계")

# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # genre: 세로막대 기호(|) 기준 첫 번째 장르만 추출 (Pandas str 메서드 사용)
    df['genre'] = df['genre'].astype(str).str.split('|').str[0].str.strip()
    return df

df = load_data()

st.divider()

# ----------------------------------------------------
# 첫 번째 그래프: 장르별 영화 편수 (도넛 그래프)
# ----------------------------------------------------
st.subheader("1. 장르별 영화 편수 분포")

genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['genre', 'count']

fig_donut = px.pie(
    genre_counts,
    names='genre',
    values='count',
    hole=0.4,
    title="장르별 영화 편수"
)

# 마우스 호버 시 편수와 비율 표기 설정
fig_donut.update_traces(
    hovertemplate="<b>장르: %{label}</b><br>편수: %{value}편<br>비율: %{percent}"
)

st.plotly_chart(fig_donut, use_container_width=True)

# 그래프 설명 구역
st.info("**이 그래프로 알 수 있는 것:** 개봉한 영화 중 어떤 장르가 가장 큰 비중을 차지하는지 한눈에 파악할 수 있습니다.")

st.divider()

# ----------------------------------------------------
# 두 번째 그래프: 장르별 영화 점유율 트리맵 (칸 크기: 총 관객수)
# ----------------------------------------------------
st.subheader("2. 장르 및 영화별 총 관객수 분포 (트리맵)")

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체"), 'genre', 'movieNm'],  # 계층 구조: 전체 -> 장르 -> 영화명
    values='total_audi',
    color='genre',
    title="장르 및 영화별 총 관객수 트리맵"
)

# 마우스 호버 시 영화명과 총 관객수 표기 설정
fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,.0f}명"
)

st.plotly_chart(fig_treemap, use_container_width=True)

# 그래프 설명 구역
st.info("**이 그래프로 알 수 있는 것:** 특정 장르 내에서 어떤 영화가 가장 많은 관객을 모았는지, 전체 총 관객수에서 차지하는 비중을 직관적으로 비교할 수 있습니다.")
