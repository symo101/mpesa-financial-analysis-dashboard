import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#Page config
st.set_page_config(
    page_title="M-Pesa Financial Dashboard",
    layout="wide"
)

st.markdown("""
<style>
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #4CAF50;
    }
    .metric-value { font-size: 26px; font-weight: bold; color: #2E7D32; }
    .metric-label { font-size: 13px; color: #666; margin-top: 4px; }
    .metric-delta { font-size: 12px; color: #388E3C; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)


#Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("mpesa_data.csv", parse_dates=["date"])

    # Annual summary for growth calculations
    annual = df.groupby("year").agg(
        total_value   = ("transaction_value_kes_billions",  "sum"),
        total_volume  = ("transaction_volume_millions",     "sum"),
        avg_agents    = ("active_agents",                   "mean"),
        avg_accounts  = ("registered_accounts_millions",    "mean"),
        avg_inclusion = ("financial_inclusion_pct",         "mean"),
    ).reset_index()
    annual["value_growth_pct"]  = annual["total_value"].pct_change()  * 100
    annual["volume_growth_pct"] = annual["total_volume"].pct_change() * 100
    annual["agents_growth_pct"] = annual["avg_agents"].pct_change()   * 100

    return df, annual

df, annual = load_data()

#HEADER
st.title("M-Pesa Financial Dashboard")
st.markdown("**CBK Official Data · Monthly 2017–2024 · 96 data points · Kenya Mobile Money**")
st.markdown("---")

#  SIDEBAR
st.sidebar.header("⚙️ Controls")

years = sorted(df["year"].unique())
year_range = st.sidebar.slider(
    "Year Range",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=(int(min(years)), int(max(years)))
)

filtered = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

st.sidebar.markdown("---")
st.sidebar.markdown("**Data Source:** Central Bank of Kenya")
st.sidebar.markdown("**Period:** Monthly 2017–2024")
st.sidebar.markdown("**Built by:** Simon")
st.sidebar.markdown("**GitHub:** [symo101](https://github.com/symo101)")

#  TOP METRICS — based on 2024 annual totals
latest = annual[annual["year"] == 2024].iloc[0]
prev   = annual[annual["year"] == 2023].iloc[0]

col1, col2, col3, col4 = st.columns(4)

with col1:
    g = ((latest["total_value"] - prev["total_value"]) / prev["total_value"] * 100)
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">KES {latest['total_value']:,.0f}B</div>
        <div class="metric-label">Total Value 2024</div>
        <div class="metric-delta">▲ {g:.1f}% from 2023</div>
    </div>""", unsafe_allow_html=True)

with col2:
    g2 = ((latest["total_volume"] - prev["total_volume"]) / prev["total_volume"] * 100)
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{latest['total_volume']:,.0f}M</div>
        <div class="metric-label">Transactions 2024</div>
        <div class="metric-delta">▲ {g2:.1f}% from 2023</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{latest['avg_agents']:,.0f}</div>
        <div class="metric-label">Avg Active Agents 2024</div>
        <div class="metric-delta">All-time high</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{latest['avg_inclusion']:.0f}%</div>
        <div class="metric-label">Financial Inclusion 2024</div>
        <div class="metric-delta">Up from 75.3% in 2017</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

#  TABS
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Transaction Trends",
    "👥 Agents & Accounts",
    "💹 Growth Rates",
    "🏦 Economic Impact"
])


#TAB 1: Transaction Trends
with tab1:
    # Monthly value line chart
    fig = px.line(
        filtered, x="date", y="transaction_value_kes_billions",
        title="Monthly Transaction Value (KES Billions) — 2017 to 2024",
        color_discrete_sequence=["#2E7D32"],
        labels={"transaction_value_kes_billions": "KES Billions", "date": "Month"}
    )
    fig.update_traces(line_width=2)
    fig.add_vrect(x0="2020-03-01", x1="2020-09-01",
                  fillcolor="rgba(255,152,0,0.15)", line_width=0,
                  annotation_text="COVID-19 CBK Free Transfers",
                  annotation_position="top left")
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        fig2 = px.line(
            filtered, x="date", y="transaction_volume_millions",
            title="Monthly Transaction Volume (Millions)",
            color_discrete_sequence=["#1565C0"],
            labels={"transaction_volume_millions": "Millions", "date": "Month"}
        )
        fig2.update_traces(line_width=2)
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        # Annual totals bar chart
        ann_filtered = annual[(annual["year"] >= year_range[0]) &
                              (annual["year"] <= year_range[1])]
        fig3 = px.bar(
            ann_filtered, x="year", y="total_value",
            title="Annual Transaction Value (KES Billions)",
            color="total_value",
            color_continuous_scale="Greens",
            text="total_value",
            labels={"total_value": "KES Billions", "year": "Year"}
        )
        fig3.update_traces(texttemplate="%{text:,.0f}B", textposition="outside")
        fig3.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)


#TAB 2: Agents & Accounts
with tab2:
    col_a, col_b = st.columns(2)

    with col_a:
        fig = px.area(
            filtered, x="date", y="active_agents",
            title="Active M-Pesa Agents Over Time",
            color_discrete_sequence=["#4CAF50"],
            labels={"active_agents": "Active Agents", "date": "Month"}
        )
        fig.update_traces(fillcolor="rgba(76,175,80,0.2)", line_color="#2E7D32")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig2 = px.area(
            filtered, x="date", y="registered_accounts_millions",
            title="Registered Accounts (Millions)",
            color_discrete_sequence=["#1565C0"],
            labels={"registered_accounts_millions": "Accounts (M)", "date": "Month"}
        )
        fig2.update_traces(fillcolor="rgba(21,101,192,0.2)", line_color="#1565C0")
        st.plotly_chart(fig2, use_container_width=True)

    ann_filtered = annual[(annual["year"] >= year_range[0]) &
                          (annual["year"] <= year_range[1])]
    fig3 = px.bar(
        ann_filtered, x="year", y="avg_inclusion",
        title="Kenya Financial Inclusion Rate (%) by Year",
        color="avg_inclusion",
        color_continuous_scale="Greens",
        text="avg_inclusion",
        labels={"avg_inclusion": "Inclusion %", "year": "Year"}
    )
    fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig3.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

    st.info("Financial inclusion grew from **75.3% in 2017** to **85% in 2024** — largely driven by M-Pesa adoption across rural Kenya.")


#TAB 3: Growth Rates
with tab3:
    ann_filtered = annual[(annual["year"] >= year_range[0]) &
                          (annual["year"] <= year_range[1])].dropna()

    col_a, col_b = st.columns(2)

    with col_a:
        colors = ["#C62828" if v < 0 else "#2E7D32"
                  for v in ann_filtered["value_growth_pct"]]
        fig = go.Figure(go.Bar(
            x=ann_filtered["year"],
            y=ann_filtered["value_growth_pct"].round(1),
            marker_color=colors,
            text=ann_filtered["value_growth_pct"].round(1),
            texttemplate="%{text:.1f}%",
            textposition="outside"
        ))
        fig.update_layout(title="Annual Transaction Value Growth (%)",
                          yaxis_title="Growth %", xaxis_title="Year")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        colors2 = ["#C62828" if v < 0 else "#1565C0"
                   for v in ann_filtered["agents_growth_pct"]]
        fig2 = go.Figure(go.Bar(
            x=ann_filtered["year"],
            y=ann_filtered["agents_growth_pct"].round(1),
            marker_color=colors2,
            text=ann_filtered["agents_growth_pct"].round(1),
            texttemplate="%{text:.1f}%",
            textposition="outside"
        ))
        fig2.update_layout(title="Active Agents Annual Growth (%)",
                           yaxis_title="Growth %", xaxis_title="Year")
        st.plotly_chart(fig2, use_container_width=True)

    # Monthly value heatmap by year and month
    pivot = filtered.pivot_table(
        index="year", columns="month",
        values="transaction_value_kes_billions", aggfunc="sum"
    )
    month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                   7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    pivot.columns = [month_names[m] for m in pivot.columns]

    fig3 = px.imshow(
        pivot, color_continuous_scale="Greens",
        title="Monthly Transaction Value Heatmap (KES Billions)",
        labels={"color": "KES B", "x": "Month", "y": "Year"},
        text_auto=".0f"
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.info("**2020 saw the biggest jump (+19.5%)** — CBK's COVID-19 emergency measures waived mobile money fees, massively boosting usage.")


#TAB 4: Economic Impact
with tab4:
    ann_filtered = annual[(annual["year"] >= year_range[0]) &
                          (annual["year"] <= year_range[1])]

    # GDP estimates (KES Billions)
    gdp = {2017:7745, 2018:8413, 2019:9452, 2020:10411,
           2021:11835, 2022:13032, 2023:14100, 2024:15100}
    ann_filtered = ann_filtered.copy()
    ann_filtered["gdp_kes_billions"] = ann_filtered["year"].map(gdp)
    ann_filtered["value_pct_gdp"]    = (ann_filtered["total_value"] /
                                        ann_filtered["gdp_kes_billions"] * 100)

    col_a, col_b = st.columns(2)

    with col_a:
        fig = px.line(
            ann_filtered, x="year", y="value_pct_gdp",
            title="M-Pesa Transactions as % of Kenya GDP",
            markers=True,
            color_discrete_sequence=["#4CAF50"],
            labels={"value_pct_gdp": "% of GDP", "year": "Year"}
        )
        fig.update_traces(line_width=3, marker_size=10)
        fig.add_hline(y=50, line_dash="dash", line_color="red",
                      annotation_text="50% of GDP")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig2 = px.bar(
            ann_filtered, x="year",
            y=["total_value", "gdp_kes_billions"],
            title="M-Pesa Value vs Kenya GDP (KES Billions)",
            barmode="group",
            color_discrete_map={
                "total_value":       "#4CAF50",
                "gdp_kes_billions":  "#1565C0"
            },
            labels={"value": "KES Billions", "year": "Year", "variable": "Metric"}
        )
        newnames = {"total_value": "M-Pesa Value", "gdp_kes_billions": "Kenya GDP"}
        fig2.for_each_trace(lambda t: t.update(name=newnames.get(t.name, t.name)))
        st.plotly_chart(fig2, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("2024 M-Pesa vs GDP",      "57.6%", "+1.2% from 2023")
    col2.metric("M-Pesa Market Share",     "92.3%", "Dominates Kenya")
    col3.metric("Financial Inclusion 2024","85.0%", "+9.7% since 2017")

    st.info("In 2024, M-Pesa transactions equalled **57.6% of Kenya's GDP** — making it one of the most impactful mobile money systems in the world.")

#  FOOTER
st.markdown("---")
st.markdown(
    "**Data Source:** [Central Bank of Kenya (CBK)](https://www.centralbank.go.ke) · "
    "**Period:** Monthly 2017–2024 · "
    "**Built by:** Simon · "
    "**GitHub:** [symo101](https://github.com/symo101)"
)
