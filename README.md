# Kametv3
## About the project

**This is an Quiz/Test application.**

**The Admin can add Questions, create users, change the test settings and check the answers users have submitted.**

**The User once created can log in read instructions and take the test**


# STEPS TO RUN THE APPLICATION

## Clone the repository

    git clone https://github.com/e9srawat/Kametv3

## Create a virtual environment

**For Linux and macOS**

    python3.8 -m venv venv
    source venv/bin/activate

**For Windows**

    pip install virtualenv
    python -m venv venv
    virtualenv venv
    venv/Scripts/activate

## Go inside the project folder

    cd Kamet/Entropy

## Install the necessary modules

    pip install -r requirements.txt

**If it shows error, run**

    pip install django

## Make migrations

    python manage.py makemigrations
    python manage.py migrate


## Create superuser

    python manage.py createsuperuser

**Follow the onscreen instructions to create an Admin account, you can use these credentials to login to the app as an Admin.**

# Run the application

    python manage.py runserver

# Open the below url on your browser and login with superuser credentials to get started

     http://127.0.0.1:8000/

