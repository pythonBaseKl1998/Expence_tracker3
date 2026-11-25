"""
Одноразовая миграция существующей SQLite-БД:
добавляет колонку user.name.
Запуск: python run_once_migrate.py
"""
from sqlalchemy import inspect, text

from app import app
from models import db


with app.app_context():
    inspector = inspect(db.engine)
    columns = {c["name"] for c in inspector.get_columns("user")}
    if "name" not in columns:
        db.session.execute(
            text("ALTER TABLE user ADD COLUMN name VARCHAR(80)")
        )
        db.session.commit()
        print("OK: колонка user.name добавлена")
    else:
        print("OK: колонка user.name уже существует")