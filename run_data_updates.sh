cd /home/ubuntu/lex_project/gpt_whatsapp/
. .venv/bin/activate

python s3_data_pull.py

python src/models/runner/data_runner.py
