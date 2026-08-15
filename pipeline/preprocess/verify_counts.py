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

`start_point_name`・`end_point_name`の付与件数、および始点・終点接合部・
通称名を用いた追加解決（add-joint-based-route-matching design.md 決定3・
決定4）により解決された`common_name`・`route_number`の件数は、対応表の拡充に
伴って変動しうるため、期待値と一致するかのチェックではなく参考情報として
出力する。

IC・SIC（接合部種別`1`・`2`）については、`symbolrank`（`2`〜`5`）別件数に加え、
接続する法定路線名の組でグループ化した際のグループサイズ分布を検証する
（add-ic-sic-symbolrank design.md 決定3・決定4）。グループサイズ分布から
決まる`symbolrank`別件数の期待値は、`filter_points.py`のグループ化ロジック
（人口に依存しない）を用いて実データから独立に再算出した値であり、周辺人口
データ自体の値には依存しない。

OpenSpec Change: highway-facility-map, add-mlit-route-numbering, add-jct-symbolrank, add-joint-based-route-matching, add-ic-sic-symbolrank
tasks.md: 2.5 / 2.2 / 2.1 / 5.1 / 3.1（GitHub Issue #107）
"""
import json
import sys
from collections import Counter
from pathlib import Path

from shapely.geometry import shape

from filter_points import (
    IC_SIC_SYMBOLRANK_MINZOOM,
    IC_SIC_TYPES,
    JCT_SYMBOLRANK_MINZOOM,
    connected_route_names,
    ic_sic_symbolrank_group_key,
    load_line_geometries,
)
from route_common_names import ROUTE_COMMON_NAMES
from route_common_names_by_endpoints import ROUTE_COMMON_NAMES_BY_ENDPOINTS
from route_numbers import ROUTE_NUMBERS
from route_numbers_by_common_name import ROUTE_NUMBERS_BY_COMMON_NAME

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
# ジャンクション・IC・SIC以外（その他の接合部）のminzoomは固定値のまま
# （add-jct-symbolrank design.md Non-Goals）。ジャンクション・IC・SICの
# minzoomはsymbolrankから導出されるため、それぞれ`JCT_SYMBOLRANK_MINZOOM`・
# `IC_SIC_SYMBOLRANK_MINZOOM`（いずれもfilter_points.pyと共通）を参照する。
EXPECTED_OTHER_MINZOOM = {"4": 14}
# ジャンクションのsymbolrank別件数の期待値。245件の実データがほぼ均等な3群に
# 分かれる閾値で算出したもの（add-jct-symbolrank design.md 決定2）。
EXPECTED_JCT_SYMBOLRANK_COUNTS = {1: 79, 2: 93, 3: 73}
# IC・SICのグループ数（接続する法定路線名の組でグループ化した数）の期待値、
# および`symbolrank`別件数の期待値。グループサイズ分布は人口に依存せず接続
# 路線のみで決まるため（add-ic-sic-symbolrank design.md 決定4）、symbolrank
# 別件数の期待値（決定3の式から算出される、グループサイズ分布のみに依存する
# 値）も周辺人口データの値によらず一意に定まる。2,106件の実データから算出。
EXPECTED_IC_SIC_GROUP_COUNT = 456
EXPECTED_IC_SIC_SYMBOLRANK_COUNTS = {2: 778, 3: 435, 4: 527, 5: 366}


def expected_point_minzoom(props):
    """地点地物のtippecanoe.minzoomの期待値を返す。

    ジャンクション・IC・SICはそれぞれのsymbolrankから導出し、それ以外は
    地点種別ごとの固定値を用いる（add-jct-symbolrank design.md 決定3、
    add-ic-sic-symbolrank design.md 決定5）。
    """
    if props["point_type"] == "3":
        return JCT_SYMBOLRANK_MINZOOM.get(props.get("symbolrank"))
    if props["point_type"] in IC_SIC_TYPES:
        return IC_SIC_SYMBOLRANK_MINZOOM.get(props.get("symbolrank"))
    return EXPECTED_OTHER_MINZOOM.get(props["point_type"])


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
    start_point_name_count = sum(
        1 for f in lines["features"] if "start_point_name" in f["properties"]
    )
    end_point_name_count = sum(
        1 for f in lines["features"] if "end_point_name" in f["properties"]
    )
    print(f"[INFO] start_point_nameが付与された路線地物数: {start_point_name_count}")
    print(f"[INFO] end_point_nameが付与された路線地物数: {end_point_name_count}")

    common_name_count = sum(
        1 for f in lines["features"] if "common_name" in f["properties"]
    )
    common_name_by_endpoints_count = sum(
        1
        for f in lines["features"]
        if "common_name" in f["properties"]
        and f["properties"]["route_name"] not in ROUTE_COMMON_NAMES
    )
    print(f"[INFO] common_nameが付与された路線地物数: {common_name_count}")
    print(
        "[INFO] 始点・終点接合部による追加解決でcommon_nameが付与された路線地物数: "
        f"{common_name_by_endpoints_count}"
    )

    route_number_count = sum(
        1 for f in lines["features"] if "route_number" in f["properties"]
    )
    route_number_by_common_name_count = sum(
        1
        for f in lines["features"]
        if "route_number" in f["properties"]
        and f["properties"]["route_name"] not in ROUTE_NUMBERS
    )
    print(f"[INFO] ROUTE_NUMBERS対応表のエントリ数: {len(ROUTE_NUMBERS)}")
    print(f"[INFO] route_numberが付与された路線地物数: {route_number_count}")
    print(
        "[INFO] 通称名による追加解決でroute_numberが付与された路線地物数: "
        f"{route_number_by_common_name_count}"
    )
    print(
        "[INFO] ROUTE_COMMON_NAMES_BY_ENDPOINTS対応表のエントリ数: "
        f"{sum(len(entries) for entries in ROUTE_COMMON_NAMES_BY_ENDPOINTS.values())}"
    )
    print(
        "[INFO] ROUTE_NUMBERS_BY_COMMON_NAME対応表のエントリ数: "
        f"{len(ROUTE_NUMBERS_BY_COMMON_NAME)}"
    )

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
    ic_sic_features = [
        f for f in points["features"] if f["properties"]["point_type"] in IC_SIC_TYPES
    ]
    missing_ic_sic_symbolrank = sum(
        1 for f in ic_sic_features if "symbolrank" not in f["properties"]
    )
    check(ok_flags, "IC・SICのsymbolrank属性の欠落件数", missing_ic_sic_symbolrank, 0)
    ic_sic_symbolrank_counts = Counter(
        f["properties"]["symbolrank"]
        for f in ic_sic_features
        if "symbolrank" in f["properties"]
    )
    for rank, expected_count in EXPECTED_IC_SIC_SYMBOLRANK_COUNTS.items():
        check(
            ok_flags,
            f"IC・SICのsymbolrank={rank}の件数",
            ic_sic_symbolrank_counts.get(rank, 0),
            expected_count,
        )

    line_geometries = load_line_geometries(lines)
    route_name_candidates = [(geom, route_name) for geom, _, route_name, _ in line_geometries]
    group_keys = []
    for f in ic_sic_features:
        point_geom = shape(f["geometry"])
        route_names = connected_route_names(point_geom, route_name_candidates)
        group_keys.append(
            ic_sic_symbolrank_group_key(route_names, f["properties"]["point_name"])
        )
    group_sizes = Counter(group_keys)
    check(ok_flags, "IC・SICのグループ数", len(group_sizes), EXPECTED_IC_SIC_GROUP_COUNT)
    group_size_distribution = Counter(group_sizes.values())
    print(
        "[INFO] IC・SICのグループサイズ分布（グループサイズ -> グループ数）: "
        f"{dict(sorted(group_size_distribution.items()))}"
    )

    other_with_symbolrank = sum(
        1
        for f in points["features"]
        if f["properties"]["point_type"] not in ("3", *IC_SIC_TYPES)
        and "symbolrank" in f["properties"]
    )
    check(ok_flags, "その他の接合部へのsymbolrank誤付与件数", other_with_symbolrank, 0)

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
