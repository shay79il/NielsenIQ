from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator
from airflow.models import Variable
import os

#############################################################
def environment_branch(**kwargs):
    
    # get the environment_type parameter from the DAG Run configuration
    environment_type = kwargs['dag_run'].conf.get('environment_type')
    
    
    if environment_type not in ['development', 'production']:
        raise ValueError(f"Invalid environment_type: {environment_type}")
    
    if environment_type == 'development':
        return 'file_creation_development'
    else:
        return 'file_creation_production'


#############################################################
def create_file(environment_type, **kwargs):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"civalue_{environment_type}_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"hello ci_value from {environment_type} branch\n")
    
    # set an XCom variable with the filename for later retrieval
    task_instance = kwargs['ti']
    task_instance.xcom_push(key='filename', value=filename)


#############################################################
def print_file(**kwargs):
    
    # get the filename from the XCom variable
    task_instance = kwargs['ti']
    filename = task_instance.xcom_pull(key='filename')
    
    # read the file and print its contents
    with open(filename, 'r') as f:
        contents = f.read()
        print(contents)

#############################################################
with DAG(
    dag_id='example_dag',
    start_date=datetime(2023, 4, 20),
    schedule_interval=None,
) as dag:

    # define the branching task
    branching_task = BranchPythonOperator(
        task_id='environment_branch',
        python_callable=environment_branch,
        provide_context=True,
        dag=dag,
    )

    # define the file creation tasks
    file_creation_development = PythonOperator(
        task_id='file_creation_development',
        python_callable=create_file,
        op_kwargs={'environment_type': 'development'},
        provide_context=True,
        dag=dag,
    )

    file_creation_production = PythonOperator(
        task_id='file_creation_production',
        python_callable=create_file,
        op_kwargs={'environment_type': 'production'},
        provide_context=True,
        dag=dag,
    )

    # define the print task
    print_to_console = PythonOperator(
        task_id='print_to_console',
        python_callable=print_file,
        provide_context=True,
        trigger_rule='all_done',
        dag=dag,
    )

    # set up the task dependencies
    branching_task >> [file_creation_development, file_creation_production] >> print_to_console
