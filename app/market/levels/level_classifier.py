class LevelClassifier:
    def classify(self, levels, current_price: float):
        supports = []
        resistances = []

        for lvl in levels:
            if current_price > lvl["max_price"]:
                supports.append(lvl)
            elif current_price < lvl["min_price"]:
                resistances.append(lvl)

        supports.sort(key=lambda x: abs(current_price - x["avg_price"]))
        resistances.sort(key=lambda x: abs(current_price - x["avg_price"]))

        return {
            "supports": supports,
            "resistances": resistances,
        }
