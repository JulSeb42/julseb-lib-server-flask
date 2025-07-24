
# Flask MongoDB Boilerplate

A starter Flask backend with MongoDB, JWT authentication, CORS, and user management.

## Features

- Flask API with modular routes
- MongoDB integration (via PyMongo)
- JWT authentication
- CORS support for frontend dev
- User signup, login, password reset, and email verification
- User seeding with Faker

## Requirements

- Python 3.12+
- MongoDB Atlas or local MongoDB
- Node.js (for frontend, optional)

## Setup

### 1. Clone and install dependencies

```sh
git clone https://github.com/JulSeb42/julseb-lib-server-flask.git
cd server-flask
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy the template environment file and edit it with your own values:

```shell
cp template.env .env
```

Then open `.env` and fill in your secrets and database info.

### 3. Run the app

```shell
PYTHONPATH=src gunicorn src.app:app
```

Or for development:

```shell
PYTHONPATH=src gunicorn src.app:app --reload
```

### 4. Seed users

```shell
PYTHONPATH=src python src/seed/seed_users.py
```

## Useful scripts

- `src/seed/seed_users.py` — Seed the database with fake users
- `src/routes/` — API route blueprints
- `src/utils/` — Utility modules (DB, consts, etc)

## Troubleshooting

- If you get `ModuleNotFoundError: No module named 'utils'`, make sure to set `PYTHONPATH=src` when running scripts from the project root.
- For CORS issues, check your `CORS` setup in `src/app.py`.
- For bcrypt errors, use Python 3.12 and ensure `bcrypt` is installed.

## License

MIT

## Author

[Julien Sebag](https://julien-sebag.com)