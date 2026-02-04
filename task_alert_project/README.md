# 🚀 High-Performance Log Alerting System

A scalable, event-driven system designed to process massive log datasets (100M+ records), simulate real-time data streaming, and trigger alerts based on sliding window logic.

Built with **Python**, **Redis**, **Docker**, and **Pydantic**.

---

## 🏗 Architecture & Design Decisions

The system follows the **Producer-Consumer** pattern to ensure high throughput and separation of concerns.

### 1. Data Flow
1.  **Loader (Producer):** Reads the CSV file in chunks (to save RAM), converts rows to JSON, and pushes them into a Redis Queue (`LPUSH`). It simulates a live stream.
2.  **Redis (Broker):** Acts as a high-performance buffer. It decouples the speed of reading from the speed of processing.
3.  **Processor (Consumer):** Continuously pulls data (`BRPOP`) from Redis, validates it, and runs it through the Rule Engine.
4.  **Rule Engine:** Uses Redis **Sorted Sets (ZSET)** to implement efficient **Sliding Window** algorithms.

### 2. Key Technologies
* **Redis Pipelines:** Used to batch commands (add event, remove old events, count total) in a single network request, drastically reducing latency.
* **Redis Sorted Sets:** Allows for O(log(N)) complexity when calculating error rates over time windows, which is significantly faster than SQL queries for this use case.
* **Pydantic V2:** Ensures strict data validation and type safety. Malformed logs are discarded before they can crash the system.
* **Docker Compose:** Orchestrates the environment, ensuring the system runs identically on any machine.

---

## 🛠 How to Run

### Prerequisites
* Docker & Docker Compose installed.
* Place your data file `alert_project_data.csv` into the `data/` directory.

### Steps
1.  **Build and Start the System:**
    ```bash
    docker-compose up -d --build
    ```

2.  **Check Logs (Real-time):**
    To see the processor in action:
    ```bash
    docker-compose logs -f processor
    ```

3.  **View Alerts:**
    Generated alerts are saved to the persistent file:
    ```bash
    cat logs/alerts.log
    ```

---

## 🧩 Extensibility: How to Add New Rules

The system implements the **Strategy Pattern**. Adding a new rule does not require changing the core logic.

1.  **Create a new file** in `src/rules/` (e.g., `us_error_rule.py`).
2.  **Inherit from `BaseRule`** and implement the `check` method:
    ```python
    from src.rules.base import BaseRule

    class USErrorRule(BaseRule):
        LIMIT = 5
        WINDOW = 60  # 1 minute

        def check(self, log):
            if log.country_code != "US":
                return
            
            key = "alert:US:errors"
            count = self.check_threshold(key, log.timestamp, self.WINDOW, self.LIMIT)
            
            if count > self.LIMIT:
                print(f"Too many errors in US! Count: {count}")
    ```
3.  **Register the rule** in `src/processor.py`:
    ```python
    rules = [
        FatalGlobalRule(r),
        FatalBundleRule(r),
        USErrorRule(r)  # <--- Add your new rule here
    ]
    ```

---

## 📂 Project Structure

```text
.
├── data/                   # Data directory (CSV file goes here)
├── logs/                   # Output logs (alerts.log)
├── src/
│   ├── rules/              # Alerting logic (Strategy Pattern)
│   │   ├── base.py         # Abstract base class + Sliding Window logic
│   │   ├── fatal_global.py # Rule 2.1 implementation
│   │   └── fatal_bundle.py # Rule 2.2 implementation
│   ├── config.py           # Configuration settings
│   ├── loader.py           # Producer (Reads CSV -> Redis)
│   ├── logger.py           # Rotating file logger setup
│   ├── models.py           # Pydantic data models
│   ├── processor.py        # Consumer (Redis -> Rules)
│   └── redis_client.py     # Connection pool manager
├── docker-compose.yaml      # Service orchestration
├── Dockerfile              # Container definition
└── requirements.txt        # Python dependencies