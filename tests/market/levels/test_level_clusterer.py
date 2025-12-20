from app.market.levels.level_clusterer import LevelClusterer


def test_cluster_levels():
    pivot_prices = [
        100.0,
        100.2,
        99.9,
        150.0,
        150.1,
        149.9,
        200.0,
    ]

    tolerance = 0.3
    levels = LevelClusterer().build_levels(pivot_prices, tolerance, min_touches=2)

    assert len(levels) == 2

    avgs = sorted([lvl["avg_price"] for lvl in levels])

    assert 99.8 < avgs[0] < 100.2
    assert 149.8 < avgs[1] < 150.2

    touches = sorted([lvl["touches"] for lvl in levels])
    assert touches == [3, 3]
