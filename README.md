# Expense Tracker

## Features
- User can create an account and login
- User can add expenses
- User can view their balance sheet
- User can view their individual expenses
- User can view overall expenses

## Tech Stack
- Django
- Django Rest Framework
- Simple JWT

## Setup
1. Clone the repository
```
git clone https://github.com/rohitkori/Expense-Tracker.git
```
2. Create a virtual environment and install dependencies
```
pipenv shell
pipenv install
```
3. Run migrations
```
python manage.py makemigrations
python manage.py migrate
```
4. Run the server
```
python manage.py runserver
```

- Note: The server will run on `http://127.0.0.1:8000/`

- To run tests
```
python manage.py test
```

## Docker

To run the application using docker, run the following command:
```
docker compose up
```

- Note: The server will run on `http://127.0.0.1:8000/`