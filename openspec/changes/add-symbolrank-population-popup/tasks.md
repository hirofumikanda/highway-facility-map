## 1. 周辺人口の出力属性への追加 (#132)

- [x] 1.1 `pipeline/preprocess/filter_points.py`のIC・SICの`symbolrank`付与処理に、`entry["population"]`を四捨五入した整数値を`properties["population"]`へ書き込む処理を追加する
- [x] 1.2 `pipeline/preprocess/run.sh`を実行し、`pipeline/output/points.current.geojson`のIC・SIC地物に`population`属性が付与されることを確認する
- [x] 1.3 `pipeline/preprocess/verify_counts.py`に、IC・SICの`population`属性の欠落件数検証を追加する
- [x] 1.4 `pipeline/preprocess/verify_counts.py`を実行し、全チェックが成功することを確認する

## 2. タイルの再生成 (#133)

- [x] 2.1 `./pipeline/build.sh`を実行し、`site/tiles/points.pmtiles`を再生成する

## 3. ポップアップへの表示追加 (#134)

- [x] 3.1 `site/main.js`の`points`クリックハンドラに、`feature.properties.symbolrank`が存在する場合に`symbolrank: <値>`を表示する行を追加する
- [x] 3.2 `site/main.js`の`points`クリックハンドラに、`feature.properties.population`が存在する場合に`周辺人口: <値>人（半径10km以内）`（3桁区切り表示）を表示する行を追加する

## 4. 動作確認 (#135)

- [x] 4.1 `npx serve site`でローカル起動し、ジャンクションのマーカークリックで`symbolrank`が表示され、周辺人口は表示されないことを確認する
- [x] 4.2 一般インターチェンジ・スマートインターチェンジのマーカークリックで`symbolrank`・周辺人口の両方が表示されることを確認する
- [x] 4.3 その他の接合部のマーカークリックで`symbolrank`・周辺人口いずれも表示されないことを確認する
- [x] 4.4 既存の地点名・地点種別・車線数の表示に変化がないことを確認する

## 5. デプロイ (#136)

- [ ] 5.1 `pipeline/**`・`site/**`の変更を`main`にpushし、`site/**`分の既存GitHub Actionsによる自動デプロイを確認する
- [ ] 5.2 再生成した`site/tiles/points.pmtiles`が配置されていることを手動で確認する
