if [ ! -d "\data" ]; then
    echo "Directory does not exist"
    mkdir data/
    mkdir data/processed
    mkdir data/processed/updates
    mkdir data/updates
    chmod 755 data/
else
    echo "Directory already exists"
fi


if [ ! -f "cron_jobs_logs.txt" ]; then
    echo "cron_jobs_logs.txt does not exist"
    touch cron_jobs_logs.txt
    chmod 755 cron_jobs_logs.txt
else
    echo "cron_jobs_logs.txt exists"

fi
