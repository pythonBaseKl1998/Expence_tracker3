from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    FloatField,
    SelectField,
    SubmitField,
    DateField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
    EqualTo,
)

MONTH_CHOICES = [
    ("01", "Январь"), ("02", "Февраль"), ("03", "Март"),
    ("04", "Апрель"), ("05", "Май"), ("06", "Июнь"),
    ("07", "Июль"), ("08", "Август"), ("09", "Сентябрь"),
    ("10", "Октябрь"), ("11", "Ноябрь"), ("12", "Декабрь"),
]


def build_year_choices(start, end):
    """Список (str, str) для SelectField: ('2024', '2024'), ..."""
    return [(str(y), str(y)) for y in range(start, end + 1)]


class RegisterForm(FlaskForm):
    username = StringField(
        "Логин", validators=[DataRequired(), Length(min=3, max=40)]
    )
    name = StringField("Имя", validators=[Optional(), Length(max=80)])
    password = PasswordField(
        "Пароль", validators=[DataRequired(), Length(min=6, max=128)]
    )
    confirm = PasswordField(
        "Повтор пароля", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    username = StringField("Логин", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")


class ExpenseForm(FlaskForm):
    amount = FloatField(
        "Сумма, ₽", validators=[DataRequired(), NumberRange(min=0.01)]
    )
    type = SelectField(
        "Тип",
        choices=[("expense", "Расход"), ("income", "Доход")],
        validators=[DataRequired()],
    )
    category_id = SelectField(
        "Категория", coerce=int, validators=[DataRequired()]
    )
    description = StringField(
        "Описание", validators=[Optional(), Length(max=200)]
    )
    date = DateField("Дата", validators=[DataRequired()], format="%Y-%m-%d")
    time = StringField(
        "Время (ЧЧ:ММ)", validators=[Optional(), Length(min=5, max=5)]
    )
    submit = SubmitField("Сохранить")


class BudgetForm(FlaskForm):
    category_id = SelectField(
        "Категория", coerce=int, validators=[DataRequired()]
    )
    month = SelectField(
        "Месяц",
        choices=MONTH_CHOICES,
        validators=[DataRequired()],
    )
    year = SelectField(
        "Год",
        choices=[],  # заполняется в роуте
        validators=[DataRequired()],
    )
    limit_amount = FloatField(
        "Лимит, ₽", validators=[DataRequired(), NumberRange(min=0.01)]
    )
    submit = SubmitField("Создать")


class ProfileForm(FlaskForm):
    name = StringField("Имя", validators=[Optional(), Length(max=80)])
    old_password = PasswordField("Текущий пароль", validators=[Optional()])
    new_password = PasswordField(
        "Новый пароль", validators=[Optional(), Length(min=6)]
    )
    submit = SubmitField("Сохранить")


class CategoryForm(FlaskForm):
    name = StringField(
        "Название", validators=[DataRequired(), Length(min=1, max=50)]
    )
    submit = SubmitField("Добавить")