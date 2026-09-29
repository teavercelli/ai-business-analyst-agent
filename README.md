# AI Business Analyst Agent
## Live Demo

🚀 [Open the live AI Business Analyst dashboard](https://ai-business-analyst-agent.streamlit.app/)

> The live AI features use the Gemini API free tier and may occasionally be unavailable when API rate limits are reached.
An autonomous AI-powered business monitoring and root-cause analysis system built with Python, SQL, Gemini and Streamlit.

The system goes beyond a traditional analytics dashboard: it automatically monitors business KPIs, detects unusual changes across multiple dimensions, groups related signals into business incidents, and uses an AI agent to investigate potential root causes directly from the underlying SQL database.

---

## Business Problem

Business analysts often spend significant time manually:

- monitoring KPIs
- identifying unusual performance changes
- drilling down across countries, products, channels and customer segments
- writing SQL queries
- investigating possible root causes
- preparing explanations for stakeholders

This project explores how an AI agent can automate part of that analytical workflow.

Instead of requiring the user to know where a problem exists, the system can automatically detect unusual business changes and trigger an investigation.

---

## How It Works

```text
E-commerce Data
       ↓
SQL Database
       ↓
KPI Engine
       ↓
Anomaly Detection
       ↓
Multi-dimensional Analysis
       ↓
Incident Clustering
       ↓
AI Business Analyst Agent
       ↓
SQL Tool Calling
       ↓
Root-Cause Investigation
       ↓
Business Insights
       ↓
Streamlit Dashboard
```

---

## Key Features

### Automated KPI Monitoring

The system calculates and monitors business metrics including:

- Revenue
- Gross Profit
- Gross Margin
- Orders
- Active Customers
- Average Order Value

### Multi-Dimensional Anomaly Detection

Performance changes are analyzed across:

- Country
- Product
- Product Category
- Sales Channel
- Customer Segment

The system also analyzes combinations such as:

- Country × Product
- Country × Channel
- Country × Segment
- Country × Category

This allows local problems to be detected even when they are hidden by company-level aggregates.

### Incident Clustering

Related anomaly signals are grouped into business incidents before being sent to the AI agent.

This reduces duplicate investigations and helps the agent reason about related KPI movements together.

### Autonomous Root-Cause Investigation

The AI agent can:

1. Receive a detected business incident
2. Determine what additional data is required
3. Generate SQL queries
4. Query the database through controlled tools
5. Analyze the returned evidence
6. Perform additional drill-downs
7. Produce a structured root-cause analysis

### Evidence-Based Reasoning

The agent separates conclusions into:

1. **Data Evidence** — facts directly observed in the database
2. **Interpretation** — conclusions supported by those observations
3. **Hypotheses to Verify** — explanations that require additional data

This prevents unsupported hypotheses from being presented as confirmed facts.

### SQL Safety

The AI agent receives read-only database access.

The SQL tool includes controls that:

- allow only SELECT queries
- block destructive SQL operations
- prevent multiple SQL statements
- limit returned rows
- open SQLite in read-only mode

### Interactive Dashboard

The Streamlit interface provides:

- Business KPI overview
- Revenue trends
- Gross margin trends
- Country performance
- Detected anomalies
- AI Analyst interface
- Investigation history

---

## Synthetic Dataset & Ground Truth

The project uses a reproducible synthetic e-commerce dataset containing:

- 1,000 customers
- 10,000 orders
- ~25,000 order-item records
- 5 countries
- multiple customer segments
- multiple sales channels
- 8 products

A fixed random seed makes the dataset reproducible.

Several business changes are deliberately embedded in the dataset generator as hidden ground truth for evaluation.

Examples include:

- profitability deterioration linked to a specific country/product combination
- a major sales-channel mix shift
- deterioration within a customer segment

These ground-truth events are known to the dataset generator but are **not provided to the anomaly detection engine or AI agent**.

The objective is to evaluate whether the system can independently discover them from transactional data.

---

## Example Investigation

One automatically detected incident showed a significant gross-margin deterioration in Spain.

The system autonomously drilled down through the data and identified:

```text
Spain
   ↓
Computers
   ↓
Laptop Pro
   ↓
Unit cost: €700 → €1,015
   ↓
+45% cost increase
   ↓
Gross margin: 36.4% → 7.7%
```

The agent also verified that the same cost increase was not present in the other markets.

Importantly, it did not claim to know why the underlying cost changed because supplier, logistics and procurement data were not available.

---

## Evaluation

The project includes an evaluation framework using known synthetic ground truth.

The goal is not simply to check whether the agent produces fluent answers, but whether it identifies the correct:

- affected business dimension
- KPI
- product/channel/segment
- direction of change
- underlying data-supported driver

This helps distinguish convincing AI-generated explanations from analytically correct investigations.
### Current Evaluation Results

| Ground-truth incident | Result |
|---|---|
| Spain — Laptop Pro margin deterioration | PASS |
| Germany — Marketplace decline | PASS |
| United Kingdom — Enterprise decline | PASS |

**Anomaly detection benchmark: 3/3 incidents detected (100%).**

The benchmark uses three synthetic business incidents deliberately embedded in the dataset generator. These ground-truth events are not provided to the anomaly detection engine.

The 100% result refers specifically to this small synthetic benchmark and should not be interpreted as general model accuracy.

AI root-cause investigations are evaluated separately because their performance can vary depending on LLM behavior and API availability.
---

## Technology Stack

- **Python** — application logic and analytics
- **SQLite / SQL** — transactional data and analytical queries
- **Gemini API** — LLM reasoning and tool calling
- **Pandas** — data handling
- **Streamlit** — interactive web application
- **python-dotenv** — secure local environment variables

---

## Project Structure

```text
ai-business-analyst-agent/
│
├── agent/
│   ├── agent.py
│   ├── monitor.py
│   ├── prompts.py
│   └── tools.py
│
├── analytics/
│   ├── anomalies.py
│   ├── dashboard_data.py
│   ├── incidents.py
│   └── kpi.py
│
├── app/
│   └── dashboard.py
│
├── database/
│   ├── investigations.py
│   └── setup.py
│
├── tests/
│   └── evaluate_agent.py
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Running the Project

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd ai-business-analyst-agent
```

### 2. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 3. Configure the Gemini API key

Create a `.env` file:

```text
GEMINI_API_KEY=your_api_key
```

The `.env` file is excluded from Git and should never be committed.

### 4. Generate the database

```bash
python3 database/setup.py
```

### 5. Run the command-line application

```bash
python3 main.py
```

### 6. Run the dashboard

```bash
python3 -m streamlit run app/dashboard.py
```

---

## Limitations

This project is a portfolio prototype rather than a production analytics platform.

Current limitations include:

- synthetic rather than real company data
- rule-based anomaly thresholds
- rule-based incident clustering
- API rate limits
- limited historical data for seasonality analysis
- SQLite rather than a production data warehouse
- agent investigations are constrained by the available database schema

Potential future improvements include statistical anomaly detection, seasonality-aware monitoring, more robust evaluation datasets, production data-warehouse integration and optimized agent workflows requiring fewer LLM calls.

---

## Project Goal

The goal of this project is to explore how traditional business analytics and modern AI agents can work together.

Rather than replacing SQL or deterministic analytics with an LLM, the architecture uses each component for what it does best:

```text
SQL / Python
→ reliable calculations and data retrieval

Anomaly Detection
→ systematic monitoring

LLM Agent
→ investigation strategy and interpretation

Dashboard
→ decision support
```

The result is an AI-assisted business monitoring system designed to move from **data → anomaly → investigation → evidence-based insight**.