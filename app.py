import streamlit as st
import pandas as pd
import yfinance as yf
import ta as ta_indicators
from datetime import datetime

# Page configuration
st.set_page_config(page_title="MasterPro Premium Scalper", layout="wide")

# Custom UI Styling (Dark Premium Glassmorphism Theme)
st.markdown("""
<style>
    body {
        color: #f8fafc;
    }
    .header-box {
        background: linear-gradient(135deg, #1e1b4b, #311042); 
        padding: 30px; 
        border-radius: 16px; 
        color: white; 
        text-align: center; 
        border: 1px solid #4338ca;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: #1e293b;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 15px;
    }
    .buy-title {
        background: #065f46; 
        color: #a7f3d0; padding: 12px; border-radius: 8px 8px 0 0; 
        font-weight: bold; text-align: center; font-size: 18px;
        margin-top: 10px;
    }
    .sell-title {
        background: #991b1b; 
        color: #fca5a5; padding: 12px; border-radius: 8px 8px 0 0; 
        font-weight: bold; text-align: center; font-size: 18px;
        margin-top: 10px;
    }
    .footer-text {
        text-align: center; color: #64748b; font-size: 12px; margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Header Interface
st.markdown('<div class="header-box"><h1>⚡ MASTERPRO PRO-SCALPER</h1><p>⚡ Real-time Index Options & Midcap Smart Trading Dashboard</p></div>', unsafe_allow_html=True)

# Sidebar Interface
st.sidebar.markdown("### 🛠️ Control Panel")
segment_choice = st.sidebar.radio("⚡ Select Market Segment", ["Index Options (Spot)", "Live Option Premiums (High Volume)", "Midcap Stocks Only"])
tf_choice = st.sidebar.selectbox("⏱️ Select Scalping Candle", ["1m", "5m", "15m"], index=1)

# Status Metrics on Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Strategy Rules")
st.sidebar.info("• BUY/CE: EMA Trend Up + Price > VWAP + RSI > 55\n• SELL/PE: EMA Trend Down + Price < VWAP + RSI < 45")

# Mapping periods safely
period_map = {"1m": "7d", "5m": "5d", "15m": "5d"}
data_period = period_map[tf_choice]

# Tickers Definition
indices_map = {
    "NIFTY 50 (SPOT)": "^NSEI",
    "BANK NIFTY (SPOT)": "^NSEBANK",
    "FIN NIFTY (SPOT)": "NIFTY-FIN-SERVICE.NS",
    "MIDCAP NIFTY (SPOT)": "NIFTY-MID-SELECT.NS"
}

tv_indices_map = {
    "^NSEI": "NSE:NIFTY",
    "^NSEBANK": "NSE:BANKNIFTY",
    "NIFTY-FIN-SERVICE.NS": "NSE:CNXFINANCE",
    "NIFTY-MID-SELECT.NS": "NSE:MIDCPNIFTY"
}

# 🚨 ഓട്ടോമാറ്റിക് ആയി ഏറ്റവും പുതിയ പ്രധാനപ്പെട്ട ഓപ്ഷൻ പ്രീമിയം ലിസ്റ്റ് ക്രിയേറ്റ് ചെയ്യാനുള്ള ലോജിക്
# വോളിയം കൂടുതലുള്ള എടിഎം (ATM) സ്ട്രൈക്കുകൾ ഡൈനാമിക് ആയി ഇവിടെ ജനറേറ്റ് ചെയ്യാം
current_year_short = datetime.now().strftime("%y") # '26'
current_month_short = datetime.now().strftime("%b").upper() # 'MAY' / 'JUN'

# സാധാരണയായി എപ്പോഴും ട്രേഡിംഗ് നടക്കുന്ന റൗണ്ട് സ്ട്രൈക്കുകളുടെ ലിസ്റ്റ്
nifty_strikes = [22800, 22900, 23000, 23100, 23200, 23300, 23400, 23500]
banknifty_strikes = [49000, 49200, 49500, 49800, 50000, 50200, 50500, 51000]

options_premium_map = {}

# മന്ത്‌ലി കോൺട്രാക്റ്റുകൾ ട്രാക്ക് ചെയ്യാൻ യാഹൂ ഫോർമാറ്റ് ബിൽഡ് ചെയ്യുന്നു
for strike in nifty_strikes:
    options_premium_map[f"NIFTY {strike} CE"] = f"NIFTY{current_year_short}{current_month_short}{strike}CE.NS"
    options_premium_map[f"NIFTY {strike} PE"] = f"NIFTY{current_year_short}{current_month_short}{strike}PE.NS"

for strike in banknifty_strikes:
    options_premium_map[f"BANKNIFTY {strike} CE"] = f"BANKNIFTY{current_year_short}{current_month_short}{strike}CE.NS"
    options_premium_map[f"BANKNIFTY {strike} PE"] = f"BANKNIFTY{current_year_short}{current_month_short}{strike}PE.NS"


midcap_stocks = [
    "MAXHEALTH", "YESBANK", "IDFCFIRSTB", "GMRINFRA", "IDEA", "RVNL", "IRFC", "SUZLON", "ZOMATO", "NYKAA",
    "PAYTM", "CONCOR", "POLYCAB", "PERSISTENT", "OBEROIRLTY", "KPITtech", "TATACOMM", "COFORGE", "MPHASIS", "DIXON",
    "AUBANK", "FEDERALBNK", "VOLTAS", "CUMMINSIND", "ASHOKLEY", "BALKRISIND", "MRF", "ASTRAL", "SUPREMEIND", "KEI"
]

if segment_choice == "Index Options (Spot)":
    symbols_to_scan = list(indices_map.values())
    display_names = indices_map
elif segment_choice == "Live Option Premiums (High Volume)":
    symbols_to_scan = list(options_premium_map.values())
    display_names = options_premium_map
else:
    symbols_to_scan = [f"{sym}.NS" for sym in midcap_stocks]
    display_names = {f"{sym}.NS": sym for sym in midcap_stocks}

buy_signals = []
sell_signals = []

# Top Stats Row on Main Screen
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.markdown(f'<div class="metric-card">🎯 <b>Segment</b><br><span style="font-size:20px; color:#3b82f6; font-weight:bold;">{segment_choice}</span></div>', unsafe_allow_html=True)
with m_col2:
    st.markdown(f'<div class="metric-card">⏱️ <b>Timeframe</b><br><span style="font-size:20px; color:#e2e8f0; font-weight:bold;">{tf_choice}</span></div>', unsafe_allow_html=True)
with m_col3:
    if st.button("🔄 FORCE REFRESH DATA", use_container_width=True):
        st.rerun()

# Bulk Download for Speed
with st.spinner("📥 Downloading Live Market Feeds..."):
    try:
        group_data = yf.download(symbols_to_scan, period=data_period, interval=tf_choice, group_by='ticker', progress=False)
    except Exception as e:
        st.error(f"Connection Error: {e}")
        group_data = None

if group_data is not None and not group_data.empty:
    for sym in symbols_to_scan:
        try:
            if len(symbols_to_scan) == 1:
                df = group_data.dropna().copy()
            else:
                if sym in group_data.columns.levels[0]:
                    df = group_data[sym].dropna().copy()
                else:
                    continue
                
            if df.empty or len(df) < 21: # സൂപ്പർ ഫാസ്റ്റ് സ്കാൽപ്പിംഗിന് മിനിമം കാൻഡിലുകൾ അഡ്ജസ്റ്റ് ചെയ്തു
                continue
                
            # Technical Indicators Calculations
            df['EMA8'] = ta_indicators.trend.ema_indicator(df['Close'], window=8)
            df['EMA13'] = ta_indicators.trend.ema_indicator(df['Close'], window=13)
            df['EMA21'] = ta_indicators.trend.ema_indicator(df['Close'], window=21)
            
            typical_price = (df['High'] + df['Low'] + df['Close']) / 3
            
            if 'Volume' in df.columns and df['Volume'].sum() > 0:
                df['VWAP'] = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
            else:
                df['VWAP'] = df['Close']
            
            df['RSI'] = ta_indicators.momentum.rsi(df['Close'], window=14)
            df['MACD'] = ta_indicators.trend.macd(df['Close'], window_fast=12, window_slow=26)
            df['MACD_Signal'] = ta_indicators.trend.macd_signal(df['Close'], window_fast=12, window_slow=26, window_sign=9)
            
            latest = df.iloc[-1]
            
            ltp = float(latest['Close'])
            rsi_val = float(latest['RSI'])
            vwap_val = float(latest['VWAP'])
            volume_val = float(latest['Volume']) if 'Volume' in latest else 0
            
            ema8_val = float(latest['EMA8'])
            ema13_val = float(latest['EMA13'])
            ema21_val = float(latest['EMA21'])
            macd_val = float(latest['MACD'])
            macd_sig = float(latest['MACD_Signal'])

            # Fast Scalping Logic for Options & Spot
            buy_condition = (ema8_val > ema13_val > ema21_val) and (ltp >= vwap_val) and (rsi_val > 55) and (macd_val > macd_sig)
            sell_condition = (ema8_val < ema13_val < ema21_val) and (ltp <= vwap_val) and (rsi_val < 45) and (macd_val < macd_sig)
            
            clean_name = "Unknown"
            tv_symbol = ""
            
            # കറക്റ്റ് പേരും ട്രേഡിംഗ് വ്യൂ ടിക്കറും കണ്ടെത്തുന്നു
            if segment_choice == "Index Options (Spot)":
                for name, ticker in display_names.items():
                    if ticker == sym:
                        clean_name = name
                        tv_symbol = tv_indices_map.get(ticker, "NSE:NIFTY")
            elif segment_choice == "Live Option Premiums (High Volume)":
                for name, ticker in display_names.items():
                    if ticker == sym:
                        clean_name = name
                        # യാഹൂ ഓപ്ഷൻ ടിക്കറിനെ ട്രേഡിംഗ് വ്യൂ ഫോർമാറ്റിലേക്ക് മാറ്റുന്നു
                        tv_symbol = sym.replace(".NS", "")
            else:
                clean_name = display_names[sym]
                tv_symbol = f"NSE:{clean_name}"
            
            tv_link = f"https://in.tradingview.com/chart/?symbol={tv_symbol}"
            
            stock_data = {
                "Asset Name": clean_name,
                "TradingView": tv_link,
                "LTP": round(ltp, 2),
                "RSI": round(rsi_val, 1),
                "VWAP": round(vwap_val, 2),
                "Volume": int(volume_val)
            }
            
            # ഓപ്ഷൻ സെഗ്മെന്റിൽ വോളിയം കുറഞ്ഞ പ്രീമിയങ്ങൾ ഒഴിവാക്കാനുള്ള ഫിൽട്ടർ
            if segment_choice == "Live Option Premiums (High Volume)" and volume_val < 500:
                continue
                
            if buy_condition:
                buy_signals.append(stock_data)
            elif sell_condition:
                sell_signals.append(stock_data)
        except:
            pass

    # Dashboard Signals Display
    col1, col2 = st.columns(2)

    link_config = {
        "TradingView": st.column_config.LinkColumn(
            "📈 Open Chart",
            display_text="View Chart ↗"
        )
    }

    with col1:
        if segment_choice == "Index Options (Spot)":
            st.markdown('<div class="buy-title">🟢 CALL OPTION (CE) - BUY SIGNALS</div>', unsafe_allow_html=True)
        elif segment_choice == "Live Option Premiums (High Volume)":
            st.markdown('<div class="buy-title">🟢 OPTIONS BULLISH BREAKOUT (BUY)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="buy-title">🟢 STOCKS BULLISH MOMENTUM</div>', unsafe_allow_html=True)
            
        if buy_signals:
            st.dataframe(pd.DataFrame(buy_signals), use_container_width=True, hide_index=True, column_config=link_config)
        else:
            st.info("No Bullish Scalping setups found right now.")

    with col2:
        if segment_choice == "Index Options (Spot)":
            st.markdown('<div class="sell-title">🔴 PUT OPTION (PE) - BUY SIGNALS</div>', unsafe_allow_html=True)
        elif segment_choice == "Live Option Premiums (High Volume)":
            st.markdown('<div class="sell-title">🔴 OPTIONS BEARISH MOMENTUM (SHORT)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="sell-title">🔴 STOCKS BEARISH MOMENTUM</div>', unsafe_allow_html=True)
            
        if sell_signals:
            st.dataframe(pd.DataFrame(sell_signals), use_container_width=True, hide_index=True, column_config=link_config)
        else:
            st.info("No Bearish Scalping setups found right now.")

st.markdown('<div class="footer-text">MasterPro Scalper Tool v2.5 • Designed for High-Speed Execution</div>', unsafe_allow_html=True)
