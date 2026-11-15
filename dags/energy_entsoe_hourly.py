# dags/energy_entsoe_hourly.py
from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.operators.python import PythonOperator

from ingestion.job_entsoe_hourly import run, ZONES

DEFAULT_ARGS = {
    "owner": "energy-platform",
    "retries": 3,
    "retry_delay": timedelta(minutes=15),
    "email_on_failure": True,
    "email": ["ops@example.com"],  # sostituire con il contatto reale
}

##example of a DAG that runs hourly to fetch ENTSO-E load data for Italian zones. The DAG is set to start on November 1, 2026, and will catch up on any missed runs since that date. 
## It limits the number of active runs to 2 to avoid overloading the ENTSO-E API.
def load_window(data_interval_end: datetime, **_) -> None:
    # data_interval_end è l'inizio dell'ora successiva: la finestra è (end - 1h, end)
    # Ritardo di 3 ore: si carica l'ora che ENTSO-E ha già pubblicato
    end = data_interval_end - timedelta(hours=3)
    end = end.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
    for name, code in ZONES.items():
        run(end, name, code)

with DAG(
    dag_id="energy_entsoe_hourly",
    start_date=datetime(2026, 11, 1, tzinfo=timezone.utc),
    schedule="@hourly",
    catchup=True,          # recupera le ore mancanti dalla data di start
    max_active_runs=2,     # limita il carico sull'API
    default_args=DEFAULT_ARGS,
    tags=["energy", "entsoe"],
) as dag:
    PythonOperator(
        task_id="load_entsoe_load_window",
        python_callable=load_window,
    )