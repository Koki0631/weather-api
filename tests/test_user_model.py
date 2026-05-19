from sqlalchemy import create_engine, inspect

from app.db import Base
from app.models.user import User


def test_user_table_is_registered() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    table_names = inspect(engine).get_table_names()
    assert "users" in table_names

    columns = {column["name"] for column in inspect(engine).get_columns("users")}
    assert columns == {
        "id",
        "email",
        "hashed_password",
        "created_at",
    }

    assert User.__table__.c.email.unique is True
    assert User.__table__.c.email.index is True
