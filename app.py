import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from utils.predictor import get_prioritized_data


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AceN Collections Prioritization",
    page_icon="🚀",
    layout="wide"
)


# -----------------------------
# CUSTOM CSS
# -----------------------------
css_file = Path("assets/style.css")

if css_file.exists():
    with open(css_file) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )


# -----------------------------
# LOAD DATA
# -----------------------------

@st.cache_data
def load_data():

    path = "sample_data/banking_collections_cleaned.csv"

    return pd.read_csv(path)



df = load_data()


# -----------------------------
# BACKEND CONNECTION
# -----------------------------
# Later Member 3 will replace predictor.py logic
# with calculate_priority(df)

prioritized = get_prioritized_data(df)



# -----------------------------
# SIDEBAR FILTERS
# -----------------------------

st.sidebar.title("🚀 AceN Collections")

st.sidebar.caption(
    "AI-powered Debt Recovery Prioritization"
)

st.sidebar.divider()

st.sidebar.subheader("🔎 Filters")


priority_filter = st.sidebar.multiselect(
    "Priority Level",
    prioritized["Priority_Level"].unique(),
    default=prioritized["Priority_Level"].unique()
)


risk_filter = st.sidebar.multiselect(
    "Risk Level",
    prioritized["Risk_Level"].unique(),
    default=prioritized["Risk_Level"].unique()
)


region_filter = st.sidebar.multiselect(
    "Region",
    prioritized["Region"].unique(),
    default=prioritized["Region"].unique()
)



filtered = prioritized[
    (prioritized["Priority_Level"].isin(priority_filter))
    &
    (prioritized["Risk_Level"].isin(risk_filter))
    &
    (prioritized["Region"].isin(region_filter))
]



# -----------------------------
# HEADER
# -----------------------------

st.title(
    "🚀 AceN Collections Prioritization System"
)


st.markdown(
"""
### Problem 2: Reducing Collection Costs

An AI-driven dashboard that identifies high-value overdue customers,
optimizes collection strategies, and reduces unnecessary field visits.
"""
)


st.divider()



# -----------------------------
# KPI CARDS
# -----------------------------

c1,c2,c3,c4,c5 = st.columns(5)


c1.metric(
    "👥 Customers",
    f"{len(filtered):,}"
)


c2.metric(
    "🔴 High Priority",
    f"{(filtered['Priority_Level']=='High').sum():,}"
)


c3.metric(
    "💰 Outstanding",
    f"₹{filtered['Outstanding_Amount'].sum()/10000000:.2f} Cr"
)


c4.metric(
    "💳 Collection Cost",
    f"₹{filtered['Est_Collection_Cost'].sum()/100000:.2f} L"
)


if "Recovery_Potential" in filtered.columns:

    c5.metric(
        "⭐ Recovery Potential",
        f"{filtered['Recovery_Potential'].mean():.1f}"
    )

else:

    c5.metric(
        "⭐ Avg Score",
        f"{filtered['Customer_Score'].mean():.1f}"
    )



st.divider()



# -----------------------------
# TABS
# -----------------------------

tab1,tab2,tab3,tab4 = st.tabs(
[
"📋 Prioritized Customers",
"📊 Insights",
"💰 Cost Simulation",
"🤖 AI Insights"
]
)



# =================================================
# TAB 1 - PRIORITY LIST
# =================================================


with tab1:

    st.subheader(
        "🎯 Top Priority Customers"
    )


    display = filtered.sort_values(
        "Priority_Score",
        ascending=False
    ).copy()


    display["Recommended_Action"] = (
        display["Priority_Level"]
        .map(
            {
                "High":"🚗 Field Visit",
                "Medium":"📞 Phone Call",
                "Low":"📩 SMS Reminder"
            }
        )
    )


    st.dataframe(
        display[
        [
            "Customer_ID",
            "Name",
            "Loan_Type",
            "Outstanding_Amount",
            "Payment_Delay_Days",
            "Risk_Level",
            "Priority_Level",
            "Priority_Score",
            "Recommended_Action"
        ]
        ],
        use_container_width=True,
        height=500
    )


    csv = display.to_csv(index=False)


    st.download_button(
        "📥 Download Priority Report",
        csv,
        "priority_customers_report.csv",
        "text/csv"
    )



# =================================================
# TAB 2 - INSIGHTS
# =================================================


with tab2:

    st.subheader(
        "📊 Portfolio Insights"
    )


    col1,col2 = st.columns(2)


    with col1:

        priority_chart = (
            filtered["Priority_Level"]
            .value_counts()
            .reset_index()
        )

        priority_chart.columns=[
            "Priority",
            "Customers"
        ]


        fig = px.bar(
            priority_chart,
            x="Priority",
            y="Customers",
            title="Customers by Priority"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )



    with col2:

        risk_chart = (
            filtered["Risk_Level"]
            .value_counts()
            .reset_index()
        )

        risk_chart.columns=[
            "Risk",
            "Customers"
        ]


        fig = px.pie(
            risk_chart,
            names="Risk",
            values="Customers",
            title="Risk Distribution"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )



    st.divider()


    region_data = (
        filtered.groupby("Region")
        ["Outstanding_Amount"]
        .sum()
        .reset_index()
    )


    fig = px.bar(
        region_data,
        x="Region",
        y="Outstanding_Amount",
        title="Outstanding Amount by Region"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )



# =================================================
# TAB 3 - COST SIMULATION
# =================================================


with tab3:

    st.subheader(
        "💰 Collection Strategy Simulation"
    )


    st.info(
"""
### Traditional Strategy

• Contact every customer equally  
• More field visits  
• Higher operational cost  


### AI Strategy

• High Priority → Field Visit  
• Medium Priority → Phone Call  
• Low Priority → SMS Reminder
"""
)



    traditional_cost = (
        len(filtered)*50
        +
        len(
            filtered[
                filtered["Priority_Level"]=="High"
            ]
        )*900
    )



    ai_cost = (
        len(filtered[filtered["Priority_Level"]=="High"])*900
        +
        len(filtered[filtered["Priority_Level"]=="Medium"])*50
        +
        len(filtered[filtered["Priority_Level"]=="Low"])*5
    )



    saving = traditional_cost-ai_cost


    percentage = (
        saving/traditional_cost*100
        if traditional_cost>0
        else 0
    )



    a,b,c = st.columns(3)


    a.metric(
        "Traditional Cost",
        f"₹{traditional_cost:,.0f}"
    )


    b.metric(
        "AI Strategy Cost",
        f"₹{ai_cost:,.0f}"
    )


    c.metric(
        "Estimated Saving",
        f"{percentage:.1f}%"
    )



    comparison = pd.DataFrame(
    {
        "Strategy":
        [
            "Traditional",
            "AI Powered"
        ],

        "Cost":
        [
            traditional_cost,
            ai_cost
        ]
    })


    fig = px.bar(
        comparison,
        x="Strategy",
        y="Cost",
        text="Cost",
        title="Collection Cost Comparison"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )
    # =================================================
# TAB 4 - AI INSIGHTS
# =================================================

with tab4:

    st.subheader(
        "🤖 AI Collection Recommendations"
    )

    st.caption(
        "Automatically generated insights based on customer risk, priority and recovery potential."
    )


    high_count = (
        filtered["Priority_Level"]=="High"
    ).sum()


    medium_count = (
        filtered["Priority_Level"]=="Medium"
    ).sum()


    low_count = (
        filtered["Priority_Level"]=="Low"
    ).sum()



    st.success(
    f"""
    ### 🎯 Priority Strategy

    The system identified:

    🔴 {high_count} High Priority customers  
    🟡 {medium_count} Medium Priority customers  
    🟢 {low_count} Low Priority customers  


    Recommended action:

    • High Priority → Deploy field officers  
    • Medium Priority → Contact through phone calls  
    • Low Priority → Use automated reminders
    """
    )



    st.divider()



    col1,col2 = st.columns(2)



    with col1:

        st.subheader(
            "⚠️ Risk Insights"
        )


        high_risk = (
            filtered[
                filtered["Risk_Level"]=="High"
            ]
        )


        st.write(
            f"""
            - High risk customers: **{len(high_risk)}**

            - Outstanding amount:
            **₹{high_risk['Outstanding_Amount'].sum():,.0f}**

            These customers require immediate attention
            to prevent further recovery loss.
            """
        )



    with col2:

        st.subheader(
            "💡 Operational Recommendation"
        )


        rural = 0

        if "Area_Type" in filtered.columns:

            rural = (
                filtered[
                    filtered["Area_Type"]=="Rural"
                ]
                .shape[0]
            )


        st.write(
            f"""
            - Rural customers detected:
            **{rural}**

            - Avoid unnecessary travel for low-value accounts.

            - Prioritize customers with high outstanding
            amount and high recovery potential.
            """
        )



    st.divider()



    st.subheader(
        "📌 AI Generated Action Plan"
    )


    recommendations = [
        "Focus field visits only on High Priority customers.",
        "Use automated SMS reminders for Low Priority accounts.",
        "Monitor customers with long payment delays.",
        "Allocate collection agents based on region and risk.",
        "Continuously retrain the model using recovery outcomes."
    ]


    for r in recommendations:

        st.write(
            "✅ " + r
        )