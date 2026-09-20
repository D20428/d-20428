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
    df['first_scrn'] = pd.to_numeric(df['first_scrn'], errors='coerce').fillna(0)
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
movie_summary = df.groupby(['genre', 'movieCd', 'movieNm'], as_index=False)['total_audi'].sum()
genre_summary = movie_summary.groupby('genre', as_index=False)['total_audi'].sum()

# 트리맵 노드 생성
ids = ["All"]
labels = ["전체 영화"]
parents = [""]
values = [genre_summary['total_audi'].sum()]

for _, row in genre_summary.iterrows():
    ids.append(f"genre_{row['genre']}")
    labels.append(row['genre'])
    parents.append("All")
    values.append(row['total_audi'])

for _, row in movie_summary.iterrows():
    ids.append(f"movie_{row['movieCd']}")
    labels.append(row['movieNm'])
    parents.append(f"genre_{row['genre']}")
    values.append(row['total_audi'])

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

st.divider()

# ----------------------------------------------------
# 세 번째 그래프: 총 관객수 히스토그램
# ----------------------------------------------------
st.subheader("3. 총 관객수 히스토그램")

fig_hist = px.histogram(
    df,
    x='total_audi',
    nbins=30,
    title="총 관객수 분포 히스토그램",
    labels={'total_audi': '총 관객수'},
    color_discrete_sequence=['#636EFA']
)

fig_hist.update_traces(
    hovertemplate="관객수 구간: %{x}<br>영화 수: %{y}편"
)

fig_hist.update_layout(
    xaxis_title="총 관객수 (명)",
    yaxis_title="영화 수 (편)"
)

st.plotly_chart(fig_hist, use_container_width=True)

# 가장 관객수가 많은 영화 정보 계산
top_movie = df.loc[df['total_audi'].idxmax()]
top_movie_name = top_movie['movieNm']
top_movie_audi = top_movie['total_audi']

st.info(
    f"**이 그래프로 알 수 있는 것:** 대부분의 영화는 관객수 **500만 명 이하(주로 100만~300만 명) 구간**에 밀집해 있으며, "
    f"가장 많은 관객을 모은 영화는 **'{top_movie_name}'** (약 {top_movie_audi:,.0f}명)입니다."
)

st.divider()

# ----------------------------------------------------
# 네 번째 그래프: 개봉일 스크린수 vs 총 관객수 산점도
# ----------------------------------------------------
st.subheader("4. 개봉일 스크린수와 총 관객수 관계")

fig_scatter = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    color='genre',
    hover_name='movieNm',
    labels={
        'first_scrn': '개봉일 스크린수 (개)',
        'total_audi': '총 관객수 (명)',
        'genre': '장르'
    },
    title="개봉일 스크린수 vs 총 관객수 산점도"
)

fig_scatter.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,.0f}개<br>총 관객수: %{y:,.0f}명<extra></extra>"
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** 개봉 당일 확보한 스크린수가 많을수록 대체로 최종 총 관객수도 높게 형성되는 양의 관계가 있음을 알 수 있습니다.")

st.divider()

# ----------------------------------------------------
# 다섯 번째 그래프: 영화 10편 이상 장르별 총 관객수 박스플롯
# ----------------------------------------------------
st.subheader("5. 주요 장르별 총 관객수 박스플롯")

# 영화가 10편 이상인 장르만 필터링
genre_counts_series = df['genre'].value_counts()
major_genres = genre_counts_series[genre_counts_series >= 10].index.tolist()
df_filtered_box = df[df['genre'].isin(major_genres)]

fig_box = px.box(
    df_filtered_box,
    x='genre',
    y='total_audi',
    color='genre',
    hover_name='movieNm',
    points="outliers",  # 이상치(outliers) 점 표기
    labels={
        'genre': '장르',
        'total_audi': '총 관객수 (명)'
    },
    title="영화 10편 이상 주요 장르별 총 관객수 분포 (박스플롯)"
)

fig_box.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>총 관객수: %{y:,.0f}명<extra></extra>"
)

fig_box.update_layout(
    xaxis_title="장르 (10편 이상)",
    yaxis_title="총 관객수 (명)",
    showlegend=False
)

st.plotly_chart(fig_box, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** 주요 장르 간 관객수 중앙값과 분포 범위를 비교할 수 있으며, 상자 밖의 점을 통해 대흥행을 거둔 극단적인 이상치(Outlier) 영화들을 확인할 수 있습니다.")
