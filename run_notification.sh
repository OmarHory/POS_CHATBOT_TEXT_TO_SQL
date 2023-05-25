cd /home/ubuntu/lex_project/gpt_whatsapp/
. .venv/bin/activate


if [ "$push_notification_var" = "reminder" ]; then
    python src/push_notification.py --option reminder
else
    python src/push_notification.py --option report
fi