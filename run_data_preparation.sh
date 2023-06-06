cd /home/ubuntu/chicks_project/foodics_gpt/
. .venv/bin/activate

jupyter nbconvert --execute data_notebooks/orders/prepare_data.ipynb --to python --inplace
jupyter nbconvert --execute data_notebooks/orders/process_tables.ipynb --to python --inplace

#python data_notebooks/orders/update_data.py
#python data_notebooks/orders/update_process_tables.py

python src/models/runner/data_runner.py

echo "$Data Prepare --> (date +'%Y-%m-%d %H:%M:%S') End" >> /home/ubuntu/chicks_project/foodics_gpt/cron_jobs_logs.txt
