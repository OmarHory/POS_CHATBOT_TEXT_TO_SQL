. export_vars.sh

echo "$(date +'%Y-%m-%d %H:%M:%S') Start" >> /home/ubuntu/$PROJECT_NAME_BOT/foodics_gpt/cron_jobs_logs.txt
cd /home/ubuntu/
. .venv/bin/activate

jupyter nbconvert --execute data_notebooks/orders/update_data.ipynb --to python --inplace
jupyter nbconvert --execute data_notebooks/orders/update_process_tables.ipynb --to python --inplace

#python data_notebooks/orders/update_data.py
#python data_notebooks/orders/update_process_tables.py

python src/models/runner/data_runner_update.py

python s3_operations.py upload

echo "$(date +'%Y-%m-%d %H:%M:%S') End" >> /home/ubuntu/$PROJECT_NAME_BOT/foodics_gpt/cron_jobs_logs.txt
