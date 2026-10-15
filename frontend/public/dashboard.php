<?php

declare(strict_types=1);

date_default_timezone_set('Asia/Bangkok');
header('Content-Type: text/html; charset=utf-8');
header('Cache-Control: no-store');

?>
<!doctype html>
<html lang="th">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#10231d">
    <title>Smart Farm Pro | Dashboard</title>
    <style>
        :root {
            color-scheme: light;
            --bg: #f5f7f4;
            --panel: #ffffff;
            --panel-soft: #ffffff;
            --border: #e5ebe5;
            --text: #25352c;
            --muted: #7b877e;
            --green: #367d55;
            --amber: #a87420;
            --red: #bd5555;
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            background: var(--bg);
            color: var(--text);
            font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
            min-height: 100vh;
        }

        .shell { width: min(1120px, 100% - 40px); margin: auto; }

        .sidebar {
            position: fixed;
            inset: 0 auto 0 0;
            width: 218px;
            padding: 22px 14px;
            background: #fff;
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            gap: 24px;
            z-index: 5;
            overflow-y: auto;
        }

        .sidebar-brand { display: flex; align-items: center; gap: 9px; padding: 0 4px 18px; border-bottom: 1px solid var(--border); }
        .sidebar-brand img { width: 39px; height: 39px; object-fit: contain; }
        .sidebar-brand strong { display: block; font-size: 14px; }
        .sidebar-brand small { color: var(--muted); font-size: 9px; letter-spacing: .08em; }
        .nav-label { margin: 0 8px 8px; color: #9aa39c; font-size: 10px; font-weight: 750; letter-spacing: .12em; }
        .nav-link { display: flex; align-items: center; gap: 10px; padding: 10px 11px; margin: 3px 0; border-radius: 9px; color: #66736a; font-size: 13px; font-weight: 600; }
        .nav-link.active { color: #285d40; background: #e8f2eb; }
        .nav-icon { width: 18px; text-align: center; }
        .sidebar-note { margin-top: auto; padding: 13px; border: 1px solid var(--border); border-radius: 12px; color: var(--muted); font-size: 11px; line-height: 1.6; }
        .workspace { margin-left: 218px; min-width: 0; }
        header { padding: 14px 0; background: #fff; border-bottom: 1px solid var(--border); }
        header .shell { width: calc(100% - 40px); }
        header .eyebrow { color: var(--muted); letter-spacing: .08em; }
        header h1 { font-size: 18px; margin-top: 2px; }

        .topline, .section-heading, .sensor-heading, .metric-line {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .brand-mark {
            display: flex;
            flex: 0 0 56px;
            align-items: center;
            justify-content: center;
            width: 56px;
            height: 56px;
            border-radius: 10px;
            overflow: hidden;
            background: #fff;
        }
        .brand-mark img {
            display: block;
            width: 100%;
            height: 100%;
            object-fit: contain;
            background: #fff;
        }
        .status-detail {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            color: var(--muted);
            font-size: 12px;
        }
        .status-detail.warn { color: #9a6700; }
        .status-detail.ok { color: var(--green); }
        .status-detail.error { color: var(--red); }

        .eyebrow {
            color: var(--green);
            font-size: 11px;
            font-weight: 750;
            letter-spacing: .1em;
            text-transform: uppercase;
        }

        h1 { font-size: clamp(23px, 4vw, 34px); margin: 5px 0 0; }
        h2 { font-size: 20px; margin: 0; }
        h3 { font-size: 16px; margin: 0; }
        p { line-height: 1.6; }
        .muted { color: var(--muted); }
        .small { font-size: 13px; }

        button {
            border: 1px solid #dce6dd;
            border-radius: 9px;
            background: #fff;
            color: var(--text);
            padding: 9px 13px;
            font: inherit;
            font-size: 12px;
            font-weight: 650;
            cursor: pointer;
        }

        button:hover { background: #f0f5f0; }
        button:disabled { opacity: .6; cursor: wait; }
        button:focus-visible { outline: 2px solid var(--green); outline-offset: 3px; }

        main { padding: 28px 0 44px; }
        .intro { margin-bottom: 22px; }
        .intro h2 { font-size: clamp(23px, 3vw, 30px); letter-spacing: -.04em; }
        .intro p { margin: 7px 0 0; font-size: 13px; }
        .statusbar { background: #fff; border-color: var(--border); font-size: 12px; }
        .section-heading h2 { font-size: 17px; }
        .grid { grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
        .panel { border-radius: 12px; background: #fff; padding: 17px; box-shadow: 0 2px 8px #25352c05; }
        .metric-value { font-size: clamp(27px, 3vw, 36px); margin: 15px 0 4px; }
        .metric-label { font-size: 12px; }
        .metric-note { font-size: 11px; }
        .sensor-card { background: #fff; border-color: var(--border); border-radius: 12px; }
        .sensor-metric { background: #f5f8f5; }
        .zone-group { margin: 18px 0 24px; }
        .zone-heading { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 10px; }
        .zone-heading h3 { font-size: 15px; }
        .zone-sensors { display: grid; gap: 12px; }
        .zone-caption { color: var(--muted); font-size: 11px; }
        footer { margin-left: 0; padding: 18px 0 26px; border-top: 1px solid var(--border); background: #fff; }
        .workspace footer .shell { width: calc(100% - 40px); }

        .statusbar {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
            padding: 13px 16px;
            border: 1px solid var(--border);
            border-radius: 14px;
            background: #fff;
            margin: 20px 0 28px;
        }

        .dot {
            display: inline-block;
            width: 9px;
            height: 9px;
            border-radius: 50%;
            background: var(--muted);
            flex: 0 0 auto;
        }

        .dot.ok { background: var(--green); }
        .dot.warn { background: var(--amber); }
        .dot.error { background: var(--red); }

        .section-heading { margin-bottom: 14px; }
        .grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 16px;
        }

        .panel {
            border: 1px solid var(--border);
            border-radius: 18px;
            background: linear-gradient(145deg, var(--panel-soft), var(--panel));
            padding: 20px;
            min-width: 0;
        }

        .metric-label { color: var(--muted); font-size: 14px; }
        .metric-value {
            font-size: clamp(30px, 5vw, 43px);
            font-weight: 750;
            letter-spacing: -.04em;
            margin: 20px 0 4px;
            overflow-wrap: anywhere;
        }

        .unit { font-size: 17px; font-weight: 550; color: var(--muted); }
        .metric-note { font-size: 13px; color: var(--muted); }
        .sensor-list { display: grid; gap: 14px; margin-top: 16px; }

        .sensor-card {
            border: 1px solid var(--border);
            border-radius: 16px;
            background: #fff;
            padding: 18px;
        }

        .sensor-meta { color: var(--muted); font-size: 13px; margin-top: 5px; }
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            border-radius: 999px;
            border: 1px solid var(--border);
            padding: 6px 10px;
            font-size: 12px;
            white-space: nowrap;
        }

        .badge.ok { color: var(--green); }
        .badge.warn { color: var(--amber); }
        .badge.error { color: var(--red); }

        .sensor-metrics {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
            margin-top: 18px;
        }

        .sensor-metric {
            border-radius: 12px;
            background: #f5f8f5;
            padding: 13px;
            min-width: 0;
        }

        .sensor-metric .value {
            font-size: 22px;
            font-weight: 720;
            margin-top: 7px;
            overflow-wrap: anywhere;
        }

        .sensor-metric .label { color: var(--muted); font-size: 12px; }
        .empty { text-align: center; padding: 36px 20px; }
        .error-text { color: var(--red); }
        footer { padding: 20px 0 30px; border-top: 1px solid var(--border); }

        @media (max-width: 900px) {
            .sidebar { width: 70px; padding: 18px 8px; }
            .sidebar-brand { justify-content: center; padding: 0 0 16px; }
            .sidebar-brand img { width: 42px; }
            .sidebar-brand div, .nav-label, .nav-text, .sidebar-note { display: none; }
            .nav-link { justify-content: center; padding: 11px 4px; }
            .workspace { margin-left: 70px; }
            .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }

        @media (max-width: 560px) {
            .sidebar { width: 54px; padding: 12px 5px; }
            .sidebar-brand img { width: 36px; }
            .workspace { margin-left: 54px; }
            .shell, header .shell, .workspace footer .shell { width: calc(100% - 24px); }
            main { padding-top: 22px; }
            .grid { grid-template-columns: 1fr 1fr; gap: 8px; }
            .panel { padding: 12px; }
            .metric-value { font-size: 25px; }
            .topline { align-items: center; }
            .brand { gap: 7px; }
            .brand-mark {
                flex-basis: 42px;
                width: 42px;
                height: 42px;
            }
            .brand-mark img { width: 100%; height: 100%; }
            .statusbar { flex-wrap: wrap; }
            .status-detail { width: 100%; margin-left: 24px; }
            .topline button { padding: 8px; font-size: 11px; }
            .sensor-heading { align-items: flex-start; flex-direction: column; }
            .sensor-metrics { grid-template-columns: 1fr 1fr; gap: 8px; }
        }
    </style>
</head>
<body>
<aside class="sidebar" aria-label="เมนูหลัก">
    <div class="sidebar-brand">
        <img src="/assets/smart-farm-pro-logo.png" alt="Smart Farm Pro">
        <div><strong>Smart Farm Pro</strong><small>PRO · FARM INTELLIGENCE</small></div>
    </div>
    <nav aria-label="Workspace">
        <p class="nav-label">WORKSPACE</p>
        <div class="nav-link active"><span class="nav-icon">▦</span><span class="nav-text">Overview</span></div>
        <div class="nav-link"><span class="nav-icon">⌂</span><span class="nav-text">Farms &amp; Zones</span></div>
        <div class="nav-link"><span class="nav-icon">◉</span><span class="nav-text">Sensors</span></div>
        <div class="nav-link"><span class="nav-icon">◌</span><span class="nav-text">Actuators</span></div>
        <div class="nav-link"><span class="nav-icon">⟳</span><span class="nav-text">Automation</span></div>
        <div class="nav-link"><span class="nav-icon">♧</span><span class="nav-text">Alerts</span></div>
    </nav>
    <nav aria-label="System">
        <p class="nav-label">SYSTEM</p>
        <div class="nav-link"><span class="nav-icon">⌘</span><span class="nav-text">Gateway &amp; System</span></div>
        <div class="nav-link"><span class="nav-icon">⚙</span><span class="nav-text">Settings</span></div>
    </nav>
    <div class="sidebar-note"><strong>Farm monitoring</strong><br>ติดตามข้อมูลจากเซนเซอร์ที่เชื่อมต่อกับระบบ</div>
</aside>
<div class="workspace">
<header>
    <div class="shell topline">
        <div class="brand">
            <div class="brand-mark"><img src="/assets/smart-farm-pro-logo.png" alt=""></div>
            <div>
                <div class="eyebrow">IoT · Monitoring Platform</div>
                <h1>Smart Farm Pro</h1>
            </div>
        </div>
        <button id="refreshButton" type="button">↻ รีเฟรชข้อมูล</button>
    </div>
</header>

<main class="shell">
    <section class="intro">
        <div class="eyebrow">Farm overview</div>
        <h2>ภาพรวมฟาร์ม</h2>
        <p class="muted">ติดตามข้อมูลจากเซนเซอร์และเวลาที่บันทึกค่าล่าสุด</p>
    </section>

    <div class="statusbar" role="status" aria-live="polite">
        <span id="connectionDot" class="dot"></span>
        <strong id="connectionText">กำลังเชื่อมต่อ API…</strong>
        <span id="lastUpdated" class="muted small"></span>
        <span id="sensorDataStatus" class="status-detail" aria-live="polite">
            รอการตรวจสอบข้อมูลเซนเซอร์
        </span>
    </div>

    <section aria-labelledby="summaryTitle">
        <div class="section-heading">
            <h2 id="summaryTitle">สรุปสถานะ</h2>
            <span class="muted small" id="sensorCount">กำลังโหลด…</span>
        </div>

        <div class="grid">
            <article class="panel">
                <div class="metric-label">อุณหภูมิล่าสุด</div>
                <div class="metric-value" id="temperatureValue">— <span class="unit">°C</span></div>
                <div class="metric-note" id="temperatureNote">รอข้อมูลจากเซนเซอร์</div>
            </article>

            <article class="panel">
                <div class="metric-label">ความชื้นล่าสุด</div>
                <div class="metric-value" id="humidityValue">— <span class="unit">%</span></div>
                <div class="metric-note" id="humidityNote">รอข้อมูลจากเซนเซอร์</div>
            </article>

            <article class="panel">
                <div class="metric-label">สถานะเซนเซอร์</div>
                <div class="metric-value" id="activeValue">—</div>
                <div class="metric-note" id="activeNote">รอข้อมูลจากเซนเซอร์</div>
            </article>
            <article class="panel">
                <div class="metric-label">โซนที่ตรวจพบ</div>
                <div class="metric-value" id="zoneCount">—</div>
                <div class="metric-note">อ้างอิงจาก zone_id ในระบบ</div>
            </article>
        </div>
    </section>

    <section style="margin-top: 30px" aria-labelledby="sensorsTitle">
        <div class="section-heading">
            <h2 id="sensorsTitle">รายการเซนเซอร์</h2>
            <span class="muted small">อัปเดตอัตโนมัติทุก 30 วินาที</span>
        </div>
        <div id="sensorList" class="sensor-list">
            <div class="panel empty muted">กำลังโหลดข้อมูลเซนเซอร์…</div>
        </div>
    </section>
</main>

<footer>
    <div class="shell muted small">
        Smart Farm Pro · Monitoring only · ข้อมูลแสดงตามเวลาที่ API บันทึกไว้
    </div>
</footer>
</div>

<script>
(() => {
    'use strict';

    const API_URL = '/api/sensors.php';
    const REFRESH_MS = 30000;
    const STALE_AFTER_MS = 5 * 60 * 1000;

    const el = (id) => document.getElementById(id);

    function escapeHtml(value) {
        return String(value ?? '').replace(/[&<>"']/g, (char) => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        })[char]);
    }

    function numberOrDash(value, digits = 1) {
        if (value === null || value === undefined || value === '') return '—';
        const number = Number(value);
        return Number.isFinite(number) ? number.toFixed(digits) : '—';
    }

    function parseTimestamp(value) {
        if (!value) return null;
        const normalized = String(value).replace(' ', 'T');
        const timestamp = Date.parse(normalized);
        return Number.isFinite(timestamp) ? timestamp : null;
    }

    function formatTimestamp(value) {
        const timestamp = parseTimestamp(value);
        if (timestamp === null) return 'ไม่ทราบเวลาบันทึก';
        return new Intl.DateTimeFormat('th-TH', {
            dateStyle: 'medium',
            timeStyle: 'medium',
            timeZone: 'Asia/Bangkok'
        }).format(timestamp);
    }

    function dataFreshness(sensor) {
        const timestamp = parseTimestamp(sensor.recorded_at);
        if (timestamp === null) {
            return { label: 'ไม่มีเวลาบันทึก', kind: 'warn' };
        }

        const age = Date.now() - timestamp;
        if (age < -60000) {
            return { label: 'เวลาในข้อมูลผิดปกติ', kind: 'warn' };
        }
        if (age > STALE_AFTER_MS) {
            return { label: 'ข้อมูลเก่า', kind: 'warn' };
        }
        return { label: 'ข้อมูลล่าสุด', kind: 'ok' };
    }

    function setConnection(message, kind) {
        el('connectionText').textContent = message;
        el('connectionDot').className = 'dot ' + kind;
    }

    function renderSensors(sensors) {
        const active = sensors.filter((sensor) => sensor.is_active === true);
        const withTemperature = sensors.find((sensor) =>
            sensor.temperature_c !== null && sensor.temperature_c !== undefined
        );
        const withHumidity = sensors.find((sensor) =>
            sensor.humidity_pct !== null && sensor.humidity_pct !== undefined
        );

        el('sensorCount').textContent = `${sensors.length} เซนเซอร์`;
        const zoneIds = [...new Set(sensors
            .map((sensor) => sensor.zone_id)
            .filter((zoneId) => zoneId !== null && zoneId !== undefined && zoneId !== '')
            .map(String))];
        el('zoneCount').textContent = String(zoneIds.length);
        el('activeValue').textContent = `${active.length}/${sensors.length}`;
        el('activeNote').textContent = 'เซนเซอร์ที่เปิดใช้งาน / ทั้งหมด';
        el('temperatureValue').innerHTML =
            `${escapeHtml(withTemperature ? numberOrDash(withTemperature.temperature_c) : '—')} <span class="unit">°C</span>`;
        el('temperatureNote').textContent = withTemperature
            ? `${withTemperature.name || withTemperature.sensor_code} · ${formatTimestamp(withTemperature.recorded_at)}`
            : 'ไม่มีข้อมูลอุณหภูมิ';
        el('humidityValue').innerHTML =
            `${escapeHtml(withHumidity ? numberOrDash(withHumidity.humidity_pct) : '—')} <span class="unit">%</span>`;
        el('humidityNote').textContent = withHumidity
            ? `${withHumidity.name || withHumidity.sensor_code} · ${formatTimestamp(withHumidity.recorded_at)}`
            : 'ไม่มีข้อมูลความชื้น';

        if (sensors.length === 0) {
            el('sensorList').innerHTML =
                '<div class="panel empty muted">ยังไม่มีรายการเซนเซอร์</div>';
            return;
        }

        const groups = new Map();
        sensors.forEach((sensor) => {
            const key = sensor.zone_id === null || sensor.zone_id === undefined || sensor.zone_id === ''
                ? '__unassigned__'
                : String(sensor.zone_id);
            if (!groups.has(key)) groups.set(key, []);
            groups.get(key).push(sensor);
        });

        const sortedGroups = [...groups.entries()].sort(([a], [b]) => {
            if (a === '__unassigned__') return 1;
            if (b === '__unassigned__') return -1;
            return a.localeCompare(b, undefined, { numeric: true });
        });

        const renderCard = (sensor) => {
            const freshness = dataFreshness(sensor);
            const isActive = sensor.is_active === true;
            const state = isActive
                ? { label: 'เปิดใช้งาน', kind: 'ok' }
                : { label: 'ปิดใช้งาน', kind: 'error' };

            return `
                <article class="sensor-card">
                    <div class="sensor-heading">
                        <div>
                            <h3>${escapeHtml(sensor.name || sensor.sensor_code || `Sensor ${sensor.id}`)}</h3>
                            <div class="sensor-meta">
                                ${escapeHtml(sensor.sensor_code || 'ไม่มีรหัส')}
                                · ${escapeHtml(sensor.sensor_type || 'ไม่ระบุประเภท')}
                            </div>
                        </div>
                        <div style="display:flex; gap:8px; flex-wrap:wrap">
                            <span class="badge ${state.kind}">
                                <span class="dot ${state.kind}"></span>${state.label}
                            </span>
                            <span class="badge ${freshness.kind}">
                                <span class="dot ${freshness.kind}"></span>${freshness.label}
                            </span>
                        </div>
                    </div>
                    <div class="sensor-metrics">
                        <div class="sensor-metric">
                            <div class="label">อุณหภูมิ</div>
                            <div class="value">${escapeHtml(numberOrDash(sensor.temperature_c))} <span class="unit">°C</span></div>
                        </div>
                        <div class="sensor-metric">
                            <div class="label">ความชื้น</div>
                            <div class="value">${escapeHtml(numberOrDash(sensor.humidity_pct))} <span class="unit">%</span></div>
                        </div>
                        <div class="sensor-metric">
                            <div class="label">ค่าทั่วไป</div>
                            <div class="value">${escapeHtml(numberOrDash(sensor.value, 2))}</div>
                        </div>
                    </div>
                    <p class="sensor-meta">บันทึกล่าสุด: ${escapeHtml(formatTimestamp(sensor.recorded_at))}</p>
                </article>`;
        };

        el('sensorList').innerHTML = sortedGroups.map(([zoneId, zoneSensors]) => {
            const zoneTitle = zoneId === '__unassigned__'
                ? 'ไม่ระบุโซน'
                : `Zone ${zoneId}`;
            return `
                <section class="zone-group" aria-label="${escapeHtml(zoneTitle)}">
                    <div class="zone-heading">
                        <h3>${escapeHtml(zoneTitle)}</h3>
                        <span class="zone-caption">${zoneSensors.length} เซนเซอร์</span>
                    </div>
                    <div class="zone-sensors">${zoneSensors.map(renderCard).join('')}</div>
                </section>`;
        }).join('');
    }

    async function refresh() {
        const button = el('refreshButton');
        button.disabled = true;

        try {
            const response = await fetch(API_URL, {
                method: 'GET',
                headers: { 'Accept': 'application/json' },
                cache: 'no-store',
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const payload = await response.json();
            if (payload.status !== 'ok' || !Array.isArray(payload.data)) {
                throw new Error('Invalid API response');
            }

            renderSensors(payload.data);
            el('lastUpdated').textContent =
                `ตรวจสอบ API ล่าสุด ${new Intl.DateTimeFormat('th-TH', {
                    hour: '2-digit', minute: '2-digit', second: '2-digit',
                    timeZone: 'Asia/Bangkok'
                }).format(new Date())}`;

            // API connectivity and sensor-data freshness are separate statuses.
            setConnection('เชื่อมต่อ API สำเร็จ', 'ok');

            const sensorStatus = el('sensorDataStatus');
            if (payload.data.length === 0) {
                sensorStatus.textContent = 'ยังไม่มีข้อมูลเซนเซอร์';
                sensorStatus.className = 'status-detail warn';
            } else {
                const freshness = payload.data.map(dataFreshness);
                const staleCount = freshness.filter(item => item.kind !== 'ok').length;

                if (staleCount > 0) {
                    sensorStatus.textContent =
                        `ข้อมูลเก่าหรือเวลาไม่สมบูรณ์ ${staleCount}/${payload.data.length} เซนเซอร์`;
                    sensorStatus.className = 'status-detail warn';
                } else {
                    sensorStatus.textContent = 'ข้อมูลเซนเซอร์เป็นปัจจุบัน';
                    sensorStatus.className = 'status-detail ok';
                }
            }
        } catch (error) {
            setConnection('ไม่สามารถโหลดข้อมูลจาก API ได้', 'error');
            el('sensorDataStatus').textContent = 'ไม่สามารถตรวจสอบข้อมูลเซนเซอร์ได้';
            el('sensorDataStatus').className = 'status-detail error';
            el('sensorList').innerHTML =
                '<div class="panel empty"><p class="error-text">โหลดข้อมูลไม่สำเร็จ</p>' +
                '<p class="muted small">ตรวจสอบการเชื่อมต่อและลองรีเฟรชอีกครั้ง</p></div>';
            el('sensorCount').textContent = 'ไม่พร้อมใช้งาน';
            console.error('Sensor API request failed:', error);
        } finally {
            button.disabled = false;
        }
    }

    el('refreshButton').addEventListener('click', refresh);
    refresh();
    window.setInterval(refresh, REFRESH_MS);
})();
</script>
</body>
</html>
