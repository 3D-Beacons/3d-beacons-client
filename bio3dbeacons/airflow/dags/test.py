"""
Master DAG for end to end weekly process
"""
# import os
from datetime import datetime

from airflow import DAG

# from airflow.contrib.sensors.bash_sensor import BashSensor
# from airflow.hooks.base_hook import BaseHook
# from airflow.models import Variable
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator

# from airflow.operators.python_operator import PythonOperator
# from airflow.operators.subdag_operator import SubDagOperator
# from airflow.utils.task_group import TaskGroup

PARENT_DAG_NAME = "test"


with DAG(
    dag_id=PARENT_DAG_NAME,
    # default_args=default_args,
    start_date=datetime(2020, 9, 18),
    schedule_interval="0 7 * * 5",
) as main_dag:

    start_release = DummyOperator(task_id="start_release")

    one_letter_mapping = BashOperator(
        task_id="one_letter_mapping",
        bash_command="release_chem_letter_mapping batch",
        retries=1,
    )

    start_release >> one_letter_mapping
