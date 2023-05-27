cd /home/ubuntu/chicks_project/foodics_gpt/
. .venv/bin/activate


if [ "$push_notification_var" = "reminder" ]; then
    python src/push_notification.py --option reminder
else
    python src/push_notification.py --option report
fi