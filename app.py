import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ----------------- 기본 설정 -----------------
st.set_page_config(page_title="기온 예측기", page_icon="🌡️", layout="centered")

CSV_URL = "https://raw.githubusercontent.com/greatsong/modudata/bb860932644270ad1199f10d3e7670e30231bce4/data/seoul.csv"
LAST_YEAR = 2025   # 기준 기간의 마지막 해
MIN_DAYS = 300     # 이 날짜 수보다 적은 해는 제외

# ----------------- 디자인용 CSS -----------------
st.markdown("""
<risu-style>0a40696d706f72742075726c282768747470733a2f2f666f6e74732e676f6f676c65617069732e636f6d2f637373323f66616d696c793d4e6f746f2b53616e732b4b523a77676874403430303b3530303b3730303b39303026646973706c61793d7377617027293b0a0a68746d6c2c20626f64792c205b636c6173732a3d22637373225d207b20666f6e742d66616d696c793a274e6f746f2053616e73204b52272c2073616e732d73657269663b207d0a2e626c6f636b2d636f6e7461696e6572207b206d61782d77696474683a2039383070783b2070616464696e672d746f703a20312e3572656d3b207d0a0a2f2a20ec8381eb8ba820ebb0b0eb8488202a2f0a2e6865726f207b0a20206261636b67726f756e643a206c696e6561722d6772616469656e74283132306465672c20236637623236372030252c2023663438343566203430252c2023653435373265203735252c20236134313333632031303025293b0a2020626f726465722d7261646975733a20323470783b2070616464696e673a203330707820333470783b20636f6c6f723a236666663b0a2020626f782d736861646f773a2030203132707820333270782072676261283232382c38372c34362c2e3330293b0a20206d617267696e2d626f74746f6d3a20333070783b0a7d0a2e6865726f202e74207b20666f6e742d73697a653a20322e3172656d3b20666f6e742d7765696768743a203930303b206c65747465722d73706163696e673a2d2e3570783b207d0a2e6865726f202e73207b20666f6e742d73697a653a20312e303272656d3b206f7061636974793a2e39323b206d617267696e2d746f703a3670783b207d0a0a2f2a20ec868ceca09cebaaa9202a2f0a2e736563207b0a2020666f6e742d73697a653a312e323272656d3b20666f6e742d7765696768743a3930303b20636f6c6f723a233164333535373b0a2020626f726465722d6c6566743a36707820736f6c696420236534353732653b2070616464696e672d6c6566743a313070783b0a20206d617267696e3a323670782030203134707820303b0a7d0a0a2f2a20ec9e91ec9d8020eca095ebb3b420ecb9b4eb939c202a2f0a2e63617264207b0a2020626f726465722d7261646975733a20313870783b2070616464696e673a203136707820313270783b20746578742d616c69676e3a63656e7465723b0a20206261636b67726f756e643a236666663b20626f726465723a31707820736f6c696420236630663066303b0a2020626f782d736861646f773a203020387078203230707820726762612833302c33302c36302c2e3037293b0a7d0a2e63617264202e6b207b20666f6e742d73697a653a2e393572656d3b20636f6c6f723a233636373b207d0a2e63617264202e76207b20666f6e742d73697a653a312e3672656d3b20666f6e742d7765696768743a3930303b20636f6c6f723a233164333535373b206d617267696e2d746f703a3270783b207d0a0a2f2a20eab8b0ec9ab8eab8b020ebb984eab59020ecb9b4eb939c202a2f0a2e736c6f70652d63617264207b20626f726465722d7261646975733a20323270783b2070616464696e673a203236707820313870783b20746578742d616c69676e3a63656e7465723b207d0a2e736c6f70652d636172642e7761726d207b206261636b67726f756e643a206c696e6561722d6772616469656e74283133356465672c236666663165362c23666665306363293b20626f726465723a32707820736f6c696420236634613236313b207d0a2e736c6f70652d636172642e636f6f6c207b206261636b67726f756e643a206c696e6561722d6772616469656e74283133356465672c236539663666342c23643765666563293b20626f726465723a32707820736f6c696420233261396438663b207d0a2e736c6f70652d63617264202e6c6162207b20666f6e742d73697a653a312e303272656d3b20636f6c6f723a233535363b20666f6e742d7765696768743a3730303b207d0a2e736c6f70652d63617264202e6e756d207b20666f6e742d73697a653a3372656d3b20666f6e742d7765696768743a3930303b206c65747465722d73706163696e673a2d3170783b206d617267696e3a34707820303b207d0a2e736c6f70652d636172642e7761726d202e6e756d207b20636f6c6f723a236439346632623b207d0a2e736c6f70652d636172642e636f6f6c202e6e756d207b20636f6c6f723a233166376136663b207d0a2e736c6f70652d63617264202e756e6974207b20666f6e742d73697a653a312e3072656d3b20636f6c6f723a233636373b207d0a0a2f2a20ec9888ecb8a120ecb9b4eb939c202a2f0a2e707265642d63617264207b0a2020626f726465722d7261646975733a20323470783b20746578742d616c69676e3a63656e7465723b20636f6c6f723a236666663b0a20206261636b67726f756e643a206c696e6561722d6772616469656e74283133356465672c20233164333535372030252c2023326135373838203630252c20233435376239642031303025293b0a2020626f782d736861646f773a20302031327078203330707820726762612832392c35332c38372c2e3335293b0a202070616464696e673a203236707820323070783b0a7d0a2e707265642d63617264202e6c6162207b20666f6e742d73697a653a312e313572656d3b206f7061636974793a2e39323b207d0a2e707265642d63617264202e6e756d207b20666f6e742d73697a653a342e3272656d3b20666f6e742d7765696768743a3930303b206c696e652d6865696768743a312e31353b206c65747465722d73706163696e673a2d3170783b207d0a2e707265642d63617264202e6e756d202e646567207b20666f6e742d73697a653a3272656d3b20666f6e742d7765696768743a3730303b207d0a2e707265642d63617264202e737562207b20666f6e742d73697a653a2e393272656d3b206f7061636974793a2e37353b206d617267696e2d746f703a3470783b207d0a0a2f2a20ed91b8ed84b0202a2f0a2e666f6f74207b20746578742d616c69676e3a63656e7465723b20636f6c6f723a233838393b20666f6e742d73697a653a2e383572656d3b206d617267696e2d746f703a323870783b207d0a</risu-style>
""", unsafe_allow_html=True)

# ----------------- 상단 배너 -----------------
st.markdown("""
<div class="hero">
  <div class="t">🌡️ 서울 기온 예측기</div>
  <div class="s">100여 년에 걸친 서울의 연평균기온 자료로 우리 도시가 얼마나 따뜻해지는지 확인하고, 미래 기온을 예측해 봅시다.</div>
</div>
""", unsafe_allow_html=True)


# ----------------- 데이터 불러오기 -----------------
@st.cache_data(show_spinner="서울 기온 데이터를 불러오는 중...")
def load_data():
    df = pd.read_csv(CSV_URL, encoding="utf-8")
    df["날짜"] = pd.to_datetime(df["날짜"])
    df["연도"] = df["날짜"].dt.year
    return df


try:
    raw = load_data()
except Exception as e:
    st.error(f"데이터를 불러오지 못했어요. 인터넷 연결을 확인해 주세요. ({e})")
    st.stop()

# ----------------- 연도별 평균기온 -----------------
yearly = (
    raw.dropna(subset=["평균기온"])
    .groupby("연도")["평균기온"]
    .agg(관측일수="count", 연평균기온="mean")
    .reset_index()
)
yearly = yearly[
    (yearly["연도"] <= LAST_YEAR) & (yearly["관측일수"] >= MIN_DAYS)
].reset_index(drop=True)

if len(yearly) < 2:
    st.error("조건에 맞는 자료가 너무 적어요. 데이터를 확인해 주세요.")
    st.stop()

x = yearly["연도"].to_numpy(dtype=float)
y = yearly["연평균기온"].to_numpy(dtype=float)

# ----------------- 회귀 (전체 기간) -----------------
slope, intercept = np.polyfit(x, y, 1)
r = np.corrcoef(x, y)[0, 1]
slope_100 = slope * 100

start_year = int(yearly["연도"].min())
end_year = int(yearly["연도"].max())
n_years = len(yearly)

# ----------------- 회귀 (최근 20년) -----------------
recent = yearly.tail(20)
rx = recent["연도"].to_numpy(dtype=float)
ry = recent["연평균기온"].to_numpy(dtype=float)
recent_start = int(recent["연도"].min())

slope_r, intercept_r = np.polyfit(rx, ry, 1)
r_r = np.corrcoef(rx, ry)[0, 1]
slope_r_100 = slope_r * 100

# ----------------- 자료 정보 카드 -----------------
st.markdown('<div class="sec">📌 회귀 직선을 만든 자료</div>', unsafe_allow_html=True)

def mini(label, value, color="#1d3557"):
    return f'<div class="card"><div class="k">{label}</div><div class="v" style="color:{color}">{value}</div></div>'

m1, m2, m3, m4 = st.columns(4)
m1.markdown(mini("사용한 해", f"{n_years}년"), unsafe_allow_html=True)
m2.markdown(mini("시작 연도", f"{start_year}년"), unsafe_allow_html=True)
m3.markdown(mini("끝 연도", f"{end_year}년"), unsafe_allow_html=True)
m4.markdown(mini("상관계수 r", f"{r:.3f}", "#d94f2b"), unsafe_allow_html=True)

# ----------------- 100년당 상승 속도 비교 -----------------
st.markdown('<div class="sec">🌡️ 100년에 몇 ℃ 오를까?</div>', unsafe_allow_html=True)

left, right = st.columns(2, gap="medium")
left.markdown(f"""
<div class="slope-card warm">
  <div class="lab">📅 전체 기간 ({start_year}–{end_year}년)</div>
  <div class="num">{slope_100:+.2f}</div>
  <div class="unit">℃ / 100년 · r = {r:.3f}</div>
</div>""", unsafe_allow_html=True)

right.markdown(f"""
<div class="slope-card cool">
  <div class="lab">🔥 최근 20년 ({recent_start}–{end_year}년)</div>
  <div class="num">{slope_r_100:+.2f}</div>
  <div class="unit">℃ / 100년 · r = {r_r:.3f}</div>
</div>""", unsafe_allow_html=True)

st.caption("💡 두 숫자가 다른 이유를 생각해 봅시다. 최근 들어 온도 상승이 빨라졌을까요?")

# ----------------- 연도 슬라이더 & 예측 -----------------
st.markdown('<div class="sec">🔮 기온 예측해 보기</div>', unsafe_allow_html=True)

year = st.slider("예측하고 싶은 연도를 고르세요",
                 min_value=1900, max_value=2100, value=2025, step=1)

pred = slope * year + intercept

emoji = "🥶" if pred < 11 else "😊" if pred < 12.5 else "🙂" if pred < 14 else "😅" if pred < 15.5 else "🥵"

st.markdown(f"""
<div class="pred-card">
  <div class="lab">{year}년 서울의 예상 연평균기온 {emoji}</div>
  <div class="num">{pred:.2f}<span class="deg"> ℃</span></div>
  <div class="sub">전체 기간 추세선을 이용해 계산한 값이에요.</div>
</div>
""", unsafe_allow_html=True)

if year > end_year:
    st.caption(f"⚠️ {end_year}년 이후는 자료가 없는 범위라서, 직선을 늘여서 예측(외삽)한 값이에요.")
elif year < start_year:
    st.caption(f"⚠️ {start_year}년 이전도 직선을 늘여서 예측한 값이에요.")

# ----------------- plotly 그래프 -----------------
fig = go.Figure()

# 최근 20년 구간 음영 표시
fig.add_vrect(x0=recent_start, x1=end_year,
              fillcolor="#2a9d8f", opacity=0.07, line_width=0)

# 산점도 — 기온이 높을수록 따뜻한 색
fig.add_trace(go.Scatter(
    x=x, y=y, mode="markers", name="연평균기온",
    marker=dict(
        size=9, color=y, opacity=0.9,
        colorscale=[[0, "#457b9d"], [0.5, "#ffd166"], [1, "#e63946"]],
        line=dict(width=1, color="white"),
        colorbar=dict(title="℃", thickness=12, outlinewidth=0),
    ),
    hovertemplate="%{x:.0f}년 · %{y:.2f}℃<extra></extra>",
))

# 추세선 — 전체 기간 (실선)
line_x = np.array([start_year, end_year], dtype=float)
fig.add_trace(go.Scatter(
    x=line_x, y=slope * line_x + intercept,
    mode="lines", name=f"추세선·전체 ({slope_100:+.2f}℃/100년)",
    line=dict(color="#e4572e", width=3.5),
))

# 예측 구간 (점선)
ext_x = np.array([end_year, 2100], dtype=float)
fig.add_trace(go.Scatter(
    x=ext_x, y=slope * ext_x + intercept,
    mode="lines", name="예측 구간",
    line=dict(color="#e4572e", width=3, dash="dot"),
))

# 추세선 — 최근 20년 (점선)
fig.add_trace(go.Scatter(
    x=rx, y=slope_r * rx + intercept_r,
    mode="lines", name=f"추세선·최근 20년 ({slope_r_100:+.2f}℃/100년)",
    line=dict(color="#2a9d8f", width=3, dash="dash"),
))

# 선택한 연도의 예측 표시
fig.add_trace(go.Scatter(
    x=[year], y=[pred], mode="markers+text", name=f"{year}년 예측",
    text=[f"{pred:.1f}℃"], textposition="top center",
    textfont=dict(size=15, color="#1d3557", family="Noto Sans KR"),
    marker=dict(size=16, color="#ffd166", symbol="star",
                line=dict(color="#b07d00", width=1.5)),
))

fig.update_layout(
    template="plotly_white",
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Noto Sans KR, sans-serif", size=13, color="#333"),
    title=dict(text="📈 서울 연평균기온 추세와 회귀 직선", font=dict(size=18)),
    xaxis=dict(title="연도", gridcolor="#eef0f3", zeroline=False),
    yaxis=dict(title="평균기온 (℃)", gridcolor="#eef0f3", zeroline=False),
    height=580,
    margin=dict(l=50, r=20, t=70, b=50),
    legend=dict(orientation="h", yanchor="bottom", y=1.01,
                bgcolor="rgba(255,255,255,.65)"),
    hoverlabel=dict(bgcolor="white", font_size=13, font_family="Noto Sans KR"),
)

st.plotly_chart(fig, use_container_width=True)

# ----------------- 푸터 -----------------
st.markdown(
    f'<div class="foot">자료 출처: 서울 기상관측 데이터(기상청) · 기준: {LAST_YEAR}년까지, 관측일 {MIN_DAYS}일 이상인 해 · 예측값은 직선 외삽이므로 참고용</div>',
    unsafe_allow_html=True,
)
