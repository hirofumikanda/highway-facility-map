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

ジャンクション（接合部種別`3`）については、接続する路線の車線数合計に基づく
`symbolrank`（1〜3、値が小さいほど上位）を付与し、`symbolrank`から細分化した
minzoom（8/9/10）を用いる（add-jct-symbolrank design.md 決定1〜3）。

地点座標とライン地物の座標一致判定は`spatial_match.py`の共通ロジックを用いる
（add-joint-based-route-matching design.md 決定1）。

OpenSpec Change: highway-facility-map, add-jct-symbolrank, add-joint-based-route-matching
tasks.md: 2.3, 2.4 / 1.1, 1.2 / 1.2
"""
import json
from pathlib import Path

from shapely.geometry import shape

from spatial_match import matching_values

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = REPO_ROOT / "geojson" / "N06-25_Joint.geojson"
LINES_PATH = REPO_ROOT / "pipeline" / "output" / "lines.current.geojson"
OUTPUT_PATH = REPO_ROOT / "pipeline" / "output" / "points.current.geojson"

CURRENT_END_YEAR = 9999

# N06_019（接合部種別コード） -> tippecanoeの地物単位minzoom
# ジャンクション(3) > 一般IC(1) > スマートIC(2) > その他(4) の重要度順に、
# 低いズームから段階的に収録されるよう割り当てる（design.md 決定5）。
# ジャンクションについては、地物ごとのsymbolrank（下記）に応じてさらに
# minzoomを細分化する（add-jct-symbolrank design.md 決定3）。この辞書の
# "3"の値はsymbolrank=1のジャンクションのminzoomと一致する。
POINT_TYPE_MINZOOM = {
    "3": 8,  # ジャンクション
    "1": 10,  # 一般インターチェンジ
    "2": 12,  # スマートインターチェンジ
    "4": 14,  # その他の接合部
}

# ジャンクションのsymbolrank（1〜3、値が小さいほど上位）->tippecanoeのminzoom
# （add-jct-symbolrank design.md 決定3）。
JCT_SYMBOLRANK_MINZOOM = {1: 8, 2: 9, 3: 10}


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


def load_line_geometries(lines_source):
    """路線地物ごとの(ジオメトリ, 車線数)のリストを構築する。"""
    return [
        (shape(feature["geometry"]), feature["properties"]["lane_count"])
        for feature in lines_source["features"]
    ]


def connected_lane_counts(point_geom, line_geometries):
    """地点座標に頂点一致判定で接続する路線の車線数を、重複を排除せず昇順ソートして返す。

    同じ車線数を持つ路線が複数接続する場合（主にJCT）も、接続する路線の数だけ
    値を保持する（design.md 決定4）。
    """
    return sorted(matching_values(point_geom, line_geometries))


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

        properties = {
            "point_name": props.get("N06_018"),
            "point_type": point_type,
            "lane_counts": lane_counts,
        }

        if point_type == "3":
            symbolrank = jct_symbolrank(lane_counts)
            properties["symbolrank"] = symbolrank
            minzoom = JCT_SYMBOLRANK_MINZOOM[symbolrank]
        else:
            minzoom = POINT_TYPE_MINZOOM[point_type]

        features.append(
            {
                "type": "Feature",
                "geometry": feature["geometry"],
                "properties": properties,
                "tippecanoe": {"minzoom": minzoom},
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
