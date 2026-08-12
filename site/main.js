// MapLibre GL JSでPMTiles（路線・地点）を読み込み、背景地図なしで
// 高速道路レイヤーのみを描画する。
//
// OpenSpec Change: highway-facility-map
// tasks.md: 5.1, 5.2, 5.3

import {
  Map,
  NavigationControl,
  Popup,
  addProtocol,
} from "https://cdn.jsdelivr.net/npm/maplibre-gl@6.2.0/dist/maplibre-gl.mjs";
import {
  mapStyle,
  registerRouteNumberBadgeImage,
  registerRouteNumberBadgeShieldImage,
} from "./style/map-style.js";

// 接合部種別（point_type）を人が読める種別名に変換する（design.md 決定3）。
const POINT_TYPE_LABELS = {
  1: "一般インターチェンジ",
  2: "スマートインターチェンジ",
  3: "ジャンクション",
  4: "その他の接合部",
};

// 路線種別区分（route_category）を人が読める種別名に変換する（design.md 決定2）。
const ROUTE_CATEGORY_LABELS = {
  1: "高速自動車国道",
  2: "高速自動車国道に並行する自専道",
  3: "一般国道の自専道",
  4: "本州四国連絡高速道路",
  5: "指定都市高速道路",
  6: "その他",
};

// pmtilesは index.html 内の通常のscriptタグ（依存関係を内包したグローバル
// バンドル）で読み込まれ、window.pmtiles として参照できる。
const protocol = new window.pmtiles.Protocol();
addProtocol("pmtiles", protocol.tile);

const map = new Map({
  container: "map",
  style: mapStyle,
  // 日本全体の高速道路網が収まる初期表示範囲・ズーム（URLにハッシュ
  // パラメータが含まれる場合はそちらが優先される）
  center: [137.5, 36.5],
  zoom: 4.3,
  // ズーム・中心緯度経度・回転・傾きをURLハッシュに同期し、ハッシュ付き
  // URLからその表示状態で初期化できるようにする
  hash: true,
  // MapLibreはデフォルトで漢字等の表意文字をクライアント側のシステムフォント
  // でローカル描画し帯域を節約するが、利用者の環境にCJKフォントが無いと文字
  // が表示されない。路線名・地点名を確実に表示するため無効化し、style側の
  // `glyphs`（CJK対応のSDFフォント）から取得させる。
  localIdeographFontFamily: false,
});

map.addControl(new NavigationControl(), "top-right");

// route-number-badges（矩形バッジ）・route-number-badges-shield（シールド
// バッジ）レイヤーが参照するSDF画像は、実行時に`map.addImage`で登録する
// 必要があるため、styleの読み込み完了後に登録する
// （design.md 決定3、fix-route-number-badges design.md 決定3）。
map.on("load", () => {
  registerRouteNumberBadgeImage(map);
  registerRouteNumberBadgeShieldImage(map);
});

// 現在表示中のポップアップ（路線・地点で共有）。新しいポップアップを開く前に
// 既存のものを閉じ、路線・地点いずれにも該当しないクリックでは既存の
// ポップアップを閉じるだけにする。
let activePopup = null;

function showPopup(lngLat, container) {
  if (activePopup) {
    activePopup.remove();
  }
  // innerHTMLへのプロパティ直接埋め込みは行わず、DOM APIでテキストノード
  // として組み立てた要素をポップアップに渡す（design.md 決定3）。
  activePopup = new Popup().setLngLat(lngLat).setDOMContent(container).addTo(map);
}

// 地点（IC・JCT等）のクリック時に、地点名・種別ラベルを表示するポップアップ
// を出す。`points`レイヤーのみをリッスンするため、地点以外のクリックでは
// 発火しない（design.md 決定3）。
map.on("click", "points", (event) => {
  const feature = event.features?.[0];
  if (!feature) {
    return;
  }

  const coordinates = feature.geometry.coordinates.slice();
  const { point_name, point_type, lane_counts } = feature.properties;

  const container = document.createElement("div");
  const nameEl = document.createElement("div");
  nameEl.textContent = point_name;
  const typeEl = document.createElement("div");
  typeEl.textContent = POINT_TYPE_LABELS[point_type] ?? point_type;
  container.append(nameEl, typeEl);

  // lane_countsはMVT仕様上の制約でJSON文字列としてタイルに保持されている
  // ため、表示前にパースする（design.md 決定6）。空配列の場合は行を表示
  // しない（design.md 決定5）。
  const laneCounts = lane_counts ? JSON.parse(lane_counts) : [];
  if (laneCounts.length > 0) {
    const laneEl = document.createElement("div");
    laneEl.textContent = `車線数: ${laneCounts.join(", ")}`;
    container.append(laneEl);
  }

  showPopup(coordinates, container);
});

// 地点マーカーへのホバー時にカーソルをpointerに変更する。
map.on("mouseenter", "points", () => {
  map.getCanvas().style.cursor = "pointer";
});
map.on("mouseleave", "points", () => {
  map.getCanvas().style.cursor = "";
});

// 路線のクリック時に、法定名・通称名（存在時のみ）・種別・車線数・路線番号
// （存在時のみ）をラベル付きで表示するポップアップを出す（design.md 決定6）。
// 塗り部分（`lines-fill`、判定領域として最も広い）のみをリッスンし、
// `lines-casing`には登録しない（同一地物で二重発火するため、design.md 決定2）。
map.on("click", "lines-fill", (event) => {
  const feature = event.features?.[0];
  if (!feature) {
    return;
  }

  // 地点（IC・JCT等）は路線ジオメトリの頂点上に位置するため、地点マーカーの
  // クリックはこのハンドラにも同時にヒットする。地点ポップアップを優先し、
  // このハンドラでは何もしない。
  const pointHit = map.queryRenderedFeatures(event.point, { layers: ["points"] });
  if (pointHit.length > 0) {
    return;
  }

  const { route_name, route_category, lane_count, common_name, route_number } =
    feature.properties;

  const container = document.createElement("div");

  // 法定名は通称名の有無にかかわらず常に表示する（design.md 決定6）。
  const routeNameEl = document.createElement("div");
  routeNameEl.textContent = `法定名: ${route_name}`;
  container.append(routeNameEl);

  // 通称名（common_name）が付与されている路線にのみ表示する（design.md 決定6）。
  if (common_name) {
    const commonNameEl = document.createElement("div");
    commonNameEl.textContent = `通称名: ${common_name}`;
    container.append(commonNameEl);
  }

  const categoryEl = document.createElement("div");
  categoryEl.textContent = `種別: ${ROUTE_CATEGORY_LABELS[route_category] ?? route_category}`;
  container.append(categoryEl);

  const laneEl = document.createElement("div");
  laneEl.textContent = `車線数: ${lane_count}`;
  container.append(laneEl);

  // 路線番号（例：E1）が付与されている路線には、通称名の有無にかかわらず
  // 表示する（design.md 決定4）。
  if (route_number) {
    const routeNumberEl = document.createElement("div");
    routeNumberEl.textContent = `路線番号: ${route_number}`;
    container.append(routeNumberEl);
  }

  showPopup(event.lngLat, container);
});

// 路線へのホバー時にカーソルをpointerに変更する。
map.on("mouseenter", "lines-fill", () => {
  map.getCanvas().style.cursor = "pointer";
});
map.on("mouseleave", "lines-fill", () => {
  map.getCanvas().style.cursor = "";
});

// 路線・地点いずれの地物にも該当しない位置をクリックした場合、表示中の
// ポップアップがあれば閉じる。路線・地点それぞれのハンドラは対象地物が
// ある場合のみ発火するため、こちらは常に発火するリスナーとして別途登録する。
map.on("click", (event) => {
  const hits = map.queryRenderedFeatures(event.point, {
    layers: ["points", "lines-fill"],
  });
  if (hits.length === 0 && activePopup) {
    activePopup.remove();
    activePopup = null;
  }
});
