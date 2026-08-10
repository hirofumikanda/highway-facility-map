#!/usr/bin/env python3
"""現況の地点地物を抽出し、重要度ティア付きのタイル生成用GeoJSONを書き出す。

`geojson/N06-25_Joint.geojson` から供用期間終了年（`N06_014`）が `9999`
（現況として有効）の地物のみを抽出し、スタイリング／ラベル表示に必要な属性
（地点名・接合部種別）を残す。あわせて、接合部種別（`N06_019`）に基づく重要度
順（ジャンクション ＞ 一般インターチェンジ ＞ スマートインターチェンジ ＞
その他の接合部）に沿ったtippecanoe用`minzoom`を地物ごとに付与し、
`pipeline/output/points.current.geojson` を書き出す。

minzoomの割り当ては design.md の「決定5」に基づく設計値であり、後続のタイル
生成・表示確認（Issue #3, #7）でのビジュアル確認により調整され得る。

OpenSpec Change: highway-facility-map
tasks.md: 2.3, 2.4
"""
import json
from pathlib import Path

from shapely.geometry import shape

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = REPO_ROOT / "geojson" / "N06-25_Joint.geojson"
LINES_PATH = REPO_ROOT / "pipeline" / "output" / "lines.current.geojson"
OUTPUT_PATH = REPO_ROOT / "pipeline" / "output" / "points.current.geojson"

CURRENT_END_YEAR = 9999

# 地点座標とライン地物の頂点一致判定に用いる距離閾値（度）。約0.1m相当
# （design.md 決定4）。国土数値情報の同一整備由来データで座標が実質一致する
# ため、頂点一致判定で十分と考える。
CONNECTION_DISTANCE_THRESHOLD_DEGREES = 1e-6

# N06_019（接合部種別コード） -> tippecanoeの地物単位minzoom
# ジャンクション(3) > 一般IC(1) > スマートIC(2) > その他(4) の重要度順に、
# 低いズームから段階的に収録されるよう割り当てる（design.md 決定5）。
POINT_TYPE_MINZOOM = {
    "3": 8,  # ジャンクション
    "1": 10,  # 一般インターチェンジ
    "2": 12,  # スマートインターチェンジ
    "4": 14,  # その他の接合部
}


def load_line_geometries(lines_source):
    """路線地物ごとの(ジオメトリ, 車線数)のリストを構築する。"""
    return [
        (shape(feature["geometry"]), feature["properties"]["lane_count"])
        for feature in lines_source["features"]
    ]


def connected_lane_counts(point_geom, line_geometries):
    """地点座標に頂点一致判定で接続する路線の車線数を、重複排除・昇順ソートして返す。"""
    matched = {
        lane_count
        for line_geom, lane_count in line_geometries
        if point_geom.distance(line_geom) <= CONNECTION_DISTANCE_THRESHOLD_DEGREES
    }
    return sorted(matched)


def filter_current_points(source, line_geometries):
    features = []
    for feature in source["features"]:
        props = feature["properties"]
        if props.get("N06_014") != CURRENT_END_YEAR:
            continue

        point_type = props.get("N06_019")
        if point_type not in POINT_TYPE_MINZOOM:
            raise ValueError(
                f"未知の接合部種別コード: {point_type!r} "
                f"(N06_015={props.get('N06_015')!r})"
            )

        point_geom = shape(feature["geometry"])
        lane_counts = connected_lane_counts(point_geom, line_geometries)

        features.append(
            {
                "type": "Feature",
                "geometry": feature["geometry"],
                "properties": {
                    "point_name": props.get("N06_018"),
                    "point_type": point_type,
                    "lane_counts": lane_counts,
                },
                "tippecanoe": {"minzoom": POINT_TYPE_MINZOOM[point_type]},
            }
        )
    return {"type": "FeatureCollection", "features": features}


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
