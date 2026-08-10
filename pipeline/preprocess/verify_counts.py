#!/usr/bin/env python3
"""前処理結果の件数・内訳を検証する。

`filter_lines.py` / `filter_points.py` の出力（`pipeline/output/*.current.geojson`）
が、元データを実際に集計して得られた現況件数（design.md Context節に記載）と
一致していること、および地点データのminzoomが接合部種別に応じて正しく割り当て
られていることを確認する。

期待値:
  - 現況路線: 1,289件
  - 現況地点: 2,384件（ジャンクション245 / 一般IC1,942 / スマートIC164 / その他33）

OpenSpec Change: highway-facility-map
tasks.md: 2.5
"""
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LINES_PATH = REPO_ROOT / "pipeline" / "output" / "lines.current.geojson"
POINTS_PATH = REPO_ROOT / "pipeline" / "output" / "points.current.geojson"

EXPECTED_LINE_COUNT = 1289
EXPECTED_POINT_COUNT = 2384
EXPECTED_POINT_TYPE_COUNTS = {
    "3": 245,  # ジャンクション
    "1": 1942,  # 一般インターチェンジ
    "2": 164,  # スマートインターチェンジ
    "4": 33,  # その他の接合部
}
EXPECTED_POINT_TYPE_MINZOOM = {"3": 8, "1": 10, "2": 12, "4": 14}


def check(ok_flags, label, actual, expected):
    passed = actual == expected
    ok_flags.append(passed)
    status = "OK" if passed else "NG"
    print(f"[{status}] {label}: {actual} (期待値: {expected})")


def main():
    ok_flags = []

    with open(LINES_PATH, encoding="utf-8") as f:
        lines = json.load(f)
    check(ok_flags, "現況路線の件数", len(lines["features"]), EXPECTED_LINE_COUNT)
    missing_line_props = sum(
        1
        for f in lines["features"]
        if "route_name" not in f["properties"] or "route_category" not in f["properties"]
    )
    check(ok_flags, "route_name/route_category属性の欠落件数", missing_line_props, 0)
    missing_lane_count = sum(
        1
        for f in lines["features"]
        if not isinstance(f["properties"].get("lane_count"), int)
    )
    check(ok_flags, "lane_count属性の欠落件数", missing_lane_count, 0)

    with open(POINTS_PATH, encoding="utf-8") as f:
        points = json.load(f)
    check(ok_flags, "現況地点の件数", len(points["features"]), EXPECTED_POINT_COUNT)
    missing_lane_counts = sum(
        1 for f in points["features"] if "lane_counts" not in f["properties"]
    )
    check(ok_flags, "lane_counts属性の欠落件数", missing_lane_counts, 0)
    empty_lane_counts = sum(
        1 for f in points["features"] if f["properties"].get("lane_counts") == []
    )
    print(f"[INFO] lane_countsが空の地点数: {empty_lane_counts}")

    type_counts = Counter(f["properties"]["point_type"] for f in points["features"])
    for point_type, expected_count in EXPECTED_POINT_TYPE_COUNTS.items():
        check(
            ok_flags,
            f"接合部種別{point_type}の件数",
            type_counts.get(point_type, 0),
            expected_count,
        )

    minzoom_mismatches = sum(
        1
        for f in points["features"]
        if f.get("tippecanoe", {}).get("minzoom")
        != EXPECTED_POINT_TYPE_MINZOOM.get(f["properties"]["point_type"])
    )
    check(ok_flags, "minzoom付与の不一致件数", minzoom_mismatches, 0)

    if not all(ok_flags):
        print("検証に失敗した項目があります。", file=sys.stderr)
        sys.exit(1)
    print("すべての検証項目がOKでした。")


if __name__ == "__main__":
    main()
