# vidricur-workshop-control

Software for car operation

## Installation (Windows)

Clone the repository from Gitlab
```
git clone "https://vidricur-workshop-control:glpat-jqH565Gqzy8tk4FWZbGK@gitlab.fhnw.ch/vidricur/vidricur-workshop-control.git"
```
Install virtual env (you have to do that only once)
```
pip install virtualenv
```

Change into vidricur-workshop-control and initialize a new python environment
```
cd vidricur-workshop-control
virtualenv venv
```

Change into python environment
```
source ./venv/Scripts/activate
```

Install all needed dependencies 
```
pip install -r requirements.txt
```

## Start control software (Windows)
```
cd  vidricur-workshop-control
source ./venv/Scripts/activate
python –u main.py
```


## Installation (Raspberry Pi)

Install all needed packages
```
sudo apt-get install git pip python3-venv​
```

Enable and start pigpiod service
```
sudo systemctl enable pigpiod​
sudo systemctl start pigpiod​
```

Clone the repository from Gitlab
```
git clone "https://vidricur-workshop-control:glpat-jqH565Gqzy8tk4FWZbGK@gitlab.fhnw.ch/vidricur/vidricur-workshop-control.git"​
```
Change into vidricur-workshop-control and initialize a new python environment
```
cd vidricur-workshop-control
python -m venv ./venv​
```
Change into python environment
```
source venv/bin/activate​
```

Upgrade pip and install packages
```
pip3 install --upgrade pip​
pip3 install -r requirements.txt
```

## Start control software (Raspberry Pi)
```
cd ~/vidricur-workshop-control​/vidricur-workshop-control
source venv/bin/activate​
python main.py
```

## Wiring

![Schema Wiring](doc/img/gpio.png)

