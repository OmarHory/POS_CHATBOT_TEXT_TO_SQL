cd /home/ubuntu/chicks_project/foodics_gpt/
. .venv/bin/activate

# python s3_data_pull.py
jupyter nbconvert --execute data_notebooks/orders/update_orders_data.ipynb --to python --inplace

python src/models/runner/data_runner_update.py
