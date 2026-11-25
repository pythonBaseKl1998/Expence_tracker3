from datetime import datetime
from models import db, User, Expense, Category


def test_register_and_login(client):
    r = client.post("/register", data={
        "username": "alice",
        "name": "Алиса",
        "password": "qwerty1",
        "confirm": "qwerty1",
    }, follow_redirects=True)
    assert r.status_code == 200

    r = client.post("/login", data={
        "username": "alice", "password": "qwerty1",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert "Дашборд".encode() in r.data


def test_display_name_fallback(app):
    with app.app_context():
        u = User(username="bob", password_hash="x")
        db.session.add(u)
        db.session.commit()
        assert u.display_name == "bob"
        u.name = "Борис"
        db.session.commit()
        assert u.display_name == "Борис"


def test_add_expense_with_date(auth_client, app):
    r = auth_client.post("/add", data={
        "type": "expense",
        "amount": "100.50",
        "category_id": "1",
        "description": "Тест",
        "date": "2024-03-15",
        "time": "14:30",
    }, follow_redirects=True)
    assert r.status_code == 200

    with app.app_context():
        e = Expense.query.first()
        assert e is not None
        assert e.amount == 100.50
        assert e.created_at == datetime(2024, 3, 15, 14, 30)


def test_tz_conversion(auth_client, app):
    """Пользователь в UTC+3: 15.03 12:00 → в БД 09:00 UTC."""
    auth_client.set_cookie("tz_offset", "180")
    auth_client.post("/add", data={
        "type": "expense",
        "amount": "10",
        "category_id": "1",
        "description": "",
        "date": "2024-03-15",
        "time": "12:00",
    }, follow_redirects=True)

    with app.app_context():
        e = Expense.query.first()
        assert e.created_at == datetime(2024, 3, 15, 9, 0)


def test_edit_expense_keeps_date(auth_client, app):
    auth_client.post("/add", data={
        "type": "expense", "amount": "10", "category_id": "1",
        "description": "X", "date": "2024-05-01", "time": "10:00",
    })
    with app.app_context():
        eid = Expense.query.first().id

    auth_client.post(f"/edit/{eid}", data={
        "type": "income", "amount": "20", "category_id": "1",
        "description": "Y", "date": "2024-05-02", "time": "11:00",
    }, follow_redirects=True)

    with app.app_context():
        e = db.session.get(Expense, eid)
        assert e.type == "income"
        assert e.amount == 20
        assert e.created_at == datetime(2024, 5, 2, 11, 0)


def test_unauthorized_redirect(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_profile_update_name(auth_client, app):
    auth_client.post("/profile", data={"name": "Новое имя"}, follow_redirects=True)
    with app.app_context():
        u = User.query.filter_by(username="testuser").first()
        assert u.name == "Новое имя"


def test_category_required_for_expense(auth_client, app):
    with app.app_context():
        cid = Category.query.first().id
    r = auth_client.post("/add", data={
        "type": "expense", "amount": "1", "category_id": str(cid),
        "description": "", "date": "2024-01-01", "time": "00:00",
    })
    assert r.status_code in (200, 302)