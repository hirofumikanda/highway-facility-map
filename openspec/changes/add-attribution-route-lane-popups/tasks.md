## 1. パイプライン前処理: 路線の車線数属性（Issue: #28）

- [ ] 1.1 `pipeline/preprocess/filter_lines.py`の出力属性に`lane_count`
      （`N06_010`を整数として保持）を追加する
- [ ] 1.2 `pipeline/preprocess/README.md`の出力属性説明を更新する

## 2. パイプライン前処理: 地点への接続路線車線数の付与（Issue: #29）

- [ ] 2.1 前処理の依存関係にShapelyを追加し、`check-tools.sh`または
      `pipeline/preprocess/README.md`に依存追加を明記する
- [ ] 2.2 `pipeline/preprocess/filter_points.py`で`lines.current.geojson`を
      読み込み、各地点座標とライン地物の頂点一致判定（design.md 決定4の閾値）
      により接続路線を判定するロジックを実装する
- [ ] 2.3 判定した接続路線の`lane_count`を重複排除・昇順ソートし、地点属性
      `lane_counts`（配列）として付与する
- [ ] 2.4 `pipeline/preprocess/verify_counts.py`に、`lane_count`・
      `lane_counts`属性の存在検証と、`lane_counts`が空になる地点件数の報告を
      追加する
- [ ] 2.5 `pipeline/preprocess/run.sh`を実行し、新属性が期待通り付与される
      ことを確認する

## 3. タイル生成・配置（Issue: #30）

- [ ] 3.1 `./pipeline/build.sh`を実行し、`lane_count`・`lane_counts`属性を
      含む`lines.pmtiles`・`points.pmtiles`を再生成する
- [ ] 3.2 `pipeline/tilegen/verify_tiles.py`で新属性がタイル内に保持されて
      いることを確認する
- [ ] 3.3 再生成した`site/tiles/lines.pmtiles`・`points.pmtiles`を配置する

## 4. サイト: データ出典（attribution）表示（Issue: #31）

- [ ] 4.1 `site/style/map-style.js`の`lines`・`points`ソースに国土数値情報
      （高速道路時系列データ）の出典attributionを設定する
- [ ] 4.2 `site/style/map-style.js`の`prefectures`ソースに国土数値情報
      （行政区域データ）の出典attributionを設定する

## 5. サイト: 路線クリック時のポップアップ（Issue: #32）

- [ ] 5.1 `site/main.js`に路線種別区分（`route_category`）コードを人が読める
      種別名に変換するラベル表（design.md 決定2）を追加する
- [ ] 5.2 `site/main.js`に`lines-fill`レイヤーの`click`ハンドラを追加し、
      路線名・路線種別名・車線数を表示するポップアップを実装する
- [ ] 5.3 `lines-fill`レイヤーへのホバー時にカーソルをpointerに変更する
      処理を追加する

## 6. サイト: 地点ポップアップへの接続路線車線数の追加（Issue: #33）

- [ ] 6.1 `site/main.js`の地点クリックハンドラで`lane_counts`属性を読み取り、
      カンマ区切り等で表示する要素をポップアップに追加する（design.md 決定5）
- [ ] 6.2 `lane_counts`が空の地点でも既存の地点名・地点種別表示が崩れない
      ことを確認する

## 7. 動作確認（Issue: #34）

- [ ] 7.1 `npx serve site`でローカル起動し、AttributionControlに出典が
      表示されることを確認する
- [ ] 7.2 単一路線に接続するIC、複数路線が接続するJCTそれぞれで地点
      ポップアップの車線数表示を確認する
- [ ] 7.3 路線クリックでのポップアップ（路線名・路線種別名・車線数）を
      複数路線種別で確認する
- [ ] 7.4 README.mdに変更点（出典表示・ポップアップ拡張）があれば反映する
