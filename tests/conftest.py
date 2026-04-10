# tests/conftest.py
"""
Fixtures partagées entre tous les tests.
Hiérarchie : db_engine → db_session → product_sample / coupon_sample
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app.models import Product, Cart, CartItem, Order, Coupon


# ── FIXTURES BASE DE DONNÉES ───────────────────────────────────

@pytest.fixture(scope="function")
def db_engine():
    """
    Moteur SQLite en mémoire, recréé pour chaque test.
    StaticPool force une connexion unique (obligatoire avec :memory:).
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Session SQLAlchemy fraîche pour chaque test.
    Rollback automatique après chaque test → isolation garantie.
    """
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


# ── FIXTURES DE DONNÉES ────────────────────────────────────────

@pytest.fixture
def product_sample(db_session):
    """
    Produit prêt à l'emploi : Laptop Pro, 999.99€ HT, stock=10.
    """
    p = Product(
        name="Laptop Pro",
        price=999.99,
        stock=10,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture
def coupon_sample(db_session):
    """
    Coupon prêt à l'emploi : PROMO20, 20% de réduction, actif=True.
    """
    c = Coupon(
        code="PROMO20",
        reduction=20.0,
        actif=True,
    )
    db_session.add(c)
    db_session.commit()
    return c