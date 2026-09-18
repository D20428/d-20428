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
    
    # genre: 세로막대 기호(|) 기준 첫 번째 장르만 추출
    df['genre'] = df['genre'].astype(str).str.split('|').str[0].str.strip()
    
    # 숫자형 컬럼 변환 및 결측치/음수 처리 (0 이하 값 제외)
    df['total_audi'] = pd.to_numeric(df['total_audi'], errors='coerce').fillna(0)
    df = df[df['total_audi'] > 0]
    
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

fig_donut.update_traces(
    hovertemplate="<b>장르: %{label}</b><br>편수: %{value}편<br>비율: %{percent}"
)

st.plotly_chart(fig_donut, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** 개봉한 영화 중 어떤 장르가 가장 큰 비중을 차지하는지 한눈에 파악할 수 있습니다.")

st.divider()

# ----------------------------------------------------
# 두 번째 그래프: 장르 및 영화별 총 관객수 분포 (트리맵)
# ----------------------------------------------------
st.subheader("2. 장르 및 영화별 총 관객수 분포 (트리맵)")

# 데이터 가공
# 1. 영화 데이터 정제 (장르 + 영화명 기준 관객수 합계)
movie_summary = df.groupby(['genre', 'movieCd', 'movieNm'], as_index=False)['total_audi'].sum()

# 2. 장르별 관객수 합계 계산
genre_summary = movie_summary.groupby('genre', as_index=False)['total_audi'].sum()

# 3. 트리맵 노드 생성
# 루트 노드
ids = ["All"]
labels = ["전체 영화"]
parents = [""]
values = [genre_summary['total_audi'].sum()]

# 장르 노드
for _, row in genre_summary.iterrows():
    ids.append(f"genre_{row['genre']}")
    labels.append(row['genre'])
    parents.append("All")
    values.append(row['total_audi'])

# 영화 노드
for _, row in movie_summary.iterrows():
    ids.append(f"movie_{row['movieCd']}")
    labels.append(row['movieNm'])
    parents.append(f"genre_{row['genre']}")
    values.append(row['total_audi'])

# 4. go.Treemap 생성
fig_treemap = go.Figure(go.Treemap(
    ids=ids,
    labels=labels,
    parents=parents,
    values=values,
    branchvalues="total",
    hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,.0f}명<extra></extra>"
))

fig_treemap.update_layout(
    title="장르 및 영화별 총 관객수 트리맵",
    margin=dict(t=50, l=10, r=10, b=10)
)

st.plotly_chart(fig_treemap, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** 특정 장르 내에서 어떤 영화가 가장 많은 관객을 모았는지, 전체 총 관객수에서 차지하는 비중을 직관적으로 비교할 수 있습니다.")
