# Productivity Notes API

## Description

A secure Flask REST API for a productivity Notes application.

The API provides JWT-based authentication and allows authenticated users to create, view, update, and delete their own notes.

Users cannot access or modify notes belonging to other users.

## Technologies

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Flask-Migrate
- Flask-Bcrypt
- Flask-JWT-Extended
- Flask-RESTful
- Marshmallow
- Faker
- Pytest

## Installation

Clone the repository and enter the project directory.

Install dependencies:

```bash
pipenv install