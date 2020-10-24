# Running Wolomapp 

## This is the backend project for Wolomapp

Clone the repo

```
git clone git@github.com:kollie/wolomapp-backend.git
```

Ensure that python is installed and create a virtual environment

Install flask

```
pip install flask
```

Install requirements

```
pip install -r requirements.txt
```

Run sqlalchemy migrations

```
flask db init

flask db migrate -m 'message'

flask db upgrade
```

Start the project

```
flask run
```

Test live project with the frontend native app


[Frontend](https://github.com/kollie/wolomapp-backend)
