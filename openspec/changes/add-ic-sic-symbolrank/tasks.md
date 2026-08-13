## 1. 周辺人口の算出 (#105)

- [x] 1.1 `pipeline/preprocess/point_population.py`を新設し、`geojson/250m_mesh_2024_GEOJSON/`の94ファイルを1回ずつ読み込みながら、与えられた地点座標群それぞれの半径10km以内メッシュの`PTN_2025`合計をNumPy配列演算で算出する関数を実装する（design.md 決定1・決定2）
- [x] 1.2 メッシュ中心点はジオメトリのバウンディングボックス中心から算出し、距離は緯度補正した平面近似式で判定する（design.md 決定2）

## 2. IC・SICへのsymbolrank付与 (#106)

- [x] 2.1 `filter_points.py`で、IC・SIC地点が接続する路線地物の法定路線名（`route_name`）の組をグループキーとして算出する（design.md 決定4）
- [x] 2.2 グループごとに、1.1で算出した周辺人口の降順順位から`symbolrank`（`2`〜`5`）を算出する（`symbolrank = 2 + floor((r - 1) * 4 / n)`、design.md 決定3）
- [x] 2.3 `IC_SIC_SYMBOLRANK_MINZOOM`（`{2: 9, 3: 10, 4: 11, 5: 12}`）を新設し、IC・SICの`symbolrank`から`tippecanoe.minzoom`を導出する（既存の`POINT_TYPE_MINZOOM`のIC・SIC固定値は廃止する、design.md 決定5）
- [x] 2.4 JCT・その他の接合部には引き続き`symbolrank`（IC/SIC向け）を付与しない

## 3. 前処理パイプラインの検証 (#107)

- [ ] 3.1 `pipeline/preprocess/verify_counts.py`に、IC・SICの`symbolrank`別件数、グループサイズ分布の集計を追加する
- [ ] 3.2 `pipeline/preprocess/run.sh`を実行し、`points.current.geojson`が期待通り生成され検証が通ることを確認する（実行時間の実測を含む）

## 4. タイル生成・検証 (#108)

- [ ] 4.1 `pipeline/tilegen/verify_tiles.py`に、IC・SICの`symbolrank`別ズーム収録（`z9`は`symbolrank=2`のみ、`z12`以降は全IC・SIC）の検証を追加する
- [ ] 4.2 `./pipeline/build.sh`を実行し、`site/tiles/points.pmtiles`を再生成・配置する

## 5. 地点名ラベルの表示形式変更 (#109)

- [ ] 5.1 `site/style/map-style.js`の`point-labels`レイヤーの`symbol-sort-key`を、IC・SICは`symbolrank + 3`（値域5〜8）、その他の接合部は固定値`9`に変更する（design.md 決定6）

## 6. ドキュメント更新・動作確認 (#110)

- [ ] 6.1 `pipeline/preprocess/README.md`に、新設スクリプトの依存関係（NumPy、人口メッシュデータ）を追記する
- [ ] 6.2 `npx serve site`でローカル動作確認を行う（IC/SICのsymbolrank別表示開始ズーム、人口の多いSICが人口の少ないICより先に表示されること、JCTが常に最優先のままであること、その他の接合部の表示に変化がないことを含む）
