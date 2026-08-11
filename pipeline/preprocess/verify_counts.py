#!/usr/bin/env python3
"""前処理結果の件数・内訳を検証する。

`filter_lines.py` / `filter_points.py` の出力（`pipeline/output/*.current.geojson`）
が、元データを実際に集計して得られた現況件数（design.md Context節に記載）と
一致していること、および地点データのminzoomが接合部種別に応じて正しく割り当て
られていることを確認する。

期待値:
  - 現況路線: 1,289件
  - 現況地点: 2,384件（ジャンクション245 / 一般IC1,942 / スマートIC164 / その他33）
  - ジャンクションのsymbolrank: 1が79件 / 2が93件 / 3が73件

OpenSpec Change: highway-facility-map, add-mlit-route-numbering, add-jct-symbolrank
tasks.md: 2.5 / 2.2 / 2.1
"""
import json
import sys
from collections import Counter
from pathlib import Path

from filter_points import JCT_SYMBOLRANK_MINZOOM
from route_numbers import ROUTE_NUMBERS

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
# ジャンクション以外の地点種別のminzoomは固定値のまま（add-jct-symbolrank
# design.md Non-Goals）。ジャンクションのminzoomはsymbolrankから導出される
# ため、`JCT_SYMBOLRANK_MINZOOM`（filter_points.pyと共通）を参照する。
EXPECTED_NON_JCT_MINZOOM = {"1": 10, "2": 12, "4": 14}
# ジャンクションのsymbolrank別件数の期待値。245件の実データがほぼ均等な3群に
# 分かれる閾値で算出したもの（add-jct-symbolrank design.md 決定2）。
EXPECTED_JCT_SYMBOLRANK_COUNTS = {1: 79, 2: 93, 3: 73}


def expected_point_minzoom(props):
    """地点地物のtippecanoe.minzoomの期待値を返す。

    ジャンクションはsymbolrankから導出し、それ以外は地点種別ごとの固定値を
    用いる（add-jct-symbolrank design.md 決定3）。
    """
    if props["point_type"] == "3":
        return JCT_SYMBOLRANK_MINZOOM.get(props.get("symbolrank"))
    return EXPECTED_NON_JCT_MINZOOM.get(props["point_type"])


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
    common_name_count = sum(
        1 for f in lines["features"] if "common_name" in f["properties"]
    )
    print(f"[INFO] common_nameが付与された路線地物数: {common_name_count}")
    route_number_count = sum(
        1 for f in lines["features"] if "route_number" in f["properties"]
    )
    print(f"[INFO] ROUTE_NUMBERS対応表のエントリ数: {len(ROUTE_NUMBERS)}")
    print(f"[INFO] route_numberが付与された路線地物数: {route_number_count}")

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

    jct_features = [f for f in points["features"] if f["properties"]["point_type"] == "3"]
    missing_symbolrank = sum(1 for f in jct_features if "symbolrank" not in f["properties"])
    check(ok_flags, "ジャンクションのsymbolrank属性の欠落件数", missing_symbolrank, 0)
    symbolrank_counts = Counter(
        f["properties"]["symbolrank"] for f in jct_features if "symbolrank" in f["properties"]
    )
    for rank, expected_count in EXPECTED_JCT_SYMBOLRANK_COUNTS.items():
        check(
            ok_flags,
            f"ジャンクションのsymbolrank={rank}の件数",
            symbolrank_counts.get(rank, 0),
            expected_count,
        )
    non_jct_with_symbolrank = sum(
        1
        for f in points["features"]
        if f["properties"]["point_type"] != "3" and "symbolrank" in f["properties"]
    )
    check(ok_flags, "ジャンクション以外へのsymbolrank誤付与件数", non_jct_with_symbolrank, 0)

    minzoom_mismatches = sum(
        1
        for f in points["features"]
        if f.get("tippecanoe", {}).get("minzoom") != expected_point_minzoom(f["properties"])
    )
    check(ok_flags, "minzoom付与の不一致件数", minzoom_mismatches, 0)

    if not all(ok_flags):
        print("検証に失敗した項目があります。", file=sys.stderr)
        sys.exit(1)
    print("すべての検証項目がOKでした。")


if __name__ == "__main__":
    main()
