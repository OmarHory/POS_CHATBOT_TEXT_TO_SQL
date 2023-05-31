cd /home/ubuntu/chicks_project/foodics_gpt/
. .venv/bin/activate

jupyter nbconvert --execute data_notebooks/orders/prepare_data.ipynb --to python --inplace
jupyter nbconvert --execute data_notebooks/orders/process_tables.ipynb --to python --inplace

python src/models/runner/data_runner.py
