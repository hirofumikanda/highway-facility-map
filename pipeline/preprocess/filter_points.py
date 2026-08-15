#!/usr/bin/env python3
"""現況の地点地物を抽出し、重要度ティア付きのタイル生成用GeoJSONを書き出す。

`geojson/N06-25_Joint.geojson` から供用期間終了年（`N06_014`）が `9999`
（現況として有効）の地物のみを抽出し、スタイリング／ラベル表示に必要な属性
（地点名・接合部種別）を残す。あわせて、接合部種別（`N06_019`）に基づく重要度
順（ジャンクション ＞ 一般インターチェンジ・スマートインターチェンジ ＞
その他の接合部）に沿ったtippecanoe用`minzoom`を地物ごとに付与し、
`pipeline/output/points.current.geojson` を書き出す。

minzoomの割り当ては design.md の「決定5」に基づく設計値であり、後続のタイル
生成・表示確認（Issue #3, #7）でのビジュアル確認により調整され得る。

ジャンクション（接合部種別`3`）については、接続する路線の車線数合計に基づく
`symbolrank`（1〜3、値が小さいほど上位）を付与し、`symbolrank`から細分化した
minzoom（8/9/10）を用いる（add-jct-symbolrank design.md 決定1〜3）。

一般インターチェンジ・スマートインターチェンジ（接合部種別`1`・`2`）に
ついては、接続する路線地物の法定路線名（`route_name`、複数の場合はその組を
1つの複合グループとして扱う）でグループ化した上で、
`point_population.surrounding_population`で算出した周辺人口のグループ内
相対順位（人口降順の四分位）から`symbolrank`（2〜5、値が小さいほど上位）を
付与し、`IC_SIC_SYMBOLRANK_MINZOOM`から細分化したminzoom（9/10/11/12）を
用いる（add-ic-sic-symbolrank design.md 決定3〜5）。

地点座標とライン地物の座標一致判定は`spatial_match.py`の共通ロジックを用いる
（add-joint-based-route-matching design.md 決定1）。

OpenSpec Change: highway-facility-map, add-jct-symbolrank, add-joint-based-route-matching, add-ic-sic-symbolrank, demote-city-other-joints
tasks.md: 2.3, 2.4 / 1.1, 1.2 / 1.2 / 2.1, 2.2, 2.3, 2.4（GitHub Issue #106） / 1.1-1.3, 2.1-2.4（GitHub Issue #117, #118）
"""
import json
from collections import defaultdict
from pathlib import Path

from shapely.geometry import shape

from point_population import surrounding_population
from spatial_match import matching_values

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = REPO_ROOT / "geojson" / "N06-25_Joint.geojson"
LINES_PATH = REPO_ROOT / "pipeline" / "output" / "lines.current.geojson"
OUTPUT_PATH = REPO_ROOT / "pipeline" / "output" / "points.current.geojson"

CURRENT_END_YEAR = 9999

# N06_019（接合部種別コード） -> tippecanoeの地物単位minzoom
# ジャンクション(3)、その他(4)は種別固定値を用いる。一般IC(1)・スマートIC(2)は
# 種別固定のminzoomを廃止し、地点固有のsymbolrankから導出する
# （IC_SIC_SYMBOLRANK_MINZOOM、add-ic-sic-symbolrank design.md 決定5）。
# ジャンクションについても、地物ごとのsymbolrank（下記）に応じてさらに
# minzoomを細分化する（add-jct-symbolrank design.md 決定3）。この辞書の
# "3"の値はsymbolrank=1のジャンクションのminzoomと一致する。
POINT_TYPE_MINZOOM = {
    "3": 8,  # ジャンクション
    "4": 14,  # その他の接合部
}

# 接合部種別の重要度順（値が小さいほど重要度が高い。ジャンクション＞一般IC＞
# スマートIC＞その他の接合部）。複数の接合部地物が同一座標に一致する場合の
# 優先順位判定（filter_lines.pyのendpoint_joint_name）や、既知の接合部種別
# コードの検証に用いる。POINT_TYPE_MINZOOMからIC・SICの固定値を廃止した後も
# この順序自体は変わらないため、独立した対応表として定義する。
POINT_TYPE_IMPORTANCE_ORDER = {"3": 0, "1": 1, "2": 2, "4": 3}

# IC・SICの接合部種別コード（一般インターチェンジ・スマートインターチェンジ）。
IC_SIC_TYPES = {"1", "2"}

# ジャンクションのsymbolrank（1〜4、値が小さいほど上位。4は指定都市高速道路・
# その他限定の補正が適用された場合のみ発生する）->tippecanoeのminzoom
# （add-jct-symbolrank design.md 決定3、demote-city-other-joints design.md 決定3）。
JCT_SYMBOLRANK_MINZOOM = {1: 8, 2: 9, 3: 10, 4: 11}

# IC・SICのsymbolrank（2〜6、値が小さいほど上位。6は指定都市高速道路・その他
# 限定の補正が適用された場合のみ発生する）->tippecanoeのminzoom
# （add-ic-sic-symbolrank design.md 決定5、demote-city-other-joints design.md 決定3）。
IC_SIC_SYMBOLRANK_MINZOOM = {2: 9, 3: 10, 4: 11, 5: 12, 6: 13}

# 路線種別区分（route_category）のうち、指定都市高速道路・その他を表すコード
# （demote-city-other-joints design.md 決定2）。
CITY_OR_OTHER_ROUTE_CATEGORIES = {"5", "6"}


def jct_symbolrank(lane_counts):
    """ジャンクションのsymbolrankを、接続する路線の車線数合計から算出する。

    245件のジャンクション実データでほぼ均等な3群に分かれる閾値
    （合計12以上->1、8〜11->2、7以下->3）を使用する（design.md 決定1・決定2）。
    """
    lane_count_sum = sum(lane_counts)
    if lane_count_sum >= 12:
        return 1
    if lane_count_sum >= 8:
        return 2
    return 3


def ic_sic_symbolrank_group_key(route_names, point_name):
    """IC・SICのsymbolrank算出用グループキーを、接続する法定路線名の組から求める。

    複数の法定路線名に接続する地点は、接続する法定路線名の組（frozenset、
    順不同）を1つの複合グループとして扱う（design.md 決定4）。接続する路線
    地物が1件もない地点は、自身の`point_name`のみをキーとする単独グループ
    （n=1、常にsymbolrank=2）として扱う（design.md 決定4）。
    """
    if not route_names:
        return ("__no_route__", point_name)
    return frozenset(route_names)


def assign_ic_sic_symbolranks(entries):
    """IC・SIC地点のエントリ群に、グループ内人口降順順位から`symbolrank`を算出して設定する。

    `entries`の各要素は`group_key`・`population`・`point_name`キーを持つ辞書。
    同一`group_key`の地点群を1グループとし、グループ内で人口降順に順位付け
    （同順位は`point_name`昇順でタイブレーク）した上で、n件のグループ内で
    r番目（1始まり、人口が多い方から）の地点に
    `symbolrank = 2 + floor((r - 1) * 4 / n)`を設定する（design.md 決定3）。
    """
    groups = defaultdict(list)
    for entry in entries:
        groups[entry["group_key"]].append(entry)

    for group_entries in groups.values():
        n = len(group_entries)
        group_entries.sort(key=lambda e: (-e["population"], e["point_name"]))
        for rank, entry in enumerate(group_entries, start=1):
            entry["symbolrank"] = 2 + (rank - 1) * 4 // n


def load_line_geometries(lines_source):
    """路線地物ごとの(ジオメトリ, 車線数, 法定路線名, 路線種別区分)のリストを構築する。"""
    return [
        (
            shape(feature["geometry"]),
            feature["properties"]["lane_count"],
            feature["properties"]["route_name"],
            feature["properties"]["route_category"],
        )
        for feature in lines_source["features"]
    ]


def connected_lane_counts(point_geom, lane_count_candidates):
    """地点座標に頂点一致判定で接続する路線の車線数を、重複を排除せず昇順ソートして返す。

    同じ車線数を持つ路線が複数接続する場合（主にJCT）も、接続する路線の数だけ
    値を保持する（design.md 決定4）。
    """
    return sorted(matching_values(point_geom, lane_count_candidates))


def connected_route_names(point_geom, route_name_candidates):
    """地点座標に頂点一致判定で接続する路線地物の法定路線名を、一致した順に返す（重複を含む）。"""
    return matching_values(point_geom, route_name_candidates)


def connected_route_categories(point_geom, route_category_candidates):
    """地点座標に頂点一致判定で接続する路線地物のroute_categoryの集合を返す。

    接続する路線地物が1件もない場合は空集合を返す
    （demote-city-other-joints design.md 決定2）。
    """
    return set(matching_values(point_geom, route_category_candidates))


def is_city_or_other_only(route_categories):
    """接続する路線のroute_categoryが、指定都市高速道路・その他のみで構成されるかを判定する。

    `route_categories`が空集合（接続する路線地物が1件もない）の場合は`False`を
    返す（demote-city-other-joints design.md 決定2）。
    """
    return bool(route_categories) and route_categories <= CITY_OR_OTHER_ROUTE_CATEGORIES


def filter_current_points(source, line_geometries):
    lane_count_candidates = [(geom, lane_count) for geom, lane_count, _, _ in line_geometries]
    route_name_candidates = [(geom, route_name) for geom, _, route_name, _ in line_geometries]
    route_category_candidates = [
        (geom, route_category) for geom, _, _, route_category in line_geometries
    ]

    entries = []
    for feature in source["features"]:
        props = feature["properties"]
        if props.get("N06_014") != CURRENT_END_YEAR:
            continue

        point_type = props.get("N06_019")
        if point_type not in POINT_TYPE_IMPORTANCE_ORDER:
            raise ValueError(
                f"未知の接合部種別コード: {point_type!r} "
                f"(N06_015={props.get('N06_015')!r})"
            )

        point_geom = shape(feature["geometry"])
        point_name = props.get("N06_018")
        lane_counts = connected_lane_counts(point_geom, lane_count_candidates)

        properties = {
            "point_name": point_name,
            "point_type": point_type,
            "lane_counts": lane_counts,
        }
        entry = {"geometry": feature["geometry"], "properties": properties}

        if point_type == "3":
            symbolrank = jct_symbolrank(lane_counts)
            route_categories = connected_route_categories(point_geom, route_category_candidates)
            if is_city_or_other_only(route_categories):
                symbolrank += 1
            properties["symbolrank"] = symbolrank
            entry["minzoom"] = JCT_SYMBOLRANK_MINZOOM[symbolrank]
        elif point_type in IC_SIC_TYPES:
            route_names = connected_route_names(point_geom, route_name_candidates)
            entry["group_key"] = ic_sic_symbolrank_group_key(route_names, point_name)
            entry["point_name"] = point_name
            entry["coordinates"] = (point_geom.x, point_geom.y)
            entry["route_categories"] = connected_route_categories(
                point_geom, route_category_candidates
            )
        else:
            entry["minzoom"] = POINT_TYPE_MINZOOM[point_type]

        entries.append(entry)

    ic_sic_entries = [entry for entry in entries if "group_key" in entry]
    if ic_sic_entries:
        populations = surrounding_population(
            [entry["coordinates"] for entry in ic_sic_entries]
        )
        for entry, population in zip(ic_sic_entries, populations):
            entry["population"] = population
        assign_ic_sic_symbolranks(ic_sic_entries)
        for entry in ic_sic_entries:
            symbolrank = entry["symbolrank"]
            if is_city_or_other_only(entry["route_categories"]):
                symbolrank += 1
            entry["properties"]["symbolrank"] = symbolrank
            entry["properties"]["population"] = round(entry["population"])
            entry["minzoom"] = IC_SIC_SYMBOLRANK_MINZOOM[symbolrank]

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": entry["geometry"],
                "properties": entry["properties"],
                "tippecanoe": {"minzoom": entry["minzoom"]},
            }
            for entry in entries
        ],
    }


def main():
    with open(INPUT_PATH, encoding="utf-8") as f:
        source = json.load(f)
    with open(LINES_PATH, encoding="utf-8") as f:
        lines_source = json.load(f)

    line_geometries = load_line_geometries(lines_source)
    result = filter_current_points(source, line_geometries)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    print(
        f"{INPUT_PATH.name}: {len(source['features'])} 件中 "
        f"{len(result['features'])} 件が現況 -> {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
