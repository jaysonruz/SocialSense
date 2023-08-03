
# Useful Commands:
## alembic commands
- alembic init migrations
- alembic revision --autogenerate -m "initial"
- alembic upgrade head

## Fastapi commands
- uvicorn main:app --reload
- uvicorn main:app --host 0.0.0.0 --port 8000