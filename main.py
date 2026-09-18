# main.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 페이지 설정
st.set_page_config(page_title="영화 데이터 - 분포와 관계", layout="wide")

st.title("영화 데이터 - 분포와 관계")

# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # genre: 세로막대 기호(|)로 여러 개 적힌 경우 첫 번째 장르만 추출
    df['genre'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0].strip())
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
# 추가 분석 그래프 (예시: 스크린수와 총 관객수 관계)
# ----------------------------------------------------
st.subheader("2. 개봉일 스크린수와 총 관객수 관계")

fig_scatter = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    color='genre',
    hover_data=['movieNm'],
    labels={'first_scrn': '개봉일 스크린수', 'total_audi': '총 관객수'},
    title="개봉일 스크린수 vs 총 관객수"
)

st.plotly_chart(fig_scatter, use_container_width=True)

# 그래프 설명 구역
st.info("**이 그래프로 알 수 있는 것:** 개봉 당일 확보한 스크린수가 많을수록 최종 총 관객수도 증가하는 경향이 있는지 확인할 수 있습니다.")
