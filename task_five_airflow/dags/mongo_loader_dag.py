from airflow.models.dag import DAG
from airflow.decorators import task
from airflow.datasets import Dataset
from pendulum import datetime


# The same variable as in etl_dag is used for the dag trigger
PROCESSED_DATA_DATASET = Dataset("file://airflow/processed_data_ready")
# This variable stores the path to the processed files to connect it to mongodb.
PROCESSED_DATA_PATH = "/opt/airflow/output/processed_data.csv"


with DAG(
    dag_id="mongo_loader_dag",
    start_date=datetime(2025, 1, 1),
    schedule=[PROCESSED_DATA_DATASET],
    catchup=False,
    tags=["etl", "mongo", "load"]
) as dag:
    
    @task(task_id="load_to_mongo_task")
    def load_to_mongo(input_path: str):
        """
            Task that loads data into MongoDB
        """
        import pandas as pd      
        from pymongo import MongoClient
        
        df = pd.read_csv(input_path)

        MONGO_URI = "mongodb://mongodb:27017/"
        client = MongoClient(MONGO_URI)
        db = client['airflow-mongodb']
        collection = db['processed_reviews']

        collection.delete_many({})

        data_dict = df.to_dict('records')

        if data_dict:
            result = collection.insert_many(data_dict)
            print(f"Успешно загружено {len(result.inserted_ids)} файлов в MongoDB.")
        else:
            print("DataFrame пуст. Данные не загружены!")
    
    load_to_mongo_task = load_to_mongo(input_path=PROCESSED_DATA_PATH)
