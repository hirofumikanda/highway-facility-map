#!/usr/bin/env python3
"""現況の路線地物を抽出し、タイル生成用GeoJSONを書き出す。

`geojson/N06-25_HighwaySection.geojson` から供用期間終了年（`N06_003`）が
`9999`（現況として有効）の地物のみを抽出し、スタイリング／ラベル表示に必要な
属性（路線名・路線種別区分・車線数）のみを残した
`pipeline/output/lines.current.geojson` を書き出す。

OpenSpec Change: highway-facility-map
tasks.md: 2.1, 2.2
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = REPO_ROOT / "geojson" / "N06-25_HighwaySection.geojson"
OUTPUT_PATH = REPO_ROOT / "pipeline" / "output" / "lines.current.geojson"

CURRENT_END_YEAR = 9999


def filter_current_lines(source):
    features = []
    for feature in source["features"]:
        props = feature["properties"]
        if props.get("N06_003") != CURRENT_END_YEAR:
            continue
        features.append(
            {
                "type": "Feature",
                "geometry": feature["geometry"],
                "properties": {
                    "route_name": props.get("N06_007"),
                    "route_category": props.get("N06_008"),
                    "lane_count": int(props.get("N06_010")),
                },
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
