# Blog App FastAPI

A small blog API built with FastAPI. It provides authentication (using JWT), posts, tags, categories, and media uploads,
with SQLAlchemy handling database models and persistence.

## Stack

- [FastAPI](https://fastapi.tiangolo.com/) - web framework and API documentation
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM and database access
- SQLite by default, with PostgreSQL support through the configured database URL

## Installation

1. Clone the repository and move into the project directory:

   ```bash
   git clone https://github.com/ASPupiales99/blog-app-fastapi.git
   cd blog-app-fastapi
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

   On Windows, activate it with:

   ```powershell
   venv\Scripts\Activate.ps1
   ```

3. Install the requirements:

   ```bash
   pip install -r requirements.txt
   ```

## Running the application

Start the development server with:

```bash
uvicorn app.main:blog --reload
```

The API is available at `http://127.0.0.1:8000`, and interactive documentation is available at
`http://127.0.0.1:8000/docs`.

By default, the application uses `sqlite:///./blog.db`. Set `DATABASE_URL` in a `.env` file to use another
SQLAlchemy-compatible database.
