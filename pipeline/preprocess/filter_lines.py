#!/usr/bin/env python3
"""現況の路線地物を抽出し、タイル生成用GeoJSONを書き出す。

`geojson/N06-25_HighwaySection.geojson` から供用期間終了年（`N06_003`）が
`9999`（現況として有効）の地物のみを抽出し、スタイリング／ラベル表示に必要な
属性（路線名・路線種別区分・車線数）のみを残した
`pipeline/output/lines.current.geojson` を書き出す。通称名（`common_name`）・
路線番号（`route_number`）は、それぞれ独立した対応表・条件で解決する
（design.md 決定2）。

- `common_name`: 法定路線名（`route_name`）が`route_common_names.ROUTE_COMMON_NAMES`
  にヒットする地物にのみ付与する。
- `route_number`: 路線種別区分（`route_category`）が`1`〜`5`のいずれかであり、
  `route_name`が`route_numbers.ROUTE_NUMBERS`にヒットする地物に、`common_name`の
  有無にかかわらず付与する。

各路線地物には、ジオメトリの始点・終点座標に空間的に一致する接合部の地点名
（`N06_018`）を`start_point_name`・`end_point_name`として付与する
（add-joint-based-route-matching design.md 決定2）。現況路線地物の`geometry`は
いずれも単一パートの`MultiLineString`（`coordinates`の要素数は常に1）である
ことをデータ確認済みのため、最初のパートの最初・最後の座標を始点・終点として
扱う。

法定路線名による`ROUTE_COMMON_NAMES`照合で`common_name`が解決されなかった
路線地物のうち、`route_category`が`1`であり、`start_point_name`・
`end_point_name`が両方付与されているものについては、
`route_common_names_by_endpoints.ROUTE_COMMON_NAMES_BY_ENDPOINTS`との追加照合
により`common_name`を解決する（add-joint-based-route-matching design.md 決定3）。

法定路線名による`ROUTE_NUMBERS`照合で`route_number`が解決されなかった路線
地物のうち、`route_category`が`1`〜`5`のいずれかであり、`common_name`が
（上記いずれかの経路により）付与されているものについては、
`route_numbers_by_common_name.ROUTE_NUMBERS_BY_COMMON_NAME`との追加照合により
`route_number`を解決する（add-joint-based-route-matching design.md 決定4）。

OpenSpec Change: highway-facility-map, add-route-common-name-jct-lanes, add-mlit-route-numbering, add-joint-based-route-matching
tasks.md: 2.1, 2.2 / 2.1 / 2.1 / 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3
"""
import json
from pathlib import Path

from shapely.geometry import Point, shape

from filter_points import POINT_TYPE_IMPORTANCE_ORDER
from route_common_names import ROUTE_COMMON_NAMES
from route_common_names_by_endpoints import ROUTE_COMMON_NAMES_BY_ENDPOINTS
from route_numbers import ROUTE_NUMBERS
from route_numbers_by_common_name import ROUTE_NUMBERS_BY_COMMON_NAME
from spatial_match import matching_values

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = REPO_ROOT / "geojson" / "N06-25_HighwaySection.geojson"
JOINT_INPUT_PATH = REPO_ROOT / "geojson" / "N06-25_Joint.geojson"
OUTPUT_PATH = REPO_ROOT / "pipeline" / "output" / "lines.current.geojson"

CURRENT_END_YEAR = 9999
JOINT_END_YEAR_FIELD = "N06_014"

# route_numberの解決対象とする路線種別区分（design.md 決定1・決定2）。
# 6（その他）は対象外。
ROUTE_NUMBER_CATEGORIES = {"1", "2", "3", "4", "5"}


def load_joint_geometries(joint_source):
    """現況接合部地物ごとの(ジオメトリ, (接合部種別, 地点名))のリストを構築する。"""
    return [
        (shape(feature["geometry"]), (props.get("N06_019"), props.get("N06_018")))
        for feature in joint_source["features"]
        if (props := feature["properties"]).get(JOINT_END_YEAR_FIELD) == CURRENT_END_YEAR
    ]


def endpoint_joint_name(point_geom, joint_geometries):
    """路線の端点座標に空間的に一致する接合部の地点名を1件解決する。

    一致する接合部が存在しない場合は`None`を返す。同一座標に複数の接合部が
    一致する場合、接合部種別の重要度順（ジャンクション＞一般IC＞スマートIC＞
    その他の接合部、`filter_points.py`の`POINT_TYPE_IMPORTANCE_ORDER`）で
    最も重要度の高い接合部を採用する（design.md 決定2）。
    """
    matches = matching_values(point_geom, joint_geometries)
    if not matches:
        return None
    point_type, point_name = min(
        matches, key=lambda match: POINT_TYPE_IMPORTANCE_ORDER[match[0]]
    )
    return point_name


def endpoint_common_name(route_name, start_point_name, end_point_name):
    """始点・終点接合部名の組から、追加対応表で`common_name`を解決する。

    `route_name`が対応表に存在しない場合、または始点・終点接合部名の組に
    一致するエントリがない場合は`None`を返す（design.md 決定3）。
    """
    entries = ROUTE_COMMON_NAMES_BY_ENDPOINTS.get(route_name)
    if entries is None:
        return None
    points = frozenset({start_point_name, end_point_name})
    for entry in entries:
        if entry["points"] == points:
            return entry["common_name"]
    return None


def filter_current_lines(source, joint_geometries):
    features = []
    for feature in source["features"]:
        props = feature["properties"]
        if props.get("N06_003") != CURRENT_END_YEAR:
            continue
        route_name = props.get("N06_007")
        route_category = props.get("N06_008")
        properties = {
            "route_name": route_name,
            "route_category": route_category,
            "lane_count": int(props.get("N06_010")),
        }

        line_coords = feature["geometry"]["coordinates"][0]
        start_point_name = endpoint_joint_name(
            Point(line_coords[0]), joint_geometries
        )
        if start_point_name is not None:
            properties["start_point_name"] = start_point_name
        end_point_name = endpoint_joint_name(
            Point(line_coords[-1]), joint_geometries
        )
        if end_point_name is not None:
            properties["end_point_name"] = end_point_name

        common_name_entry = ROUTE_COMMON_NAMES.get(route_name)
        if common_name_entry is not None:
            properties["common_name"] = common_name_entry["common_name"]
        elif (
            route_category == "1"
            and start_point_name is not None
            and end_point_name is not None
        ):
            endpoint_common_name_value = endpoint_common_name(
                route_name, start_point_name, end_point_name
            )
            if endpoint_common_name_value is not None:
                properties["common_name"] = endpoint_common_name_value

        if route_category in ROUTE_NUMBER_CATEGORIES:
            route_number = ROUTE_NUMBERS.get(route_name)
            if route_number is None:
                common_name_value = properties.get("common_name")
                if common_name_value is not None:
                    route_number = ROUTE_NUMBERS_BY_COMMON_NAME.get(common_name_value)
            if route_number is not None:
                properties["route_number"] = route_number

        features.append(
            {
                "type": "Feature",
                "geometry": feature["geometry"],
                "properties": properties,
            }
        )
    return {"type": "FeatureCollection", "features": features}


def main():
    with open(INPUT_PATH, encoding="utf-8") as f:
        source = json.load(f)
    with open(JOINT_INPUT_PATH, encoding="utf-8") as f:
        joint_source = json.load(f)

    joint_geometries = load_joint_geometries(joint_source)
    result = filter_current_lines(source, joint_geometries)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    print(
        f"{INPUT_PATH.name}: {len(source['features'])} 件中 "
        f"{len(result['features'])} 件が現況 -> {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
