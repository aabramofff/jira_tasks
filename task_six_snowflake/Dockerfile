FROM apache/airflow:2.8.4

USER root

USER airflow

RUN pip install --no-cache-dir \
    apache-airflow-providers-snowflake \
    snowflake-connector-python \
    snowflake-sqlalchemy