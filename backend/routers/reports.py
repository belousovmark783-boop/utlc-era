"""
HTML-отчёты: GET /api/report/{analysis_id}/html
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from db.database import get_analysis_by_id

router = APIRouter()


@router.get("/report/{analysis_id}/html")
def get_report(analysis_id: int):
    a = get_analysis_by_id(analysis_id)
    if not a:
        raise HTTPException(404, "Analysis not found")

    res = a["results"]
    w   = a.get("weights", {})

    # ── table rows ──
    table_rows = ""
    for i, r in enumerate(res, 1):
        score  = r.get("score", 0)
        sc     = "#00e676" if score >= .7 else "#ffab00" if score >= .4 else "#ff5252"
        sc_bg  = f"{sc}18"
        rk     = r.get("risk_index", 0)
        rc     = "#ff5252" if rk > .6 else "#ffab00" if rk > .3 else "#00e676"
        mode   = r.get("mode", "").lower()
        mb     = {"rail": "#1565c0", "sea": "#006979"}.get(mode, "#444")
        mi     = {"rail": "🚂", "sea": "🚢"}.get(mode, "📦")
        medal  = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"#{i}"
        row_bg = "background:rgba(0,230,118,.04);" if i == 1 else ""
        bd     = r.get("breakdown", {})
        bd_html = "".join(
            f'<span style="display:inline-block;margin:3px;padding:4px 9px;'
            f'background:#1a2235;border:1px solid rgba(255,255,255,.07);border-radius:8px;">'
            f'<span style="display:block;font-size:9px;color:#7a8699;text-transform:uppercase;'
            f'letter-spacing:1px;font-family:Barlow Condensed,sans-serif">{lbl}</span>'
            f'<span style="display:block;font-size:12px;font-family:IBM Plex Mono,monospace;'
            f'color:#38bdf8;font-weight:600">${bd.get(key, 0):,.0f}</span></span>'
            for lbl, key in [
                ("База", "base"), ("Таможня", "customs"), ("Обработка", "handling"),
                ("Углерод", "carbon"), ("Страховка", "insurance"),
                ("Обор.кап.", "working_cap"), ("Запасы", "inventory"),
                ("Администр.", "admin"), ("Резерв", "contingency"),
            ]
        )
        table_rows += f"""<tr style="{row_bg}">
          <td style="text-align:center;font-size:18px">{medal}</td>
          <td style="font-family:'IBM Plex Mono',monospace;font-weight:700;color:{'#00e676' if i==1 else '#e2e8f4'}">{r.get('route_id','')}</td>
          <td><span style="display:inline-flex;align-items:center;gap:5px;color:white;padding:3px 11px;
            border-radius:20px;font-size:11px;font-weight:700;letter-spacing:1px;background:{mb}">{mi} {mode.upper()}</span></td>
          <td style="font-size:13px">{r.get('origin','')} <span style="color:#00b355;margin:0 5px">→</span> {r.get('destination','')}</td>
          <td style="font-family:'IBM Plex Mono',monospace;font-weight:600">${r.get('cost_usd',0):,.0f}</td>
          <td style="font-family:'IBM Plex Mono',monospace">{r.get('time_days',0)}<span style="color:#7a8699;font-size:11px"> д</span></td>
          <td><span style="display:inline-block;padding:2px 8px;border-radius:6px;font-family:'IBM Plex Mono',monospace;
            font-size:12px;font-weight:600;color:{rc};background:{rc}18">{rk:.3f}</span></td>
          <td style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:#7a8699">{r.get('emissions',0):.2f}</td>
          <td><span style="display:inline-block;padding:4px 10px;border-radius:8px;font-family:'IBM Plex Mono',monospace;
            font-size:15px;font-weight:800;color:{sc};background:{sc_bg};{'box-shadow:0 0 14px '+sc+'55;' if i==1 else ''}">{score:.4f}</span></td>
          <td>{bd_html}</td>
        </tr>"""

    # ── weight bars ──
    wbars = ""
    for key, lbl, color in [
        ("cost",      "💰 Стоимость", "#38bdf8"),
        ("time",      "⏱ Время",      "#fbbf24"),
        ("risk",      "⚠️ Риск",       "#f87171"),
        ("emissions", "🌿 Выбросы",   "#4ade80"),
    ]:
        pct = int(w.get(key, 0) * 100)
        wbars += f"""<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
          <div style="font-size:12px;width:110px;flex-shrink:0">{lbl}</div>
          <div style="flex:1;height:6px;background:#1a2235;border-radius:4px;overflow:hidden">
            <div style="height:100%;width:{pct}%;background:{color};border-radius:4px"></div>
          </div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;font-weight:700;
            color:{color};width:34px;text-align:right">{w.get(key,0):.2f}</div>
        </div>"""

    # ── KPI values ──
    min_tco  = min((r["cost_usd"]  for r in res), default=0)
    min_days = min((r["time_days"] for r in res), default=0)
    min_co2  = min((r["emissions"] for r in res), default=0)
    best     = res[0] if res else {}

    # ── SVG animations ──
    train_svg = """<svg style="display:block;width:100%;height:58px" viewBox="0 0 1100 58" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .tr{animation:trmv 13s linear infinite}
      .pk{animation:pkup 1.3s ease-out infinite}
      .pk2{animation:pkup 1.3s ease-out .42s infinite}
      .ww{animation:wspin .7s linear infinite}
      @keyframes trmv{0%{transform:translateX(-360px)}100%{transform:translateX(1160px)}}
      @keyframes pkup{0%{opacity:.7;transform:translateY(0) scale(1)}100%{opacity:0;transform:translateY(-24px) scale(2)}}
      @keyframes wspin{to{transform:rotate(360deg)}}
    </style>
    <linearGradient id="lb" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#d4d4d4"/><stop offset="100%" stop-color="#888"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="1100" height="58" fill="#0b0f1a"/>
  <rect x="0" y="42" width="1100" height="6" fill="#1a2235"/>
  <rect x="0" y="38" width="1100" height="2.5" fill="#7a6040"/>
  <rect x="0" y="43" width="1100" height="2.5" fill="#7a6040"/>
  <g class="tr">
    <rect x="195" y="20" width="95" height="18" rx="3" fill="url(#lb)"/>
    <rect x="252" y="15" width="40" height="18" rx="2" fill="url(#lb)"/>
    <rect x="195" y="27" width="97" height="4" fill="#00b355"/>
    <path d="M292,17 L310,20 L310,36 L292,37Z" fill="#aaa"/>
    <rect x="292" y="26" width="18" height="4" fill="#00b355"/>
    <circle cx="308" cy="27" r="3.5" fill="#ffe566"/>
    <rect x="212" y="12" width="8" height="9" rx="1" fill="#666"/>
    <rect x="209" y="10" width="14" height="4" rx="2" fill="#777"/>
    <ellipse class="pk"  cx="215" cy="6"  rx="6" ry="3.5" fill="#ccc" opacity=".7"/>
    <ellipse class="pk2" cx="221" cy="2"  rx="5" ry="3"   fill="#aaa" opacity=".5"/>
    <rect x="264" y="17" width="13" height="8" rx="2" fill="#9dd8f0" opacity=".9"/>
    <rect x="280" y="17" width="10" height="8" rx="2" fill="#9dd8f0" opacity=".9"/>
    <g class="ww" style="transform-origin:214px 38px"><circle cx="214" cy="38" r="7" fill="#444" stroke="#222" stroke-width="1.5"/><circle cx="214" cy="38" r="2.5" fill="#888"/><line x1="214" y1="31" x2="214" y2="45" stroke="#666" stroke-width="1.5"/><line x1="207" y1="38" x2="221" y2="38" stroke="#666" stroke-width="1.5"/></g>
    <g class="ww" style="transform-origin:241px 38px"><circle cx="241" cy="38" r="7" fill="#444" stroke="#222" stroke-width="1.5"/><circle cx="241" cy="38" r="2.5" fill="#888"/><line x1="241" y1="31" x2="241" y2="45" stroke="#666" stroke-width="1.5"/><line x1="234" y1="38" x2="248" y2="38" stroke="#666" stroke-width="1.5"/></g>
    <g class="ww" style="transform-origin:269px 38px"><circle cx="269" cy="38" r="7" fill="#444" stroke="#222" stroke-width="1.5"/><circle cx="269" cy="38" r="2.5" fill="#888"/><line x1="269" y1="31" x2="269" y2="45" stroke="#666" stroke-width="1.5"/><line x1="262" y1="38" x2="276" y2="38" stroke="#666" stroke-width="1.5"/></g>
    <rect x="60" y="18" width="125" height="20" rx="2" fill="url(#lb)"/>
    <rect x="60" y="26" width="125" height="4" fill="#00b355"/>
    <rect x="68" y="16" width="109" height="14" rx="2" fill="#b0b0b0"/>
    <text x="122" y="26" text-anchor="middle" font-size="7" fill="#005a2b" font-weight="bold" font-family="monospace" letter-spacing="1">UTLC ERA</text>
    <g class="ww" style="transform-origin:75px 38px"><circle cx="75" cy="38" r="7" fill="#444" stroke="#222" stroke-width="1.5"/><circle cx="75" cy="38" r="2.5" fill="#888"/><line x1="75" y1="31" x2="75" y2="45" stroke="#666" stroke-width="1.5"/><line x1="68" y1="38" x2="82" y2="38" stroke="#666" stroke-width="1.5"/></g>
    <g class="ww" style="transform-origin:106px 38px"><circle cx="106" cy="38" r="7" fill="#444" stroke="#222" stroke-width="1.5"/><circle cx="106" cy="38" r="2.5" fill="#888"/><line x1="106" y1="31" x2="106" y2="45" stroke="#666" stroke-width="1.5"/><line x1="99" y1="38" x2="113" y2="38" stroke="#666" stroke-width="1.5"/></g>
    <g class="ww" style="transform-origin:158px 38px"><circle cx="158" cy="38" r="7" fill="#444" stroke="#222" stroke-width="1.5"/><circle cx="158" cy="38" r="2.5" fill="#888"/><line x1="158" y1="31" x2="158" y2="45" stroke="#666" stroke-width="1.5"/><line x1="151" y1="38" x2="165" y2="38" stroke="#666" stroke-width="1.5"/></g>
  </g>
</svg>"""

    ship_svg = """<svg style="display:block;width:100%;height:58px" viewBox="0 0 1100 58" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .sh{animation:shmv 18s linear infinite}
      .sp{animation:spup 1.5s ease-out infinite}
      .sp2{animation:spup 1.5s ease-out .5s infinite}
      .bw{animation:bwav 2.8s ease-in-out infinite}
      .wd{animation:wvdr 5s linear infinite}
      @keyframes shmv{0%{transform:translateX(1160px)}100%{transform:translateX(-420px)}}
      @keyframes spup{0%{opacity:.65;transform:translateY(0) scale(1)}100%{opacity:0;transform:translateY(-24px) scale(2)}}
      @keyframes bwav{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
      @keyframes wvdr{0%{transform:translateX(0)}100%{transform:translateX(-120px)}}
    </style>
    <linearGradient id="hl" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1b3f5e"/><stop offset="100%" stop-color="#0b1e2e"/>
    </linearGradient>
    <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#f0ead8"/><stop offset="100%" stop-color="#c4af85"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="1100" height="58" fill="#061520"/>
  <g class="wd"><path d="M0,30 Q55,24 110,30 T220,30 T330,30 T440,30 T550,30 T660,30 T770,30 T880,30 T990,30 T1100,30 T1210,30" fill="none" stroke="#4fc3f7" stroke-width="1.4" opacity=".45"/></g>
  <g class="wd" style="animation-delay:.8s"><path d="M0,38 Q55,32 110,38 T220,38 T330,38 T440,38 T550,38 T660,38 T770,38 T880,38 T990,38 T1100,38 T1210,38" fill="none" stroke="#29a0d8" stroke-width="1" opacity=".3"/></g>
  <g class="sh">
    <g class="bw">
      <path d="M10,40 L210,40 L218,54 L2,54Z" fill="url(#hl)"/>
      <path d="M6,49 L212,49 L218,54 L2,54Z" fill="#0b1e2e"/>
      <rect x="2" y="51" width="216" height="2.5" fill="#c0392b"/>
      <rect x="30" y="26" width="136" height="15" rx="3" fill="url(#sg)"/>
      <rect x="50" y="18" width="92" height="10" rx="2" fill="#d4c08a"/>
      <rect x="65" y="12" width="62" height="8" rx="2" fill="#c8b070"/>
      <rect x="90" y="4" width="18" height="10" rx="2" fill="#1e2d40"/>
      <rect x="87" y="2" width="24" height="4" rx="2" fill="#253545"/>
      <rect x="87" y="4" width="24" height="3" fill="#c0392b"/>
      <ellipse class="sp"  cx="99" cy="-1" rx="7"  ry="4.5" fill="#bbb" opacity=".65"/>
      <ellipse class="sp2" cx="105" cy="-5" rx="5" ry="3.5" fill="#999" opacity=".45"/>
      <line x1="99" y1="-2" x2="99" y2="12" stroke="#888" stroke-width="2"/>
      <path d="M99,0 L114,3 L99,8Z" fill="#00b355"/>
      <rect x="54" y="20" width="10" height="6" rx="1" fill="#9dd8f0" opacity=".85"/>
      <rect x="68" y="20" width="10" height="6" rx="1" fill="#9dd8f0" opacity=".85"/>
      <rect x="82" y="20" width="10" height="6" rx="1" fill="#9dd8f0" opacity=".85"/>
      <rect x="96" y="20" width="10" height="6" rx="1" fill="#9dd8f0" opacity=".85"/>
      <rect x="110" y="20" width="10" height="6" rx="1" fill="#9dd8f0" opacity=".85"/>
      <rect x="124" y="20" width="10" height="6" rx="1" fill="#9dd8f0" opacity=".85"/>
      <rect x="36" y="29" width="10" height="7" rx="1" fill="#9dd8f0" opacity=".8"/>
      <rect x="54" y="29" width="10" height="7" rx="1" fill="#9dd8f0" opacity=".8"/>
      <rect x="72" y="29" width="10" height="7" rx="1" fill="#9dd8f0" opacity=".8"/>
      <rect x="90" y="29" width="10" height="7" rx="1" fill="#9dd8f0" opacity=".8"/>
      <rect x="108" y="29" width="10" height="7" rx="1" fill="#9dd8f0" opacity=".8"/>
      <rect x="126" y="29" width="10" height="7" rx="1" fill="#9dd8f0" opacity=".8"/>
      <rect x="144" y="29" width="10" height="7" rx="1" fill="#9dd8f0" opacity=".8"/>
      <text x="12" y="52" font-size="11" fill="#4a8fc4">⚓</text>
      <path d="M213,49 Q230,43 248,49 Q264,43 280,49" fill="none" stroke="#4fc3f7" stroke-width="1.8" opacity=".6"/>
    </g>
  </g>
</svg>"""

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>UTLC ERA — Отчёт #{a['id']}</title>
  <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;600&family=Barlow:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root{{
      --bg:#0b0f1a;--surf:#111827;--surf2:#1a2235;--surf3:#1f2d42;
      --border:rgba(255,255,255,.07);--green:#00e676;--gm:#00b355;
      --text:#e2e8f4;--muted:#7a8699;--accent:#38bdf8;--gold:#fbbf24;
    }}
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:var(--bg);color:var(--text);font-family:'Barlow',sans-serif;padding-bottom:60px}}
    ::-webkit-scrollbar{{width:5px}}::-webkit-scrollbar-track{{background:var(--bg)}}
    ::-webkit-scrollbar-thumb{{background:#005a2b;border-radius:4px}}
    .header{{background:linear-gradient(180deg,#07101f,#0b0f1a);border-bottom:1px solid rgba(0,230,118,.12);overflow:hidden}}
    .hrow{{display:flex;align-items:center;gap:18px;padding:18px 36px 10px}}
    .logo-box{{width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,#005a2b,#00e676);
      display:flex;align-items:center;justify-content:center;font-size:28px;flex-shrink:0;
      box-shadow:0 4px 24px rgba(0,230,118,.3)}}
    .logo-title{{font-family:'Barlow Condensed';font-size:30px;font-weight:800;letter-spacing:5px;color:#fff;line-height:1}}
    .logo-sub{{font-family:'Barlow Condensed';font-size:12px;color:var(--muted);letter-spacing:3px;text-transform:uppercase;margin-top:2px}}
    .report-id{{font-family:'Barlow Condensed';font-size:36px;font-weight:800;color:var(--green);line-height:1}}
    .report-id-lbl{{font-family:'IBM Plex Mono';font-size:11px;color:var(--muted);letter-spacing:1px}}
    .meta-bar{{background:var(--surf);border-bottom:1px solid var(--border);
      padding:14px 36px;display:flex;gap:36px;align-items:center;flex-wrap:wrap}}
    .m-item{{display:flex;flex-direction:column;gap:3px}}
    .m-lbl{{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:2px;font-family:'Barlow Condensed'}}
    .m-val{{font-size:18px;font-weight:800;font-family:'IBM Plex Mono'}}
    .section{{padding:24px 36px 0}}
    .sec-title{{font-family:'Barlow Condensed';font-size:12px;font-weight:700;letter-spacing:3px;
      text-transform:uppercase;color:var(--muted);margin-bottom:14px}}
    .kpi-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;padding:24px 36px 0}}
    .kpi{{background:var(--surf);border:1px solid var(--border);border-radius:14px;padding:18px 20px}}
    .kpi-lbl{{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:1.5px;
      font-family:'Barlow Condensed';margin-bottom:5px}}
    .kpi-val{{font-family:'Barlow Condensed';font-size:28px;font-weight:800}}
    .kpi-sub{{font-size:11px;color:var(--muted);margin-top:3px}}
    .table-wrap{{background:var(--surf);border:1px solid var(--border);border-radius:14px;overflow:hidden}}
    table{{width:100%;border-collapse:collapse;font-size:13px}}
    th{{background:var(--surf2);padding:10px 14px;text-align:left;color:var(--muted);font-size:10px;
      font-family:'Barlow Condensed';letter-spacing:2px;text-transform:uppercase;font-weight:700}}
    td{{padding:11px 14px;border-top:1px solid var(--border);vertical-align:middle}}
    tr:hover td{{background:rgba(255,255,255,.02)}}
    .two-col{{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:20px 36px 0}}
    .card{{background:var(--surf);border:1px solid var(--border);border-radius:14px;padding:20px}}
    .bm-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:14px}}
    .bm{{background:var(--surf2);border-radius:10px;padding:10px 12px}}
    .bm-lbl{{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-family:'Barlow Condensed'}}
    .bm-val{{font-family:'IBM Plex Mono';font-size:18px;font-weight:800;margin-top:3px}}
    footer{{margin-top:40px;padding:14px 36px;border-top:1px solid var(--border);
      text-align:center;color:var(--muted);font-family:'IBM Plex Mono';font-size:11px;letter-spacing:1.5px}}
    @media print{{
      body{{background:white;color:#111}}
      :root{{--bg:white;--surf:#f9f9f9;--surf2:#f0f0f0;--surf3:#e8e8e8;--border:#ddd;--text:#111;--muted:#555}}
    }}
  </style>
</head>
<body>

<div class="header">
  <div class="hrow">
    <div class="logo-box">🌐</div>
    <div>
      <div class="logo-title">UTLC ERA</div>
      <div class="logo-sub">Отчёт об анализе логистических маршрутов</div>
    </div>
    <div style="margin-left:auto;text-align:right">
      <div class="report-id-lbl">Отчёт #</div>
      <div class="report-id">{a['id']}</div>
    </div>
  </div>
  {train_svg}
  {ship_svg}
</div>

<div class="meta-bar">
  <div class="m-item"><div class="m-lbl">Дата</div><div class="m-val">{a['created_at'][:10]}</div></div>
  <div class="m-item"><div class="m-lbl">Стоимость груза</div><div class="m-val" style="color:var(--green)">${a['cargo_value']:,.0f}</div></div>
  <div class="m-item"><div class="m-lbl">Ставка WACC</div><div class="m-val">{a['capital_rate']}%</div></div>
  <div class="m-item"><div class="m-lbl">Маршрутов</div><div class="m-val" style="color:var(--accent)">{len(res)}</div></div>
  <div class="m-item"><div class="m-lbl">Статус</div><div class="m-val" style="color:#00e676;font-size:14px">✓ ЗАВЕРШЁН</div></div>
</div>

<div class="kpi-grid">
  <div class="kpi" style="border-left:3px solid #00e676">
    <div class="kpi-lbl">🏆 Лучший маршрут</div>
    <div class="kpi-val" style="color:#00e676">{best.get('route_id','—')}</div>
    <div class="kpi-sub">{best.get('mode','').upper()} · {best.get('origin','')} → {best.get('destination','')}</div>
  </div>
  <div class="kpi" style="border-left:3px solid var(--accent)">
    <div class="kpi-lbl">💰 Минимальный TCO</div>
    <div class="kpi-val" style="color:var(--accent)">${min_tco:,.0f}</div>
    <div class="kpi-sub">Полная стоимость владения</div>
  </div>
  <div class="kpi" style="border-left:3px solid var(--gold)">
    <div class="kpi-lbl">⏱ Мин. транзит</div>
    <div class="kpi-val" style="color:var(--gold)">{min_days} дней</div>
    <div class="kpi-sub">Самый быстрый маршрут</div>
  </div>
  <div class="kpi" style="border-left:3px solid #4ade80">
    <div class="kpi-lbl">🌿 Мин. выбросы CO₂</div>
    <div class="kpi-val" style="color:#4ade80">{min_co2:.2f} т</div>
    <div class="kpi-sub">Экологически чистый</div>
  </div>
</div>

<div class="section" style="margin-top:24px">
  <div class="sec-title">📊 Сравнение маршрутов</div>
  <div class="table-wrap" style="overflow-x:auto">
    <table>
      <thead><tr>
        <th>#</th><th>ID маршрута</th><th>Тип</th><th>Откуда → Куда</th>
        <th>TCO (USD)</th><th>Дни</th><th>Риск</th><th>CO₂ (т)</th>
        <th>Балл</th><th>Разбивка затрат</th>
      </tr></thead>
      <tbody>{table_rows}</tbody>
    </table>
  </div>
</div>

<div class="two-col">
  <div class="card">
    <div class="sec-title">⚖️ Веса критериев</div>
    {wbars}
  </div>
  <div class="card">
    <div class="sec-title">🥇 Лучший маршрут — детали</div>
    <div style="font-family:'IBM Plex Mono';font-size:20px;font-weight:800;color:var(--green)">{best.get('route_id','—')}</div>
    <div style="font-size:12px;color:var(--muted);margin-bottom:14px">{best.get('origin','')} → {best.get('destination','')}</div>
    <div class="bm-grid">
      <div class="bm"><div class="bm-lbl">TCO</div><div class="bm-val" style="color:var(--accent)">${best.get('cost_usd',0):,.0f}</div></div>
      <div class="bm"><div class="bm-lbl">Дни</div><div class="bm-val" style="color:var(--gold)">{best.get('time_days',0)}</div></div>
      <div class="bm"><div class="bm-lbl">Балл</div><div class="bm-val" style="color:var(--green)">{best.get('score',0):.4f}</div></div>
      <div class="bm"><div class="bm-lbl">Риск</div><div class="bm-val" style="color:#f87171">{best.get('risk_index',0):.3f}</div></div>
      <div class="bm"><div class="bm-lbl">CO₂</div><div class="bm-val" style="color:#4ade80">{best.get('emissions',0):.2f}</div></div>
      <div class="bm"><div class="bm-lbl">Тип</div><div class="bm-val" style="color:var(--accent)">{best.get('mode','').upper()}</div></div>
    </div>
  </div>
</div>

<footer>UTLC ERA v2.0 · DECISION SUPPORT SYSTEM · MULTIMODAL ROUTE OPTIMIZATION · {a['created_at'][:16].replace('T',' ')}</footer>
</body>
</html>"""
    return HTMLResponse(html)
