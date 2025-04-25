#!/bin/bash

# activate venv 
#! NOT WORKING
source "venv/bin/activate.csh"

# run main.py
sudo -E env "PATH=$PATH" python "vidricur-workshop-control/main.py"
