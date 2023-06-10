#!/bin/bash

USERNAME="flasgger"

# Clone the repository
cd /home/$USERNAME
git clone https://github.com/flasgger/flasgger.git
cd flasgger

# Change to the desired branch if necessary
# git checkout <branch_name>

## Create a new virtual environment
#mkvirtualenv --python=python3.10

virtualenv /home/flasgger/.virtualenvs/flasgger --python=python3.10
source /home/flasgger/.virtualenvs/flasgger/bin/activate

# Install the required dependencies
pip3 install -r requirements.txt -r requirements-dev.txt

# Update the WSGI configuration
cd /var/www
rm ${USERNAME}_pythonanywhere_com_wsgi.py
ln -s /home/$USERNAME/flasgger/etc/pythonanywhere/pythonanywhere_com_wsgi.py ${USERNAME}_pythonanywhere_com_wsgi.py

echo "Setup complete. Reload the web app and visit https://${USERNAME}.pythonanywhere.com/ to see the demo_app landing page."