# Airline Data Warehouse & ETL Pipeline Project

## 📌 Project Overview
This project implements a professional cloud-based Data Warehouse (DWH) solution using **Snowflake**, orchestrated by **Apache Airflow**. It demonstrates a complete end-to-end data lifecycle: from ingesting raw CSV data into a landing zone to building a multi-layered architecture with automated transformations, robust security, and interactive visualizations.



## 🛠 Tech Stack
* **Orchestration:** Apache Airflow (Dockerized).
* **Cloud DWH:** Snowflake.
* **Languages:** Python (Airflow & Streamlit), SQL (Snowflake Scripting).
* **Security:** Row Level Security (RLS), Secure Views.
* **Visualization:** Snowflake Dashboards, Streamlit.

---

## 🏗 Data Architecture (Medallion Layers)
The project follows the **Medallion Architecture** to ensure data quality and separation of concerns:
1.  **RAW Layer (L1):** 1:1 copy of the source CSV file using Snowflake `Internal Stage` and `COPY INTO` command.
2.  **INTEGRATION Layer (L2):** A normalized **Star Schema**. Data is de-duplicated and distributed into dimensions (`DIM_PASSENGERS`, `DIM_AIRPORTS`) and a fact table (`FACT_FLIGHTS`).
3.  **ANALYTICS Layer (L3):** Aggregated Data Marts (`FLIGHT_ANALYTICS_MART`) optimized for business reporting.



---

## 📂 Project Structure

```text
├── dags/                                # Airflow DAG definitions
│   ├── airline_ingestion.py          # Data ingestion from CSV to Snowflake Raw
│   └── airline_main_pipeline.py      # L2/L3 Transformation orchestration
├── data_in/                             # Local source data (Git ignored)
│   └── airline_dataset.csv              # Raw dataset file
├── sql/                                 # Snowflake SQL Scripts
│   ├── 01_airline_structure_creation.sql # DB and Schema setup
│   ├── 02_airline_raw_data_tables_creation.sql # Landing zone tables
│   ├── 03_airline_roles_and_rights.sql  # RBAC (Roles & Privileges) setup
│   ├── 04_airline_tables_creation.sql   # DWH Layers (L2/L3) tables
│   ├── 05_airline_main_procedure.sql    # ETL Stored Procedure logic
│   ├── 06_airline_sequre_view.sql       # RLS and Secure View implementation
│   └── 07_airline_dml_ddl_time_travel_queries.sql # Time Travel test cases
├── bi_tools/                            # Visualization & Analytics
│   ├── Snowflake Dashboards.png         # Screenshot of Snowsight analytics
│   ├── Snowflake Streamlit Apps.png     # Screenshot of Streamlit application
│   └── streamlit_app.py                 # Python code for native Snowflake App
├── Dockerfile                           # Custom Airflow image with Snowflake provider
├── docker-compose.yaml                  # Infrastructure as Code (Airflow services)
└── .gitignore                           # Files excluded from version control
```

## 🚀 Key Features

### 1. Automated ETL Pipelines (Airflow)
The workflow is managed by two main DAGs:
* **Ingestion DAG:** Automates the movement of local CSV data into Snowflake Internal Stage and then into the RAW schema.
* **Transformation DAG:** Triggers the Snowflake Stored Procedure to process data through the Star Schema and Analytics layers.

### 2. Stored Procedures & Audit Logging
The entire transformation logic is encapsulated within the `SP_TRANSFORM_AIRLINE_DATA` procedure.
* **Audit System:** Every run automatically logs an entry into the `AUDIT_LOG` table, capturing the timestamp, row counts, and execution status.

### 3. Advanced Snowflake Functionality
* **Time Travel:** Implemented 2 DDL and 2 DML scenarios to demonstrate data recovery capabilities using `AT`, `BEFORE`, and `UNDROP` commands.
* **Security & Governance:**
    * **Row Level Security (RLS):** Attached a `ROW ACCESS POLICY` to the fact table to filter visibility based on roles.
    * **Secure Views:** Created a `SECURE VIEW` to provide analytics-ready data while masking sensitive pilot information.

---

## 📊 Data Visualization
* **Snowsight Dashboard:** Built-in Snowflake charts showing total flights per airport and passenger demographics.
* **Streamlit App:** A native Snowflake Python application providing an interactive interface to explore the DWH metrics.

---

## 🔧 Setup & Execution

1.  **Clone the Repo:** Copy this repository to your local machine.
2.  **Infrastructure:** Run `docker-compose up -d --build` to start the Airflow environment and ensure the `data_in/` folder is mapped correctly.
3.  **Snowflake Database Configuration:**
    Execute the SQL scripts in the `sql/` folder sequentially to set up the environment:
    * `01` to `02`: Set up the database structure and Raw landing tables.
    * `03`: Configure RBAC (Roles, Users, and Permissions).
    * `04`: Create the Integration (L2) and Analytics (L3) tables.
    * `05`: Deploy the Main Stored Procedure for ETL transformations.
    * `06`: Implement Security features (RLS and Secure Views).
    * `07`: (Optional) Run Time-Travel queries to verify data recovery features.
4.  **Airflow Connection:** * Access the Airflow UI at `localhost:8080`.
    * Go to **Admin -> Connections** and create a connection named `snowflake_conn`.
    * Provide your Snowflake account details, using the role created in script `03`.
5.  **Run Pipeline:** * Unpause the DAGs in the Airflow UI.
    * Trigger `01_airline_ingestion` first to load raw data.
    * Trigger `02_airline_main_pipeline` to execute the full DWH transformation.