def test_calculer_total_avec_coupon(db_session, coupon_sample):
    from app.models import Product
    from app.services.pricing import calculer_total

    # 1. Créer 2 produits
    p1 = Product(name="Produit1", price=50.0, stock=10)
    p2 = Product(name="Produit2", price=30.0, stock=10)

    # 2. Les insérer en base
    db_session.add_all([p1, p2])
    db_session.commit()

    # 3. Construire la liste (produit, quantité)
    produits = [
        (p1, 1),
        (p2, 1),
    ]

    # 4. Appeler la fonction avec coupon
    total = calculer_total(produits, coupon_sample)

    # 5. Vérifier le résultat
    assert total == 76.8