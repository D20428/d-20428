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
    df['first_week네 번째 산점도를 바탕으로 **점의 크기를 `first_week_audi`(첫 주 관객 수)로 설정한 여섯 번째 버블 차트**를 추가하는 파이썬(Seaborn/Matplotlib) 코드 예시입니다.

```python
import matplotlib.pyplot as plt
import seaborn as sns

# 기존 차트들이 위치한 리사이징 파트 및 서브플롯 설정
# 예: 2행 3열(총 6개) 구도로 설정하는 경우
fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# ... [첫 번째 ~ 다섯 번째 그래프 코드] ...

# 6. 여섯 번째 그래프: 버블 차트 (네 번째 산점도 + 점 크기 반영)
sns.scatterplot(
    data=df,
    x="x_variable",  # 네 번째 산점도에서 사용한 X축 변수명
    y="y_variable",  # 네 번째 산점도에서 사용한 Y축 변수명
    size="first_week_audi",  # 점 크기에 첫 주 관객 수 반영
    sizes=(20, 500),  # 버블 크기의 최소/최대 범위 조절
    hue="first_week_audi",  # (선택 사항) 크기에 따른 색상 구분
    alpha=0.6,  # 겹친 점을 보기 쉽게 투명도 설정
    ax=axes[1, 2],  # 여섯 번째 위치 (2행 3열)
)

axes[1, 2].set_title("버블 차트 (점 크기: 첫 주 관객 수)")
axes[1, 2].legend(
    bbox_to_anchor=(1.05, 1), loc="upper left"
)  # 범례 위치 정리

plt.tight_layout()
plt.show()
