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

OpenSpec Change: highway-facility-map, add-route-common-name-jct-lanes, add-mlit-route-numbering
tasks.md: 2.1, 2.2 / 2.1 / 2.1
"""
import json
from pathlib import Path

from route_common_names import ROUTE_COMMON_NAMES
from route_numbers import ROUTE_NUMBERS

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = REPO_ROOT / "geojson" / "N06-25_HighwaySection.geojson"
OUTPUT_PATH = REPO_ROOT / "pipeline" / "output" / "lines.current.geojson"

CURRENT_END_YEAR = 9999

# route_numberの解決対象とする路線種別区分（design.md 決定1・決定2）。
# 6（その他）は対象外。
ROUTE_NUMBER_CATEGORIES = {"1", "2", "3", "4", "5"}


def filter_current_lines(source):
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
        common_name_entry = ROUTE_COMMON_NAMES.get(route_name)
        if common_name_entry is not None:
            properties["common_name"] = common_name_entry["common_name"]
        if route_category in ROUTE_NUMBER_CATEGORIES:
            route_number = ROUTE_NUMBERS.get(route_name)
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

    result = filter_current_lines(source)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    print(
        f"{INPUT_PATH.name}: {len(source['features'])} 件中 "
        f"{len(result['features'])} 件が現況 -> {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
