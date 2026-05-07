# Harta României - UAT și limite administrative

Mirror al limitelor administrative ale României (UAT, județe, regiuni, macroregiuni, frontieră) în formatele uzuale: **GeoJSON, TopoJSON, Shapefile, GeoPackage, FlatGeobuf, GeoParquet, KML**.

Resursă pentru proiectele organizației [National Youth Foundation](https://github.com/National-Youth-Foundation) și pentru oricine are nevoie de date oficiale despre granițele administrative ale României.

> **Sursă originală:** [geo-spatial.org](https://geo-spatial.org/descarcare/date/administrative-boundaries/) (date prelucrate pe baza ANCPI + INS).
> **Licență:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — atribuire obligatorie, share-alike.

---

## Ce conține

| Categorie | Conținut | Variante |
|---|---|---|
| `country/` | Frontiera României | poligon, linie + simplified |
| `macroregion/` | 4 macroregiuni de dezvoltare | poligon, linie + simplified |
| `region/` | 8 regiuni de dezvoltare | poligon, linie + simplified |
| `county/` | 42 județe | poligon, linie + simplified |
| `lau/` | ~3.181 UAT (comune, orașe, municipii, sectoare București) | poligon, linie + simplified + variante cu București unificat |

Total: **168 fișiere** (24 seturi × 7 formate).
- Fișiere **sub 25 MB** sunt în `data/` (committed direct în repo).
- Fișierele **mari** (UAT poligon nesimplificat) sunt în [Releases](../../releases).
- Indexul complet, cu hash-uri SHA256 și URL-uri stabile, e în [`manifest.json`](./manifest.json).

---

## Quick start - cele mai folosite fișiere

Pentru hărți interactive în browser, începe cu varianta **simplified TopoJSON** (cea mai mică):

| Nivel | Format | URL stabil |
|---|---|---|
| Țară | TopoJSON | `data/country/ro_admin_country_simplified_polygon.topojson` |
| Județe | TopoJSON | `data/county/ro_admin_county_simplified_polygon.topojson` |
| Regiuni | TopoJSON | `data/region/ro_admin_region_simplified_polygon.topojson` |
| UAT (toate) | TopoJSON | `data/lau/ro_admin_lau_simplified_polygon.topojson` |
| UAT (București unificat) | TopoJSON | `data/lau/ro_admin_lau_simplified_bucharest_merged_polygon.topojson` |

Toate fișierele din `data/` pot fi accesate direct prin **jsdelivr CDN** sau `raw.githubusercontent.com`:

```
https://cdn.jsdelivr.net/gh/National-Youth-Foundation/harta-romania-uat@main/data/county/ro_admin_county_simplified_polygon.geojson
```

---

## Exemple de utilizare

### Leaflet

```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<div id="map" style="height: 600px"></div>
<script>
  const map = L.map('map').setView([45.94, 24.97], 7);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map);

  fetch('https://cdn.jsdelivr.net/gh/National-Youth-Foundation/harta-romania-uat@main/data/county/ro_admin_county_simplified_polygon.geojson')
    .then(r => r.json())
    .then(data => {
      L.geoJSON(data, {
        style: { color: '#1f6feb', weight: 1, fillOpacity: 0.1 },
        onEachFeature: (f, layer) => layer.bindPopup(f.properties.name)
      }).addTo(map);
    });
</script>
```

### MapLibre GL JS

```javascript
map.on('load', async () => {
  const url = 'https://cdn.jsdelivr.net/gh/National-Youth-Foundation/harta-romania-uat@main/data/lau/ro_admin_lau_simplified_polygon.geojson';
  map.addSource('uat', { type: 'geojson', data: url });
  map.addLayer({
    id: 'uat-fill',
    type: 'fill',
    source: 'uat',
    paint: { 'fill-color': '#88c', 'fill-opacity': 0.3 }
  });
  map.addLayer({
    id: 'uat-outline',
    type: 'line',
    source: 'uat',
    paint: { 'line-color': '#226', 'line-width': 0.5 }
  });
});
```

### d3.js + TopoJSON (cel mai eficient pentru ~3000 UAT)

```javascript
import * as d3 from 'd3';
import * as topojson from 'topojson-client';

const topology = await d3.json(
  'https://cdn.jsdelivr.net/gh/National-Youth-Foundation/harta-romania-uat@main/data/lau/ro_admin_lau_simplified_polygon.topojson'
);
const objectName = Object.keys(topology.objects)[0];
const features = topojson.feature(topology, topology.objects[objectName]);

const projection = d3.geoMercator().fitSize([960, 600], features);
const path = d3.geoPath(projection);
svg.selectAll('path').data(features.features).enter()
  .append('path').attr('d', path).attr('fill', '#eee').attr('stroke', '#333');
```

### Python (geopandas)

```python
import geopandas as gpd

# Direct din GitHub (CDN), fără descărcare locală
url = "https://cdn.jsdelivr.net/gh/National-Youth-Foundation/harta-romania-uat@main/data/county/ro_admin_county_polygon.geojson"
counties = gpd.read_file(url)
counties.plot()

# Pentru UAT-uri full (180 MB GeoJSON), folosește GeoParquet din Releases
uat = gpd.read_parquet(
    "https://github.com/National-Youth-Foundation/harta-romania-uat/releases/download/2025.1/ro_admin_lau_polygon.parquet"
)
print(uat.head())
print(f"Total UAT: {len(uat)}")
```

### R (sf)

```r
library(sf)

counties <- st_read(
  "https://cdn.jsdelivr.net/gh/National-Youth-Foundation/harta-romania-uat@main/data/county/ro_admin_county_polygon.geojson"
)
plot(st_geometry(counties))
```

### DuckDB (cu spatial extension)

```sql
INSTALL spatial; LOAD spatial;

SELECT name, ST_Area(geom) AS area_m2
FROM ST_Read('https://github.com/National-Youth-Foundation/harta-romania-uat/releases/download/2025.1/ro_admin_lau_polygon.fgb')
ORDER BY area_m2 DESC LIMIT 10;
```

### QGIS / ArcGIS Pro

Descarcă Shapefile-ul (`.zip`) sau GeoPackage-ul (`.gpkg`) din [Releases](../../releases) și deschide-l direct. Sistemul de coordonate e **WGS 84 / EPSG:4326**.

---

## Structura repo-ului

```
harta-romania-uat/
├── manifest.json              # index complet (168 fișiere, hash-uri, URL-uri)
├── data/                      # fișiere mici (sub 25 MB), committed direct
│   ├── country/
│   ├── macroregion/
│   ├── region/
│   ├── county/
│   └── lau/                   # doar variantele simplified + .topojson
├── scripts/
│   ├── build_manifest.py      # regenerează manifest skeleton
│   ├── download_all.py        # descarcă toate fișierele upstream
│   ├── split_assets.py        # distribuie small → data/, big → release-assets/
│   └── make_release.py        # creează GitHub release cu assets
└── .github/workflows/sync.yml # mirror lunar automatizat
```

## Cum să refaci mirror-ul local

```bash
git clone https://github.com/National-Youth-Foundation/harta-romania-uat.git
cd harta-romania-uat

python3 scripts/build_manifest.py        # opțional, dacă upstream are categorii noi
python3 scripts/download_all.py          # → tmp/, ~10 minute, ~800 MB
python3 scripts/split_assets.py \
    --release-tag 2025.1 \
    --repo National-Youth-Foundation/harta-romania-uat
```

## Cum funcționează sincronizarea automată

Workflow-ul [`sync.yml`](./.github/workflows/sync.yml) rulează:
- **lunar** (prima zi a lunii, 03:17 UTC), automat
- **manual**, prin „Run workflow" în tab-ul Actions

La fiecare rulare:
1. descarcă toate fișierele upstream
2. compară SHA256 cu cele din `manifest.json`
3. dacă există schimbări → deschide PR cu fișierele mici noi + (re)creează release-ul cu fișierele mari

---

## Atribuire (obligatorie)

La folosirea acestor date, includeți o mențiune similară cu:

> Date administrative © [geo-spatial.org](https://geo-spatial.org/) pe baza datelor [ANCPI](https://www.ancpi.ro/) și [INS](https://insse.ro/), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Mirror: [National-Youth-Foundation/harta-romania-uat](https://github.com/National-Youth-Foundation/harta-romania-uat).

## Licență

- **Date** (toate fișierele din `data/` și Releases): [CC BY-SA 4.0](./LICENSE)
- **Cod** (scripturi, workflow-uri): [MIT](./LICENSE-CODE)
