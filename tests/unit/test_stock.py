import pytest
from app.services.stock import verifier_stock, reserver_stock, liberer_stock

REDIS_MOCK_PATH = "app.services.stock.redis_client"


# ─────────────────────────────────────────────
# TESTS verifier_stock
# ─────────────────────────────────────────────

@pytest.mark.unit
class TestVerifierStock:

    def test_stock_suffisant(self, product_sample):
        assert verifier_stock(product_sample, 5) is True

    def test_stock_insuffisant(self, product_sample):
        assert verifier_stock(product_sample, 999) is False

    def test_stock_exact(self, product_sample):
        assert verifier_stock(product_sample, 10) is True

    def test_quantite_zero(self, product_sample):
        with pytest.raises(ValueError):
            verifier_stock(product_sample, 0)

    def test_quantite_negative(self, product_sample):
        with pytest.raises(ValueError):
            verifier_stock(product_sample, -1)


# ─────────────────────────────────────────────
# TESTS reserver_stock
# ─────────────────────────────────────────────

class TestReserverStock:

    def test_reservation_reussie(self, product_sample, db_session, mocker):
        mock_redis = mocker.patch(REDIS_MOCK_PATH)

        stock_avant = product_sample.stock
        updated = reserver_stock(product_sample, 3, db_session)

        assert updated.stock == stock_avant - 3
        mock_redis.delete.assert_called_once()

    def test_cle_redis_correcte(self, product_sample, db_session, mocker):
        mock_redis = mocker.patch(REDIS_MOCK_PATH)

        reserver_stock(product_sample, 1, db_session)

        expected_key = f"product:{product_sample.id}:stock"
        mock_redis.delete.assert_called_once_with(expected_key)

    def test_stock_insuffisant(self, product_sample, db_session, mocker):
        mocker.patch(REDIS_MOCK_PATH)

        with pytest.raises(ValueError, match="insuffisant"):
            reserver_stock(product_sample, 999, db_session)

    def test_pas_modification_si_echec(self, product_sample, db_session, mocker):
        mocker.patch(REDIS_MOCK_PATH)

        stock_avant = product_sample.stock

        with pytest.raises(ValueError):
            reserver_stock(product_sample, 999, db_session)

        assert product_sample.stock == stock_avant

    def test_redis_non_appele_si_echec(self, product_sample, db_session, mocker):
        mock_redis = mocker.patch(REDIS_MOCK_PATH)

        with pytest.raises(ValueError):
            reserver_stock(product_sample, 999, db_session)

        mock_redis.delete.assert_not_called()


# ─────────────────────────────────────────────
# TESTS liberer_stock
# ─────────────────────────────────────────────

class TestLibererStock:

    def test_liberation_stock(self, product_sample, db_session, mocker):
        mock_redis = mocker.patch(REDIS_MOCK_PATH)

        stock_avant = product_sample.stock

        updated = liberer_stock(product_sample, 2, db_session)

        assert updated.stock == stock_avant + 2

        expected_key = f"product:{product_sample.id}:stock"
        mock_redis.set.assert_called_once_with(expected_key, updated.stock)

    def test_quantite_invalide(self, product_sample, db_session, mocker):
        mocker.patch(REDIS_MOCK_PATH)

        with pytest.raises(ValueError):
            liberer_stock(product_sample, 0, db_session)

# ─────────────────────────────────────────────
# test_liberation_stock()
# ─────────────────────────────────────────────

def test_liberation_stock(self, product_sample, db_session, mocker):
    mock_redis = mocker.patch("app.services.stock.redis_client")

    stock_avant = product_sample.stock

    updated = liberer_stock(product_sample, 2, db_session)

    assert updated.stock == stock_avant + 2

    expected_key = f"product:{product_sample.id}:stock"
    mock_redis.set.assert_called_once_with(expected_key, updated.stock)