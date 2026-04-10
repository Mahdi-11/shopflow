import pytest
from app.services.pricing import calcul_prix_ttc, appliquer_coupon, calculer_total
from app.models import Coupon, Product

# ─────────────────────────────────────────────
# TESTS calcul_prix_ttc
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestCalculPrixTtc:

    def test_prix_normal(self):
        assert calcul_prix_ttc(100.0) == 120.0

    def test_prix_zero(self):
        assert calcul_prix_ttc(0.0) == 0.0

    def test_arrondi_deux_decimales(self):
        assert calcul_prix_ttc(10.0) == 12.0

    def test_prix_negatif_leve_exception(self):
        with pytest.raises(ValueError, match='invalide'):
            calcul_prix_ttc(-5.0)

    @pytest.mark.parametrize('ht,ttc', [
        (50.0, 60.0),
        (199.99, 239.99),
        (0.01, 0.01),
    ])
    def test_parametrise(self, ht, ttc):
        assert calcul_prix_ttc(ht) == ttc


# ─────────────────────────────────────────────
# TESTS appliquer_coupon
# ─────────────────────────────────────────────

class TestAppliquerCoupon:

    def test_reduction_20_pourcent(self, coupon_sample):
        result = appliquer_coupon(100.0, coupon_sample)
        assert result == 80.0

    def test_coupon_inactif_leve_exception(self):
        coupon_inactif = Coupon(code='OLD', reduction=10.0, actif=False)
        with pytest.raises(ValueError, match='inactif'):
            appliquer_coupon(100.0, coupon_inactif)

    def test_reduction_invalide(self):
        coupon_invalide = Coupon(code='BAD', reduction=150.0, actif=True)
        with pytest.raises(ValueError):
            appliquer_coupon(100.0, coupon_invalide)


# ─────────────────────────────────────────────
# PARAMETRIZED TESTS appliquer_coupon
# ─────────────────────────────────────────────

@pytest.mark.parametrize('reduction,prix_initial,prix_attendu', [
    (10, 100.0, 90.0),
    (50, 200.0, 100.0),
    (100, 50.0, 0.0),
    (1, 100.0, 99.0),
])
def test_coupon_reductions_diverses(reduction, prix_initial, prix_attendu):
    coupon = Coupon(code=f'TEST{reduction}', reduction=float(reduction), actif=True)
    assert appliquer_coupon(prix_initial, coupon) == prix_attendu


# ─────────────────────────────────────────────
# TESTS calculer_total
# ─────────────────────────────────────────────

def test_calculer_total_avec_coupon(db_session, coupon_sample):
    p1 = Product(name="P1", price=50.0, stock=10)
    p2 = Product(name="P2", price=30.0, stock=10)

    db_session.add_all([p1, p2])
    db_session.commit()

    produits = [
        (p1, 1),
        (p2, 1),
    ]

    total = calculer_total(produits, coupon_sample)

    assert total == 76.8


def test_calculer_total_sans_coupon(db_session):
    p = Product(name="P", price=100.0, stock=10)
    db_session.add(p)
    db_session.commit()

    total = calculer_total([(p, 1)])

    assert total == 120.0


def test_calculer_total_liste_vide():
    assert calculer_total([]) == 0.0