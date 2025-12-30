import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from core.db import init_db, get_conn
from core.data_loader import load_csv
from core.agent_graph import finance_graph

# -------------------------------------------------
# INIT
# -------------------------------------------------
load_dotenv()
init_db()

st.set_page_config(page_title="💰 Cash Management System", layout="wide")
st.title("💰 AI Cash Management System")

# -------------------------------------------------
# SIDEBAR – DATA LOAD
# -------------------------------------------------
with st.sidebar:
    st.header("⚙️ Setup")

    if st.button("📥 Load CSV Data"):
        load_csv("bank_statements", "data/bank_statements.csv")
        load_csv("vendor_invoices", "data/vendor_invoices.csv")
        load_csv("client_invoices", "data/client_invoices.csv")
        load_csv("payroll", "data/payroll.csv")
        load_csv("expense_receipts", "data/expense_receipts.csv")
        st.success("✅ Data Loaded Successfully")

# -------------------------------------------------
# TABS
# -------------------------------------------------
tab_agent, tab_tables, tab_dashboard, tab_alerts = st.tabs(
    ["🤖 Ask Agent", "📋 Data Tables", "📊 Dashboards", "🚨 Alerts"]
)

# =================================================
# 🤖 TAB 1 – ASK AGENT
# =================================================
with tab_agent:
    st.subheader("🤖 Ask the Cash Agent")

    query = st.text_input("Ask about your cash situation")

    if query:
        result = finance_graph.invoke({
            "messages": [HumanMessage(content=query)]
        })
        st.success(result["messages"][-1].content)

# =================================================
# 📋 TAB 2 – DATA TABLES
# =================================================
with tab_tables:
    st.subheader("📋 Financial Data Explorer")

    table = st.selectbox(
        "Select table",
        [
            "bank_statements",
            "vendor_invoices",
            "client_invoices",
            "payroll",
            "expense_receipts"
        ]
    )

    conn = get_conn()
    df = pd.read_sql(f"SELECT * FROM {table} LIMIT 500", conn)
    conn.close()

    st.dataframe(df, use_container_width=True)

# =================================================
# 📊 TAB 3 – DASHBOARDS
# =================================================
with tab_dashboard:
    st.subheader("📊 Cash & Expense Dashboard")

    conn = get_conn()

    # ------------------------------
    # KPI CALCULATIONS
    # ------------------------------
    balance_df = pd.read_sql("""
        SELECT balance_after
        FROM bank_statements
        ORDER BY transaction_date DESC
        LIMIT 1
    """, conn)

    current_balance = balance_df.iloc[0]["balance_after"]

    cash_30d = pd.read_sql("""
        SELECT
            SUM(CASE WHEN transaction_type='CREDIT' THEN amount ELSE 0 END) AS inflow,
            SUM(CASE WHEN transaction_type='DEBIT' THEN amount ELSE 0 END) AS outflow
        FROM bank_statements
        WHERE transaction_date >= date('now', '-30 day')
    """, conn)

    inflow_30d = cash_30d.iloc[0]["inflow"] or 0
    outflow_30d = cash_30d.iloc[0]["outflow"] or 0
    net_change = inflow_30d - outflow_30d

    burn_rate = outflow_30d / 30 if outflow_30d else 0
    runway_days = int(current_balance / burn_rate) if burn_rate else 999

    # ------------------------------
    # KPI CARDS
    # ------------------------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Cash Balance", f"₹{int(current_balance):,}")
    c2.metric("📉 Net Change (30d)", f"₹{int(net_change):,}")
    c3.metric("🔥 Burn / Day", f"₹{int(burn_rate):,}")
    c4.metric("⏳ Cash Runway", f"{runway_days} days")

    # ------------------------------
    # CASH TREND
    # ------------------------------
    cash_trend = pd.read_sql("""
        SELECT
            transaction_date,
            SUM(
                CASE WHEN transaction_type='CREDIT'
                     THEN amount ELSE -amount END
            ) AS net_flow
        FROM bank_statements
        GROUP BY transaction_date
        ORDER BY transaction_date
    """, conn)

    cash_trend["balance"] = cash_trend["net_flow"].cumsum()

    fig1 = px.line(
        cash_trend,
        x="transaction_date",
        y="balance",
        title="Cash Balance Over Time (₹)",
        markers=True
    )

    st.plotly_chart(fig1, use_container_width=True)

    # ------------------------------
    # EXPENSE BREAKDOWN
    # ------------------------------
    expense_df = pd.read_sql("""
        SELECT category, SUM(amount) AS total_spent
        FROM bank_statements
        WHERE transaction_type='DEBIT'
        GROUP BY category
    """, conn)

    fig2 = px.pie(
        expense_df,
        names="category",
        values="total_spent",
        title="Expense Distribution"
    )

    st.plotly_chart(fig2, use_container_width=True)

    # ------------------------------
    # MONTHLY CASH FLOW TABLE
    # ------------------------------
    monthly_df = pd.read_sql("""
        SELECT
            strftime('%Y-%m', transaction_date) AS month,
            SUM(CASE WHEN transaction_type='CREDIT' THEN amount ELSE 0 END) AS inflow,
            SUM(CASE WHEN transaction_type='DEBIT' THEN amount ELSE 0 END) AS outflow
        FROM bank_statements
        GROUP BY month
        ORDER BY month
    """, conn)

    monthly_df["net"] = monthly_df["inflow"] - monthly_df["outflow"]

    st.subheader("📆 Monthly Cash Flow")
    st.dataframe(monthly_df, use_container_width=True)

    # ------------------------------
    # AI EXPLAIN THIS
    # ------------------------------
    if st.button("🧠 Explain Cash Situation"):
        explanation = finance_graph.invoke({
            "messages": [HumanMessage(
                content="Explain the current cash situation and major trends"
            )]
        })
        st.info(explanation["messages"][-1].content)

    st.divider()
    st.subheader("🔮 What-If Scenario Simulator")

    col1, col2, col3 = st.columns(3)

    salary_hike = col1.slider("Salary Increase (%)", 0, 30, 0)
    vendor_hike = col2.slider("Vendor Cost Increase (%)", 0, 30, 0)
    revenue_drop = col3.slider("Revenue Drop (%)", 0, 30, 0)

    conn = get_conn()

    base_df = pd.read_sql("""
        SELECT
            SUM(CASE WHEN transaction_type='CREDIT' THEN amount ELSE 0 END) AS inflow,
            SUM(CASE WHEN transaction_type='DEBIT' THEN amount ELSE 0 END) AS outflow
        FROM bank_statements
        WHERE transaction_date >= date('now', '-30 day')
    """, conn)

    conn.close()

    base_inflow = base_df.iloc[0]["inflow"]
    base_outflow = base_df.iloc[0]["outflow"]

    adjusted_inflow = base_inflow * (1 - revenue_drop / 100)
    adjusted_outflow = base_outflow * (
        1 + (salary_hike + vendor_hike) / 200
    )

    adjusted_burn = adjusted_outflow / 30
    adjusted_runway = int(current_balance / adjusted_burn) if adjusted_burn else 999

    st.metric("📉 Adjusted Monthly Outflow", f"₹{int(adjusted_outflow):,}")
    st.metric("⏳ Adjusted Cash Runway", f"{adjusted_runway} days")

    st.divider()
    st.subheader("🧠 Root Cause Analysis (MoM)")

    conn = get_conn()

    df = pd.read_sql("""
        SELECT
            strftime('%Y-%m', transaction_date) AS month,
            category,
            SUM(amount) AS total
        FROM bank_statements
        WHERE transaction_type='DEBIT'
        GROUP BY month, category
    """, conn)

    conn.close()

    latest_month = df["month"].max()
    previous_month = sorted(df["month"].unique())[-2]

    latest = df[df["month"] == latest_month]
    previous = df[df["month"] == previous_month]

    merged = latest.merge(
        previous,
        on="category",
        how="left",
        suffixes=("_latest", "_prev")
    ).fillna(0)

    merged["delta"] = merged["total_latest"] - merged["total_prev"]
    top_drivers = merged.sort_values("delta", ascending=False).head(5)

    for _, row in top_drivers.iterrows():
        st.write(
            f"- {row['category']}: +₹{int(row['delta'])}"
        )

    st.divider()
    st.subheader("⚠️ Vendor Risk Scoring")

    conn = get_conn()

    vendor_df = pd.read_sql("""
        SELECT
            counterparty_name AS vendor,
            COUNT(*) AS payments,
            SUM(amount) AS total_paid,
            AVG(amount) AS avg_payment
        FROM bank_statements
        WHERE transaction_type='DEBIT'
        GROUP BY vendor
    """, conn)

    conn.close()

    vendor_df["risk_score"] = (
        vendor_df["total_paid"] * 0.5 +
        vendor_df["payments"] * 0.3 +
        vendor_df["avg_payment"] * 0.2
    )

    top_risk = vendor_df.sort_values(
        "risk_score", ascending=False
    ).head(10)

    st.dataframe(
        top_risk[["vendor", "total_paid", "payments", "risk_score"]],
        use_container_width=True
    )

    st.divider()
    st.subheader("📆 90-Day Cash Forecast")

    forecast_days = 90
    forecast_df = []

    balance = current_balance

    for day in range(1, forecast_days + 1):
        balance -= burn_rate
        forecast_df.append({
            "Day": day,
            "Projected Balance": max(balance, 0)
        })

    forecast_df = pd.DataFrame(forecast_df)

    fig_forecast = px.line(
        forecast_df,
        x="Day",
        y="Projected Balance",
        title="Projected Cash Balance (Next 90 Days)"
    )

    st.plotly_chart(fig_forecast, use_container_width=True)


    conn.close()

# =================================================
# 🚨 TAB 4 – ALERTS
# =================================================
with tab_alerts:
    st.subheader("🚨 Alerts & Risks")

    conn = get_conn()

    # Low Cash Alert
    if runway_days < 30:
        st.error("🚨 Cash runway below 30 days")
    else:
        st.success("✅ Cash runway healthy")

    # Unpaid Vendor Invoices
    unpaid_df = pd.read_sql("""
        SELECT vendor_name, net_amount, due_date
        FROM vendor_invoices
        WHERE payment_status != 'Paid'
    """, conn)

    if not unpaid_df.empty:
        st.warning("⚠️ Unpaid Vendor Invoices")
        st.dataframe(unpaid_df, use_container_width=True)

    conn.close()
