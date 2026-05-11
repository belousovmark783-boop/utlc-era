import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import RouteMapModal from './RouteMap.jsx'

const API = ''

const CITY_LIST = [
  'Москва','Санкт-Петербург','Владивосток','Новосибирск','Хабаровск','Иркутск',
  'Красноярск','Екатеринбург','Казань','Находка','Омск','Челябинск','Калининград',
  'Шанхай','Пекин','Гуанчжоу','Нинбо','Тяньцзинь','Чэнду','Иу','Харбин',
  'Урумчи','Далянь','Циндао','Гонконг','Ухань','Сиань','Чунцин','Шэньчжэнь',
  'Минск','Алматы','Астана','Актобе','Ташкент','Баку','Тбилиси','Ереван',
  'Бишкек','Душанбе','Ашхабад','Кишинев','Киев','Одесса',
  'Берлин','Гамбург','Мюнхен','Варшава','Гданьск','Прага','Вена','Роттердам',
  'Амстердам','Антверпен','Брюссель','Париж','Марсель','Лондон','Хельсинки',
  'Рига','Вильнюс','Таллин','Стамбул','Стокгольм','Осло','Копенгаген',
  'Будапешт','Бухарест','Барселона','Мадрид','Лиссабон','Милан','Генуя','Пирей',
  'Токио','Осака','Сеул','Пусан','Сингапур','Бангкок','Хошимин','Ханой',
  'Джакарта','Куала-Лумпур','Порт-Кланг','Мумбай','Дели','Ченнаи','Карачи','Дакка',
  'Дубай','Абу-Даби','Джидда','Эр-Рияд','Доха','Бейрут','Тегеран',
  'Каир','Александрия','Момбаса','Найроби','Дар-эс-Салам','Лагос','Касабланка','Кейптаун',
  'Нью-Йорк','Лос-Анджелес','Long Beach','Хьюстон','Сиэтл','Ванкувер','Монреаль',
  'Moscow','Saint Petersburg','Vladivostok','Novosibirsk','Nakhodka','Yekaterinburg',
  'Shanghai','Beijing','Guangzhou','Ningbo','Tianjin','Chengdu','Yiwu','Harbin',
  'Urumqi','Dalian','Qingdao','Hong Kong','Wuhan','Shenzhen','Xian','Chongqing',
  'Minsk','Almaty','Astana','Tashkent','Baku','Tbilisi','Yerevan','Bishkek',
  'Berlin','Hamburg','Warsaw','Prague','Vienna','Rotterdam','Amsterdam',
  'Antwerp','Brussels','Paris','London','Helsinki','Riga','Istanbul','Stockholm',
  'Oslo','Copenhagen','Budapest','Bucharest','Barcelona','Madrid','Milan','Genoa','Piraeus',
  'Tokyo','Seoul','Busan','Singapore','Bangkok','Jakarta','Kuala Lumpur',
  'Mumbai','Delhi','Karachi','Dhaka','Dubai','Jeddah','Riyadh','Tehran',
  'Cairo','Mombasa','Nairobi','Lagos','Casablanca','Cape Town','Durban',
  'New York','Los Angeles','Houston','Seattle','Vancouver','Montreal',
]

function CityInput({ value, onChange, placeholder, dark }) {
  const [open, setOpen]   = useState(false)
  const [query, setQuery] = useState(value)
  const wrapRef           = useRef(null)

  useEffect(() => { setQuery(value) }, [value])
  useEffect(() => {
    const h = e => { if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', h)
    return () => document.removeEventListener('mousedown', h)
  }, [])

  const suggestions = query.length >= 2
    ? CITY_LIST.filter(c => c.toLowerCase().startsWith(query.toLowerCase())).slice(0, 8)
    : []

  const surf2  = dark ? '#1a2235' : '#f7f8fa'
  const border = dark ? 'rgba(255,255,255,.08)' : '#e5e7eb'
  const text   = dark ? '#e2e8f4' : '#0f172a'
  const muted  = dark ? '#7a8699' : '#64748b'
  const green  = '#00a84f'

  return (
    <div ref={wrapRef} style={{ position:'relative' }}>
      <input type="text" value={query} placeholder={placeholder}
        onChange={e => { setQuery(e.target.value); onChange(e.target.value); setOpen(true) }}
        onFocus={() => query.length >= 2 && setOpen(true)}
        style={{
          width:'100%', background:surf2, border:`1px solid ${open && suggestions.length ? green : border}`,
          color:text, padding:'10px 14px', borderRadius:8,
          fontFamily:'inherit', fontSize:14, outline:'none', transition:'border-color .15s',
        }}
      />
      {open && suggestions.length > 0 && (
        <div style={{
          position:'absolute', top:'calc(100% + 4px)', left:0, right:0,
          background: dark ? '#151e2e' : '#fff',
          border:`1px solid ${green}44`, borderRadius:10,
          boxShadow:'0 8px 32px rgba(0,0,0,.25)', zIndex:9999, overflow:'hidden',
        }}>
          {suggestions.map((city, i) => (
            <div key={city} onMouseDown={() => { setQuery(city); onChange(city); setOpen(false) }}
              style={{
                padding:'9px 14px', cursor:'pointer', fontSize:14, color:text,
                display:'flex', alignItems:'center', gap:8,
                background: i===0 ? `${green}15` : 'transparent',
                borderBottom: i < suggestions.length-1 ? `1px solid ${border}` : 'none',
              }}
              onMouseEnter={e => e.currentTarget.style.background = `${green}25`}
              onMouseLeave={e => e.currentTarget.style.background = i===0 ? `${green}15` : 'transparent'}
            >
              <span>📍</span>
              <span>
                <strong>{city.slice(0, query.length)}</strong>
                <span style={{ color:muted }}>{city.slice(query.length)}</span>
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function TransportScene({ dark }) {
  const railBg = dark ? '#0f1520' : '#dce8f5'
  const seaBg  = dark ? '#061520' : '#b8d8f0'
  return (
    <div style={{ width:'100%', height:80, overflow:'hidden' }}>
      <svg width="100%" height="80" viewBox="0 0 1200 80" preserveAspectRatio="xMidYMid meet" style={{ display:'block' }}>
        <defs>
          <style>{`
            @keyframes trainGo{0%{transform:translateX(-340px)}100%{transform:translateX(1260px)}}
            @keyframes shipGo{0%{transform:translateX(1260px)}100%{transform:translateX(-380px)}}
            @keyframes puff{0%{opacity:.7;transform:translateY(0) scale(1)}100%{opacity:0;transform:translateY(-22px) scale(2)}}
            @keyframes wheel{to{transform:rotate(360deg)}}
            @keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}
            @keyframes waveSlide{0%{transform:translateX(0)}100%{transform:translateX(-200px)}}
            .tr{animation:trainGo 14s linear infinite}.sh{animation:shipGo 20s linear infinite}
            .p1{animation:puff 1.3s ease-out infinite}.p2{animation:puff 1.3s ease-out .43s infinite}
            .p3{animation:puff 1.3s ease-out .86s infinite}.w1{animation:wheel .7s linear infinite}
            .bw{animation:bob 2.6s ease-in-out infinite}.wv{animation:waveSlide 4s linear infinite}
          `}</style>
          <linearGradient id="tg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#d8d8d8"/><stop offset="100%" stopColor="#888"/></linearGradient>
          <linearGradient id="hl" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#1b3f5e"/><stop offset="100%" stopColor="#0a1e2e"/></linearGradient>
          <linearGradient id="sp" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#f0ead6"/><stop offset="100%" stopColor="#c4af85"/></linearGradient>
        </defs>
        <rect x="0" y="0" width="1200" height="40" fill={railBg}/>
        {Array.from({length:48}).map((_,i)=>(<rect key={i} x={i*26} y="32" width="10" height="5" rx="1" fill={dark?'#3a2a18':'#b8a070'} opacity=".7"/>))}
        <rect x="0" y="32" width="1200" height="2.5" fill={dark?'#7a6040':'#9a8060'}/>
        <rect x="0" y="36" width="1200" height="2.5" fill={dark?'#7a6040':'#9a8060'}/>
        <g className="tr">
          <rect x="190" y="15" width="96" height="17" rx="3" fill="url(#tg)"/><rect x="248" y="10" width="40" height="17" rx="2" fill="url(#tg)"/>
          <rect x="190" y="22" width="98" height="4" fill="#00a84f"/><path d="M288,12 L308,15 L308,30 L288,32Z" fill="#bbb"/>
          <rect x="288" y="21" width="20" height="4" fill="#00a84f"/><circle cx="306" cy="22" r="3.5" fill="#ffe566"/>
          <rect x="206" y="8" width="8" height="9" rx="1" fill="#777"/><rect x="203" y="6" width="14" height="4" rx="2" fill="#888"/>
          <ellipse className="p1" cx="210" cy="3" rx="6" ry="3.5" fill={dark?'#ccc':'#999'} opacity=".7"/>
          <ellipse className="p2" cx="216" cy="0" rx="5" ry="3" fill={dark?'#aaa':'#777'} opacity=".5"/>
          <ellipse className="p3" cx="207" cy="-3" rx="4" ry="2.5" fill={dark?'#999':'#666'} opacity=".4"/>
          <rect x="258" y="12" width="13" height="8" rx="2" fill="#9dd8f0" opacity=".9"/><rect x="274" y="11" width="11" height="8" rx="2" fill="#9dd8f0" opacity=".9"/>
          {[210,237,265].map((cx,i)=>(<g key={i} className="w1" style={{transformOrigin:`${cx}px 34px`}}><circle cx={cx} cy="34" r="7" fill="#444" stroke="#222" strokeWidth="1.5"/><circle cx={cx} cy="34" r="2.5" fill="#888"/><line x1={cx} y1="27" x2={cx} y2="41" stroke="#666" strokeWidth="1.5"/><line x1={cx-7} y1="34" x2={cx+7} y2="34" stroke="#666" strokeWidth="1.5"/></g>))}
          <rect x="55" y="14" width="126" height="18" rx="2" fill="url(#tg)"/><rect x="55" y="22" width="126" height="4" fill="#00a84f"/>
          <rect x="63" y="12" width="110" height="14" rx="2" fill="#b8b8b8"/>
          <text x="118" y="22" textAnchor="middle" fontSize="7" fill="#005a2b" fontWeight="bold" fontFamily="monospace" letterSpacing="1">UTLC ERA</text>
          {[73,102,157].map((cx,i)=>(<g key={i} className="w1" style={{transformOrigin:`${cx}px 34px`}}><circle cx={cx} cy="34" r="6.5" fill="#444" stroke="#222" strokeWidth="1.5"/><circle cx={cx} cy="34" r="2.5" fill="#888"/><line x1={cx} y1="28" x2={cx} y2="41" stroke="#666" strokeWidth="1.5"/><line x1={cx-6} y1="34" x2={cx+6} y2="34" stroke="#666" strokeWidth="1.5"/></g>))}
        </g>
        <rect x="0" y="40" width="1200" height="40" fill={seaBg}/>
        {[0,1].map(copy=>(<g key={copy} className="wv" style={{transform:`translateX(${copy*200}px)`}}>{[50,60,70].map((y,li)=>(Array.from({length:9}).map((_,i)=>(<path key={`${li}-${i}`} d={`M${i*140-10} ${y} Q${i*140+25} ${y-5},${i*140+70} ${y} T${i*140+140} ${y}`} fill="none" stroke={dark?'#4fc3f7':'#2080b0'} strokeWidth={li===0?1.4:1} opacity={li===0?.45:.25}/>))))}</g>))}
        <g className="sh"><g className="bw">
          <path d="M10,54 L210,54 L218,70 L2,70Z" fill="url(#hl)"/><path d="M6,64 L212,64 L218,70 L2,70Z" fill="#0b1e2e"/>
          <rect x="2" y="67" width="216" height="2.5" fill="#c0392b"/><rect x="30" y="38" width="136" height="17" rx="3" fill="url(#sp)"/>
          <rect x="50" y="30" width="92" height="10" rx="2" fill="#d4c08a"/><rect x="66" y="23" width="62" height="9" rx="2" fill="#c8b070"/>
          <rect x="90" y="13" width="18" height="12" rx="2" fill="#1e2d40"/><rect x="87" y="11" width="24" height="5" rx="2" fill="#253545"/>
          <rect x="87" y="13" width="24" height="3" fill="#c0392b"/>
          <ellipse className="p1" cx="99" cy="7" rx="7" ry="4" fill={dark?'#bbb':'#999'} opacity=".65"/>
          <ellipse className="p2" cx="105" cy="3" rx="5" ry="3" fill={dark?'#999':'#777'} opacity=".45"/>
          <line x1="99" y1="6" x2="99" y2="23" stroke="#888" strokeWidth="2"/><path d="M99,6 L114,9 L99,14Z" fill="#00a84f"/>
          {[54,70,86,102,118,134].map((x,i)=>(<rect key={i} x={x} y="32" width="11" height="6" rx="1" fill="#9dd8f0" opacity=".85"/>))}
          {[36,54,72,90,108,126,144].map((x,i)=>(<rect key={i} x={x} y="41" width="11" height="7" rx="1" fill="#9dd8f0" opacity=".8"/>))}
          <text x="12" y="68" fontSize="11" fill="#4a8fc4">⚓</text>
          <path d="M212,64 Q230,58 248,64 Q264,58 280,64" fill="none" stroke="#4fc3f7" strokeWidth="1.8" opacity=".55"/>
        </g></g>
        <line x1="0" y1="40" x2="1200" y2="40" stroke={dark?'#0a3d5c':'#7bbcd8'} strokeWidth="1.5"/>
      </svg>
    </div>
  )
}

function Field({ label, children }) {
  return (
    <div style={{ marginBottom:14 }}>
      <label style={{ fontSize:12, color:'var(--muted)', display:'block', marginBottom:6 }}>{label}</label>
      {children}
    </div>
  )
}
function Select({ value, onChange, options }) {
  return (
    <select value={value} onChange={e=>onChange(e.target.value)} style={{
      width:'100%', background:'var(--surf2)', border:'1px solid var(--border)',
      color:'var(--text)', padding:'9px 12px', borderRadius:8,
      fontFamily:'inherit', fontSize:14, outline:'none', cursor:'pointer'
    }}>{options.map(([v,l])=><option key={v} value={v}>{l}</option>)}</select>
  )
}
function NumInput({ value, onChange, min, step }) {
  return <input type="number" value={value} min={min||0} step={step||1} onChange={e=>onChange(+e.target.value)}/>
}

function RouteCard({ route, index, dark, onUpdate, onRemove }) {
  const [loadingRate, setLoadingRate] = useState(false)
  const [rateHint, setRateHint]       = useState(null)

  const surf  = dark ? '#111827' : '#ffffff'
  const surf2 = dark ? '#1a2235' : '#f7f8fa'
  const surf3 = dark ? '#1f2d42' : '#eef0f4'
  const border= dark ? 'rgba(255,255,255,.08)' : '#e5e7eb'
  const text  = dark ? '#e2e8f4' : '#0f172a'
  const muted = dark ? '#7a8699' : '#64748b'
  const green = '#00a84f', greenM = '#00a84f'
  const red   = dark ? '#ff5252' : '#dc2626'
  const amber = '#d97706'
  const modeBg = m => ({rail:'#2563eb',sea:'#0891b2'}[m]||'#555')
  const modeIcon = m => ({rail:'🚂',sea:'🚢'}[m]||'📦')

  const fetchIndicativeRate = async () => {
    if (!route.origin || !route.destination) {
      setRateHint({ error: 'Укажите города отправки и назначения' })
      return
    }
    setLoadingRate(true)
    setRateHint(null)
    try {
      const params = new URLSearchParams({
        origin: route.origin,
        destination: route.destination,
        mode: route.mode,
        weight_tons: 1,
      })
      const res = await fetch(`/api/indicative-rate?${params}`)
      if (!res.ok) throw new Error('Ошибка сервера')
      const data = await res.json()
      setRateHint(data)
    } catch(e) {
      setRateHint({ error: 'Не удалось получить ставку' })
    } finally {
      setLoadingRate(false)
    }
  }

  return (
    <div style={{
      background: surf, border:`1px solid ${border}`, borderRadius:14,
      padding:'16px 18px', marginBottom:10,
    }}>
      {/* Заголовок */}
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:14 }}>
        <div style={{ display:'flex', alignItems:'center', gap:10 }}>
          <span style={{ fontFamily:"'JetBrains Mono', ui-monospace, monospace", fontSize:13, fontWeight:600,
            color:green, background:`${green}15`, padding:'3px 10px', borderRadius:20 }}>
            #{index+1}
          </span>
          <input type="text" value={route.route_id} onChange={e=>onUpdate('route_id',e.target.value)}
            style={{ background:'transparent', border:'none', borderBottom:`1px solid ${border}`,
              color:text, fontSize:13, fontFamily:"'JetBrains Mono', ui-monospace, monospace", fontWeight:500,
              padding:'2px 6px', width:100, outline:'none' }}/>
        </div>
        <div style={{ display:'flex', gap:6, alignItems:'center' }}>
          {['sea','rail'].map(m=>(
            <button key={m} onClick={()=>onUpdate('mode',m)} style={{
              padding:'5px 12px', borderRadius:20, border:'none', cursor:'pointer',
              fontSize:12, fontWeight:700, fontFamily:'Inter', letterSpacing:1,
              background: route.mode===m ? modeBg(m) : surf3,
              color: route.mode===m ? 'white' : muted,
              boxShadow: route.mode===m ? `0 2px 10px ${modeBg(m)}55` : 'none',
              transition:'all .15s',
            }}>{modeIcon(m)} {m.toUpperCase()}</button>
          ))}
          <button onClick={onRemove} title="Удалить"
            style={{ width:28, height:28, borderRadius:8, border:`1px solid ${border}`,
              background:surf3, color:muted, cursor:'pointer', fontSize:13,
              display:'flex', alignItems:'center', justifyContent:'center',
              transition:'all .15s', marginLeft:4, flexShrink:0 }}
            onMouseEnter={e=>{e.currentTarget.style.borderColor=red;e.currentTarget.style.color=red}}
            onMouseLeave={e=>{e.currentTarget.style.borderColor=border;e.currentTarget.style.color=muted}}
          >✕</button>
        </div>
      </div>

      {/* Откуда → Куда */}
      <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:14 }}>
        <div style={{ flex:1 }}>
          <div style={{ fontSize:10, color:muted, fontFamily:'Inter',
            letterSpacing:2, textTransform:'uppercase', marginBottom:5 }}>📍 Откуда</div>
          <CityInput value={route.origin} onChange={val=>onUpdate('origin',val)}
            placeholder="Шанхай, Москва..." dark={dark}/>
        </div>
        <div style={{ fontSize:22, color:greenM, flexShrink:0, paddingTop:18 }}>→</div>
        <div style={{ flex:1 }}>
          <div style={{ fontSize:10, color:muted, fontFamily:'Inter',
            letterSpacing:2, textTransform:'uppercase', marginBottom:5 }}>🏁 Куда</div>
          <CityInput value={route.destination} onChange={val=>onUpdate('destination',val)}
            placeholder="Роттердам, Берлин..." dark={dark}/>
        </div>
      </div>

      {/* Ставка */}
      <div style={{ display:'grid', gridTemplateColumns:'1fr 90px', gap:10 }}>
        <div>
          <div style={{ fontSize:10, color:muted, fontFamily:'Inter',
            letterSpacing:2, textTransform:'uppercase', marginBottom:5 }}>💵 Ставка перевозчика</div>
          <input type="number" value={route.carrier_rate_usd} min={0}
            onChange={e=>onUpdate('carrier_rate_usd',+e.target.value)}
            style={{ width:'100%', background:surf2, border:`1px solid ${border}`,
              color:text, padding:'10px 14px', borderRadius:8,
              fontFamily:"'JetBrains Mono', ui-monospace, monospace", fontSize:14, outline:'none' }}/>
        </div>
        <div>
          <div style={{ fontSize:10, color:muted, fontFamily:'Inter',
            letterSpacing:2, textTransform:'uppercase', marginBottom:5 }}>Валюта</div>
          <select value={route.currency} onChange={e=>onUpdate('currency',e.target.value)}
            style={{ width:'100%', background:surf2, border:`1px solid ${border}`,
              color:text, padding:'10px 8px', borderRadius:8, fontSize:13, cursor:'pointer', outline:'none' }}>
            {['USD','EUR','CNY','RUB','KZT','JPY','GBP','AED'].map(c=>(
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Кнопка и подсказка индикативной ставки */}
      <div style={{ marginTop:10 }}>
        <button onClick={fetchIndicativeRate} disabled={loadingRate}
          style={{ fontSize:11, padding:'5px 12px', borderRadius:8,
            border:`1px solid rgba(245,158,11,.4)`,
            background:'rgba(245,158,11,.08)', color:amber,
            cursor:loadingRate?'wait':'pointer', fontWeight:600, letterSpacing:.5 }}>
          {loadingRate ? '⏳ Загрузка...' : '📊 Получить индикативную ставку'}
        </button>
        {rateHint && !rateHint.error && (
          <div style={{ marginTop:8, fontSize:12, padding:'8px 12px', borderRadius:8,
            background:'rgba(245,158,11,.08)', border:`1px solid rgba(245,158,11,.25)`, color:text }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
              <span style={{ fontWeight:700, color:amber }}>
                ${rateHint.rate_usd?.toLocaleString()} USD / TEU
              </span>
              {!rateHint.is_live && (
                <span style={{ fontSize:10, color:muted, background:surf3,
                  padding:'2px 7px', borderRadius:10 }}>📋 Индикатив</span>
              )}
              {rateHint.is_live && (
                <span style={{ fontSize:10, color:green, background:`${green}15`,
                  padding:'2px 7px', borderRadius:10 }}>🟢 Live</span>
              )}
            </div>
            <div style={{ color:muted, marginTop:3, fontSize:11 }}>
              {rateHint.source} • {rateHint.note}
            </div>
            <button onClick={()=>{ onUpdate('carrier_rate_usd', rateHint.rate_usd); setRateHint(null) }}
              style={{ marginTop:7, fontSize:11, padding:'4px 10px', borderRadius:6,
                border:`1px solid ${greenM}55`, background:`${green}15`, color:green,
                cursor:'pointer', fontWeight:600 }}>
              ✓ Применить
            </button>
          </div>
        )}
        {rateHint?.error && (
          <div style={{ marginTop:6, fontSize:11, color:red }}>{rateHint.error}</div>
        )}
      </div>
    </div>
  )
}

export default function App() {
  const [dark,setDark]           = useState(false)
  const [tab,setTab]             = useState('analyze')
  const [inputMode,setInputMode] = useState('simple')
  const [routes,setRoutes]       = useState([
    {route_id:'R-001',origin:'Шанхай',destination:'Роттердам',mode:'sea', carrier_rate_usd:2800, currency:'USD'},
    {route_id:'R-002',origin:'Шанхай',destination:'Роттердам',mode:'rail',carrier_rate_usd:4800, currency:'USD'},
  ])
  const [cargo,setCargo] = useState({
    weight_tons:20, volume_teu:1, cargo_value:250000,
    cargo_type:'обычный', container_type:'20ft', capital_rate:15,
  })
  const [csvText,setCsvText]         = useState('')
  const [fileName,setFileName]       = useState('')
  const [cargoValue,setCargoValue]   = useState(250000)
  const [capitalRate,setCapitalRate] = useState(15)
  const [weights,setWeights]   = useState({cost:0.30,time:0.50,risk:0.20,emissions:0.00})
  const [results,setResults]   = useState(null)
  const [history,setHistory]   = useState([])
  const [loading,setLoading]         = useState(false)
  const [error,setError]             = useState('')
  const [dragOver,setDragOver]       = useState(false)
  const [selectedRoute,setSelectedRoute] = useState(null)
  const [showAdvanced,setShowAdvanced]   = useState(false)

  const weightSum = Object.values(weights).reduce((a,b)=>a+b,0)

  const T = {
    bg:    dark?'#0b0f1a':'#ffffff',
    surf:  dark?'#111827':'#ffffff',
    surf2: dark?'#1a2235':'#f7f8fa',
    surf3: dark?'#1f2d42':'#eef0f4',
    border:dark?'rgba(255,255,255,.08)':'#e5e7eb',
    text:  dark?'#e2e8f4':'#0f172a',
    muted: dark?'#7a8699':'#64748b',
    green: '#00a84f', greenM:'#00a84f', greenD:'#007a3a',
    accent:dark?'#38bdf8':'#2563eb',
    gold:  '#d97706',
    red:   dark?'#ff5252':'#dc2626',
    shadow:dark?'none':'0 1px 2px rgba(15,23,42,.04)',
    hdrBg: dark?'#07101f':'#ffffff',
    hdrText: dark?'#ffffff':'#0f172a',
    hdrMuted: dark?'rgba(255,255,255,.6)':'#64748b',
  }

  const css = `
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    body{background:${T.bg};font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;color:${T.text};-webkit-font-smoothing:antialiased}
    :root{--bg:${T.bg};--surf:${T.surf};--surf2:${T.surf2};--surf3:${T.surf3};--border:${T.border};--text:${T.text};--muted:${T.muted};--green:${T.green};--accent:${T.accent};--gold:${T.gold};--red:${T.red};}
    ::-webkit-scrollbar{width:6px;height:6px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:${T.surf3};border-radius:6px}::-webkit-scrollbar-thumb:hover{background:${T.muted}}
    input[type=range]{accent-color:${T.greenM};cursor:pointer;width:100%}
    input[type=number],input[type=text]{width:100%;background:${T.surf2};border:1px solid ${T.border};color:${T.text};padding:10px 12px;border-radius:8px;font-family:inherit;font-size:14px;outline:none;transition:border-color .15s,box-shadow .15s}
    input[type=number]:focus,input[type=text]:focus{border-color:${T.greenM};box-shadow:0 0 0 3px ${T.greenM}22}
    select{transition:border-color .15s,box-shadow .15s;font-family:inherit}select:focus{border-color:${T.greenM}!important;box-shadow:0 0 0 3px ${T.greenM}22}
    @keyframes fadeUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
    @keyframes spin{to{transform:rotate(360deg)}}
    .fade-up{animation:fadeUp .25s ease both}.spinning{display:inline-block;animation:spin 1s linear infinite}
    .tab-btn{padding:12px 20px;background:none;border:none;cursor:pointer;font-family:inherit;font-size:14px;font-weight:600;color:${T.muted};border-bottom:2px solid transparent;transition:color .15s,border-color .15s}
    .tab-btn.active{color:${T.text};border-bottom-color:${T.green}}.tab-btn:hover:not(.active){color:${T.text}}
    .mode-toggle-btn{padding:9px 16px;border-radius:8px;border:1px solid ${T.border};background:${T.surf};color:${T.muted};cursor:pointer;font-family:inherit;font-size:13px;font-weight:500;transition:border-color .15s,color .15s,background .15s}
    .mode-toggle-btn.active{background:${T.greenM}10;border-color:${T.greenM};color:${T.greenM};font-weight:600}
    .btn-main{width:100%;padding:13px;border:none;border-radius:10px;background:${T.greenM};color:white;font-family:inherit;font-size:15px;font-weight:600;cursor:pointer;transition:background .15s}
    .btn-main:hover:not(:disabled){background:${T.greenD}}
    .btn-main:disabled{background:${T.surf3};color:${T.muted};cursor:not-allowed}
    .btn-sm{padding:7px 14px;border:none;border-radius:7px;cursor:pointer;font-family:inherit;font-size:12px;font-weight:600;transition:opacity .15s}
    .btn-sm:hover{opacity:.85}
    .drop-zone{display:block;border:1.5px dashed ${T.border};border-radius:12px;padding:28px 16px;text-align:center;cursor:pointer;transition:border-color .15s,background .15s}
    .drop-zone:hover,.drop-zone.on{border-color:${T.greenM};background:${T.greenM}08}
    .sec-lbl{font-family:inherit;font-size:13px;font-weight:600;color:${T.text};margin-bottom:14px;letter-spacing:-.01em}
    .card{background:${T.surf};border:1px solid ${T.border};border-radius:12px;box-shadow:${T.shadow}}
    .kpi{background:${T.surf};border:1px solid ${T.border};border-radius:12px;padding:18px 20px;box-shadow:${T.shadow}}
    .kpi-lbl{font-size:12px;color:${T.muted};margin-bottom:6px;font-weight:500}
    .kpi-val{font-family:inherit;font-size:24px;font-weight:700;letter-spacing:-.02em}
    .kpi-sub{font-size:11px;color:${T.muted};margin-top:3px}
    .rtable{width:100%;border-collapse:collapse;font-size:13px}
    .rtable thead tr{background:${T.surf2}}
    .rtable th{padding:12px 14px;text-align:left;color:${T.muted};font-size:11px;font-family:inherit;font-weight:600}
    .rtable td{padding:13px 14px;border-top:1px solid ${T.border};vertical-align:middle;color:${T.text}}
    .rtable tr.best td{background:${T.greenM}08}.rtable tr:hover td{background:${T.surf2}!important;transition:background .12s}.rtable tbody tr{cursor:pointer}
    .rank{width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700}
    .mode-pill{display:inline-flex;align-items:center;gap:4px;color:white;padding:3px 10px;border-radius:6px;font-size:11px;font-weight:600;font-family:inherit}
    .score-chip{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:13px;font-weight:600;padding:3px 9px;border-radius:6px}
    .risk-chip{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:12px;font-weight:500;padding:2px 8px;border-radius:6px}
    .bd-chip{display:inline-block;margin:3px;padding:6px 10px;background:${T.surf2};border:1px solid ${T.border};border-radius:8px}
    .bd-lbl{font-size:10px;color:${T.muted};display:block;font-weight:500}
    .bd-val{font-size:13px;color:${T.text};font-family:'JetBrains Mono',ui-monospace,monospace;font-weight:600;display:block;margin-top:1px}
    .theme-btn{padding:7px 14px;border-radius:8px;border:1px solid ${T.border};background:${T.surf};color:${T.text};cursor:pointer;font-size:13px;font-family:inherit;font-weight:500;transition:border-color .15s,background .15s}
    .theme-btn:hover{border-color:${T.muted};background:${T.surf2}}
    .cargo-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
    .meta-badge{display:inline-flex;align-items:center;gap:5px;padding:3px 10px;border-radius:20px;font-size:11px;font-family:'JetBrains Mono',ui-monospace,monospace;font-weight:600;background:${T.surf2};border:1px solid ${T.border};color:${T.muted};margin:2px}
    @media(max-width:1100px){.main-grid{grid-template-columns:1fr!important}}
    @media(max-width:600px){.cargo-grid{grid-template-columns:1fr!important}}
  `

  const modeBg    = m => ({rail:'#1565c0',sea:'#006979'}[m]||'#555')
  const modeIcon  = m => ({rail:'🚂',sea:'🚢'}[m]||'📦')
  const scoreColor= s => s>=.7?T.green:s>=.4?T.gold:T.red
  const riskColor = r => r>.6?T.red:r>.3?T.gold:T.green

  const readFile = f => {
    if (!f) return
    if (!f.name.endsWith('.csv')) { setError('Нужен .csv файл'); return }
    setFileName(f.name); setError('')
    const r = new FileReader(); r.onload = e => setCsvText(e.target.result); r.readAsText(f)
  }

  const handleSimpleAnalyze = async () => {
    if (!routes.length) { setError('Добавьте хотя бы один маршрут'); return }
    setLoading(true); setError('')
    try {
      const { data } = await axios.post(`${API}/api/simple-analyze`, {
        routes,
        cargo: { weight_tons:cargo.weight_tons, volume_teu:cargo.volume_teu,
          cargo_value:cargo.cargo_value, cargo_type:cargo.cargo_type, capital_rate:cargo.capital_rate },
        weights,
      })
      setResults(data)
    } catch(e) { setError(e.response?.data?.detail || 'Ошибка подключения к серверу') }
    setLoading(false)
  }

  const handleCsvAnalyze = async () => {
    if (!csvText) { setError('Загрузите CSV файл'); return }
    setLoading(true); setError('')
    try {
      const { data } = await axios.post(`${API}/api/analyze`, {
        csv_content:csvText, cargo_value:cargoValue, capital_rate:capitalRate, weights
      })
      setResults(data)
    } catch(e) { setError(e.response?.data?.detail || 'Ошибка подключения к серверу') }
    setLoading(false)
  }

  const loadHistory = async () => {
    try { const { data } = await axios.get(`${API}/api/history`); setHistory(data) }
    catch { setError('Не удалось загрузить историю') }
  }
  const deleteAnalysis = async id => { await axios.delete(`${API}/api/analysis/${id}`); loadHistory() }
  const addRoute = () => setRoutes(r => [...r, { route_id:`R-${String(r.length+1).padStart(3,'0')}`, origin:'', destination:'', mode:'sea', carrier_rate_usd:0, currency:'USD' }])
  const removeRoute = i => setRoutes(r => r.filter((_,idx)=>idx!==i))
  const updateRoute = (i,field,val) => setRoutes(r => r.map((row,idx)=>idx===i?{...row,[field]:val}:row))

  const ResultsPanel = ({ results }) => (
    <div className="fade-up" style={{ display:'flex', flexDirection:'column', gap:16 }}>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:12 }}>
        {[
          {lbl:'🏆 Лучший маршрут',val:results.results[0]?.route_id||'—',sub:results.results[0]?.mode?.toUpperCase(),color:T.green},
          {lbl:'📦 Маршрутов',     val:results.results.length,           sub:'в анализе',       color:T.accent},
          {lbl:'💰 Мин. TCO',      val:`$${Math.min(...results.results.map(r=>r.cost_usd)).toLocaleString('ru')}`,sub:'полная стоимость',color:T.gold},
          {lbl:'⏱ Мин. транзит',  val:`${Math.min(...results.results.map(r=>r.time_days))} д`,sub:'быстрый маршрут',color:T.red},
        ].map(({lbl,val,sub,color})=>(
          <div key={lbl} className="kpi" style={{ borderLeft:`3px solid ${color}` }}>
            <div className="kpi-lbl">{lbl}</div>
            <div className="kpi-val" style={{ color }}>{val}</div>
            {sub && <div className="kpi-sub">{sub}</div>}
          </div>
        ))}
      </div>
      <div className="card" style={{ overflow:'hidden' }}>
        <div style={{ padding:'14px 20px', borderBottom:`1px solid ${T.border}`, display:'flex', justifyContent:'space-between', alignItems:'center' }}>
          <div style={{ fontFamily:'Inter', fontSize:16, fontWeight:700, letterSpacing:1.5, color:T.text }}>Результаты сравнения маршрутов</div>
          <button className="btn-sm" onClick={()=>window.open(`${API}/api/report/${results.id}/html`,'_blank')}
            style={{ background:'linear-gradient(135deg,#005a2b,#00a84f)', color:'white' }}>📥 HTML ОТЧЁТ</button>
        </div>
        <div style={{ overflowX:'auto' }}>
          <table className="rtable">
            <thead><tr>{['#','ID маршрута','Тип','Маршрут','TCO ($)','Дни','Риск','CO₂ (т)','Балл'].map(h=><th key={h}>{h}</th>)}</tr></thead>
            <tbody>
              {results.results.map((r,i)=>(
                <tr key={r.route_id} className={i===0?'best':''} onClick={()=>setSelectedRoute(r)}>
                  <td><div className="rank" style={{ background:i===0?'rgba(0,200,83,.15)':i===1?'rgba(56,189,248,.1)':'rgba(128,128,128,.07)', color:i===0?T.green:i===1?T.accent:T.muted }}>{i===0?'🥇':i===1?'🥈':i===2?'🥉':i+1}</div></td>
                  <td style={{ fontFamily:"'JetBrains Mono', ui-monospace, monospace", fontWeight:600, color:i===0?T.green:T.text }}>{r.route_id}</td>
                  <td><span className="mode-pill" style={{ background:modeBg(r.mode) }}>{modeIcon(r.mode)} {r.mode.toUpperCase()}</span></td>
                  <td>{r.origin}<span style={{ color:T.greenM, margin:'0 6px' }}>→</span>{r.destination}</td>
                  <td style={{ fontFamily:"'JetBrains Mono', ui-monospace, monospace", fontWeight:600 }}>{r.cost_usd.toLocaleString('ru')}</td>
                  <td style={{ fontFamily:"'JetBrains Mono', ui-monospace, monospace" }}>{r.time_days}<span style={{ color:T.muted }}> д</span></td>
                  <td><span className="risk-chip" style={{ color:riskColor(r.risk_index), background:`${riskColor(r.risk_index)}18` }}>{r.risk_index.toFixed(3)}</span></td>
                  <td style={{ fontFamily:"'JetBrains Mono', ui-monospace, monospace", fontSize:12, color:T.muted }}>{r.emissions.toFixed(3)}</td>
                  <td><span className="score-chip" style={{ color:scoreColor(r.score), background:`${scoreColor(r.score)}18`, boxShadow:i===0?`0 0 12px ${scoreColor(r.score)}44`:'none' }}>{r.score.toFixed(4)}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      {results.results[0]?.meta && (
        <div className="card" style={{ padding:16 }}>
          <div className="sec-lbl" style={{ marginBottom:10 }}>🔍 Авто-параметры лучшего маршрута</div>
          <div>
            {[['📏 Расстояние',`${results.results[0].meta.distance_km?.toLocaleString('ru')} км`],['🌍 Геориск',results.results[0].meta.geo_risk?.toFixed(3)],['🌦 Погода',results.results[0].meta.weather_risk?.toFixed(3)],['💱 Валюта',`${results.results[0].meta.currency} × ${results.results[0].meta.fx_rate}`],['📦 Тип груза',results.results[0].meta.cargo_surcharge],['🌿 Цена CO₂',`$${results.results[0].meta.carbon_price_usd ?? 15}/т`]].map(([lbl,val])=>(
              <span key={lbl} className="meta-badge">{lbl}: <strong style={{ color:T.text }}>{val}</strong></span>
            ))}
            {results.results[0].meta.rate_source && (
              <span className="meta-badge" style={{
                borderColor: results.results[0].meta.rate_is_indicative ? 'rgba(245,158,11,.35)' : 'rgba(0,200,83,.35)',
                background:  results.results[0].meta.rate_is_indicative ? 'rgba(245,158,11,.08)' : 'rgba(0,200,83,.08)',
              }}>
                💵 Ставка:{' '}
                <strong style={{ color: results.results[0].meta.rate_is_indicative ? T.gold : T.green }}>
                  {results.results[0].meta.rate_is_indicative ? '📋 ' : '🟢 '}
                  {results.results[0].meta.rate_source}
                </strong>
              </span>
            )}
          </div>
        </div>
      )}
      {results.results[0]?.breakdown && (
        <div className="card" style={{ padding:20 }}>
          <div className="sec-lbl" style={{ marginBottom:12 }}>🏆 Разбивка TCO — {results.results[0].route_id}</div>
          <div>
            {[['База','base'],['Таможня','customs'],['Обработка','handling'],['Углерод','carbon'],['Страховка','insurance'],['Обор. кап.','working_cap'],['Запасы','inventory'],['Администр.','admin'],['Резерв','contingency']].map(([lbl,key])=>(
              <span key={key} className="bd-chip"><span className="bd-lbl">{lbl}</span><span className="bd-val">${Math.round(results.results[0].breakdown[key]||0).toLocaleString('ru')}</span></span>
            ))}
          </div>
        </div>
      )}
    </div>
  )

  return (
    <>
      <style>{css}</style>
      <div style={{ minHeight:'100vh', background:T.bg, color:T.text, display:'flex', flexDirection:'column' }}>
        <header style={{ background:T.hdrBg, borderBottom:`1px solid ${T.border}`, position:'sticky', top:0, zIndex:100 }}>
          <div style={{ maxWidth:1500, margin:'0 auto', padding:'0 24px' }}>
            <div style={{ display:'flex', alignItems:'center', gap:14, padding:'18px 0' }}>
              <div style={{ width:36, height:36, borderRadius:9, background:T.greenM, display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0, color:'white', fontWeight:700, fontSize:15, letterSpacing:'-.02em' }}>U</div>
              <div>
                <div style={{ fontSize:17, fontWeight:700, color:T.hdrText, lineHeight:1.1, letterSpacing:'-.02em' }}>UTLC ERA</div>
                <div style={{ fontSize:12, color:T.hdrMuted, marginTop:2 }}>Анализ логистических маршрутов</div>
              </div>
              <div style={{ marginLeft:'auto', display:'flex', alignItems:'center', gap:10 }}>
                <button className="theme-btn" onClick={()=>setDark(!dark)}>{dark?'Светлая':'Тёмная'}</button>
              </div>
            </div>
            <div style={{ display:'flex', gap:2, borderTop:`1px solid ${T.border}` }}>
              {[['analyze','Анализ'],['history','История']].map(([key,lbl])=>(
                <button key={key} className={`tab-btn ${tab===key?'active':''}`} onClick={()=>{ setTab(key); if(key==='history') loadHistory() }}>{lbl}</button>
              ))}
            </div>
          </div>
        </header>

        <main style={{ flex:1, maxWidth:1500, margin:'0 auto', width:'100%', padding:'24px 24px 48px' }}>
          {tab==='analyze' && (
            <div className="main-grid" style={{ display:'grid', gridTemplateColumns:'430px 1fr', gap:18 }}>
              <div style={{ display:'flex', flexDirection:'column', gap:14 }}>

                {/* Режим ввода */}
                <div className="card" style={{ padding:16 }}>
                  <div className="sec-lbl">🔧 Режим ввода</div>
                  <div style={{ display:'flex', gap:8 }}>
                    <button className={`mode-toggle-btn ${inputMode==='simple'?'active':''}`} style={{ flex:1 }} onClick={()=>{ setInputMode('simple'); setResults(null); setError('') }}>✨ Упрощённый</button>
                    <button className={`mode-toggle-btn ${inputMode==='csv'?'active':''}`} style={{ flex:1 }} onClick={()=>{ setInputMode('csv'); setResults(null); setError('') }}>📄 CSV</button>
                  </div>
                  <div style={{ fontSize:11, color:T.muted, marginTop:10, lineHeight:1.5 }}>
                    {inputMode==='simple' ? '✅ Риски, расстояния и сборы рассчитываются автоматически.' : '📋 Загрузите CSV со всеми параметрами маршрутов.'}
                  </div>
                </div>

                {inputMode==='simple' && (<>
                  {/* Параметры груза */}
                  <div className="card" style={{ padding:20 }}>
                    <div className="sec-lbl">📦 Параметры груза</div>
                    <div className="cargo-grid">
                      <Field label="Стоимость груза (USD)"><NumInput value={cargo.cargo_value} onChange={v=>setCargo(c=>({...c,cargo_value:v}))} min={1}/></Field>
                      <Field label="Вес груза (тонны)"><NumInput value={cargo.weight_tons} onChange={v=>setCargo(c=>({...c,weight_tons:v}))} min={0.1} step={0.5}/></Field>
                      <Field label="Объём (TEU)"><NumInput value={cargo.volume_teu} onChange={v=>setCargo(c=>({...c,volume_teu:v}))} min={0.1} step={0.5}/></Field>
                    </div>
                    <Field label="Тип груза">
                      <Select value={cargo.cargo_type} onChange={v=>setCargo(c=>({...c,cargo_type:v}))} options={[['обычный','📦 Обычный'],['опасный','⚠️ Опасный (ADR/IMDG)'],['скоропортящийся','❄️ Скоропортящийся']]}/>
                    </Field>
                    <Field label="Тип контейнера">
                      <Select value={cargo.container_type} onChange={v=>setCargo(c=>({...c,container_type:v}))} options={[['20ft','📫 20ft (1 TEU) — стандарт'],['40ft','📦 40ft (2 TEU) — стандарт'],['40ft_hc','📦 40ft HC — High Cube'],['reefer','❄️ Рефрижератор'],['flat','🔲 Flat Rack — негабарит'],['tank','🛢 Танк-контейнер']]}/>
                    </Field>
                    {/* Расширенные параметры (WACC — для финансистов/грузовладельцев) */}
                    <div style={{ marginTop:14 }}>
                      <button onClick={()=>setShowAdvanced(v=>!v)} style={{
                        fontSize:11, color:T.muted, background:'transparent', border:'none',
                        cursor:'pointer', padding:0, display:'flex', alignItems:'center', gap:6,
                      }}>
                        <span style={{ fontSize:10 }}>{showAdvanced ? '▾' : '▸'}</span>
                        Расширенные параметры
                      </button>
                      {showAdvanced && (
                        <div style={{ marginTop:12, padding:'12px 14px', borderRadius:8,
                          background:T.surf3, border:`1px solid ${T.border}` }}>
                          <Field label="Ставка WACC (%)">
                            <NumInput value={cargo.capital_rate} onChange={v=>setCargo(c=>({...c,capital_rate:v}))} min={0.1} step={0.5}/>
                          </Field>
                          <div style={{ fontSize:11, color:T.muted, marginTop:6, lineHeight:1.5 }}>
                            Стоимость капитала грузовладельца. Влияет на расчёт заморозки средств в пути.
                            Дефолт 15% — рыночный ориентир для промышленных компаний.
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Карточки маршрутов */}
                  <div className="card" style={{ padding:20 }}>
                    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:16 }}>
                      <div className="sec-lbl" style={{ marginBottom:0 }}>🗺 Маршруты</div>
                      <button className="btn-sm" onClick={addRoute} style={{ background:'rgba(0,168,79,.15)', color:T.green, border:`1px solid rgba(0,168,79,.3)` }}>+ Добавить</button>
                    </div>
                    <div style={{ maxHeight:440, overflowY:'auto', paddingRight:2 }}>
                      {routes.map((r,i)=>(
                        <RouteCard key={i} route={r} index={i} dark={dark}
                          onUpdate={(field,val)=>updateRoute(i,field,val)}
                          onRemove={()=>removeRoute(i)}/>
                      ))}
                      {!routes.length && (
                        <div style={{ textAlign:'center', color:T.muted, fontSize:13, padding:'30px 0' }}>
                          <div style={{ fontSize:36, marginBottom:10, opacity:.2 }}>🗺</div>
                          Нажмите «+ Добавить»
                        </div>
                      )}
                    </div>
                  </div>
                </>)}

                {inputMode==='csv' && (<>
                  <div className="card" style={{ padding:20 }}>
                    <div className="sec-lbl">📁 CSV Данные</div>
                    <label className={`drop-zone ${dragOver?'on':''}`}
                      onDrop={e=>{ e.preventDefault(); setDragOver(false); readFile(e.dataTransfer.files[0]) }}
                      onDragOver={e=>{ e.preventDefault(); setDragOver(true) }}
                      onDragLeave={()=>setDragOver(false)}>
                      {fileName ? (<><div style={{ fontSize:34, marginBottom:8 }}>✅</div><div style={{ fontSize:13, color:T.green, fontWeight:700 }}>{fileName}</div><div style={{ fontSize:11, color:T.muted, marginTop:4 }}>{csvText.split('\n').filter(Boolean).length-1} строк загружено</div></>) : (<><div style={{ fontSize:34, marginBottom:8, opacity:.4 }}>📂</div><div style={{ fontSize:13, color:T.text, fontWeight:600 }}>Перетащите CSV</div><div style={{ fontSize:11, color:T.muted, marginTop:4 }}>или нажмите для выбора</div></>)}
                      <input type="file" accept=".csv" onChange={e=>readFile(e.target.files[0])} style={{ display:'none' }}/>
                    </label>
                  </div>
                  <div className="card" style={{ padding:20 }}>
                    <div className="sec-lbl">⚙️ Параметры TCO</div>
                    <Field label="Стоимость груза (USD)"><NumInput value={cargoValue} onChange={setCargoValue} min={1}/></Field>
                    <div style={{ marginTop:14 }}>
                      <button onClick={()=>setShowAdvanced(v=>!v)} style={{
                        fontSize:11, color:T.muted, background:'transparent', border:'none',
                        cursor:'pointer', padding:0, display:'flex', alignItems:'center', gap:6,
                      }}>
                        <span style={{ fontSize:10 }}>{showAdvanced ? '▾' : '▸'}</span>
                        Расширенные параметры
                      </button>
                      {showAdvanced && (
                        <div style={{ marginTop:12, padding:'12px 14px', borderRadius:8,
                          background:T.surf3, border:`1px solid ${T.border}` }}>
                          <Field label="Ставка капитала WACC (%)">
                            <NumInput value={capitalRate} onChange={setCapitalRate} min={0.1} step={0.5}/>
                          </Field>
                          <div style={{ fontSize:11, color:T.muted, marginTop:6, lineHeight:1.5 }}>
                            Стоимость капитала грузовладельца. Дефолт 15%.
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </>)}

                {/* Веса */}
                <div className="card" style={{ padding:20 }}>
                  <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:14 }}>
                    <div className="sec-lbl" style={{ marginBottom:0 }}>⚖️ Веса критериев</div>
                    <span style={{ fontFamily:"'JetBrains Mono', ui-monospace, monospace", fontSize:11, padding:'3px 9px', borderRadius:20, fontWeight:700, background:Math.abs(weightSum-1)<.05?'rgba(0,200,83,.15)':'rgba(245,158,11,.15)', color:Math.abs(weightSum-1)<.05?T.green:T.gold }}>Σ {weightSum.toFixed(2)}</span>
                  </div>
                  {[['cost','💰 Стоимость','#38bdf8'],['time','⏱ Время','#f59e0b'],['risk','⚠️ Риск','#f87171'],['emissions','🌿 Выбросы','#4ade80']].map(([k,lbl,color])=>(
                    <div key={k} style={{ marginBottom:12 }}>
                      <div style={{ display:'flex', justifyContent:'space-between', fontSize:12, marginBottom:5, color:T.text }}><span>{lbl}</span><span style={{ fontFamily:"'JetBrains Mono', ui-monospace, monospace", color, fontWeight:700 }}>{weights[k].toFixed(2)}</span></div>
                      <div style={{ height:5, background:T.surf3, borderRadius:4, overflow:'hidden', marginBottom:5 }}><div style={{ height:'100%', width:`${weights[k]*100}%`, background:color, borderRadius:4, transition:'width .2s' }}/></div>
                      <input type="range" min={0} max={1} step={0.05} value={weights[k]} style={{ accentColor:color }} onChange={e=>setWeights(p=>({...p,[k]:+e.target.value}))}/>
                    </div>
                  ))}
                </div>

                <button className="btn-main" onClick={inputMode==='simple'?handleSimpleAnalyze:handleCsvAnalyze}
                  disabled={loading||(inputMode==='simple'?!routes.length:!csvText)}>
                  {loading ? <><span className="spinning">⚙</span> ВЫЧИСЛЕНИЕ...</> : '🚀 АНАЛИЗИРОВАТЬ'}
                </button>

                {error && <div style={{ background:'rgba(255,82,82,.1)', border:'1px solid rgba(255,82,82,.25)', color:T.red, padding:'10px 14px', borderRadius:8, fontSize:13 }}>❌ {error}</div>}
              </div>

              <div>
                {!results ? (
                  <div className="card fade-up" style={{ padding:70, textAlign:'center', height:'100%', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
                    <div style={{ fontSize:60, opacity:.15, marginBottom:16 }}>📊</div>
                    <div style={{ color:T.muted, fontSize:15 }}>{inputMode==='simple' ? 'Заполните маршруты и параметры груза, нажмите «Анализировать»' : 'Загрузите CSV и нажмите «Анализировать»'}</div>
                    <div style={{ color:T.muted, fontSize:12, marginTop:8, opacity:.6 }}>Маршруты: ж/д · море</div>
                  </div>
                ) : <ResultsPanel results={results}/>}
              </div>
            </div>
          )}

          {tab==='history' && (
            <div className="card fade-up" style={{ overflow:'hidden' }}>
              <div style={{ padding:'14px 20px', borderBottom:`1px solid ${T.border}` }}>
                <div style={{ fontFamily:'Inter', fontSize:17, fontWeight:700, letterSpacing:2, color:T.text }}>🕐 История анализов</div>
              </div>
              {!history.length ? (
                <div style={{ padding:60, textAlign:'center', color:T.muted }}><div style={{ fontSize:44, marginBottom:12, opacity:.25 }}>📭</div>История пуста</div>
              ) : (
                <div style={{ overflowX:'auto' }}>
                  <table className="rtable">
                    <thead><tr>{['ID','Дата','Маршрутов','Груз (USD)','Ставка','Лучший','Действия'].map(h=><th key={h}>{h}</th>)}</tr></thead>
                    <tbody>
                      {history.map(a=>(
                        <tr key={a.id}>
                          <td style={{ fontFamily:"'JetBrains Mono', ui-monospace, monospace", color:T.green, fontWeight:700 }}>#{a.id}</td>
                          <td style={{ fontSize:12, color:T.muted }}>{a.created_at?.slice(0,16).replace('T',' ')}</td>
                          <td>{a.results?.length??0}</td>
                          <td style={{ fontFamily:"'JetBrains Mono', ui-monospace, monospace" }}>${a.cargo_value?.toLocaleString('ru')}</td>
                          <td>{a.capital_rate}%</td>
                          <td style={{ fontFamily:"'JetBrains Mono', ui-monospace, monospace", fontSize:12, color:T.green, fontWeight:700 }}>{a.results?.[0]?.route_id||'—'}</td>
                          <td style={{ display:'flex', gap:8 }}>
                            <button className="btn-sm" onClick={()=>window.open(`${API}/api/report/${a.id}/html`,'_blank')} style={{ background:'linear-gradient(135deg,#005a2b,#00a84f)', color:'white' }}>📥 Отчёт</button>
                            <button className="btn-sm" onClick={()=>deleteAnalysis(a.id)} style={{ background:'rgba(239,68,68,.12)', color:T.red, border:`1px solid rgba(239,68,68,.2)` }}>🗑 Удалить</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </main>

        <footer style={{ borderTop:`1px solid ${T.border}`, padding:'16px 24px', textAlign:'center', color:T.muted, fontSize:12 }}>
          UTLC ERA v2.0 · Multimodal Route Analysis
        </footer>

        {selectedRoute && <RouteMapModal route={selectedRoute} dark={dark} onClose={()=>setSelectedRoute(null)}/>}
      </div>
    </>
  )
}
