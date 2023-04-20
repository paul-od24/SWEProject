#!/bin/bash

# path to map.py
SCRIPT="/home/ubuntu/miniconda3/envs/comp30830/bin/gunicorn  --bind unix:/home/ubuntu/SWEProject/dublinbikes.sock wsgi:app"

# email settings
TO_EMAIL="dublinbikes23@gmail.com"
SUBJECT_FAILURE="DBIKES23 maps.py crashed"
SUBJECT_RESTART="DBIKES23 maps.py restarting"

# 30 minute interval between restarts (in seconds)
interval=1800

while true; do
    # record start time
    start_time=$(date +%s)

    # start map.py & capture stderr out
    error_out=$($SCRIPT 2>&1 1>/dev/null | tr -d '\000')
    exit_code=$?

    # if map.py crashes
    if [ $exit_code -ne 0 ]; then

        # calculate time elapsed since last restart
        elapsed_time=$(($(date +%s) - start_time))

        # If less than 30 minutes have passed since last restart, set sleep_time to remaining time until 30 minutes
        if [ $elapsed_time -lt $interval ]; then
            sleep_time=$((interval - elapsed_time))
        else
            sleep_time=0
        fi

        # calculate time to restart in minutes
        remaining_time=$((sleep_time / 60))

        # send email with the error
        EMAIL_BODY_FAILURE="map.py crashed. Restarting in $remaining_time minute(s).\n\nError output:\n$error_out"
        echo "map.py crashed"
        printf "%b" "$EMAIL_BODY_FAILURE" | mail -s "$SUBJECT_FAILURE" $TO_EMAIL

        # sleep for remaining time before restarting
        sleep $sleep_time

        # send email that maps.py is being restarted
        EMAIL_BODY_RESTART="map.py is being restarted."
        echo "map.py is being restarted"
        printf "%b" "$EMAIL_BODY_RESTART" | mail -s "$SUBJECT_RESTART" $TO_EMAIL
    fi
done

