import os
import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Company Usage Dashboard", page_icon=":bar_chart:", layout="wide")
st.title("Company Usage Dashboard")

conn = st.connection("snowflake", ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL"))

DB = "ECON_AGENT_DB"
SCHEMA = "ANALYTICS"


def fmt_usd(val):
    return f"${val:,.2f}"


def fmt_col_usd(df, cols):
    """Pre-format dollar columns as display strings."""
    df = df.copy()
    for c in cols:
        df[c] = df[c].apply(fmt_usd)
    return df


@st.cache_data(ttl="5m")
def load_teams():
    return conn.query(f"SELECT * FROM {DB}.{SCHEMA}.TEAMS ORDER BY TEAM_ID")


@st.cache_data(ttl="5m")
def load_services():
    return conn.query(f"SELECT * FROM {DB}.{SCHEMA}.SERVICES ORDER BY SERVICE_ID")


@st.cache_data(ttl="5m")
def load_employees():
    return conn.query(f"SELECT * FROM {DB}.{SCHEMA}.EMPLOYEES ORDER BY EMPLOYEE_ID")


@st.cache_data(ttl="5m")
def load_usage(start_date, end_date):
    return conn.query(
        f"""
        SELECT u.*, e.FULL_NAME, e.TEAM_ID, e.SENIORITY, e.ROLE_TITLE,
               s.SERVICE_NAME, s.SERVICE_CATEGORY, t.TEAM_NAME
        FROM {DB}.{SCHEMA}.DAILY_USAGE u
        JOIN {DB}.{SCHEMA}.EMPLOYEES e ON u.EMPLOYEE_ID = e.EMPLOYEE_ID
        JOIN {DB}.{SCHEMA}.SERVICES s ON u.SERVICE_ID = s.SERVICE_ID
        JOIN {DB}.{SCHEMA}.TEAMS t ON e.TEAM_ID = t.TEAM_ID
        WHERE u.USAGE_DATE BETWEEN ? AND ?
        ORDER BY u.USAGE_DATE
        """,
        params=[str(start_date), str(end_date)],
    )


@st.cache_data(ttl="5m")
def load_alerts(start_date, end_date):
    return conn.query(
        f"""
        SELECT a.*, e.FULL_NAME, s.SERVICE_NAME, t.TEAM_NAME
        FROM {DB}.{SCHEMA}.USAGE_ALERTS a
        JOIN {DB}.{SCHEMA}.EMPLOYEES e ON a.EMPLOYEE_ID = e.EMPLOYEE_ID
        JOIN {DB}.{SCHEMA}.SERVICES s ON a.SERVICE_ID = s.SERVICE_ID
        JOIN {DB}.{SCHEMA}.TEAMS t ON e.TEAM_ID = t.TEAM_ID
        WHERE a.ALERT_DATE BETWEEN ? AND ?
        ORDER BY a.ALERT_DATE DESC
        """,
        params=[str(start_date), str(end_date)],
    )


@st.cache_data(ttl="5m")
def load_budget():
    return conn.query(
        f"""
        SELECT b.*, t.TEAM_NAME
        FROM {DB}.{SCHEMA}.MONTHLY_BUDGET b
        JOIN {DB}.{SCHEMA}.TEAMS t ON b.TEAM_ID = t.TEAM_ID
        ORDER BY b.BUDGET_MONTH, t.TEAM_NAME
        """
    )


def clear_caches():
    load_usage.clear()
    load_alerts.clear()
    load_budget.clear()
    load_teams.clear()
    load_services.clear()
    load_employees.clear()


# -- Sidebar filters --
with st.sidebar:
    st.header("Filters")
    st.button("Refresh Data", on_click=clear_caches)

    teams_df = load_teams()
    services_df = load_services()

    all_teams = teams_df["TEAM_NAME"].tolist()
    selected_teams = st.multiselect("Teams", all_teams, default=all_teams)

    all_services = services_df["SERVICE_NAME"].tolist()
    selected_services = st.multiselect("Services", all_services, default=all_services)

    date_range = st.date_input(
        "Date range",
        value=(date(2025, 1, 1), date(2025, 8, 31)),
        min_value=date(2024, 9, 1),
        max_value=date(2025, 8, 31),
    )

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = date(2025, 1, 1), date(2025, 8, 31)

# -- Load data --
with st.spinner("Loading usage data..."):
    usage_df = load_usage(start_date, end_date)
    alerts_df = load_alerts(start_date, end_date)
    budget_df = load_budget()

# Apply filters
mask = usage_df["TEAM_NAME"].isin(selected_teams) & usage_df["SERVICE_NAME"].isin(selected_services)
filtered = usage_df[mask].copy()

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# =====================
# KPI row
# =====================
total_cost = filtered["COST_USD"].sum()
total_queries = filtered["QUERY_COUNT"].sum()
spike_count = filtered["IS_SPIKE"].sum()
unique_users = filtered["EMPLOYEE_ID"].nunique()
avg_daily = filtered.groupby("USAGE_DATE")["COST_USD"].sum().mean()

with st.container(horizontal=True):
    st.metric("Total Spend", fmt_usd(total_cost), border=True)
    st.metric("Avg Daily Spend", fmt_usd(avg_daily), border=True)
    st.metric("Total Queries", f"{total_queries:,.0f}", border=True)
    st.metric("Active Users", f"{unique_users}", border=True)
    st.metric("Spike Events", f"{int(spike_count)}", border=True)

# =====================
# Tabs
# =====================
tab_cost, tab_services, tab_people, tab_spikes, tab_budget, tab_employees = st.tabs(
    ["Monthly Costs", "Services", "Top Spenders", "Spike Alerts", "Budget vs Actual", "All Employees"],
    on_change="rerun",
)

# -- Tab 1: Monthly cost trend with YTD highlight --
if tab_cost.open:
    with tab_cost:
        st.subheader("Monthly Cost Trend")
        filtered["MONTH"] = pd.to_datetime(filtered["USAGE_DATE"]).dt.to_period("M").dt.to_timestamp()
        monthly = filtered.groupby("MONTH", as_index=False)["COST_USD"].sum()
        monthly = monthly.rename(columns={"MONTH": "Month", "COST_USD": "Cost ($)"})

        ytd_start = pd.Timestamp(f"{date.today().year}-01-01")
        ytd_end = pd.Timestamp(date.today())
        monthly["Period"] = monthly["Month"].apply(
            lambda x: "YTD (Jan 2025 - Today)" if ytd_start <= x <= ytd_end else "Prior"
        )
        st.bar_chart(monthly, x="Month", y="Cost ($)", color="Period", use_container_width=True)

        st.subheader("Cost by Team (Monthly)")
        team_monthly = (
            filtered.groupby(["MONTH", "TEAM_NAME"], as_index=False)["COST_USD"].sum()
        )
        team_list = sorted(team_monthly["TEAM_NAME"].unique())
        selected_chart_teams = st.multiselect(
            "Toggle teams", team_list, default=team_list, key="cost_team_toggle"
        )
        team_monthly_vis = team_monthly[team_monthly["TEAM_NAME"].isin(selected_chart_teams)]

        cols = st.columns(min(len(selected_chart_teams), 3))
        for i, team in enumerate(selected_chart_teams):
            with cols[i % len(cols)]:
                team_data = team_monthly_vis[team_monthly_vis["TEAM_NAME"] == team]
                st.markdown(f"**{team}**")
                st.bar_chart(
                    team_data.set_index("MONTH")[["COST_USD"]].rename(columns={"COST_USD": "Cost ($)"}),
                    use_container_width=True,
                    height=200,
                )

# -- Tab 2: Service breakdown --
if tab_services.open:
    with tab_services:
        st.subheader("Cost by Service")
        svc_cost = (
            filtered.groupby("SERVICE_NAME", as_index=False)["COST_USD"]
            .sum()
            .sort_values("COST_USD", ascending=False)
        )
        st.bar_chart(svc_cost, x="SERVICE_NAME", y="COST_USD", horizontal=True, use_container_width=True)

        svc_display = svc_cost[["SERVICE_NAME", "COST_USD"]].rename(
            columns={"SERVICE_NAME": "Service", "COST_USD": "Total Cost"}
        )
        st.dataframe(
            fmt_col_usd(svc_display, ["Total Cost"]),
            hide_index=True,
            use_container_width=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Cost by Category")
            cat_cost = (
                filtered.groupby("SERVICE_CATEGORY", as_index=False)["COST_USD"]
                .sum()
                .sort_values("COST_USD", ascending=False)
            )
            st.bar_chart(cat_cost, x="SERVICE_CATEGORY", y="COST_USD", use_container_width=True)

        with col2:
            st.subheader("Service Usage Frequency")
            svc_freq = (
                filtered.groupby("SERVICE_NAME", as_index=False)["QUERY_COUNT"]
                .sum()
                .sort_values("QUERY_COUNT", ascending=False)
            )
            st.bar_chart(svc_freq, x="SERVICE_NAME", y="QUERY_COUNT", use_container_width=True)

# -- Tab 3: Top spenders --
if tab_people.open:
    with tab_people:
        st.subheader("Top 20 Spenders")
        top_users = (
            filtered.groupby(["FULL_NAME", "TEAM_NAME", "SENIORITY"], as_index=False)["COST_USD"]
            .sum()
            .sort_values("COST_USD", ascending=False)
            .head(20)
        )
        top_display = top_users.rename(columns={
            "FULL_NAME": "Employee",
            "TEAM_NAME": "Team",
            "SENIORITY": "Level",
            "COST_USD": "Total Cost",
        })
        st.dataframe(
            fmt_col_usd(top_display, ["Total Cost"]),
            hide_index=True,
            use_container_width=True,
        )

        st.subheader("Top Spender - Service Breakdown")
        if not top_users.empty:
            top_person = top_users.iloc[0]["FULL_NAME"]
            person_data = filtered[filtered["FULL_NAME"] == top_person]
            person_svc = (
                person_data.groupby("SERVICE_NAME", as_index=False)["COST_USD"]
                .sum()
                .sort_values("COST_USD", ascending=False)
            )
            st.markdown(f"**{top_person}** — {fmt_usd(person_data['COST_USD'].sum())} total")
            st.bar_chart(person_svc, x="SERVICE_NAME", y="COST_USD", use_container_width=True)

            person_display = person_svc.rename(columns={"SERVICE_NAME": "Service", "COST_USD": "Cost"})
            st.dataframe(
                fmt_col_usd(person_display, ["Cost"]),
                hide_index=True,
                use_container_width=True,
            )

        st.subheader("Cost by Seniority Level")
        seniority_cost = (
            filtered.groupby("SENIORITY", as_index=False)["COST_USD"]
            .sum()
            .sort_values("COST_USD", ascending=False)
        )
        st.bar_chart(seniority_cost, x="SENIORITY", y="COST_USD", use_container_width=True)

# -- Tab 4: Spike alerts (monthly) --
if tab_spikes.open:
    with tab_spikes:
        st.subheader("Usage Spike Alerts")

        if not alerts_df.empty:
            alerts_filtered = alerts_df[
                alerts_df["TEAM_NAME"].isin(selected_teams)
                & alerts_df["SERVICE_NAME"].isin(selected_services)
            ].copy()

            col1, col2, col3 = st.columns(3)
            with col1:
                critical = len(alerts_filtered[alerts_filtered["SEVERITY"] == "CRITICAL"])
                st.metric("Critical", critical, border=True)
            with col2:
                high = len(alerts_filtered[alerts_filtered["SEVERITY"] == "HIGH"])
                st.metric("High", high, border=True)
            with col3:
                medium = len(alerts_filtered[alerts_filtered["SEVERITY"] == "MEDIUM"])
                st.metric("Medium", medium, border=True)

            st.subheader("Monthly Spike Timeline")
            alerts_filtered["ALERT_MONTH"] = (
                pd.to_datetime(alerts_filtered["ALERT_DATE"]).dt.to_period("M").dt.to_timestamp()
            )
            spike_monthly = (
                alerts_filtered.groupby(["ALERT_MONTH", "SEVERITY"], as_index=False)
                .size()
                .rename(columns={"ALERT_MONTH": "Month", "size": "Spike Count"})
            )
            st.bar_chart(spike_monthly, x="Month", y="Spike Count", color="SEVERITY", use_container_width=True)

            st.subheader("Recent Alerts")
            alerts_display = (
                alerts_filtered[
                    ["ALERT_DATE", "FULL_NAME", "SERVICE_NAME", "SEVERITY",
                     "NORMAL_AVG_COST", "SPIKE_COST", "MULTIPLIER", "RESOLVED", "RESOLUTION_NOTES"]
                ]
                .head(50)
                .rename(columns={
                    "ALERT_DATE": "Date",
                    "FULL_NAME": "Employee",
                    "SERVICE_NAME": "Service",
                    "NORMAL_AVG_COST": "Normal Avg",
                    "SPIKE_COST": "Spike Cost",
                    "MULTIPLIER": "Multiplier",
                    "RESOLVED": "Resolved",
                    "RESOLUTION_NOTES": "Notes",
                })
            )
            alerts_display = alerts_display.copy()
            alerts_display["Normal Avg"] = alerts_display["Normal Avg"].apply(fmt_usd)
            alerts_display["Spike Cost"] = alerts_display["Spike Cost"].apply(fmt_usd)
            alerts_display["Multiplier"] = alerts_display["Multiplier"].apply(lambda x: f"{x:.1f}x")
            st.dataframe(
                alerts_display,
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("No spike alerts in the selected date range.")

# -- Tab 5: Budget vs Actual --
if tab_budget.open:
    with tab_budget:
        st.subheader("Monthly Budget vs Actual Spend")
        budget_filtered = budget_df[budget_df["TEAM_NAME"].isin(selected_teams)]

        if not budget_filtered.empty:
            monthly_agg = (
                budget_filtered.groupby("BUDGET_MONTH", as_index=False)
                .agg({"BUDGET_AMOUNT": "sum", "ACTUAL_SPEND": "sum"})
            )
            monthly_agg["BUDGET_MONTH"] = pd.to_datetime(monthly_agg["BUDGET_MONTH"])
            chart_data = monthly_agg.set_index("BUDGET_MONTH")[["BUDGET_AMOUNT", "ACTUAL_SPEND"]]
            chart_data.columns = ["Budget", "Actual"]
            st.line_chart(chart_data, use_container_width=True)

            st.subheader("Budget Detail by Team")
            budget_pivot = (
                budget_filtered.pivot_table(
                    index="TEAM_NAME",
                    values=["BUDGET_AMOUNT", "ACTUAL_SPEND"],
                    aggfunc="sum",
                )
            )
            budget_pivot["Variance"] = budget_pivot["BUDGET_AMOUNT"] - budget_pivot["ACTUAL_SPEND"]
            budget_pivot["% Used"] = (
                budget_pivot["ACTUAL_SPEND"] / budget_pivot["BUDGET_AMOUNT"] * 100
            ).round(1)
            budget_pivot = budget_pivot.rename(columns={
                "BUDGET_AMOUNT": "Budget",
                "ACTUAL_SPEND": "Actual",
            })
            budget_display = budget_pivot.copy()
            budget_display["Budget"] = budget_display["Budget"].apply(fmt_usd)
            budget_display["Actual"] = budget_display["Actual"].apply(fmt_usd)
            budget_display["Variance"] = budget_display["Variance"].apply(fmt_usd)
            budget_display["% Used"] = budget_display["% Used"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(budget_display, use_container_width=True)
        else:
            st.info("No budget data for selected teams.")

# -- Tab 6: All Employees --
if tab_employees.open:
    with tab_employees:
        st.subheader("All Employees - Usage Overview")

        emp_summary = (
            filtered.groupby(
                ["EMPLOYEE_ID", "FULL_NAME", "TEAM_NAME", "SENIORITY"], as_index=False
            ).agg(
                Total_Cost=("COST_USD", "sum"),
                Total_Queries=("QUERY_COUNT", "sum"),
                Total_Sessions=("SESSION_COUNT", "sum"),
                Services_Used=("SERVICE_NAME", "nunique"),
                Spike_Count=("IS_SPIKE", "sum"),
                Days_Active=("USAGE_DATE", "nunique"),
            )
            .sort_values("Total_Cost", ascending=False)
        )
        emp_summary["Avg Daily Cost"] = emp_summary["Total_Cost"] / emp_summary["Days_Active"]
        emp_summary["Spike_Count"] = emp_summary["Spike_Count"].astype(int)

        col_search, col_team, col_level = st.columns(3)
        with col_search:
            name_filter = st.text_input("Search by name", key="emp_search")
        with col_team:
            emp_team_filter = st.multiselect(
                "Filter team", sorted(emp_summary["TEAM_NAME"].unique()),
                default=sorted(emp_summary["TEAM_NAME"].unique()), key="emp_team"
            )
        with col_level:
            emp_level_filter = st.multiselect(
                "Filter seniority", sorted(emp_summary["SENIORITY"].unique()),
                default=sorted(emp_summary["SENIORITY"].unique()), key="emp_level"
            )

        emp_display = emp_summary[
            emp_summary["TEAM_NAME"].isin(emp_team_filter)
            & emp_summary["SENIORITY"].isin(emp_level_filter)
        ]
        if name_filter:
            emp_display = emp_display[
                emp_display["FULL_NAME"].str.contains(name_filter, case=False, na=False)
            ]

        emp_table = emp_display[
            ["FULL_NAME", "TEAM_NAME", "SENIORITY", "Total_Cost", "Avg Daily Cost",
             "Total_Queries", "Total_Sessions", "Services_Used", "Spike_Count", "Days_Active"]
        ].rename(columns={
            "FULL_NAME": "Employee",
            "TEAM_NAME": "Team",
            "SENIORITY": "Level",
            "Total_Cost": "Total Cost",
            "Avg Daily Cost": "Avg Daily Cost",
            "Total_Queries": "Queries",
            "Total_Sessions": "Sessions",
            "Services_Used": "Services Used",
            "Spike_Count": "Spikes",
            "Days_Active": "Days Active",
        })
        emp_table = fmt_col_usd(emp_table, ["Total Cost", "Avg Daily Cost"])
        emp_table["Queries"] = emp_table["Queries"].apply(lambda x: f"{x:,.0f}")
        emp_table["Sessions"] = emp_table["Sessions"].apply(lambda x: f"{x:,.0f}")
        st.dataframe(emp_table, hide_index=True, use_container_width=True, height=500)

        st.subheader("Employee Detail")
        emp_names = emp_display["FULL_NAME"].tolist()
        if emp_names:
            selected_emp = st.selectbox("Select employee", emp_names, key="emp_detail_select")
            emp_data = filtered[filtered["FULL_NAME"] == selected_emp]

            emp_data_monthly = emp_data.copy()
            emp_data_monthly["MONTH"] = (
                pd.to_datetime(emp_data_monthly["USAGE_DATE"]).dt.to_period("M").dt.to_timestamp()
            )

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Monthly Cost Trend**")
                emp_monthly_cost = (
                    emp_data_monthly.groupby("MONTH", as_index=False)["COST_USD"].sum()
                )
                st.bar_chart(
                    emp_monthly_cost.set_index("MONTH").rename(columns={"COST_USD": "Cost ($)"}),
                    use_container_width=True,
                    height=250,
                )

            with col2:
                st.markdown("**Cost by Service**")
                emp_svc = (
                    emp_data.groupby("SERVICE_NAME", as_index=False)["COST_USD"]
                    .sum()
                    .sort_values("COST_USD", ascending=False)
                )
                st.bar_chart(
                    emp_svc, x="SERVICE_NAME", y="COST_USD",
                    horizontal=True, use_container_width=True, height=250,
                )

            emp_svc_display = emp_svc.rename(columns={"SERVICE_NAME": "Service", "COST_USD": "Total Cost"})
            st.dataframe(
                fmt_col_usd(emp_svc_display, ["Total Cost"]),
                hide_index=True,
                use_container_width=True,
            )
