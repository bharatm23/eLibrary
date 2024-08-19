Library Management System v2

A project implementing an e-library application with two types of access – User/Student and Librarian.  The Librarian role can perform CRUD operations on sections and e-books while the Student role can view sections & e-books, request and return e-books. Both role types can perform keyword search operations. Graphs on recent activity can be viewed from Librarian/Student dashboards. Daily reminder to login, Monthly reports on activity can be sent to Student user. User can also download books for a price.

Features : 

- User/Student registration and login

- Librarian login

- Librarian: Create, search and manage e-books, sections and book requests. Revoke access to issued books. View graphs in dashboard.

- User: Search for e-books, sections based on attributes; request books for reading, return, rate and download them. View graphs in dashboard.

Technologies Used : 

- Flask - web framework

- Vue2 - Creating frontend

- Bootstrap - for HTML and CSS styling

- SQLAlchemy - for data storage

- Python - integration of various technologies

- Celery - Creation of tasks for reusable apps

- Flask JWT Extended - Implement login, registration and RBAC

- Javascript - Client side webpage behaviour

- Flask Restful - Building APIs to safely interchange information

- Werkzeug Security - Create and check hashed passwords

- Redis - In-memory storage, acts as a cache and memory broker

- Ubuntu WSL2 - Running of redis, celery on windows OS

- MailHog - Testing SMTP emailing functionality for alerts 

- Chart.js - Javascript library for data visualisation


Getting Started

Prerequisites

- Python 3.x
- pip
- ubuntu wsl2
- Browser Chrome

# Testing Application
## Requirements
- Ubuntu WSL2 Setup - Download from Microsoft Store

- Setup the environment (First time)

``` bash (run as administrator)
  $ sudo apt-get update
  $ sudo apt-get install libpython3-dev
  $ sudo apt-get install python3-venv
  $ python3 -m venv <environment name >
  $ pip install -r requirements.txt
```

- Redis
``` bash (run as administrator)
  $ cd to project directory - cd /mnt/d/etc/Projects/1.projec/elibrary/
  $ sudo install redis-server
```
- Celery
``` bash (run as administrator)
  $ cd to project directory - cd /mnt/d/etc/Projects/1.projec/elibrary/
  $ pip install celery
```

- MailHog service setup and execution
``` bash
  $ sudo apt-get -y install golang-go
  $ go get github.com/mailhog/MailHog
```

## Running the application

- Redis
``` bash (run as administrator)
  $ cd to project directory - cd /mnt/d/etc/Projects/1.projec/elibrary/
  $ redis-server
```

- Celery worker
``` bash (run as administrator)
  $ cd to project directory - cd /mnt/d/etc/Projects/1.projec/elibrary/
  $ celery -A main:celery_app worker --loglevel INFO 
```

- Celery beat
``` bash (run as administrator)
  $ cd to project directory - cd /mnt/d/etc/Projects/1.projec/elibrary/
  $ celery -A main:celery_app beat --loglevel INFO 
```

- MailHog service execution
``` bash
  $ ~/go/bin/MailHog
```
- Host PC Setup
- Open browser and goto `http://localhost:8025`
- This should bring up the mail interface with MailHog

Installation

1. Set up virtual environment in Code folder in cmd and activate it

```
python -m venv myenvironment
myenvironment/Scripts/activate

```

2. Install the requirements 
 
```
pip install -r requirements.txt
python upload_initial_data.py

```

3. Run the application. 

```
python main.py

```

4. Open in browser

```
http://localhost:5000/

```