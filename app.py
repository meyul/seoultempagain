import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ----------------- 기본 설정 -----------------
st.set_page_config(page_title="기온 예측기", page_icon="🌡️")
st.title("🌡️ 서울 기온 예측기")
st.caption("서울 기상관측 자료로 연평균기온 추세를 보고 미래 기온을 예측해 봅시다.")

CSV_URL = "https://raw.githubusercontent.com/greatsong/modudata/bb860932644270ad1199f10d3e7670e30231bce4/data/seoul.csv"
LAST_YEAR = 2025   # 기준 기간의 마지막 해
MIN_DAYS = 300     # 이 날짜 수보다 적은 해는 제외


# ----------------- 데이터 불러오기 -----------------
@st.cache_data(show_spinner="서울 기온 데이터를 불러오는 중...")
def load_data():
    df = pd.read_csv(CSV_URL, encoding="utf-8")
    df["날짜"] = pd.to_datetime(df["날짜"])  # 문자열 → 날짜형
    df["연도"] = df["날짜"].dt.year
    return df


try:
    raw = load_data()
except Exception as e:
    st.error(f"데이터를 불러오지 못했어요. 인터넷 연결을 확인해 주세요. ({e})")
    st.stop()

# ----------------- 연도별 평균기온 만들기 -----------------
yearly = (
    raw.dropna(subset=["평균기온"])
    .groupby("연도")["평균기온"]
    .agg(관측일수="count", 연평균기온="mean")
    .reset_index()
)

# ① 2025년까지의 자료만  ② 관측일이 300일 이상인 해만
yearly = yearly[
    (yearly["연도"] <= LAST_YEAR) & (yearly["관측일수"] >= MIN_DAYS)
].reset_index(drop=True)

x = yearly["연도"].to_numpy(dtype=float)
y = yearly["연평균기온"].to_numpy(dtype=float)

# ----------------- 회귀 직선 & 상관계수 (전체 기간) -----------------
slope, intercept = np.polyfit(x, y, 1)   # 1차(직선) 회귀
r = np.corrcoef(x, y)[0, 1]              # 상관계수

start_year = int(yearly["연도"].min())
end_year = int(yearly["연도"].max())
n_years = len(yearly)

# 기울기를 "100년당 상승 온도"로 환산
slope_100 = slope * 100

# ----------------- 회귀 직선 & 상관계수 (최근 20년) -----------------
recent = yearly[yearly["연도"] >= end_year - 19]   # 마지막 해 포함 20년
rx = recent["연도"].to_numpy(dtype=float)
ry = recent["연평균기온"].to_numpy(dtype=float)
recent_start = int(recent["연도"].min())

slope_r, intercept_r = np.polyfit(rx, ry, 1)
r_r = np.corrcoef(rx, ry)[0, 1]
slope_r_100 = slope_r * 100

# ----------------- 자료 정보 -----------------
st.subheader("📌 회귀 직선을 만든 자료")
c1, c2, c3 = st.columns(3)
c1.metric("사용한 해의 개수", f"{n_years}개")
c2.metric("시작 연도", f"{start_year}년")
c3.metric("끝 연도", f"{end_year}년")

# ----------------- 100년당 기온 상승 속도 비교 -----------------
def big_number(label, value, color):
    return f"""
    <div style="text-align:center; padding:12px 8px;
                border:2px solid {color}; border-radius:14px;">
      <div style="font-size:1.1rem; color:#555;">{label}</div>
      <div style="font-size:2.8rem; font-weight:700; color:{color};">{value}</div>
lt;div style="font-size:1.0rem; color:#555;">℃ / 100년</div>
    </div>
    """

st.subheader("🌡️ 100년에 몇 ℃ 오를까?")
col_all, col_recent = st.columns(2)
col_all.markdown(
    big_number(f"전체 기간 ({start_year}–{end_year}년)",
               f"{slope_100:+.2f}", "#e4572e"),
    unsafe_allow_html=True,
)
col_recent.markdown(
    big_number(f"최근 20년 ({recent_start}–{end_year}년)",
               f"{slope_r_100:+.2f}", "#2a9d8f"),
    unsafe_allow_html=True,
)
st.caption(
    f"상관계수 — 전체 기간: r = {r:.3f} · 최근 20년: r = {r_r:.3f}"
)

# ----------------- 연도 슬라이더 & 예측 -----------------
st.subheader("🔮 기온 예측해 보기")
year = st.slider("예측하고 싶은 연도를 고르세요",
                 min_value=1900, max_value=2100, value=2025, step=1)

pred = slope * year + intercept   # 예측은 전체 기간 직선 사용

st.markdown(
    f"""
    <div style="text-align:center; padding:8px 0 4px 0;">
      <div style="font-size:1.4rem;">{year}년 서울의 예상 연평균기온</div>
      <div style="font-size:3.2rem; font-weight:700; color:#e4572e;">{pred:.2f} ℃</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if year > end_year:
    st.caption(f"⚠️ {end_year}년 이후는 자료가 없는 범위라서, 직선을 늘여서 예측(외삽)한 값이에요.")
elif year < start_year:
    st.caption(f"⚠️ {start_year}년 이전도 직선을 늘여서 예측한 값이에요.")

# ----------------- plotly 그래프 -----------------
fig = go.Figure()

# 산점도 (연평균기온)
fig.add_trace(go.Scatter(
    x=x, y=y, mode="markers", name="연평균기온",
    marker=dict(size=7, color="#4c78a8"),
    hovertemplate="%{x:.0f}년 · %{y:.2f}℃<extra></extra>",
))

# 회귀 직선 — 전체 기간 (자료가 있는 구간: 실선)
line_x = np.array([start_year, end_year], dtype=float)
fig.add_trace(go.Scatter(
    x=line_x, y=slope * line_x + intercept,
    mode="lines", name=f"추세선·전체 ({slope_100:+.2f}℃/100년)",
    line=dict(color="#e4572e", width=3),
))

# 예측 구간 (끝 연도 → 2100: 점선)
ext_x = np.array([end_year, 2100], dtype=float)
fig.add_trace(go.Scatter(
    x=ext_x, y=slope * ext_x + intercept,
    mode="lines", name="예측 구간",
    line=dict(color="#e4572e", width=3, dash="dot"),
))

# 회귀 직선 — 최근 20년 (녹색 점선)
fig.add_trace(go.Scatter(
    x=rx, y=slope_r * rx + intercept_r,
    mode="lines", name=f"추세선·최근 20년 ({slope_r_100:+.2f}℃/100년)",
    line=dict(color="#2a9d8f", width=3, dash="dash"),
))

# 선택한 연도의 예측값 표시
fig.add_trace(go.Scatter(
    x=[year], y=[pred], mode="markers+text", name=f"{year}년 예측",
    text=[f"{pred:.1f}℃"], textposition="top center",
    marker=dict(size=14, color="#f2b134", symbol="star",
                line=dict(color="#8a6d00", width=1)),
))

fig.update_layout(
    title="서울 연평균기온 추세와 회귀 직선",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    height=560,
    margin=dict(l=40, r=40, t=60, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)

st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption(f"자료 출처: 서울 기상관측 데이터 — {LAST_YEAR}년까지, 관측일 {MIN_DAYS}일 이상인 해만 사용")
