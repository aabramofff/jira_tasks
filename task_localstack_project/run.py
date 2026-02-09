"""
Pipeline Automatisation Script.

This script acts as the main entry point (orcestrator) for the project.
Is automates the entire setup process:
1. Checks if Docker is running.
2. Installs Python dependencies.
3. Prepares the dataset (Data Prep).
4. Starts the Docker containers (LocalStack, Airflow, Spark).
5. Wait for services to become healthy.
6. Initializes the Cloud Infrastructure (S3, Lambda, DynamoDB).
7. Triggers the Airflow DAG.
"""

import subprocess
import time
import requests
import sys
import os


def check_docker_running():
    """
    Checks if the Docker Daemon is currently running.
    The pipeline cannot start without Docker.
    """
    print("🔍 Checking if Docker Engine is running...", end=" ", flush=True)
    try:
        subprocess.check_call(
            "docker info",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
        )
        print("✅ Yes!\n")
    except subprocess.CalledProcessError:
        print("❌ No.")
        print("\n⛔ CRITICAL ERROR: Docker Desktop is not running!")
        print("Please start the Docker Desktop application and try again.")
        sys.exit(1)


def run_command(command, description):
    """Запускает команду с выводом в реальном времени"""
    print(f"⏳ {description}...", flush=True)
    try:
        process = subprocess.Popen(
            command, shell=True, stdout=sys.stdout, stderr=sys.stderr
        )
        process.communicate()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)

        print(f"✅ Done: {description}\n", flush=True)
    except subprocess.CalledProcessError:
        print(f"❌ Error during: {description}", flush=True)
        sys.exit(1)


def wait_for_service(url, name, retries=30, delay=5):
    print(f"⏳ Waiting for {name} to become ready...", flush=True)
    for i in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"   -> ✅ {name} is ready!\n", flush=True)
                return
        except requests.ConnectionError:
            pass

        print(f"   ... attempt {i+1}/{retries} (waiting {delay}s)", flush=True)
        time.sleep(delay)

    print(f"❌ Timeout waiting for {name}", flush=True)
    sys.exit(1)


def main():
    print("🚀 STARTING AUTOMATED PIPELINE 🚀\n", flush=True)

    check_docker_running()

    run_command("pip install -r requirements.txt", "Installing dependencies")

    if not os.path.exists("data/raw"):
        run_command("python src/data_prep.py", "Preparing & Splitting Data")
    else:
        print("ℹ️ Data already prepared, skipping split.\n", flush=True)

    run_command("docker-compose up -d", "Starting Docker Containers")

    wait_for_service("http://localhost:4566/_localstack/health", "LocalStack")
    wait_for_service("http://localhost:8080/health", "Airflow Webserver")

    print("⏳ Giving Airflow 10 seconds to parse DAGs...", flush=True)
    time.sleep(10)

    run_command("python scripts/init_infra.py", "Initializing Cloud Infrastructure")

    dag_id = "1_upload_raw_data_to_s3"
    print(f"⏳ Triggering Airflow DAG: {dag_id}...", flush=True)
    try:
        cmd = f"docker exec airflow-scheduler airflow dags trigger {dag_id}"
        subprocess.check_call(cmd, shell=True)
        print(f"✅ DAG Triggered Successfully!", flush=True)
    except Exception:
        print(
            "⚠️ Could not trigger DAG automatically (it might be loading). Trigger it manually in UI."
        )

    print("\n🎉🎉🎉 PIPELINE LAUNCHED SUCCESSFULLY! 🎉🎉🎉")
    print("---------------------------------------------------")
    print("Dashboard: http://localhost:8080")
    print(
        "Tableau:   https://public.tableau.com/views/HelsinkiCityBikesAnalysis/Dashboard1?:language=en-US&:sid=&:redirect=auth&publish=yes&showOnboarding=true&:display_count=n&:origin=viz_share_link"
    )
    print("---------------------------------------------------")


if __name__ == "__main__":
    main()
