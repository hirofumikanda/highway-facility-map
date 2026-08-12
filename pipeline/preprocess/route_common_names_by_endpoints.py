"""始点・終点接合部名から通称名（`common_name`）を引く静的対応表。

`route_common_names.ROUTE_COMMON_NAMES`は、法定路線名（`N06_007`）が単一の
通称名に一意対応する場合にのみエントリを収録する（design.md 決定1・決定2の
方針を踏襲）。このため、法定路線名が複数の通称名区間に分かれる路線は
`ROUTE_COMMON_NAMES`から除外され、`common_name`が一切付与されない。

本対応表は、そのような法定路線名について、路線地物の始点・終点接合部名
（`filter_lines.py`が付与する`start_point_name`・`end_point_name`）を鍵として、
区間ごとに`common_name`を解決するために用いる（add-joint-based-route-matching
design.md 決定3）。1つの法定路線名につき、区間の境界となる2つの接合部名の組
（走査方向によらない組として保持・照合する）と、その区間の通称名を対応させる。

現時点では、法定路線名が複数の通称名区間に分かれることを確認できた範囲
（「北海道横断自動車道根室線」「北海道横断自動車道網走線」）のみを収録する。
他の法定路線名についても同様の区間分割は起こり得るが、個別の出典確認が
必要なため、本対応表への追加は将来の変更に委ねる（design.md Non-Goals）。

## 出典・確認内容

- Wikipedia「北海道横断自動車道」（https://ja.wikipedia.org/wiki/北海道横断自動車道
  、2026-06-06時点の版、oldid=109822251）: 「根室線」が起点を北海道寿都郡黒松内町
  （黒松内JCT）、終点を根室市とする法定路線名であり、供用中の区間が
  後志自動車道（余市IC - 小樽JCT）・札樽自動車道（小樽IC - 小樽JCT - 札幌JCT）・
  道央自動車道（札幌JCT - 千歳恵庭JCT）・道東自動車道（千歳恵庭JCT - 本別JCT、
  以東へ継続）の各通称名区間で構成されることを確認した。「網走線」については、
  本別JCT - 足寄IC間が道東自動車道（端野支線）、足寄IC - 北見西IC間（訓子府IC・
  陸別小利別ICを経由）が十勝オホーツク自動車道であることを確認した。
- Wikipedia「道東自動車道」（https://ja.wikipedia.org/wiki/道東自動車道
  、2026-08-03時点の版）: 2024年9月12日付で「釧路外環状道路」が「道東自動車道」に
  改称され、本別JCT - 釧路別保IC間（浦幌・白糠・阿寒・釧路西を含む）が道東自動車道
  に含まれることを確認した。
- `geojson/N06-25_HighwaySection.geojson`の現況路線地物（`filter_lines.py`が
  付与する`start_point_name`・`end_point_name`）と上記出典の区間境界IC/JCT名を
  突き合わせ、各区間の始点・終点接合部名の組を確定した。

`route_category`が`1`（高速自動車国道）以外の区間（例：`温根沼IC - 根室IC`間の
根室道路、`訓子府IC - 陸別小利別IC`間、`route_category`が`2`）は、既存の
`common_name`付与条件（design.md 決定3、`route_category`が`1`のみ対象）により
本対応表からの解決対象外となるため収録しない。

OpenSpec Change: add-joint-based-route-matching
tasks.md: 3.1, 3.2
"""

ROUTE_COMMON_NAMES_BY_ENDPOINTS = {
    "北海道横断自動車道根室線": [
        {"points": frozenset({"余市", "小樽JCT"}), "common_name": "後志自動車道"},
        {"points": frozenset({"小樽", "札幌西"}), "common_name": "札樽自動車道"},
        {"points": frozenset({"札幌西", "札幌JCT"}), "common_name": "札樽自動車道"},
        {"points": frozenset({"札幌JCT", "北広島"}), "common_name": "道央自動車道"},
        {"points": frozenset({"北広島", "千歳恵庭JCT"}), "common_name": "道央自動車道"},
        {"points": frozenset({"千歳恵庭JCT", "夕張"}), "common_name": "道東自動車道"},
        {"points": frozenset({"夕張", "占冠"}), "common_name": "道東自動車道"},
        {"points": frozenset({"占冠", "トマム"}), "common_name": "道東自動車道"},
        {"points": frozenset({"トマム", "十勝清水"}), "common_name": "道東自動車道"},
        {"points": frozenset({"十勝清水", "池田"}), "common_name": "道東自動車道"},
        {"points": frozenset({"池田", "本別"}), "common_name": "道東自動車道"},
        {"points": frozenset({"本別", "浦幌"}), "common_name": "道東自動車道"},
        {"points": frozenset({"浦幌", "白糠"}), "common_name": "道東自動車道"},
        {"points": frozenset({"白糠", "阿寒"}), "common_name": "道東自動車道"},
        {"points": frozenset({"阿寒", "釧路西"}), "common_name": "道東自動車道"},
    ],
    "北海道横断自動車道網走線": [
        {"points": frozenset({"本別JCT", "足寄"}), "common_name": "道東自動車道"},
        {"points": frozenset({"北見西", "訓子府"}), "common_name": "十勝オホーツク自動車道"},
    ],
}
