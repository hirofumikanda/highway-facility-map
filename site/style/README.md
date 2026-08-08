# MapLibre GL JS スタイル定義

`map-style.js` は、`site/tiles/` のPMTiles（路線・地点）をベクトルタイル
ソースとして登録するMapLibreスタイル定義（`site/main.js` から読み込まれる）。
現状は地物が表示されることを確認できる最小限の配色のみで、以下のIssueで
詳細なスタイルに拡張する:

- 路線スタイル（国土地理院 最適化ベクトルタイルを参考にしたケーシング＋塗り、
  路線名のライン沿い表示）: OpenSpec Change `highway-facility-map`、
  tasks.md タスク番号 6.1〜6.4（GitHub Issue #5）
- 地点スタイル（Googleマップのピン/POIマーカー表現を参考にした種別ごとの
  配色・形状）: tasks.md タスク番号 7.1〜7.3（GitHub Issue #6）
- 対応するspec: `openspec/changes/highway-facility-map/specs/highway-map-viewer/spec.md`
