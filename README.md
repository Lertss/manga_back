
# Manga_Back

A backend project for manga readers and authors.

## Installation and Setup

1. Clone the repository:

   ```
   
   git clone https://github.com/Lertss/manga_back.git
   
   ```
2. Install dependencies:

    ```
    
    pip install -r requirements.txt
    
    ```
3. Apply migrations:

    ```
    
    python manage.py migrate
    
    ```

4. Run the server:
    ```
    
    python manage.py runserver
    
    ```

## Database Configuration
The project uses the default SQLite database. Change the settings in the settings.py file for a different database.

## Authentication
Authentication is handled by dj_rest_auth and jwt tokens. Provide the necessary parameters in the settings.py file.


## Frontend Task
This backend is designed to be used with Vue.js. However, the frontend is hosted in a separate repository.

  [Link to frontend](https://github.com/Lertss/manga_front_v2)


## Features
User registration and authentication.

Adding manga and its chapters.

Reading manga.

Edit information about the manga.

Tracking the addition of new chapters.

Commenting on manga.

Rating manga.

And more.
