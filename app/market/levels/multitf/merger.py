from app.market.models import Timeframe

from .zones import LevelPoint, MergedZone

_TF_WEIGHT: dict[Timeframe, float] = {
    Timeframe.H1: 1.0,
    Timeframe.H4: 2.0,
    Timeframe.D1: 3.0,
}


def merge_levels_to_zones(*, points: list[LevelPoint], merge_tol: float) -> list[MergedZone]:
    """
    Combines levels (LevelPoint) from different TF into common zones (MergedZone)
    in the vicinity of avg_price.

    merge_tol — price tolerance: if the centers of the zones are close, we assume that this is one zone.
    """
    if merge_tol <= 0:
        raise ValueError("merge_tol must be > 0")

    if not points:
        return []

    zones: list[dict] = []

    # Sorting by the center of the zone
    for point in sorted(points, key=lambda p: p.avg_price):
        zone = _find_matching_zone(zones, point, merge_tol)

        if zone is None:
            zones.append(_new_zone_from_point(point))
        else:
            _merge_point_into_zone(zone, point)

    return [_to_merged_zone(z) for z in zones]


# ---------- helpers ----------


def _find_matching_zone(zones: list[dict], point: LevelPoint, merge_tol: float) -> dict | None:
    """
    searches among the already collected zones for one where you can add a new level point.
    """
    for z in zones:
        if abs(point.avg_price - z["avg_price"]) <= merge_tol:
            return z
    return None


def _point_score(point: LevelPoint) -> float:
    """
    count the "weight" of one point.
    """
    return point.touches * _TF_WEIGHT.get(point.tf, 1.0)


def _new_zone_from_point(point: LevelPoint) -> dict:
    """
    Create a new zone from a single LevelPoint.
    """
    score = _point_score(point)
    return {
        "kind": point.kind,
        "min_price": point.min_price,
        "max_price": point.max_price,
        "avg_price": point.avg_price,
        "touches_total": point.touches,
        "tfs": {point.tf},
        "score": score,
    }


def _merge_point_into_zone(zone: dict, point: LevelPoint) -> None:
    zone["min_price"] = min(zone["min_price"], point.min_price)
    zone["max_price"] = max(zone["max_price"], point.max_price)

    point_score = _point_score(point)
    old_score = zone["score"]
    new_score = old_score + point_score

    zone["avg_price"] = (zone["avg_price"] * old_score + point.avg_price * point_score) / new_score

    zone["score"] = new_score
    zone["touches_total"] += point.touches
    zone["tfs"].add(point.tf)


def _to_merged_zone(zone: dict) -> MergedZone:
    return MergedZone(
        kind=zone["kind"],
        min_price=zone["min_price"],
        max_price=zone["max_price"],
        avg_price=zone["avg_price"],
        touches_total=zone["touches_total"],
        tfs=tuple(zone["tfs"]),
        score=float(zone["score"]),
    )
