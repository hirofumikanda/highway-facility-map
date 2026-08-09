## 1. 都道府県境界PMTiles生成パイプライン（Issue: #16）

- [x] 1.1 `pipeline/tilegen/build_prefectures.sh` を作成し、`geojson/N03-20260101_prefecture.geojson` を入力にtippecanoeでPMTilesを生成する（`--minimum-zoom=4 --maximum-zoom=8 --layer=prefectures --include=N03_001 --include=N03_007 --coalesce --detect-shared-borders`、出力先 `pipeline/output/prefectures.pmtiles`）
- [x] 1.2 `pipeline/tilegen/deploy.sh` を拡張し、`prefectures.pmtiles` も `site/tiles/` に配置する
- [x] 1.3 `pipeline/build.sh` に `build_prefectures.sh` の呼び出しを追加する（`build_lines.sh`・`build_points.sh` と同様の位置づけ）
- [x] 1.4 `pipeline/tilegen/verify_tiles.py` に都道府県境界タイルの検証を追加する（z4〜z8で地物が生成されること、`N03_001`属性が保持されていること）
- [x] 1.5 `pipeline/build.sh` を実行し、`prefectures.pmtiles` が生成・配置され、検証が通ることを確認する

## 2. 背景レイヤーのスタイル・地図への統合（Issue: #17）

- [x] 2.1 `site/style/map-style.js` に `prefectures` ベクトルタイルソース（`pmtiles://.../prefectures.pmtiles`）を追加する
- [x] 2.2 都道府県境界の塗りレイヤー・境界線レイヤーを追加し、地理院地図の白地図を参考にした配色（塗り `#f5f5f2`、境界線 `#c9c5bb`、ズーム連動の線幅）で描画する。ラベルレイヤーは追加しない
- [x] 2.3 `layers` 配列内で都道府県境界レイヤーを `lines-casing` より前（下）に配置し、背景として描画されることを確認する

## 3. ナビゲーションコントロール・URLハッシュ同期（Issue: #18）

- [x] 3.1 `site/main.js` の `Map` コンストラクタに `hash: true` を追加する
- [x] 3.2 `maplibre-gl` から `NavigationControl` をインポートし、`map.addControl(new NavigationControl(), "top-right")` を追加する
- [x] 3.3 ブラウザで地図をパン・ズームした際にURLハッシュが更新されること、ハッシュ付きURLを開いた際にその状態から初期化されることを確認する

## 4. 地点クリック時のポップアップ（Issue: #19）

- [ ] 4.1 `site/main.js` に `points` レイヤーの `click` イベントハンドラーを追加する
- [ ] 4.2 `point_type` コード（1〜4）を人が読める種別名（一般インターチェンジ／スマートインターチェンジ／ジャンクション／その他の接合部）に変換するマッピングを実装する
- [ ] 4.3 クリックされた地物の位置に、地点名・種別ラベルをDOM APIで安全に組み立てた `maplibregl.Popup` を表示する
- [ ] 4.4 地点マーカー以外をクリックした場合にポップアップが表示されない・既存のポップアップが閉じることを確認する
- [ ] 4.5 マーカーへのホバー時にカーソルを `pointer` に変更する（`mouseenter`/`mouseleave` で `map.getCanvas().style.cursor` を切り替え）

## 5. 路線配色の変更（オレンジ→緑）（Issue: #20）

- [ ] 5.1 `site/style/map-style.js` の `CASING_COLOR` を緑系統の配色に変更する（路線種別区分ごとの濃淡構造は維持）
- [ ] 5.2 `FILL_COLOR` を緑系統の配色に変更する（同上）
- [ ] 5.3 `route-labels` レイヤーの `text-color`（現行 `#7a3d00`）を緑系配色に調和する色に変更する
- [ ] 5.4 ブラウザで路線の見た目を確認し、ズーム・路線種別区分による濃淡の区別が保たれていることを確認する

## 6. 動作確認（Issue: #21）

- [ ] 6.1 `site/index.html` をローカルで配信し、初期表示（背景レイヤー・緑系路線・地点）、ナビゲーションコントロール、URLハッシュ同期、地点クリックポップアップを一通り確認する
- [ ] 6.2 `README.md`（該当する場合）にPMTiles生成物が3種類（路線・地点・都道府県境界）になったことを反映する
