import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    r2_score,
    root_mean_squared_error,
    mean_absolute_error,
    mean_absolute_percentage_error
)

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="다이아몬드 가격 예측 및 회귀 분석 대시보드",
    page_icon="💎",
    layout="wide"
)

# 등급 서열 정의 (최하위 -> 최상위)
CUT_ORDER = ['Fair', 'Good', 'Very Good', 'Premium', 'Ideal']
COLOR_ORDER = ['J', 'I', 'H', 'G', 'F', 'E', 'D']
CLARITY_ORDER = ['I1', 'SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF']


def preprocess_features(df: pd.DataFrame) -> pd.DataFrame:
    """선형 회귀용 전처리: x,y,z 제거 + log(carat) + 순서형 기준 원-핫 인코딩"""
    out = df.copy()
    out['log_carat'] = np.log(out['carat'])
    out['cut'] = pd.Categorical(out['cut'], categories=CUT_ORDER, ordered=True)
    out['color'] = pd.Categorical(out['color'], categories=COLOR_ORDER, ordered=True)
    out['clarity'] = pd.Categorical(out['clarity'], categories=CLARITY_ORDER, ordered=True)

    out_ohe = pd.get_dummies(out, columns=['cut', 'color', 'clarity'], drop_first=True, dtype=int)
    feature_cols = ['log_carat', 'depth', 'table'] + [
        c for c in out_ohe.columns if c.startswith(('cut_', 'color_', 'clarity_'))
    ]
    return out_ohe[feature_cols]


@st.cache_data
def load_data():
    train_df = pd.read_csv('diamond_train.csv')
    test_df = pd.read_csv('diamond_test.csv')
    return train_df, test_df


@st.cache_resource
def train_and_evaluate(train_df: pd.DataFrame, test_df: pd.DataFrame):
    X_train = preprocess_features(train_df)
    y_train_log = np.log(train_df['price'])

    X_test = preprocess_features(test_df)
    y_test_log = np.log(test_df['price'])
    y_test_dollar = test_df['price'].values

    model = LinearRegression()
    model.fit(X_train, y_train_log)

    # 테스트 세트 예측 및 달러 역변환
    pred_test_log = model.predict(X_test)
    pred_test_dollar = np.exp(pred_test_log)
    res_log = y_test_log.values - pred_test_log

    metrics = {
        'r2_dollar': r2_score(y_test_dollar, pred_test_dollar),
        'rmse_dollar': root_mean_squared_error(y_test_dollar, pred_test_dollar),
        'mae_dollar': mean_absolute_error(y_test_dollar, pred_test_dollar),
        'mape_dollar': mean_absolute_percentage_error(y_test_dollar, pred_test_dollar) * 100,
        'r2_log': r2_score(y_test_log, pred_test_log),
        'rmse_log': root_mean_squared_error(y_test_log, pred_test_log),
    }

    coef_df = pd.DataFrame({
        'Feature': X_train.columns,
        'Coefficient': model.coef_,
        'Pct_Impact': (np.exp(model.coef_) - 1) * 100
    })

    eval_df = test_df.copy()
    eval_df['pred_log'] = pred_test_log
    eval_df['actual_log'] = y_test_log.values
    eval_df['res_log'] = res_log
    eval_df['pred_price'] = pred_test_dollar
    eval_df['abs_error'] = np.abs(y_test_dollar - pred_test_dollar)

    return model, X_train.columns.tolist(), metrics, coef_df, eval_df


# 데이터 로드 및 모델 학습 실행
try:
    train_df, test_df = load_data()
    model, feature_cols, metrics, coef_df, eval_df = train_and_evaluate(train_df, test_df)
except FileNotFoundError:
    st.error("⚠️ `diamond_train.csv` 또는 `diamond_test.csv` 파일을 찾을 수 없습니다. GitHub 저장소 최상단에 두 파일을 업로드해 주세요.")
    st.stop()

# 상단 타이틀
st.title("💎 다이아몬드 가격 예측 및 다중선형회귀 분석 웹앱")
st.markdown(
    f"정제된 데이터 **53,772건**을 8:2 층화 분할(`diamond_train.csv` **{len(train_df):,}건** / "
    f"`diamond_test.csv` **{len(test_df):,}건**)하여 학습한 로그-선형 회귀(Log-Linear Regression) 모델입니다."
)

# 3개 탭 구성
tab1, tab2, tab3 = st.tabs([
    "🔮 1. 실시간 가격 예측기",
    "📊 2. 데이터 탐색(EDA) & 심슨의 역설",
    "📈 3. 모델 성능 & 잔차 진단"
])

# ==========================================
# TAB 1: 실시간 가격 예측기
# ==========================================
with tab1:
    st.subheader("다이아몬드 스펙 입력")
    col_in1, col_in2, col_in3 = st.columns(3)

    with col_in1:
        in_carat = st.slider("중량 (Carat)", min_value=0.20, max_value=5.00, value=1.00, step=0.01)
        in_cut = st.selectbox("컷 등급 (Cut: Fair → Ideal)", options=CUT_ORDER, index=4)

    with col_in2:
        in_color = st.selectbox("색상 등급 (Color: J → D)", options=COLOR_ORDER, index=3)
        in_clarity = st.selectbox("투명도 등급 (Clarity: I1 → IF)", options=CLARITY_ORDER, index=3)

    with col_in3:
        in_depth = st.slider("전체 깊이 비율 (Depth %)", min_value=43.0, max_value=79.0, value=61.8, step=0.1)
        in_table = st.slider("상단 테이블 비율 (Table %)", min_value=43.0, max_value=95.0, value=57.0, step=0.5)

    # 입력값 예측 수행
    input_df = pd.DataFrame([{
        'carat': in_carat,
        'cut': in_cut,
        'color': in_color,
        'clarity': in_clarity,
        'depth': in_depth,
        'table': in_table
    }])
    X_input = preprocess_features(input_df)[feature_cols]
    pred_log_val = model.predict(X_input)[0]
    pred_dollar_val = np.exp(pred_log_val)

    # 95% 예측 신뢰구간 근사 (로그 잔차 표준편차 활용)
    std_log = metrics['rmse_log']
    ci_low = np.exp(pred_log_val - 1.96 * std_log)
    ci_high = np.exp(pred_log_val + 1.96 * std_log)

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("💰 예측 시장 가격", f"${pred_dollar_val:,.2f}")
    m2.metric("⚖️ 캐럿당 단가 ($/ct)", f"${pred_dollar_val / in_carat:,.2f}")
    m3.metric("📏 95% 예상 가격 범위", f"${ci_low:,.0f} ~ ${ci_high:,.0f}")

    # 유사 스펙 실제 거래 데이터 비교 차트
    similar_df = pd.concat([train_df, test_df])
    similar_df = similar_df[
        (similar_df['cut'] == in_cut) &
        (similar_df['color'] == in_color) &
        (similar_df['clarity'] == in_clarity)
    ]

    if len(similar_df) > 0:
        fig_sim = px.scatter(
            similar_df,
            x='carat',
            y='price',
            opacity=0.45,
            title=f"동일 등급({in_cut} / {in_color} / {in_clarity}) 실제 거래 분포 vs 현재 예측 위치 (n={len(similar_df):,})",
            labels={'carat': '중량 (Carat)', 'price': '실제 가격 ($)'},
            color_discrete_sequence=['#3b82f6']
        )
        fig_sim.add_trace(go.Scatter(
            x=[in_carat],
            y=[pred_dollar_val],
            mode='markers+text',
            name='현재 예측값',
            text=[f"예측: ${pred_dollar_val:,.0f}"],
            textposition="top center",
            marker=dict(color='#ef4444', size=15, symbol='star')
        ))
        st.plotly_chart(fig_sim, use_container_width=True)


# ==========================================
# TAB 2: 데이터 탐색(EDA) 및 전처리 요약
# ==========================================
with tab2:
    st.subheader("1. 데이터 정제 파이프라인 요약")
    clean_summary = pd.DataFrame({
        '단계': ['원본 데이터', '1단계: 완전 중복 제거', '2단계: 치수 0값(x,y,z=0) 제거', '3단계: 극단적 오기입(y,z>20) 제거', '최종 분할 (8:2 층화)'],
        '제거 건수': ['-', '146건', '19건', '3건', 'Train 43,017 / Test 10,755'],
        '잔여 건수': ['53,940건', '53,794건', '53,775건', '53,772건', '53,772건']
    })
    st.table(clean_summary)

    st.subheader("2. 심슨의 역설(Simpson's Paradox) 확인")
    st.info(
        "단순 등급별 가격을 비교하면 최하위 등급(I1, J)이 최고등급(IF, D)보다 비싸 보이는 역전 현상이 발생합니다. "
        "이는 저등급 다이아몬드의 평균 중량(Carat)이 훨씬 크기 때문이며, 모델에서는 log(carat)으로 중량을 통제해 이를 해결했습니다."
    )

    full_df = pd.concat([train_df, test_df])
    col_eda1, col_eda2 = st.columns(2)

    with col_eda1:
        clarity_agg = full_df.groupby('clarity', observed=False).agg(
            median_price=('price', 'median'),
            mean_carat=('carat', 'mean')
        ).reindex(CLARITY_ORDER).reset_index()

        fig_clar = px.bar(
            clarity_agg,
            x='clarity',
            y='median_price',
            text='median_price',
            title="투명도(Clarity) 등급별 중앙값 가격 ($) — 역전 현상",
            labels={'clarity': '투명도 (최하 I1 → 최상 IF)', 'median_price': '중앙값 가격 ($)'},
            color='mean_carat',
            color_continuous_scale='Blues'
        )
        fig_clar.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig_clar, use_container_width=True)

    with col_eda2:
        sample_eda = full_df.sample(n=4000, random_state=42)
        fig_log = px.scatter(
            sample_eda,
            x=np.log(sample_eda['carat']),
            y=np.log(sample_eda['price']),
            color='clarity',
            category_orders={'clarity': CLARITY_ORDER},
            opacity=0.55,
            title="로그 변환 후 선형성 확보: ln(carat) vs ln(price)",
            labels={'x': 'ln(carat)', 'y': 'ln(price)', 'clarity': '투명도'}
        )
        st.plotly_chart(fig_log, use_container_width=True)


# ==========================================
# TAB 3: 모델 성능 및 잔차 진단
# ==========================================
with tab3:
    st.subheader("1. 테스트 세트(10,755건) 최종 평가 지표")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("R² (달러 역변환)", f"{metrics['r2_dollar']:.4f}")
    k2.metric("RMSE ($)", f"${metrics['rmse_dollar']:,.2f}")
    k3.metric("MAE ($)", f"${metrics['mae_dollar']:,.2f}")
    k4.metric("MAPE (%)", f"{metrics['mape_dollar']:.2f}%")

    st.subheader("2. 회귀 계수 분석 (기준 등급 대비 순수 가격 상승률 %)")
    cat_coefs = coef_df[coef_df['Feature'].str.startswith(('cut_', 'color_', 'clarity_'))].copy()
    fig_coef = px.bar(
        cat_coefs,
        x='Pct_Impact',
        y='Feature',
        orientation='h',
        text='Pct_Impact',
        title="기준 등급(Fair, J, I1) 대비 등급별 순수 가격 상승 효과 (%)",
        labels={'Pct_Impact': '가격 상승률 (%)', 'Feature': '등급 피처'},
        color='Pct_Impact',
        color_continuous_scale='Teal'
    )
    fig_coef.update_traces(texttemplate='+%{text:.1f}%', textposition='outside')
    fig_coef.update_layout(height=550)
    st.plotly_chart(fig_coef, use_container_width=True)

    st.subheader("3. 잔차(Residual) 및 예측 적합도 진단")
    sample_eval = eval_df.sample(n=3000, random_state=42)
    c_res1, c_res2 = st.columns(2)

    with c_res1:
        fig_res = px.scatter(
            sample_eval,
            x='pred_log',
            y='res_log',
            opacity=0.35,
            title="Residuals vs. Fitted Values (로그 공간)",
            labels={'pred_log': '예측값 ln(price)', 'res_log': '잔차 (실제 - 예측)'},
            color_discrete_sequence=['#2b5c8f']
        )
        fig_res.add_hline(y=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig_res, use_container_width=True)

    with c_res2:
        fig_act = px.scatter(
            sample_eval,
            x='price',
            y='pred_price',
            opacity=0.35,
            title="실제 가격($) vs 예측 가격($)",
            labels={'price': '실제 가격 ($)', 'pred_price': '예측 가격 ($)'},
            color_discrete_sequence=['#1f77b4']
        )
        fig_act.add_trace(go.Scatter(
            x=[0, 20000], y=[0, 20000],
            mode='lines', name='완벽 예측선 (y=x)',
            line=dict(color='red', dash='dash')
        ))
        st.plotly_chart(fig_act, use_container_width=True)
