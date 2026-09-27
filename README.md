# ❄️ Snowflake Projects ❄️

Welcome! Here you will find insightful and creative ways to interpret data using a powerful AI-powered software used in many data analytical environments around the workforce known as ❄️ [Snowflake](https://www.snowflake.com/en/). 

# Projects

## 💵 Ask the US Economy

📁🔗 [Ask US Economy, files](https://github.com/enzorcortes/Snowflake_Projects/tree/main/askuseconomy)

A conversational AI agent that answers plain-English questions about the US economy.

Built entirely on Snowflake using Snowsight Workspaces, Cortex Analyst, and Cortex Agents.

> *"It's a recession when your neighbor loses his job; it's a depression when you lose your own." — Harry S. Truman*

🤖🔗 Link to AI Agent: [Uncle Economy](https://ai.snowflake.com/xntbtwm/mx19130/#/ai)

You will need a default role and default warehouse set on your Snowflake user profile to use it. On the dropdown for available agents, select Uncle Economy.

### Agent Architecture:

```mermaid
flowchart TB
    subgraph Users["👤 End Users"]
        CoWork["Snowflake CoWork<br/><i>ai.snowflake.com</i>"]
        API["Cortex Agent API<br/><i>REST :run endpoint</i>"]
    end

    subgraph Agent["🤖 Cortex Agent — UNCLEECONOMY"]
        direction TB
        Orchestrator["Orchestrator<br/><i>model: auto</i>"]
        Instructions["Instructions<br/><i>• Executive briefing format</i><br/><i>• Lead with key takeaway</i><br/><i>• No jargon, no SQL in responses</i><br/><i>• Never guess at numbers</i>"]
    end

    subgraph Tools["🔧 Agent Tools"]
        Analyst["UncleEconomy<br/><i>Cortex Analyst (text-to-SQL)</i>"]
        CodeExec["code_execution<br/><i>Charts & custom calculations</i>"]
    end

    subgraph SemanticLayer["📊 Semantic Layer"]
        SV["US_ECONOMY_SV<br/><i>Semantic View</i>"]
        subgraph Tables["Logical Tables"]
            Live["ECONOMIC_DASHBOARD_LIVE<br/><i>Real-time daily snapshots</i><br/>DATE · CPI · UNEMPLOYMENT_RATE<br/>MORTGAGE_RATE_30Y"]
            Monthly["ECONOMIC_INDICATORS_MONTHLY<br/><i>Monthly with YoY metrics</i><br/>MONTH · CPI · CPI_YOY_PCT<br/>UNEMPLOYMENT_RATE · UNEMPLOYMENT_YOY_CHANGE_BPS<br/>MORTGAGE_RATE_30Y · MORTGAGE_YOY_CHANGE_BPS"]
        end
    end

    subgraph DataSources["🌐 Data Sources"]
        BLS["Bureau of Labor Statistics<br/><i>CPI · Unemployment</i>"]
        Freddie["Freddie Mac<br/><i>30Y Mortgage Rates</i>"]
        SPDF["Snowflake Public Data Free"]
    end

    subgraph Eval["✅ Evaluation"]
        Dataset["Eval Dataset<br/><i>30 questions (10 AC + 20 TEA)</i>"]
        Metrics["Metrics<br/><i>answer_correctness</i><br/><i>logical_consistency</i><br/><i>tool_selection_accuracy</i><br/><i>tool_execution_accuracy</i><br/><i>executive_readiness (custom)</i>"]
    end

    subgraph Access["🔐 Access Control"]
        Public["PUBLIC role<br/><i>All users</i>"]
        Warehouse["COMPUTE_WH<br/><i>X-Small warehouse</i>"]
        CortexRole["SNOWFLAKE.CORTEX_USER<br/><i>Database role</i>"]
    end

    CoWork -->|chat| Orchestrator
    API -->|REST| Orchestrator
    Orchestrator --> Instructions
    Orchestrator -->|data queries| Analyst
    Orchestrator -->|charts / calculations| CodeExec
    Analyst --> SV
    SV --> Live
    SV --> Monthly
    BLS --> SPDF
    Freddie --> SPDF
    SPDF --> Live
    SPDF --> Monthly
    Dataset --> Metrics
    Public --> Warehouse
    Public --> CortexRole

    classDef agent fill:#E8762D,stroke:#C45A1A,color:#fff
    classDef tool fill:#2E8B57,stroke:#1B5E3B,color:#fff
    classDef semantic fill:#29B5E8,stroke:#1A8AB5,color:#fff
    classDef data fill:#6C757D,stroke:#495057,color:#fff
    classDef eval fill:#9B59B6,stroke:#7D3C98,color:#fff
    classDef access fill:#F39C12,stroke:#D68910,color:#fff
    classDef user fill:#3498DB,stroke:#2471A3,color:#fff

    class Orchestrator,Instructions agent
    class Analyst,CodeExec tool
    class SV,Live,Monthly semantic
    class BLS,Freddie,SPDF data
    class Dataset,Metrics eval
    class Public,Warehouse,CortexRole access
    class CoWork,API user
```

## 🤖📊 Company Usage Dashboard & CompanyLapDog Agent

📁🔗 [usage-dashboard, files](https://github.com/enzorcortes/Snowflake_Projects/tree/main/usage-dashboard)

A complete Snowflake-native project that simulates a 100-person company's cloud service usage, provides interactive dashboards via Streamlit, exposes data through a semantic view for natural language queries, and deploys a Cortex Agent (CompanyLapDog) for conversational analytics — all secured with role-based access control.

Built entirely on Snowflake using Snowsight Workspaces, Cortex Analyst, and Cortex Agents.

> *"My strengths are not in any- anything related to- it's just hard work... My greatest weaknesses are, um, a-workplace-a-workaholism. Um, I work too hard, I care too much, and sometimes I can be too invested in my job." - Michael Scott, The Office*

🤖🔗 Link to AI Agent: [Company LapDog](https://ai.snowflake.com/xntbtwm/mx19130/#/artifacts/share/2e8b0676-74d3-4f3e-bf07-4b2e1d56246f)

You will need a default role and default warehouse set on your Snowflake user profile to use it. On the dropdown for available agents, select CompanyLapDog.

### Agent Architecture:

```mermaid
graph TD

    subgraph ACCESS["🔑 USER ACCESS"]
        CoWork["Snowflake CoWork<br/><i>ai.snowflake.com</i>"]
        Snowsight["Snowsight UI<br/><i>Agent Admin</i>"]
        API["REST API<br/><i>:run endpoint</i>"]
        Public["PUBLIC Role<br/><i>All Users</i>"]
    end

    subgraph AGENT["🤖 CORTEX AGENT — GOVDEMO_DB.GOVDEMO_AGENT.COMPANYLAPDOG"]
        Core["COMPANYLAPDOG<br/><i>Model: auto</i>"]

        subgraph INSTRUCTIONS["Instructions"]
            Orch["Orchestration<br/><i>Route data questions → Analyst<br/>Charts/viz only → code_execution</i>"]
            Resp["Response<br/><i>Professional, concise, tables,<br/>bold numbers, USD formatting</i>"]
        end

        subgraph TOOLS["Tools"]
            Analyst["Company_LapDog<br/><i>cortex_analyst_text_to_sql</i>"]
            Code["code_execution<br/><i>Charts & visualizations</i>"]
        end

        Profile["Profile<br/><i>CompanyLapDog | #29B5E8 Blue</i>"]
    end

    subgraph SV["📊 SEMANTIC VIEW"]
        SemanticView["USAGE_ANALYTICS_SV<br/><i>GOVDEMO_DB.GOVDEMO_AGENT<br/>6 tables · 4 relationships · 8 VQRs</i>"]
    end

    subgraph DATA["💾 ECON_AGENT_DB.ANALYTICS"]
        DU["DAILY_USAGE<br/><i>Fact table — cost,<br/>queries, spikes</i>"]
        EMP["EMPLOYEES<br/><i>100 employees —<br/>roles, seniority</i>"]
        TEAMS["TEAMS<br/><i>5 teams — dept,<br/>manager, cost center</i>"]
        SVC["SERVICES<br/><i>Cloud services —<br/>category, cost/unit</i>"]
        BUD["MONTHLY_BUDGET<br/><i>Budget vs actual<br/>per team/month</i>"]
        ALT["USAGE_ALERTS<br/><i>Spike alerts —<br/>severity, status</i>"]
    end

    subgraph EVAL["🧪 EVALUATION"]
        Dataset["Eval Dataset<br/><i>30 questions: 10 AC + 20 TEA</i>"]
        AC["answer_correctness"]
        LC["logical_consistency"]
        TSA["tool_selection_accuracy"]
        TEA["tool_execution_accuracy"]
        Custom["response_format_quality<br/><i>Custom LLM judge</i>"]
    end

    CoWork --> Core
    Snowsight --> Core
    API --> Core
    Public -.->|grants| Core

    Core --> Orch
    Core --> Resp
    Orch --> Analyst
    Orch --> Code
    Core --- Profile

    Analyst --> SemanticView

    SemanticView --> DU
    SemanticView --> EMP
    SemanticView --> TEAMS
    SemanticView --> SVC
    SemanticView --> BUD
    SemanticView --> ALT

    DU ---|EMPLOYEE_ID| EMP
    DU ---|SERVICE_ID| SVC
    EMP ---|TEAM_ID| TEAMS
    BUD ---|TEAM_ID| TEAMS

    Core -.->|evaluated by| Dataset
    Dataset --- AC
    Dataset --- LC
    Dataset --- TSA
    Dataset --- TEA
    Dataset --- Custom

    style ACCESS fill:#1B3A4B,stroke:#29B5E8,color:#F9FAFB
    style AGENT fill:#0F2A3D,stroke:#29B5E8,color:#F9FAFB
    style INSTRUCTIONS fill:#2D1B69,stroke:#8B5CF6,color:#F9FAFB
    style TOOLS fill:#3D2600,stroke:#F59E0B,color:#F9FAFB
    style SV fill:#0A3D3D,stroke:#06B6D4,color:#F9FAFB
    style DATA fill:#1F2937,stroke:#374151,color:#F9FAFB
    style EVAL fill:#2D1B69,stroke:#8B5CF6,color:#F9FAFB

    style Core fill:#29B5E8,stroke:#F9FAFB,color:#F9FAFB
    style CoWork fill:#1B3A4B,stroke:#F9FAFB,color:#F9FAFB
    style Snowsight fill:#1B3A4B,stroke:#F9FAFB,color:#F9FAFB
    style API fill:#1B3A4B,stroke:#F9FAFB,color:#F9FAFB
    style Public fill:#10B981,stroke:#F9FAFB,color:#F9FAFB

    style Analyst fill:#F59E0B,stroke:#F9FAFB,color:#1F2937
    style Code fill:#F59E0B,stroke:#F9FAFB,color:#1F2937

    style Profile fill:#1B3A4B,stroke:#F9FAFB,color:#F9FAFB
    style Orch fill:#8B5CF6,stroke:#F9FAFB,color:#F9FAFB
    style Resp fill:#8B5CF6,stroke:#F9FAFB,color:#F9FAFB

    style SemanticView fill:#06B6D4,stroke:#F9FAFB,color:#F9FAFB

    style DU fill:#374151,stroke:#9CA3AF,color:#F9FAFB
    style EMP fill:#374151,stroke:#9CA3AF,color:#F9FAFB
    style TEAMS fill:#374151,stroke:#9CA3AF,color:#F9FAFB
    style SVC fill:#374151,stroke:#9CA3AF,color:#F9FAFB
    style BUD fill:#374151,stroke:#9CA3AF,color:#F9FAFB
    style ALT fill:#374151,stroke:#9CA3AF,color:#F9FAFB

    style Dataset fill:#8B5CF6,stroke:#F9FAFB,color:#F9FAFB
    style AC fill:#4C1D95,stroke:#8B5CF6,color:#F9FAFB
    style LC fill:#4C1D95,stroke:#8B5CF6,color:#F9FAFB
    style TSA fill:#4C1D95,stroke:#8B5CF6,color:#F9FAFB
    style TEA fill:#4C1D95,stroke:#8B5CF6,color:#F9FAFB
    style Custom fill:#4C1D95,stroke:#8B5CF6,color:#F9FAFB
```
