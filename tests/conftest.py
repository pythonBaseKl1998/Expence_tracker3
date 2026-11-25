import pytest
from app import app as flask_app
from models import db as _db


@pytest.fixture
def app():
    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SECRET_KEY="test",
    )
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """Клиент с залогиненным пользователем и UTC+0."""
    client.post("/register", data={
        "username": "testuser",
        "name": "Иван",
        "password": "secret123",
        "confirm": "secret123",
    }, follow_redirects=True)
    client.post("/login", data={
        "username": "testuser",
        "password": "secret123",
    }, follow_redirects=True)
    client.set_cookie("tz_offset", "0")
    return client
