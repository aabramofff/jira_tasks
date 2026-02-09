# 🚲 Helsinki City Bikes Data Engineering Pipeline
An end-to-end Event-Driven Data Engineering pipeline that processes Helsinki City Bike trip data. The project simulates a real-world AWS cloud environment locally using LocalStack and orchestrates hybrid processing (Real-time & Batch) using Airflow and Spark.

## 🏗 Architecture
This project implements a Lambda Architecture approach, processing data in two parallel paths:

### 1. Data Ingestion:
- Raw CSV data is prepared and split by month.
- Apache Airflow uploads chunks to an S3 Bucket (LocalStack).

### 2. Fast Path (Event-Driven / Real-time simulation):
- S3 Upload triggers an SNS Topic.
- SNS triggers an AWS Lambda function.
- Lambda parses the CSV stream and writes raw trip records into DynamoDB for low-latency access.

### 3. Batch Path (Analytics):
- After upload, Airflow triggers an Apache Spark job via REST API.
- Spark processes the data to calculate Daily and Monthly aggregated metrics (Trip counts, Avg distance, Avg duration).
- Processed data is saved to the local filesystem for reporting.

### 4. Visualization:

- Tableau Public dashboard connects to the processed data to visualize trends.

---

## 🛠 Tech Stack
- **Infrastructure**: Docker, Docker Compose.
- **Cloud Simulation**: LocalStack (S3, SNS, Lambda, DynamoDB).
- **Orhestration**: Apache Airflow.
- **Data Processing**: Apache Spark (PySpark).
- **Serverless Compute**: AWS Lambda (Python).
- **IaC (Infrastructure as Code)**: Custom Python scripts using boto3.
- **Visualization**: Tableau Public.

## 🚀 Quick Start (Automated)
The entire environment can be spun up with a single command using the orchestration script.

### Prerequisites
- Docker Desktop must be installed and running.
- Python 3.9+ installed locally.

### Installation & Launch
#### 1. Clone the repository:

```Bash
git clone <your-repo-url>
cd helsinki-bikes-project
```
#### 2. Run the orchestrator script:

```Bash
python run.py
```
### What happens next?
The run.py script will automatically:
1. Check if Docker is running.
2. Install Python dependencies (requirements.txt).
3. Prepare the dataset (split monolithic CSV into monthly chunks).
4. Start Docker containers (Airflow, Spark, LocalStack).
5. Wait for services to be healthy (Health Checks).
6. Initialize AWS resources (Buckets, Tables, Lambdas via init_infra.py).
7. Trigger the Airflow DAG to start the pipeline.

## 📂 Project Structure
```Plaintext
helsinki-bikes-project/
├── dags/                   # Airflow DAGs
│   └── upload_to_s3.py     # Main workflow: Upload -> Trigger Spark
├── data/                   # Data storage (mounted to containers)
│   ├── raw/                # Split monthly CSVs (Input)
│   └── processed/          # Spark output (Metrics)
├── lambda/                 # AWS Lambda function code
│   └── lambda_function.py  # Event handler for S3 uploads
├── scripts/                # Utility scripts
│   └── init_infra.py       # IaC: Sets up S3, SNS, DynamoDB
├── spark_jobs/             # PySpark scripts
│   └── data_processor.py   # Batch processing ETL logic
├── src/                    # Shared Python modules
│   ├── config.py           # Configuration management
│   ├── data_prep.py        # Initial data cleaning/splitting
│   └── dynamodb_schemas.py # NoSQL Table definitions
├── docker-compose.yml      # Multi-container infrastructure definition
├── requirements.txt        # Python dependencies
└── run.py                  # Automation entry point
```

## 📊 Visualization & Results
### 1. Tableau Dashboard
The final analytics are visualized using Tableau. [View the Interactive Dashboard on Tableau Public](https://public.tableau.com/views/HelsinkiCityBikesAnalysis/Dashboard1?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

- **Daily Trend**: Shows trip volume over time.
- **Top 10 Stations**: Identifies the most popular starting points.
- **Distance vs. Duration**: Scatter plot analysis of ride behaviors.

### 2. Manual Verification
If you want to inspect the system under the hood:
- Airflow UI: Access at http://localhost:8080.
- Spark Output: Check the data/processed/ directory for CSV reports.
- DynamoDB (Raw Data): You can use AWS CLI to check if data arrived in the database:

```Bash
aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name BikeTripsRaw --max-items 5
```

## 🛑 Stopping the Project
To stop and remove all containers, run:

```Bash
docker-compose down
```

📜 License
This project is for educational purposes. Data Source: [Helsinki City Bikes](https://www.kaggle.com/datasets/geometrein/helsinki-city-bikes).