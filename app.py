import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Advanced Crypto Volatility Dashboard",
    layout="wide",
    page_icon="🚀"
)

# ---------------------------------------------------
# CUSTOM CSS FOR AESTHETIC LOOK
# ---------------------------------------------------
st.markdown("""
<style>
.big-font {
    font-size:28px !important;
    font-weight: bold;
}
.metric-card {
    background-color: #111827;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🚀 Advanced Crypto Volatility Visualizer</p>', unsafe_allow_html=True)
st.markdown("Mathematics for AI – FA-2 Deployment Project")

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("crypto_data.csv")
        df.columns = df.columns.str.strip()
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        df = df.dropna()
        df = df.sort_values("Timestamp")
        return df
    except:
        return None

df = load_data()

if df is None:
    st.error("CSV file not found. Make sure crypto_data.csv is in same folder.")
    st.stop()

# ---------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------
st.sidebar.header("⚙️ Dashboard Controls")

crypto_list = df["Crypto"].unique()
selected_crypto = st.sidebar.selectbox("Select Cryptocurrency", crypto_list)

pattern = st.sidebar.selectbox(
    "Select Mode",
    ["Real Market Data", "Wave Simulation", "Random Volatility"]
)

amplitude = st.sidebar.slider("Amplitude", 1, 100, 20)
frequency = st.sidebar.slider("Frequency", 1, 10, 3)
drift = st.sidebar.slider("Drift", -5, 5, 0)

# Filter selected crypto
df = df[df["Crypto"] == selected_crypto]

# ---------------------------------------------------
# SIMULATION
# ---------------------------------------------------
t = np.arange(len(df))

if pattern == "Wave Simulation":
    df["Simulated"] = amplitude * np.sin(frequency * t * 0.1) + drift * t + df["Close"].mean()
    price_column = "Simulated"
elif pattern == "Random Volatility":
    noise = np.random.normal(0, amplitude, len(df))
    df["Simulated"] = df["Close"] + noise + drift * t
    price_column = "Simulated"
else:
    price_column = "Close"

# ---------------------------------------------------
# MOVING AVERAGES
# ---------------------------------------------------
df["MA20"] = df[price_column].rolling(window=3).mean()
df["MA50"] = df[price_column].rolling(window=5).mean()

# ---------------------------------------------------
# METRICS
# ---------------------------------------------------
volatility = df[price_column].std()
avg_price = df[price_column].mean()
max_price = df[price_column].max()
min_price = df[price_column].min()

if volatility < 200:
    status = "🟢 Stable"
elif volatility < 800:
    status = "🟡 Moderate"
else:
    status = "🔴 Highly Volatile"

st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Price", f"${avg_price:,.2f}")
col2.metric("Volatility Index", f"{volatility:,.2f}")
col3.metric("Maximum Price", f"${max_price:,.2f}")
col4.metric("Minimum Price", f"${min_price:,.2f}")

st.info(f"Market Condition: {status}")

# ---------------------------------------------------
# CANDLESTICK CHART
# ---------------------------------------------------
st.subheader("🕯️ Candlestick Chart")

fig_candle = go.Figure(data=[go.Candlestick(
    x=df['Timestamp'],
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close']
)])

fig_candle.update_layout(title=f"{selected_crypto} Price Chart")

st.plotly_chart(fig_candle, use_container_width=True)

# ---------------------------------------------------
# LINE CHART WITH MOVING AVERAGES
# ---------------------------------------------------
st.subheader("📈 Price with Moving Averages")

fig_line = go.Figure()
fig_line.add_trace(go.Scatter(x=df["Timestamp"], y=df[price_column],
                              mode="lines", name="Price"))
fig_line.add_trace(go.Scatter(x=df["Timestamp"], y=df["MA20"],
                              mode="lines", name="MA20"))
fig_line.add_trace(go.Scatter(x=df["Timestamp"], y=df["MA50"],
                              mode="lines", name="MA50"))

st.plotly_chart(fig_line, use_container_width=True)

# ---------------------------------------------------
# VOLUME CHART
# ---------------------------------------------------
st.subheader("📦 Volume Analysis")

fig_volume = px.bar(df, x="Timestamp", y="Volume",
                    title="Trading Volume")

st.plotly_chart(fig_volume, use_container_width=True)

# ---------------------------------------------------
# VOLATILITY DISTRIBUTION
# ---------------------------------------------------
st.subheader("🔥 Price Distribution")

fig_hist = px.histogram(df, x=price_column, nbins=20)
st.plotly_chart(fig_hist, use_container_width=True)

# ---------------------------------------------------
# RAW DATA
# ---------------------------------------------------
if st.checkbox("Show Raw Data"):
    st.dataframe(df)

st.success("✅ Professional Crypto Dashboard Running Successfully 🚀")