
# Useful Commands:
## virtual environment
<<<<<<< HEAD
- python -m venv .venv 
=======
- python -m venv .venv
>>>>>>> 746f198efc841eefb246ea74eb8d915ede8d776a

## install requirements
- pip install -r requirements.txt

## alembic commands
- alembic init migrations
- alembic revision --autogenerate -m "initial"
- alembic upgrade head

## Fastapi commands
- uvicorn main:app --reload
- uvicorn main:app --host 0.0.0.0 --port 80 --reload