"""通称名（`common_name`）から路線番号（`route_number`）を引く静的対応表。

`route_numbers.ROUTE_NUMBERS`は法定路線名（`route_name`）をキーとするため、
国土交通省「高速道路ナンバリング一覧」の記載が通称名ベースの表記であり法定
路線名と文字列一致しない場合は解決できない（`route_numbers.py`の既知の限界）。

本対応表は、（`route_numbers.ROUTE_NUMBERS`または
`route_common_names_by_endpoints.ROUTE_COMMON_NAMES_BY_ENDPOINTS`のいずれかに
より）解決済みの`common_name`を鍵として、`ROUTE_NUMBERS`で解決できなかった
`route_number`を追加で解決するために用いる（add-joint-based-route-matching
design.md 決定4）。

## 出典・確認内容

国土交通省「高速道路ナンバリング一覧」（https://www.mlit.go.jp/road/sign/numbering/list/index.html
、2026-08-12時点の版）の記載を通称名ベースで突き合わせた。

- `E5`: 「北海道縦貫自動車道〔道央自動車道 等〕」の記載により、`道央自動車道`に
  対応することを確認した。
- `E5A`: 「北海道横断自動車道（黒松内～札幌）〔札樽自動車道 等〕」の記載により、
  `札樽自動車道`に対応することを確認した。同区間（黒松内～札幌）に含まれる
  `後志自動車道`については、MLITページに名称の記載はないが、Wikipedia
  「後志自動車道」（https://ja.wikipedia.org/wiki/後志自動車道
  、2026-06-15時点の版）に「高速道路ナンバリングでは黒松内新道や札樽自動車道と
  ともに『E5A』が割り振られている」との記載があることを確認した。
- `E38`: 「北海道横断自動車道根室線（千歳恵庭～釧路東）〔道東自動車道 等〕」の
  記載により、`道東自動車道`に対応することを確認した。

現時点では、`route_common_names_by_endpoints.ROUTE_COMMON_NAMES_BY_ENDPOINTS`が
収録する通称名のうち出典を確認できたもののみを収録する。他の通称名についても
同様の追加解決は起こり得るが、個別の出典確認が必要なため、本対応表への追加は
将来の変更に委ねる（design.md Non-Goals）。

OpenSpec Change: add-joint-based-route-matching
tasks.md: 4.1, 4.2
"""

ROUTE_NUMBERS_BY_COMMON_NAME = {
    "後志自動車道": "E5A",
    "札樽自動車道": "E5A",
    "道央自動車道": "E5",
    "道東自動車道": "E38",
}
