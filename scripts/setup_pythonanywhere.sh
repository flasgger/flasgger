#!/bin/bash

USERNAME="flasgger"

# Clone the repository
cd /home/$USERNAME
git clone https://github.com/flasgger/flasgger.git
cd flasgger

# Change to the desired branch if necessary
# git checkout <branch_name>

# Create a new virtual environment
mkvirtualenv --python=python3.10

# Install the required dependencies
pip3 install -r requirements.txt -r requirements-dev.txt

# Update the WSGI configuration
cd /var/www
rm ${USERNAME}_pythonanywhere_com_wsgi.py
ln -s /home/$USERNAME/flasgger/etc/pythonanywhere/pythonanywhere_com_wsgi.py ${USERNAME}_pythonanywhere_com_wsgi.py

# Modify the web app configuration
# Make sure to replace /home/<username> with your actual home directory path
# Replace <username> with your PythonAnywhere username
sed -i "s@<source_path>@/home/$USERNAME/flasgger@g" /var/www/${USERNAME}_pythonanywhere_com.conf
sed -i "s@<working_directory>@/home/$USERNAME/flasgger@g" /var/www/${USERNAME}_pythonanywhere_com.conf
sed -i "s@<virtualenv_path>@/home/$USERNAME/.virtualenvs/flasgger@g" /var/www/${USERNAME}_pythonanywhere_com.conf

# Reload the web app
# You will be prompted for your PythonAnywhere username and password
pa_restart_webapp ${USERNAME}.pythonanywhere.com

echo "Setup complete. Visit https://${USERNAME}.pythonanywhere.com/ to see the demo_app landing page."