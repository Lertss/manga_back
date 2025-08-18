# Manga_Back

This project is a backend for a manga reading and publishing platform. It provides functionality for user registration, authentication via JWT, adding and editing manga and chapters, commenting and rating works, and tracking new chapters. 
The backend is implemented on Django using REST API, which allows integration with the frontend on Vue.js. 

The project supports functionality extensions and database configuration according to user needs.

## Installation and Setup

1. Clone the repository:

   ```
   git clone https://github.com/Lertss/manga_back.git
   ```

2. Install dependencies using `uv`:

   ```
   uv sync
   ```

   This will install all dependencies listed in `pyproject.toml`, including development dependencies (e.g., `django-debug-toolbar` and `ruff`).

3. Activate the virtual environment:

   On Unix/Linux/macOS:
   ```
   source .venv/bin/activate
   ```

   On Windows:
   ```
   .venv\Scripts\activate
   ```
> [!TIP]
> You can also skip starting the Python environment and use `uv run` instead of `python` in the following commands.

4. Apply migrations:

   ```
   python manage.py migrate
   ```

5. Run the server:

   ```
   python manage.py runserver
   ```

## Database Configuration
The project uses the default SQLite database. Change the settings in `settings.py` for a different database.

## Authentication
Authentication is handled by `dj_rest_auth` and JWT tokens. Provide the necessary parameters in the `settings.py` file.

## Frontend Task
This backend is designed to be used with Vue.js. However, the frontend is hosted in a separate repository.

  [Link to frontend](https://github.com/Lertss/manga_front_v2)

## Features
- User registration and authentication.
- Adding manga and its chapters.
- Reading manga.
- Editing information about the manga.
- Tracking the addition of new chapters.
- Commenting on manga.
- Rating manga.
- And more.
