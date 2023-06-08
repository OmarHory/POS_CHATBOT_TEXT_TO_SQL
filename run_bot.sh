export ENV=prod

python src/update_variables.py

gunicorn --bind 127.0.0.1:4000 src.app:app --chdir src --workers 4 --timeout 120