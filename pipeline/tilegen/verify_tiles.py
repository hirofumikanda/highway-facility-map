#!/usr/bin/env python3
"""生成タイル（PMTiles）の内容を検証する。

`tippecanoe-decode` で指定ズームのタイル群をデコードし、以下を確認する:
  - 4.1: z8では地点種別がジャンクション（point_type="3"）のみ収録される
  - 4.2: z9で一般IC・スマートIC（point_type="1"・"2"）が種別を問わず
         symbolrankに応じて段階的に追加され、より低いズームの収録集合を
         包含する（add-ic-sic-symbolrank design.md 決定5、下記参照）
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
  - ジャンクションは、地物ごとのsymbolrank（1〜4、値が小さいほど上位。
    4は指定都市高速道路・その他限定の補正が適用された場合のみ発生する）に
    応じて、z8はsymbolrank=1のみ、z9はsymbolrank=1・2、z10は1・2・3、
    z11は全ジャンクション（symbolrank1〜4すべて）が収録され、各ズームの
    収録集合はより低いズームの収録集合を包含する（add-jct-symbolrank
    design.md 決定3、demote-city-other-joints design.md 決定3）
  - IC・SICは、地物ごとのsymbolrank（2〜6、値が小さいほど上位。6は同様に
    補正が適用された場合のみ発生する。種別を問わず接続路線内の周辺人口
    相対順位で決まる）に応じて、z9はsymbolrank=2のみ、z10は2・3、z11は
    2・3・4、z12は2・3・4・5、z13は全IC・SIC（symbolrank2〜6すべて）が
    収録され、各ズームの収録集合はより低いズームの収録集合を包含する
    （add-ic-sic-symbolrank design.md 決定5、demote-city-other-joints
    design.md 決定3）

タイルには境界付近のバッファにより同一地物が隣接タイルに重複して現れ得る
ため、地点の集計は`build_points.sh`で付与した`--generate-ids`の`id`で
重複排除して行う。

OpenSpec Change: highway-facility-map, map-interactivity-and-basemap, add-route-common-name-jct-lanes, add-mlit-route-numbering, add-jct-symbolrank, add-ic-sic-symbolrank, demote-city-other-joints
tasks.md: 4.1, 4.2, 4.3, 4.4（highway-facility-map）, 1.4（map-interactivity-and-basemap）, 5.2（add-route-common-name-jct-lanes）, 4.2（add-mlit-route-numbering）, 3.1（add-jct-symbolrank）, 4.1（add-ic-sic-symbolrank、GitHub Issue #108）, 4.2, 4.3（demote-city-other-joints、GitHub Issue #120）
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
# IC・SIC（1・2）はsymbolrankに応じてz9〜z13で段階的に収録されるが、
# 両種別ともsymbolrank=2〜6の地物が存在するため、いずれのズームでも
# 種別の集合としては{"1", "2"}が揃って現れる
# （add-ic-sic-symbolrank design.md 決定5、demote-city-other-joints
# design.md 決定3、種別ごとの段階的収録はEXPECTED_IC_SIC_SYMBOLRANKS_BY_ZOOM
# で別途検証する）。
EXPECTED_TYPES_BY_ZOOM = {
    8: {"3"},
    9: {"3", "1", "2"},
    10: {"3", "1", "2"},
    11: {"3", "1", "2"},
    12: {"3", "1", "2"},
    13: {"3", "1", "2"},
    14: {"3", "1", "2", "4"},
}

# ジャンクションのsymbolrank（1〜4、値が小さいほど上位。4は指定都市高速
# 道路・その他にのみ連結する地点への補正が適用された場合のみ発生する）
# 別の件数の期待値。245件のジャンクション実データに基づく
# （add-jct-symbolrank design.md 決定2、demote-city-other-joints
# design.md 決定1・決定3）。
EXPECTED_JCT_SYMBOLRANK_COUNTS = {1: 59, 2: 74, 3: 99, 4: 13}

# ズームごとに収録されるべきジャンクションのsymbolrankの集合
# （add-jct-symbolrank design.md 決定3、demote-city-other-joints
# design.md 決定3）。
EXPECTED_JCT_SYMBOLRANKS_BY_ZOOM = {
    8: {1},
    9: {1, 2},
    10: {1, 2, 3},
    11: {1, 2, 3, 4},
}

# IC・SICの接合部種別コード（一般インターチェンジ・スマートインターチェンジ）。
IC_SIC_TYPES = {"1", "2"}

# IC・SICのsymbolrank（2〜6、値が小さいほど上位。6は指定都市高速道路・
# その他にのみ連結する地点への補正が適用された場合のみ発生する）別の件数
# の期待値。2,106件のIC・SIC実データに基づく（symbolrank算出式がグループ
# サイズ分布のみに依存するため、周辺人口データの値によらず一意に定まる値。
# add-ic-sic-symbolrank design.md 決定3・決定4、demote-city-other-joints
# design.md 決定1・決定3、verify_counts.pyと共通）。
EXPECTED_IC_SIC_SYMBOLRANK_COUNTS = {2: 651, 3: 472, 4: 514, 5: 398, 6: 71}

# ズームごとに収録されるべきIC・SICのsymbolrankの集合
# （add-ic-sic-symbolrank design.md 決定5、demote-city-other-joints
# design.md 決定3）。
EXPECTED_IC_SIC_SYMBOLRANKS_BY_ZOOM = {
    9: {2},
    10: {2, 3},
    11: {2, 3, 4},
    12: {2, 3, 4, 5},
    13: {2, 3, 4, 5, 6},
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


def verify_jct_symbolrank(ok_flags):
    """ジャンクションがsymbolrankに応じてz8/z9/z10で段階的に収録されることを確認する。

    z8はsymbolrank=1のみ、z9はsymbolrank=1・2、z10はsymbolrank=1・2・3
    （全ジャンクション）が収録され、各ズームの収録集合はより低いズームの
    収録集合を包含する（add-jct-symbolrank design.md 決定3）。
    """
    previous_ids = set()
    for zoom in sorted(EXPECTED_JCT_SYMBOLRANKS_BY_ZOOM):
        expected_ranks = EXPECTED_JCT_SYMBOLRANKS_BY_ZOOM[zoom]
        features = decode_zoom(POINTS_PMTILES, zoom)
        jct_symbolrank_by_id = {
            f["id"]: f["properties"]["symbolrank"]
            for f in features
            if f["properties"]["point_type"] == "3"
        }
        ranks = set(jct_symbolrank_by_id.values())

        check(
            ok_flags,
            f"z{zoom}で収録されるジャンクションのsymbolrankの集合",
            ranks,
            expected_ranks,
        )

        expected_count = sum(EXPECTED_JCT_SYMBOLRANK_COUNTS[r] for r in expected_ranks)
        check(
            ok_flags,
            f"z{zoom}で収録されるジャンクションの件数（重複排除後）",
            len(jct_symbolrank_by_id),
            expected_count,
        )

        ids = set(jct_symbolrank_by_id)
        check(
            ok_flags,
            f"z{zoom}のジャンクション収録集合が下位ズームの集合を包含する"
            f"（{len(previous_ids)}件 <= {len(ids)}件）",
            previous_ids <= ids,
            True,
        )
        previous_ids = ids


def verify_ic_sic_symbolrank(ok_flags):
    """IC・SICがsymbolrankに応じてz9〜z12で段階的に収録されることを確認する。

    z9はsymbolrank=2のみ、z10は2・3、z11は2・3・4、z12は2・3・4・5
    （全IC・SIC）が収録され、各ズームの収録集合はより低いズームの収録集合を
    包含する。種別（IC/SIC）を問わずsymbolrankのみで判定する
    （add-ic-sic-symbolrank design.md 決定5）。
    """
    previous_ids = set()
    for zoom in sorted(EXPECTED_IC_SIC_SYMBOLRANKS_BY_ZOOM):
        expected_ranks = EXPECTED_IC_SIC_SYMBOLRANKS_BY_ZOOM[zoom]
        features = decode_zoom(POINTS_PMTILES, zoom)
        ic_sic_symbolrank_by_id = {
            f["id"]: f["properties"]["symbolrank"]
            for f in features
            if f["properties"]["point_type"] in IC_SIC_TYPES
        }
        ranks = set(ic_sic_symbolrank_by_id.values())

        check(
            ok_flags,
            f"z{zoom}で収録されるIC・SICのsymbolrankの集合",
            ranks,
            expected_ranks,
        )

        expected_count = sum(EXPECTED_IC_SIC_SYMBOLRANK_COUNTS[r] for r in expected_ranks)
        check(
            ok_flags,
            f"z{zoom}で収録されるIC・SICの件数（重複排除後）",
            len(ic_sic_symbolrank_by_id),
            expected_count,
        )

        ids = set(ic_sic_symbolrank_by_id)
        check(
            ok_flags,
            f"z{zoom}のIC・SIC収録集合が下位ズームの集合を包含する"
            f"（{len(previous_ids)}件 <= {len(ids)}件）",
            previous_ids <= ids,
            True,
        )
        previous_ids = ids


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
    verify_jct_symbolrank(ok_flags)
    verify_ic_sic_symbolrank(ok_flags)
    verify_lines(ok_flags)
    verify_prefectures(ok_flags)

    if not all(ok_flags):
        print("検証に失敗した項目があります。", file=sys.stderr)
        sys.exit(1)
    print("すべての検証項目がOKでした。")


if __name__ == "__main__":
    main()
