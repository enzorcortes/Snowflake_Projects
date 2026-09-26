# ❄️ Snowflake Projects ❄️

Welcome! Here you will find insightful and creative ways to interpret data using a powerful AI-powered software used in many data analytical environments around the workforce known as ❄️ [Snowflake](https://www.snowflake.com/en/). 

# Projects

## 💵 Ask the US Economy

A conversational AI agent that answers plain-English questions about the US economy — powered entirely by Snowflake.

📁🔗 [Ask US Economy, files](https://github.com/enzorcortes/Snowflake_Projects/tree/main/askuseconomy)

> *"It's a recession when your neighbor loses his job; it's a depression when you lose your own." — Harry S. Truman*

<img src="askuseconomy/StreamlitAskUSecon.gif" width="50%">

> *Streamlit live use of the AI*



## Pseudo Company Project - CompanyLapDog

Link to AI Agent: [CompanyLapDog](https://ai.snowflake.com/xntbtwm/mx19130/#/artifacts/share/2e8b0676-74d3-4f3e-bf07-4b2e1d56246f)

Agent overview

CompanyLapDog queries the USAGE_ANALYTICS_SV semantic view in GOVDEMO_DB.GOVDEMO_AGENT (backed by ECON_AGENT_DB.ANALYTICS tables: DAILY_USAGE, EMPLOYEES, SERVICES, TEAMS, MONTHLY_BUDGET, USAGE_ALERTS) to answer questions about cloud service costs, employee usage patterns, team budget variances, usage spike alerts, and service-level breakdowns. It can identify top spenders, compare actual spend versus allocated budgets by team and month, surface unresolved high-severity alerts, analyze usage by seniority or role, and rank services by cost or consumption. It also supports code execution for charts, visualizations, and statistical calculations that go beyond SQL. This agent handles cloud cost analytics and FinOps questions for a 100-employee, 5-team organization; it does not cover infrastructure provisioning, access control, or data outside the ECON_AGENT_DB.ANALYTICS schema.
