# Paris Beer Club Agenda
This repo is used to scrap events of Paris Beer Club pro subscribers

Subscribers are for now listed in [subscribers.csv](subscribers.csv) based on PBC [followed accounts](https://www.facebook.com/parisbeerclub/following)

# Requirements
Is is meant to be used on Linux (debian based) and needs chromedriver to work

# Installation
This repo needs a selenium driver to work, for now chrome driver is used
## Google Chrome
```
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f
```

## Chrome driver
```
wget https://chromedriver.storage.googleapis.com/[compatible_version]/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
cd chromedriver-linux64
sudo mv chromedriver /usr/bin/chromedriver
sudo chown root:root /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver
```
## Requirements
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
# Execution
```
source venv/bin/activate
python main.py
```
