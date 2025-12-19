from app.market.levels.level_classifier import LevelClassifier


def test_classify_levels():
    current_price = 120.0

    levels = [
        {"min_price": 98.0, "max_price": 102.0, "avg_price": 100.0, "touches": 3},  # support
        {"min_price": 148.0, "max_price": 152.0, "avg_price": 150.0, "touches": 3},  # resistance
        {
            "min_price": 119.0,
            "max_price": 121.0,
            "avg_price": 120.0,
            "touches": 5,
        },  # inside the zone
    ]

    res = LevelClassifier().classify(levels, current_price)

    assert [lvl["avg_price"] for lvl in res["supports"]] == [100.0]
    assert [lvl["avg_price"] for lvl in res["resistances"]] == [150.0]
