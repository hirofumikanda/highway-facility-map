"""地点・路線間の座標一致判定を行う共通ロジック。

`filter_points.py`（地点→接続路線の車線数の解決）と`filter_lines.py`（路線の
始点・終点→接合部名の解決）の両方から、同一の距離閾値・判定方法で座標の
空間的な一致を判定するために利用する（add-joint-based-route-matching
design.md 決定1）。

OpenSpec Change: add-joint-based-route-matching
tasks.md: 1.1
"""

# 座標の一致判定に用いる距離閾値（度）。約0.1m相当（highway-facility-map
# design.md 決定4）。国土数値情報の同一整備由来データで座標が実質一致する
# ため、頂点一致判定で十分と考える。
CONNECTION_DISTANCE_THRESHOLD_DEGREES = 1e-6


def is_coincident(geom_a, geom_b):
    """2つのジオメトリが座標一致判定の距離閾値内にあるかを判定する。"""
    return geom_a.distance(geom_b) <= CONNECTION_DISTANCE_THRESHOLD_DEGREES


def matching_values(target_geom, candidates):
    """target_geomに座標一致判定で一致する候補の値を、一致した順に返す。

    `candidates`は`(ジオメトリ, 値)`のイテラブル。一致がなければ空リストを返す。
    """
    return [value for geom, value in candidates if is_coincident(target_geom, geom)]
