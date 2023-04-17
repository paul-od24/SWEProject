#!/bin/bash

# stopping the gunicorn instance so pickle files can be updated
sudo systemctl stop dublinbikes

#updating pickle files
/home/ubuntu/miniconda3/envs/comp30830/bin/python3 /home/ubuntu/SWEProject/bike_stand_gen.py
/home/ubuntu/miniconda3/envs/comp30830/bin/python3 /home/ubuntu/SWEProject/model_gen.py

#starting gunicorn instance again once updates have finished
sudo systemctl start dublinbikes
