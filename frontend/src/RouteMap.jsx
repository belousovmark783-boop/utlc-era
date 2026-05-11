import { useEffect, useRef, useState } from 'react'

// ── База координат ──
const COORDS = {
  'москва':[55.7558,37.6173],'moscow':[55.7558,37.6173],'питер':[59.9311,30.3609],
  'санкт-петербург':[59.9311,30.3609],'saint petersburg':[59.9311,30.3609],'spb':[59.9311,30.3609],
  'новосибирск':[54.9884,82.9657],'novosibirsk':[54.9884,82.9657],
  'екатеринбург':[56.8389,60.6057],'yekaterinburg':[56.8389,60.6057],
  'владивосток':[43.1155,131.8855],'vladivostok':[43.1155,131.8855],
  'находка':[42.8274,132.886],'nakhodka':[42.8274,132.886],
  'хабаровск':[48.4827,135.084],'khabarovsk':[48.4827,135.084],
  'иркутск':[52.2978,104.2964],'irkutsk':[52.2978,104.2964],
  'красноярск':[56.0153,92.8932],'krasnoyarsk':[56.0153,92.8932],
  'омск':[54.9885,73.3242],'omsk':[54.9885,73.3242],
  'казань':[55.7887,49.1221],'kazan':[55.7887,49.1221],
  'минск':[53.9045,27.5615],'minsk':[53.9045,27.5615],
  'алматы':[43.2567,76.9286],'almaty':[43.2567,76.9286],
  'астана':[51.1801,71.446],'astana':[51.1801,71.446],'nur-sultan':[51.1801,71.446],
  'ташкент':[41.2995,69.2401],'tashkent':[41.2995,69.2401],
  'баку':[40.4093,49.8671],'baku':[40.4093,49.8671],
  'тбилиси':[41.6938,44.8015],'tbilisi':[41.6938,44.8015],
  'шанхай':[31.2304,121.4737],'shanghai':[31.2304,121.4737],
  'пекин':[39.9042,116.4074],'beijing':[39.9042,116.4074],
  'гуанчжоу':[23.1291,113.2644],'guangzhou':[23.1291,113.2644],
  'нинбо':[29.8683,121.544],'ningbo':[29.8683,121.544],
  'тяньцзинь':[39.3434,117.3616],'tianjin':[39.3434,117.3616],
  'чэнду':[30.5728,104.0668],'chengdu':[30.5728,104.0668],
  'иу':[29.3064,120.0754],'yiwu':[29.3064,120.0754],
  'харбин':[45.8038,126.5349],'harbin':[45.8038,126.5349],
  'урумчи':[43.8256,87.6169],'urumqi':[43.8256,87.6169],
  'гонконг':[22.3193,114.1694],'hong kong':[22.3193,114.1694],
  'далянь':[38.914,121.6147],'dalian':[38.914,121.6147],
  'циндао':[36.0671,120.3826],'qingdao':[36.0671,120.3826],
  'берлин':[52.52,13.405],'berlin':[52.52,13.405],
  'гамбург':[53.5753,10.0153],'hamburg':[53.5753,10.0153],
  'варшава':[52.2297,21.0122],'warsaw':[52.2297,21.0122],
  'прага':[50.0755,14.4378],'prague':[50.0755,14.4378],
  'вена':[48.2082,16.3738],'vienna':[48.2082,16.3738],
  'rotterdam':[51.9244,4.4777],'роттердам':[51.9244,4.4777],
  'antwerp':[51.2194,4.4025],'антверпен':[51.2194,4.4025],
  'paris':[48.8566,2.3522],'париж':[48.8566,2.3522],
  'london':[51.5074,-0.1278],'лондон':[51.5074,-0.1278],
  'istanbul':[41.0082,28.9784],'стамбул':[41.0082,28.9784],
  'helsinki':[60.1699,24.9384],'хельсинки':[60.1699,24.9384],
  'riga':[56.946,24.1059],'рига':[56.946,24.1059],
  'токио':[35.6762,139.6503],'tokyo':[35.6762,139.6503],
  'сеул':[37.5665,126.978],'seoul':[37.5665,126.978],
  'пусан':[35.1796,129.0756],'busan':[35.1796,129.0756],
  'сингапур':[1.3521,103.8198],'singapore':[1.3521,103.8198],
  'бангкок':[13.7563,100.5018],'bangkok':[13.7563,100.5018],
  'мумбай':[19.076,72.8777],'mumbai':[19.076,72.8777],
  'дели':[28.7041,77.1025],'delhi':[28.7041,77.1025],
  'дубай':[25.2048,55.2708],'dubai':[25.2048,55.2708],
  'джидда':[21.4858,39.1925],'jeddah':[21.4858,39.1925],
  'нью-йорк':[40.7128,-74.006],'new york':[40.7128,-74.006],
  'лос-анджелес':[34.0522,-118.2437],'los angeles':[34.0522,-118.2437],
  'long beach':[33.7701,-118.1937],
  'vancouver':[49.2827,-123.1207],'ванкувер':[49.2827,-123.1207],
  'каир':[30.0444,31.2357],'cairo':[30.0444,31.2357],
  'момбаса':[-4.0435,39.6682],'mombasa':[-4.0435,39.6682],
}

async function getCoords(name) {
  const k = name.toLowerCase().trim()
  if (COORDS[k]) return COORDS[k]
  try {
    const r = await fetch(
      `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(name)}&format=json&limit=1`,
      { headers: { 'Accept-Language': 'ru,en' } }
    )
    const d = await r.json()
    if (d[0]) return [parseFloat(d[0].lat), parseFloat(d[0].lon)]
  } catch {}
  return null
}

// ══════════════════════════════════════════════════
//  РЕАЛИСТИЧНАЯ МАРШРУТИЗАЦИЯ
// ══════════════════════════════════════════════════

const W = {
  suez_s:[29.9,32.55], suez_n:[31.25,32.35], bab:[12.6,43.45],
  hormuz:[26.6,56.5], malacca_w:[5.35,100.3], malacca_e:[1.25,104.0],
  taiwan:[25.1,122.1], tsugaru:[41.5,140.7],
  la_manche:[50.8,1.5], gibraltar:[35.95,-5.45], bosporus:[41.1,29.05],
  dover:[51.1,1.35], skagerrak:[57.5,9.0],
  cape_good:[-34.5,19.8], cape_horn:[-57.0,-65.0],
  panama_a:[9.35,-79.9], panama_p:[8.9,-79.5],
  indian_c:[-10.0,72.0], med_c:[35.0,18.0],
  atlantic_n:[45.0,-30.0], pacific_n:[45.0,170.0], pacific_c:[10.0,160.0],
}

function interpolatePath(pts, density=60) {
  if (pts.length < 2) return pts
  const total = pts.length - 1
  const out = []
  for (let seg = 0; seg < total; seg++) {
    const a = pts[seg], b = pts[seg+1]
    const steps = Math.max(6, Math.round(density / total))
    for (let i = 0; i < steps; i++) {
      const t = i / steps
      out.push([a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t])
    }
  }
  out.push(pts[pts.length-1])
  return out
}

function seaRoute(from, to) {
  const [fLat,fLon] = from, [tLat,tLon] = to
  const inMed      = (lat,lon) => lat>30&&lat<47&&lon>-6&&lon<37
  const inBlackSea = (lat,lon) => lat>40&&lat<47&&lon>27&&lon<42
  const inRedSea   = (lat,lon) => lat>12&&lat<30&&lon>32&&lon<45
  const inPersGulf = (lat,lon) => lat>22&&lat<30&&lon>47&&lon<60
  const inIndian   = (lat,lon) => lon>44&&lon<100&&lat<30
  const inEastAsia = lon => lon>100&&lon<150
  const inAtlantic = lon => lon>-80&&lon<20
  const inPacificW = lon => lon<-80
  const inNorthEurope = (lat,lon) => lat>54&&lon>5&&lon<30
  const inBlackOrCaspian = (lat,lon) => inBlackSea(lat,lon)||(lat>36&&lat<48&&lon>47&&lon<55)

  const needBosporus = inBlackOrCaspian(fLat,fLon)||inBlackOrCaspian(tLat,tLon)
  const needSuez = (
    (inAtlantic(fLon)||inMed(fLat,fLon)||inBlackOrCaspian(fLat,fLon))&&
    (inIndian(tLat,tLon)||inEastAsia(tLon)||inRedSea(tLat,tLon)||inPersGulf(tLat,tLon))
  )||(
    (inIndian(fLat,fLon)||inEastAsia(fLon)||inRedSea(fLat,fLon)||inPersGulf(fLat,fLon))&&
    (inAtlantic(tLon)||inMed(tLat,tLon)||inBlackOrCaspian(tLat,tLon))
  )
  const needMalacca = (
    (inIndian(fLat,fLon)||needSuez)&&inEastAsia(tLon)
  )||(
    inEastAsia(fLon)&&(inIndian(tLat,tLon)||needSuez)
  )
  const needGibraltar = (
    inMed(fLat,fLon)&&!inMed(tLat,tLon)&&!inBlackSea(tLat,tLon)
  )||(
    inMed(tLat,tLon)&&!inMed(fLat,fLon)&&!inBlackSea(fLat,fLon)
  )
  const needPanama = (
    (inEastAsia(fLon)||fLon>-80&&fLon<-60)&&(inPacificW(tLon)||inAtlantic(tLon))
  )||(
    (inEastAsia(tLon)||tLon>-80&&tLon<-60)&&(inPacificW(fLon)||inAtlantic(fLon))
  )

  let via = []

  if (needBosporus&&inBlackOrCaspian(fLat,fLon)) via.push(W.bosporus)
  if (needGibraltar&&inMed(fLat,fLon)) via.push(W.med_c, W.gibraltar)
  if (needSuez) {
    if (!needGibraltar&&inAtlantic(fLon)&&fLon<20) via.push(W.gibraltar, W.med_c)
    via.push(W.suez_n, W.suez_s, W.bab)
    if (inPersGulf(tLat,tLon)||inPersGulf(fLat,fLon)) via.push(W.hormuz)
    else via.push(W.indian_c)
  }
  if (needMalacca) {
    const fromEast = inEastAsia(fLon)
    if (fromEast) via.push(W.malacca_e, W.malacca_w)
    else via.push(W.malacca_w, W.malacca_e)
  }
  if (needPanama) {
    if (inEastAsia(fLon)) via.push(W.pacific_c, W.panama_p, W.panama_a)
    else via.push(W.panama_a, W.panama_p, W.pacific_c)
  }
  if (!needSuez&&!needMalacca&&!needPanama&&!needGibraltar&&!needBosporus) {
    if (inNorthEurope(fLat,fLon)||inNorthEurope(tLat,tLon)) via.push(W.skagerrak)
    else if (inMed(fLat,fLon)||inMed(tLat,tLon)) { /* прямой */ }
    else if (inEastAsia(fLon)&&inEastAsia(tLon)) { /* прямой */ }
    else if (inAtlantic(fLon)&&inAtlantic(tLon)) via.push(W.atlantic_n)
  }
  if (needGibraltar&&inMed(tLat,tLon)) via.push(W.gibraltar, W.med_c)
  if (needBosporus&&inBlackOrCaspian(tLat,tLon)) via.push(W.bosporus)

  return interpolatePath([from, ...via, to], 100)
}

// Ж/Д узлы и коридоры
const N = {
  msk:[55.76,37.62], spb:[59.93,30.36], ekb:[56.84,60.61],
  novsib:[54.99,82.97], krasnoy:[56.02,92.89], irkutsk:[52.30,104.30],
  chita:[52.03,113.50], vlad:[43.12,131.89], khabar:[48.48,135.08],
  nakhodka:[42.83,132.89],
  almaty:[43.26,76.93], astana:[51.18,71.45], aktobe:[50.28,57.21],
  urumqi:[43.83,87.62], xian:[34.34,108.94], zhengzhou:[34.75,113.66],
  beijing:[39.90,116.41], shanghai:[31.23,121.47], guangzhou:[23.13,113.26],
  chengdu:[30.57,104.07], lianyungang:[34.60,119.22], harbin:[45.80,126.53],
  warsaw:[52.23,21.01], berlin:[52.52,13.40], hamburg:[53.58,10.02],
  vienna:[48.21,16.37], rotterdam:[51.92,4.48], frankfurt:[50.11,8.68],
  tashkent:[41.30,69.24], tehran:[35.69,51.39], istanbul:[41.01,28.98],
  tbilisi:[41.69,44.80], baku:[40.41,49.87],
  delhi:[28.70,77.10], mumbai:[19.08,72.88],
  seoul:[37.57,126.98], busan:[35.18,129.08],
  tokyo:[35.68,139.65],
}

const CORRIDORS = {
  // Китай — Европа через Казахстан (основной МЧЖ)
  china_eu_kaz: [N.beijing,N.zhengzhou,N.xian,N.urumqi, [44.8,80.3], N.almaty,N.astana,N.aktobe, [52,55], N.ekb,N.msk,N.warsaw,N.berlin,N.rotterdam],
  // Транссиб: Европа — Дальний Восток
  transsib: [N.rotterdam,N.berlin,N.warsaw,N.msk,N.ekb,N.novsib,N.krasnoy,N.irkutsk,N.chita,[49.6,117.5],N.khabar,N.vlad],
  // БАМ ответвление
  bam: [N.irkutsk,[55.5,114.0],[52.5,120.0],N.khabar,N.vlad],
  // ТМТМ (через Каспий)
  tmtm: [N.beijing,N.urumqi,N.aktobe,[46.0,50.5],N.baku,N.tbilisi,N.istanbul,N.vienna,N.rotterdam],
  // Через Иран
  south_iran: [N.urumqi,N.tashkent,N.tehran,N.istanbul,N.vienna],
  // Россия — Европа
  ru_eu: [N.msk,N.warsaw,N.berlin,N.rotterdam],
  // Корея — Транссиб
  korea_eu: [N.busan,N.seoul,[42.0,130.5],N.vlad,N.khabar,N.irkutsk,N.novsib,N.ekb,N.msk,N.warsaw,N.berlin],
  // Японское направление
  japan_eu: [N.tokyo,N.busan,N.seoul,[42.0,130.5],N.vlad,N.khabar,N.irkutsk,N.novsib,N.ekb,N.msk,N.warsaw],
  // Китай — Россия напрямую
  china_ru: [N.beijing,N.harbin,[49.6,117.5],N.chita,N.irkutsk,N.novsib,N.ekb,N.msk],
  // Центральная Азия — Европа
  centasia_eu: [N.tashkent,N.aktobe,N.astana,N.ekb,N.msk,N.warsaw,N.berlin],
}

function dist2(a,b){ const d=a[0]-b[0],e=a[1]-b[1]; return d*d+e*e }

function railRoute(from, to) {
  const [fLat,fLon] = from, [tLat,tLon] = to
  const inChina    = (la,lo) => lo>98&&lo<135&&la>18&&la<55
  const inRussia   = (la,lo) => lo>28&&lo<145&&la>48&&la<75
  const inEurope   = (la,lo) => lo>-5&&lo<35&&la>36&&la<62
  const inCentAsia = (la,lo) => lo>55&&lo<90&&la>36&&la<55
  const inFarEast  = (la,lo) => lo>128&&la>35&&la<55
  const inKorea    = (la,lo) => lo>126&&lo<130&&la>34&&la<39
  const inJapan    = (la,lo) => lo>130&&lo<146&&la>30&&la<46
  const inSouthAsia= (la,lo) => lo>65&&lo<100&&la>8&&la<36

  let corridor = null

  if ((inChina(fLat,fLon)||inFarEast(fLat,fLon))&&(inEurope(tLat,tLon)||inRussia(tLat,tLon)&&tLon<60)) {
    corridor = CORRIDORS.china_eu_kaz
  } else if ((inEurope(fLat,fLon)||inRussia(fLat,fLon)&&fLon<60)&&(inChina(tLat,tLon)||inFarEast(tLat,tLon))) {
    corridor = [...CORRIDORS.china_eu_kaz].reverse()
  } else if (inKorea(fLat,fLon)&&inEurope(tLat,tLon)) {
    corridor = CORRIDORS.korea_eu
  } else if (inEurope(fLat,fLon)&&inKorea(tLat,tLon)) {
    corridor = [...CORRIDORS.korea_eu].reverse()
  } else if (inJapan(fLat,fLon)||inJapan(tLat,tLon)) {
    corridor = inJapan(fLat,fLon) ? CORRIDORS.japan_eu : [...CORRIDORS.japan_eu].reverse()
  } else if (inRussia(fLat,fLon)&&inFarEast(tLat,tLon)) {
    corridor = CORRIDORS.transsib
  } else if (inFarEast(fLat,fLon)&&inRussia(tLat,tLon)) {
    corridor = [...CORRIDORS.transsib].reverse()
  } else if (inRussia(fLat,fLon)&&inEurope(tLat,tLon)) {
    corridor = CORRIDORS.ru_eu
  } else if (inEurope(fLat,fLon)&&inRussia(tLat,tLon)) {
    corridor = [...CORRIDORS.ru_eu].reverse()
  } else if (inChina(fLat,fLon)&&inRussia(tLat,tLon)) {
    corridor = CORRIDORS.china_ru
  } else if (inCentAsia(fLat,fLon)||inCentAsia(tLat,tLon)) {
    corridor = CORRIDORS.centasia_eu
  } else {
    return interpolatePath([from,to],40)
  }

  // Находим ближайшие узлы входа/выхода
  let fi=0, ti=corridor.length-1, minF=Infinity, minT=Infinity
  corridor.forEach((n,i) => {
    const df=dist2(from,n), dt=dist2(to,n)
    if(df<minF){minF=df;fi=i}
    if(dt<minT){minT=dt;ti=i}
  })

  const slice = fi<=ti ? corridor.slice(fi,ti+1) : [...corridor.slice(ti,fi+1)].reverse()
  return interpolatePath([from,...slice,to], 80)
}

function straight(a,b,n=40){
  const p=[];for(let i=0;i<=n;i++){const t=i/n;p.push([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t])}
  return p
}

// ── Запрос геометрии с бэкенда (searoute) или локальный fallback ──
const API = ''

async function fetchRouteGeometry(from, to, mode) {
  try {
    const url = `${API}/api/route-geometry?from_lat=${from[0]}&from_lon=${from[1]}&to_lat=${to[0]}&to_lon=${to[1]}&mode=${mode}`
    const ctl = new AbortController()
    setTimeout(() => ctl.abort(), 6000)
    const r = await fetch(url, { signal: ctl.signal })
    if (!r.ok) throw new Error('HTTP ' + r.status)
    const d = await r.json()
    return { pts: d.coordinates, source: d.source }
  } catch {
    // Fallback — встроенные коридоры
    if (mode === 'sea')  return { pts: seaRoute(from, to),  source: 'local' }
    if (mode === 'rail') return { pts: railRoute(from, to), source: 'local' }
    return { pts: straight(from, to), source: 'local' }
  }
}

// ── MODAL ──
export default function RouteMapModal({ route, dark, onClose }) {
  const mapDiv  = useRef(null)
  const mapInst = useRef(null)
  const [msg, setMsg]   = useState('Загружаем...')
  const [err, setErr]   = useState(null)
  const [ready, setReady] = useState(false)

  const mode = route?.mode?.toLowerCase()

  useEffect(() => {
    if (!route || !mapDiv.current) return
    let dead = false
    setErr(null); setReady(false); setMsg('Ищем координаты...')

    const run = async () => {
      // Ждём Leaflet
      let attempts = 0
      while (!window.L && attempts < 30) {
        await new Promise(r => setTimeout(r, 100)); attempts++
      }
      if (!window.L) { setErr('Leaflet не загружен'); return }
      if (dead) return

      setMsg(`Геокодируем: ${route.origin}...`)
      const from = await getCoords(route.origin)
      if (!from) { setErr(`Не нашли: "${route.origin}"`); return }
      if (dead) return

      setMsg(`Геокодируем: ${route.destination}...`)
      const to = await getCoords(route.destination)
      if (!to) { setErr(`Не нашли: "${route.destination}"`); return }
      if (dead) return

      setMsg('Рисуем карту...')
      await new Promise(r => setTimeout(r, 30))

      if (mapInst.current) { mapInst.current.remove(); mapInst.current = null }
      if (mapDiv.current._leaflet_id) {
        mapDiv.current._leaflet_id = null
        mapDiv.current.innerHTML = ''
      }

      const L = window.L
      const map = L.map(mapDiv.current, {
        center: [(from[0]+to[0])/2, (from[1]+to[1])/2],
        zoom: 4, zoomControl: true
      })
      mapInst.current = map

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19, crossOrigin: true
      }).addTo(map)

      const makeIcon = (color, label) => L.divIcon({
        className: '', iconSize: [16,16], iconAnchor: [8,8],
        html: `<div style="position:relative;width:16px;height:16px">
          <div style="width:16px;height:16px;border-radius:50%;background:${color};border:3px solid #fff;box-shadow:0 2px 10px rgba(0,0,0,.6)"></div>
          <div style="position:absolute;bottom:22px;left:50%;transform:translateX(-50%);white-space:nowrap;
            background:rgba(10,15,30,.92);color:#e2e8f4;font-size:12px;font-weight:700;
            padding:3px 9px;border-radius:6px;border:1px solid rgba(255,255,255,.15);
            font-family:Arial,sans-serif;pointer-events:none">${label}</div>
        </div>`
      })
      L.marker(from, { icon: makeIcon('#00c853', route.origin) }).addTo(map)
      L.marker(to,   { icon: makeIcon('#f59e0b', route.destination) }).addTo(map)

      const allLines = []

      if (mode === 'sea') {
        setMsg('Строим морской маршрут (searoute)...')
        const { pts, source } = await fetchRouteGeometry(from, to, 'sea')
        if (dead) return
        const l = L.polyline(pts, {color:'#38bdf8',weight:3.5,opacity:.9}).addTo(map)
        l.bindTooltip(`🚢 Морской маршрут${source==='searoute'?' (searoute)':''}`,{sticky:true})
        allLines.push(l)
        setMsg('Строим ж/д для сравнения (OSRM)...')
        const { pts: rPts, source: rs } = await fetchRouteGeometry(from, to, 'rail')
        if (dead) return
        const rl = L.polyline(rPts, {color:'#f97316',weight:2,opacity:.4,dashArray:'9,5'}).addTo(map)
        rl.bindTooltip(`🚂 Ж/Д (сравнение)${rs==='osrm'?' ✓ OSRM':''}`,{sticky:true})
        allLines.push(rl)
      } else if (mode === 'rail') {
        setMsg('Строим ж/д маршрут (OSRM)...')
        const { pts, source } = await fetchRouteGeometry(from, to, 'rail')
        if (dead) return
        const l = L.polyline(pts, {color:'#f97316',weight:4,opacity:.9}).addTo(map)
        l.bindTooltip(`🚂 Ж/Д маршрут${source==='osrm'?' (OSRM)':''}`,{sticky:true})
        allLines.push(l)
        setMsg('Строим море для сравнения (searoute)...')
        const { pts: sPts, source: ss } = await fetchRouteGeometry(from, to, 'sea')
        if (dead) return
        const sl = L.polyline(sPts, {color:'#38bdf8',weight:2,opacity:.4,dashArray:'9,5'}).addTo(map)
        sl.bindTooltip(`🚢 Морской (сравнение)${ss==='searoute'?' ✓':''}`,{sticky:true})
        allLines.push(sl)
      } else {
        const { pts: sPts, source: ss } = await fetchRouteGeometry(from, to, 'sea')
        if (dead) return
        const sl = L.polyline(sPts, {color:'#38bdf8',weight:3,opacity:.8}).addTo(map)
        sl.bindTooltip(`🚢 Морской${ss==='searoute'?' (searoute)':''}`,{sticky:true})
        allLines.push(sl)
        const { pts: rPts, source: rs } = await fetchRouteGeometry(from, to, 'rail')
        if (dead) return
        const rl = L.polyline(rPts, {color:'#f97316',weight:3,opacity:.8}).addTo(map)
        rl.bindTooltip(`🚂 Ж/Д${rs==='osrm'?' (OSRM)':''}`,{sticky:true})
        allLines.push(rl)
      }

      // fitBounds из точек маршрутов
      const lats=[from[0],to[0]], lons=[from[1],to[1]]
      allLines.forEach(line => {
        try {
          line.getLatLngs().forEach(ll => {
            if (ll.lat!==undefined){lats.push(ll.lat);lons.push(ll.lng)}
            else if(Array.isArray(ll)) ll.forEach(p=>{if(p.lat){lats.push(p.lat);lons.push(p.lng)}})
          })
        } catch {}
      })
      const pad=0.12, dLat=(Math.max(...lats)-Math.min(...lats))*pad, dLon=(Math.max(...lons)-Math.min(...lons))*pad
      map.fitBounds([[Math.min(...lats)-dLat,Math.min(...lons)-dLon],[Math.max(...lats)+dLat,Math.max(...lons)+dLon]])
      setTimeout(()=>map.invalidateSize(),150)

      if (!dead) { setReady(true); setMsg('') }
    }

    run().catch(e => { if (!dead) setErr('Ошибка: '+e.message) })
    return () => { dead=true; if(mapInst.current){mapInst.current.remove();mapInst.current=null} }
  }, [route?.route_id, dark])

  // Theme
  const bg=dark?'#111827':'#fff', surf=dark?'#1a2235':'#f5f8ff'
  const bd=dark?'rgba(255,255,255,.08)':'rgba(0,0,0,.1)'
  const text=dark?'#e2e8f4':'#1a2235', muted=dark?'#7a8699':'#5566aa'
  const green='#00c853', gold='#f59e0b', accent=dark?'#38bdf8':'#0077cc'
  const modeBg={rail:'#1565c0',sea:'#006979'}[mode]||'#555'
  const modeLabel={rail:'🚂 ЖД',sea:'🚢 МОРЕ'}[mode]||mode?.toUpperCase()
  const scC=s=>s>=.7?green:s>=.4?gold:'#ff5252'
  const rcC=r=>r>.6?'#ff5252':r>.3?gold:green

  return (
    <>
      <style>{`
        .lf-tip{background:rgba(10,15,30,.92)!important;color:#e2e8f4!important;
          border:1px solid rgba(255,255,255,.1)!important;border-radius:6px!important;
          font-size:11px!important;font-weight:700!important;padding:3px 9px!important}
        .leaflet-tooltip{background:rgba(10,15,30,.92)!important;color:#e2e8f4!important;
          border:1px solid rgba(255,255,255,.1)!important;border-radius:6px!important;
          font-size:11px!important;font-weight:700!important;padding:3px 9px!important}
      `}</style>
      {/* backdrop */}
      <div onClick={onClose} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.72)',zIndex:9000,backdropFilter:'blur(3px)'}}/>
      {/* modal */}
      <div style={{position:'fixed',top:'50%',left:'50%',transform:'translate(-50%,-50%)',
        zIndex:9001,width:'min(96vw,980px)',maxHeight:'90vh',background:bg,
        borderRadius:14,border:`1px solid ${bd}`,boxShadow:'0 24px 80px rgba(0,0,0,.65)',
        display:'flex',flexDirection:'column',overflow:'hidden'}}>

        {/* header */}
        <div style={{display:'flex',alignItems:'center',gap:12,padding:'13px 18px',
          background:surf,borderBottom:`1px solid ${bd}`,flexShrink:0}}>
          <div style={{flex:1}}>
            <div style={{fontFamily:'Inter,sans-serif',fontSize:20,fontWeight:800,
              letterSpacing:2,color:text,display:'flex',alignItems:'center',gap:9}}>
              {route.route_id}
              <span style={{background:modeBg,color:'white',padding:'2px 9px',borderRadius:20,fontSize:11,fontWeight:700}}>{modeLabel}</span>
            </div>
            <div style={{fontSize:12,color:muted,marginTop:2}}>
              <span style={{color:green,fontWeight:700}}>{route.origin}</span>
              <span style={{color:muted,margin:'0 7px'}}>→</span>
              <span style={{color:gold,fontWeight:700}}>{route.destination}</span>
            </div>
          </div>
          <button onClick={onClose} style={{width:30,height:30,borderRadius:'50%',border:`1px solid ${bd}`,
            background:'transparent',color:muted,fontSize:15,cursor:'pointer',
            display:'flex',alignItems:'center',justifyContent:'center'}}>✕</button>
        </div>

        {/* metrics */}
        <div style={{display:'flex',flexWrap:'wrap',background:surf,borderBottom:`1px solid ${bd}`,flexShrink:0}}>
          {[['TCO',`$${(route.cost_usd||0).toLocaleString('ru')}`,accent],
            ['Транзит',`${route.time_days||0} дней`,gold],
            ['Риск',(route.risk_index||0).toFixed(3),rcC(route.risk_index||0)],
            ['CO₂',`${(route.emissions||0).toFixed(2)} т`,'#4ade80'],
            ['Балл',(route.score||0).toFixed(4),scC(route.score||0)],
          ].map(([l,v,c])=>(
            <div key={l} style={{padding:'9px 16px',borderRight:`1px solid ${bd}`}}>
              <div style={{fontSize:9,color:muted,textTransform:'uppercase',letterSpacing:1.5,fontFamily:'Inter,sans-serif',marginBottom:2}}>{l}</div>
              <div style={{fontFamily:'JetBrains Mono,ui-monospace,monospace',fontWeight:700,fontSize:15,color:c}}>{v}</div>
            </div>
          ))}
        </div>

        {/* map */}
        <div style={{position:'relative',flex:1,minHeight:380}}>
          {(!ready||err) && (
            <div style={{position:'absolute',inset:0,zIndex:10,display:'flex',flexDirection:'column',
              alignItems:'center',justifyContent:'center',gap:12,
              background:err?'rgba(11,15,26,.97)':'rgba(11,15,26,.88)'}}>
              {err ? (
                <>
                  <div style={{fontSize:34}}>⚠️</div>
                  <div style={{color:'#ff7070',fontSize:13,fontWeight:600,textAlign:'center',maxWidth:320,lineHeight:1.5}}>{err}</div>
                </>
              ) : (
                <>
                  <div style={{width:36,height:36,borderRadius:'50%',
                    border:'3px solid rgba(255,255,255,.1)',borderTopColor:'#00c853',
                    animation:'mapSpin 1s linear infinite'}}/>
                  <style>{'@keyframes mapSpin{to{transform:rotate(360deg)}}'}</style>
                  <div style={{color:muted,fontSize:12}}>{msg}</div>
                </>
              )}
            </div>
          )}
          <div ref={mapDiv} style={{width:'100%',height:'100%',minHeight:380}}/>
        </div>

        {/* legend */}
        <div style={{padding:'9px 18px',background:surf,borderTop:`1px solid ${bd}`,flexShrink:0,
          display:'flex',flexWrap:'wrap',gap:14,alignItems:'center',fontSize:11}}>
          <span style={{fontSize:9,color:muted,fontFamily:'Inter,sans-serif',letterSpacing:2,textTransform:'uppercase'}}>Легенда:</span>
          <div style={{display:'flex',alignItems:'center',gap:5,color:text}}><div style={{width:20,height:3,background:'#f97316',borderRadius:2}}/>🚂 Ж/Д</div>
          <div style={{display:'flex',alignItems:'center',gap:5,color:text}}><div style={{width:20,height:3,background:'#38bdf8',borderRadius:2}}/>🚢 Морской</div>
          <div style={{display:'flex',alignItems:'center',gap:5,color:text}}><div style={{width:9,height:9,borderRadius:'50%',background:green,border:'2px solid white',flexShrink:0}}/><span style={{color:green,fontWeight:700}}>{route.origin}</span></div>
          <div style={{display:'flex',alignItems:'center',gap:5,color:text}}><div style={{width:9,height:9,borderRadius:'50%',background:gold,border:'2px solid white',flexShrink:0}}/><span style={{color:gold,fontWeight:700}}>{route.destination}</span></div>
          <div style={{marginLeft:'auto',fontSize:9,color:muted}}>© OpenStreetMap · searoute · OSRM</div>
        </div>
      </div>
    </>
  )
}
