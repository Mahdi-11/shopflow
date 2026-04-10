# tests/unit/test_cart.py
"""
Tests unitaires de app/services/cart.py

Couvre :
  - ajouter_au_panier()    → ajoute un produit (ou incrémente la quantité)
  - vider_panier()         → supprime tous les items du panier
  - calculer_sous_total()  → somme des (prix × quantité) des items du panier
"""
import pytest
from app.services.cart import ajouter_au_panier, vider_panier, calculer_sous_total
from app.models import Cart, CartItem, Product


# ── Fixtures locales ───────────────────────────────────────────

@pytest.fixture
def cart(db_session):
    """Panier vide prêt à l'emploi."""
    c = Cart()
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


@pytest.fixture
def cart_avec_items(db_session, product_sample, cart):
    """
    Panier contenant 2 unités du product_sample (Laptop Pro 999.99€).
    Sous-total brut = 2 × 999.99 = 1999.98€
    """
    item = CartItem(cart_id=cart.id, product_id=product_sample.id, quantite=2)
    db_session.add(item)
    db_session.commit()
    return cart


# ── ajouter_au_panier() ────────────────────────────────────────

class TestAjouterAuPanier:

    def test_ajout_nouveau_produit(self, db_session, cart, product_sample):
        """
        Ajouter un produit absent du panier → un CartItem est créé.
        """
        updated_cart = ajouter_au_panier(
            cart_id=cart.id,
            product_id=product_sample.id,
            quantite=1,
            session=db_session,
        )
        items = db_session.query(CartItem).filter_by(cart_id=cart.id).all()
        assert len(items) == 1
        assert items[0].quantite == 1

    def test_ajout_produit_existant_incremente_quantite(self, db_session, cart_avec_items, product_sample):
        """
        Ajouter un produit déjà dans le panier → la quantité s'additionne.
        Panier initial : 2 unités → après ajout de 3 → 5 unités.
        """
        ajouter_au_panier(
            cart_id=cart_avec_items.id,
            product_id=product_sample.id,
            quantite=3,
            session=db_session,
        )
        item = db_session.query(CartItem).filter_by(
            cart_id=cart_avec_items.id,
            product_id=product_sample.id,
        ).first()
        assert item.quantite == 5

    def test_ajout_quantite_zero_leve_exception(self, db_session, cart, product_sample):
        """Quantité = 0 → ValueError."""
        with pytest.raises(ValueError):
            ajouter_au_panier(cart.id, product_sample.id, quantite=0, session=db_session)

    def test_ajout_quantite_negative_leve_exception(self, db_session, cart, product_sample):
        """Quantité négative → ValueError."""
        with pytest.raises(ValueError):
            ajouter_au_panier(cart.id, product_sample.id, quantite=-2, session=db_session)

    def test_ajout_produit_inexistant_leve_exception(self, db_session, cart):
        """Produit introuvable en base → ValueError."""
        with pytest.raises(ValueError):
            ajouter_au_panier(cart.id, product_id=99999, quantite=1, session=db_session)

    def test_ajout_panier_inexistant_leve_exception(self, db_session, product_sample):
        """Panier introuvable → ValueError."""
        with pytest.raises(ValueError):
            ajouter_au_panier(cart_id=99999, product_id=product_sample.id, quantite=1, session=db_session)


# ── vider_panier() ─────────────────────────────────────────────

class TestViderPanier:

    def test_vider_panier_supprime_tous_les_items(self, db_session, cart_avec_items):
        """
        Panier avec items → après vider_panier() → aucun CartItem restant.
        """
        vider_panier(cart_id=cart_avec_items.id, session=db_session)

        items = db_session.query(CartItem).filter_by(cart_id=cart_avec_items.id).all()
        assert items == []

    def test_vider_panier_vide_leve_exception(self, db_session, cart):
        """
        Vider un panier déjà vide → ValueError.
        """
        with pytest.raises(ValueError, match="vide"):
            vider_panier(cart_id=cart.id, session=db_session)

    def test_vider_panier_inexistant_leve_exception(self, db_session):
        """Panier introuvable → ValueError."""
        with pytest.raises(ValueError):
            vider_panier(cart_id=99999, session=db_session)


# ── calculer_sous_total() ──────────────────────────────────────

class TestCalculerSousTotal:

    def test_sous_total_panier_avec_items(self, db_session, cart_avec_items, product_sample):
        """
        2 × Laptop Pro (999.99€) = 1999.98€ HT (brut, sans TVA).
        """
        result = calculer_sous_total(cart_id=cart_avec_items.id, session=db_session)
        assert result == round(2 * 999.99, 2)

    def test_sous_total_panier_vide_retourne_zero(self, db_session, cart):
        """Panier vide → sous-total = 0.0."""
        result = calculer_sous_total(cart_id=cart.id, session=db_session)
        assert result == 0.0

    def test_sous_total_plusieurs_produits(self, db_session, cart):
        """
        Produit A (10€ × 3) + Produit B (25€ × 2) = 30 + 50 = 80€.
        """
        prod_a = Product(name="Prod A", price=10.0, stock=10)
        prod_b = Product(name="Prod B", price=25.0, stock=10)
        db_session.add_all([prod_a, prod_b])
        db_session.commit()
        db_session.refresh(prod_a)
        db_session.refresh(prod_b)

        db_session.add_all([
            CartItem(cart_id=cart.id, product_id=prod_a.id, quantite=3),
            CartItem(cart_id=cart.id, product_id=prod_b.id, quantite=2),
        ])
        db_session.commit()

        assert calculer_sous_total(cart_id=cart.id, session=db_session) == 80.0

    def test_sous_total_panier_inexistant_leve_exception(self, db_session):
        """Panier introuvable → ValueError."""
        with pytest.raises(ValueError):
            calculer_sous_total(cart_id=99999, session=db_session)