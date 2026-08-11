#!/usr/bin/env python3
"""生成タイル（PMTiles）の内容を検証する。

`tippecanoe-decode` で指定ズームのタイル群をデコードし、以下を確認する:
  - 4.1: z8では地点種別がジャンクション（point_type="3"）のみ収録される
  - 4.2: z10で一般IC、z12でスマートICが段階的に追加され、
         より低いズームの収録集合を包含する
  - 4.3: z14では地物数（タイル境界の重複を`id`で除去した一意な数）が
         現況地点数（2,384件）と一致する
  - 4.4: 路線タイルはズーム4〜14の各レベルで生成され、
         route_name/route_category/lane_count属性を保持する
  - 都道府県境界タイルはズーム4〜8の各レベルで生成され、
    N03_001（都道府県名）属性を保持する
  - 地点タイルはlane_counts属性を保持する
  - 路線タイルは、通称名・路線番号（common_name/route_number）が付与された
    地物について、z14でそれらの属性を保持する。両属性は独立に解決される
    ため、route_numberはcommon_nameの有無にかかわらず保持されることを
    確認する（add-mlit-route-numbering design.md 決定2）

タイルには境界付近のバッファにより同一地物が隣接タイルに重複して現れ得る
ため、地点の集計は`build_points.sh`で付与した`--generate-ids`の`id`で
重複排除して行う。

OpenSpec Change: highway-facility-map, map-interactivity-and-basemap, add-route-common-name-jct-lanes, add-mlit-route-numbering
tasks.md: 4.1, 4.2, 4.3, 4.4（highway-facility-map）, 1.4（map-interactivity-and-basemap）, 5.2（add-route-common-name-jct-lanes）, 4.2（add-mlit-route-numbering）
"""
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LINES_PMTILES = REPO_ROOT / "pipeline" / "output" / "lines.pmtiles"
POINTS_PMTILES = REPO_ROOT / "pipeline" / "output" / "points.pmtiles"
PREFECTURES_PMTILES = REPO_ROOT / "pipeline" / "output" / "prefectures.pmtiles"

EXPECTED_POINT_COUNT = 2384
LINE_MIN_ZOOM, LINE_MAX_ZOOM = 4, 14
PREFECTURE_MIN_ZOOM, PREFECTURE_MAX_ZOOM = 4, 8

# ズームごとに収録されるべき地点種別コードの集合
# （3: ジャンクション, 1: 一般IC, 2: スマートIC, 4: その他の接合部）
EXPECTED_TYPES_BY_ZOOM = {
    8: {"3"},
    10: {"3", "1"},
    12: {"3", "1", "2"},
    14: {"3", "1", "2", "4"},
}


def decode_zoom(pmtiles_path, zoom):
    """指定ズームのタイル群をデコードし、地物のリストを返す。"""
    proc = subprocess.run(
        ["tippecanoe-decode", "-Z", str(zoom), "-z", str(zoom), str(pmtiles_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    decoded = json.loads(proc.stdout)
    features = []
    for tile in decoded["features"]:
        for layer in tile["features"]:
            features.extend(layer["features"])
    return features


def check(ok_flags, label, actual, expected):
    passed = actual == expected
    ok_flags.append(passed)
    status = "OK" if passed else "NG"
    print(f"[{status}] {label}: {actual} (期待値: {expected})")


def verify_points(ok_flags):
    previous_types = set()
    for zoom in sorted(EXPECTED_TYPES_BY_ZOOM):
        expected_types = EXPECTED_TYPES_BY_ZOOM[zoom]
        features = decode_zoom(POINTS_PMTILES, zoom)
        type_by_id = {f["id"]: f["properties"]["point_type"] for f in features}
        types = set(type_by_id.values())

        check(ok_flags, f"z{zoom}で収録される地点種別の集合", types, expected_types)
        check(
            ok_flags,
            f"z{zoom}の収録集合が下位ズームの集合を包含する（{sorted(previous_types)} <= {sorted(types)}）",
            previous_types <= types,
            True,
        )
        previous_types = types

        missing_lane_counts = sum(
            1 for f in features if "lane_counts" not in f["properties"]
        )
        check(
            ok_flags,
            f"z{zoom}でlane_counts属性が欠落している件数",
            missing_lane_counts,
            0,
        )

        if zoom == 14:
            check(ok_flags, "z14の一意な地物数（重複排除後）", len(type_by_id), EXPECTED_POINT_COUNT)


def verify_lines(ok_flags):
    for zoom in range(LINE_MIN_ZOOM, LINE_MAX_ZOOM + 1):
        features = decode_zoom(LINES_PMTILES, zoom)
        check(ok_flags, f"z{zoom}の路線タイルに地物が存在する（{len(features)}件）", len(features) > 0, True)

        missing_attrs = sum(
            1
            for f in features
            if "route_name" not in f["properties"] or "route_category" not in f["properties"]
        )
        check(
            ok_flags,
            f"z{zoom}でroute_name/route_category属性が欠落している件数",
            missing_attrs,
            0,
        )

        missing_lane_count = sum(
            1 for f in features if "lane_count" not in f["properties"]
        )
        check(
            ok_flags,
            f"z{zoom}でlane_count属性が欠落している件数",
            missing_lane_count,
            0,
        )

        common_name_count = sum(
            1 for f in features if "common_name" in f["properties"]
        )
        route_number_count = sum(
            1 for f in features if "route_number" in f["properties"]
        )
        route_number_without_common_name_count = sum(
            1
            for f in features
            if "route_number" in f["properties"] and "common_name" not in f["properties"]
        )
        print(f"[INFO] z{zoom}でcommon_name属性を保持する路線地物数: {common_name_count}")
        print(f"[INFO] z{zoom}でroute_number属性を保持する路線地物数: {route_number_count}")
        if zoom == LINE_MAX_ZOOM:
            check(
                ok_flags,
                "z14でcommon_name属性を保持する路線地物が存在する",
                common_name_count > 0,
                True,
            )
            check(
                ok_flags,
                "z14でroute_number属性を保持する路線地物が存在する",
                route_number_count > 0,
                True,
            )
            check(
                ok_flags,
                "z14でcommon_nameなしでroute_number属性を保持する路線地物が存在する"
                "（route_numberがcommon_nameから独立して解決されることの確認）",
                route_number_without_common_name_count > 0,
                True,
            )


def verify_prefectures(ok_flags):
    for zoom in range(PREFECTURE_MIN_ZOOM, PREFECTURE_MAX_ZOOM + 1):
        features = decode_zoom(PREFECTURES_PMTILES, zoom)
        check(ok_flags, f"z{zoom}の都道府県境界タイルに地物が存在する（{len(features)}件）", len(features) > 0, True)

        missing_attrs = sum(
            1 for f in features if "N03_001" not in f["properties"]
        )
        check(
            ok_flags,
            f"z{zoom}でN03_001属性が欠落している件数",
            missing_attrs,
            0,
        )


def main():
    if not LINES_PMTILES.exists() or not POINTS_PMTILES.exists() or not PREFECTURES_PMTILES.exists():
        print(
            "PMTilesが見つかりません。先に build_lines.sh / build_points.sh / "
            "build_prefectures.sh を実行してください。",
            file=sys.stderr,
        )
        sys.exit(1)

    ok_flags = []
    verify_points(ok_flags)
    verify_lines(ok_flags)
    verify_prefectures(ok_flags)

    if not all(ok_flags):
        print("検証に失敗した項目があります。", file=sys.stderr)
        sys.exit(1)
    print("すべての検証項目がOKでした。")


if __name__ == "__main__":
    main()
