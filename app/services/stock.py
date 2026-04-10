from app.models import Product
from app.cache import redis_client


def verifier_stock(product: Product, quantite: int) -> bool:
    if quantite <= 0:
        raise ValueError("Quantité invalide")
    return product.stock >= quantite


def reserver_stock(product: Product, quantite: int, session) -> Product:
    if quantite <= 0:
        raise ValueError("Quantité invalide")

    if not verifier_stock(product, quantite):
        raise ValueError(f'Stock insuffisant : {product.stock} disponible(s)')

    product.stock -= quantite
    session.commit()

    redis_client.delete(f'product:{product.id}:stock')
    return product


def liberer_stock(product: Product, quantite: int, session) -> Product:
    if quantite <= 0:
        raise ValueError("Quantité invalide")

    product.stock += quantite
    session.commit()

    redis_client.set(f'product:{product.id}:stock', product.stock)
    return product