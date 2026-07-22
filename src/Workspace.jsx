import React, { useState, useEffect, useMemo, useRef } from "react";
import {
  LayoutDashboard, Calendar, MessageSquare, Github, Mail, Settings,
  Search, Plus, Copy, Check, ExternalLink, Send, Sparkles, Clock,
  Video, ChevronRight, ChevronLeft, X, Menu, AtSign, GitCommit,
  Users, ArrowUpRight, CheckCircle2, Slack as SlackIcon, Bell, Moon, Palette,
  MessageCircle, Maximize2, Minimize2
} from "lucide-react";

const Logo = ({ size = 28 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2L22 20H2L12 2Z" />
  </svg>
);

/* =========================================================================
   Huzaifa's Workspace — AI-powered personal productivity command center
   Single-file dashboard. Dark "twilight command center" identity.
   ========================================================================= */

const CSS = `
/* ── Local fonts (served from /public/fonts/) ── */
@font-face { font-family: 'Satoshi';         src: url('/fonts/satoshi/satoshi-400.woff2')         format('woff2'); font-weight: 400; font-display: swap; }
@font-face { font-family: 'Satoshi';         src: url('/fonts/satoshi/satoshi-500.woff2')         format('woff2'); font-weight: 500; font-display: swap; }
@font-face { font-family: 'Satoshi';         src: url('/fonts/satoshi/satoshi-700.woff2')         format('woff2'); font-weight: 700; font-display: swap; }
@font-face { font-family: 'General Sans';    src: url('/fonts/general-sans/generalsans-400.woff2') format('woff2'); font-weight: 400; font-display: swap; }
@font-face { font-family: 'General Sans';    src: url('/fonts/general-sans/generalsans-500.woff2') format('woff2'); font-weight: 500; font-display: swap; }
@font-face { font-family: 'General Sans';    src: url('/fonts/general-sans/generalsans-700.woff2') format('woff2'); font-weight: 700; font-display: swap; }
@font-face { font-family: 'Cabinet Grotesk'; src: url('/fonts/cabinet-grotesk/cabinet-400.woff2') format('woff2'); font-weight: 400; font-display: swap; }
@font-face { font-family: 'Cabinet Grotesk'; src: url('/fonts/cabinet-grotesk/cabinet-500.woff2') format('woff2'); font-weight: 500; font-display: swap; }
@font-face { font-family: 'Cabinet Grotesk'; src: url('/fonts/cabinet-grotesk/cabinet-700.woff2') format('woff2'); font-weight: 700; font-display: swap; }
@font-face { font-family: 'Switzer';         src: url('/fonts/switzer/switzer-400.woff2')         format('woff2'); font-weight: 400; font-display: swap; }
@font-face { font-family: 'Switzer';         src: url('/fonts/switzer/switzer-500.woff2')         format('woff2'); font-weight: 500; font-display: swap; }
@font-face { font-family: 'Switzer';         src: url('/fonts/switzer/switzer-700.woff2')         format('woff2'); font-weight: 700; font-display: swap; }
@font-face { font-family: 'Clash Display';   src: url('/fonts/clash-display/clash-400.woff2')     format('woff2'); font-weight: 400; font-display: swap; }
@font-face { font-family: 'Clash Display';   src: url('/fonts/clash-display/clash-500.woff2')     format('woff2'); font-weight: 500; font-display: swap; }
@font-face { font-family: 'Clash Display';   src: url('/fonts/clash-display/clash-700.woff2')     format('woff2'); font-weight: 700; font-display: swap; }
@font-face { font-family: 'Synonym';         src: url('/fonts/synonym/synonym-400.woff2')         format('woff2'); font-weight: 400; font-display: swap; }
@font-face { font-family: 'Synonym';         src: url('/fonts/synonym/synonym-500.woff2')         format('woff2'); font-weight: 500; font-display: swap; }
@font-face { font-family: 'Synonym';         src: url('/fonts/synonym/synonym-700.woff2')         format('woff2'); font-weight: 700; font-display: swap; }
@font-face { font-family: 'Chillax';         src: url('/fonts/chillax/chillax-400.woff2')         format('woff2'); font-weight: 400; font-display: swap; }
@font-face { font-family: 'Chillax';         src: url('/fonts/chillax/chillax-500.woff2')         format('woff2'); font-weight: 500; font-display: swap; }
@font-face { font-family: 'Chillax';         src: url('/fonts/chillax/chillax-700.woff2')         format('woff2'); font-weight: 700; font-display: swap; }
@font-face { font-family: 'Inter';           src: url('/fonts/inter/inter-400.woff2')             format('woff2'); font-weight: 400; font-display: swap; }
@font-face { font-family: 'Inter';           src: url('/fonts/inter/inter-500.woff2')             format('woff2'); font-weight: 500; font-display: swap; }
@font-face { font-family: 'Inter';           src: url('/fonts/inter/inter-700.woff2')             format('woff2'); font-weight: 700; font-display: swap; }

:root { --font-sans: 'Inter', system-ui, -apple-system, sans-serif; }

html, body { height: 100%; margin: 0; padding: 0; overflow: hidden; }

:root {
  --bg: #0a0a0a;
  --surface: #111111;
  --card: #161616;
  --border: #272727;
  --border-strong: #333333;
  --text: #ededed;
  --text-secondary: #888888;
  --text-muted: #555555;
  --primary: #4f8ef7;
  --primary-bg: rgba(79, 142, 247, 0.08);
  --danger: #f87171;
  --success: #4ade80;
  --radius: 8px;
  --slack: #e01e5a;
  --gcal: #4285f4;
  --cly: #0069ff;
  --gh: #adbac7;
  --email: #ea4335;
  --teal: #14b8a6;
  --blue: #3b82f6;
  --rose: #f43f5e;
  --amber: #f59e0b;
  --green: #22c55e;
  --inset: rgba(255,255,255,0.04);
  --border-soft: #222222;
  --primary-2: #818cf8;
}
:root[data-theme="light"] {
  --bg: #fafafa;
  --surface: #f4f4f4;
  --card: #ffffff;
  --border: #e5e5e5;
  --border-strong: #d4d4d4;
  --text: #0a0a0a;
  --text-secondary: #666666;
  --text-muted: #999999;
  --primary: #2563eb;
  --primary-bg: rgba(37, 99, 235, 0.06);
  --danger: #dc2626;
  --success: #16a34a;
  --inset: rgba(0,0,0,0.04);
  --border-soft: #e5e5e5;
  --gh: #24292f;
}
:root[data-theme="midnight"] {
  --bg: #060d1a;
  --surface: #0c1829;
  --card: #102030;
  --border: #1c3050;
  --border-strong: #254070;
  --text: #e0e8f8;
  --text-secondary: #6888b8;
  --text-muted: #304870;
  --primary: #3d72d4;
  --primary-bg: rgba(61, 114, 212, 0.12);
  --danger: #e05555;
  --success: #38a868;
  --radius: 8px;
  --inset: rgba(255,255,255,0.04);
  --border-soft: #1c3050;
}
:root[data-theme="forest"] {
  --bg: #060d08;
  --surface: #0c1a10;
  --card: #112016;
  --border: #1a3020;
  --border-strong: #224030;
  --text: #d0e8d4;
  --text-secondary: #5a8865;
  --text-muted: #2a4830;
  --primary: #1e8a4c;
  --primary-bg: rgba(30, 138, 76, 0.12);
  --danger: #e05555;
  --success: #38a868;
  --radius: 8px;
  --inset: rgba(255,255,255,0.04);
  --border-soft: #1a3020;
}
:root[data-theme="sunset"] {
  --bg: #0d0a06;
  --surface: #181208;
  --card: #201a10;
  --border: #362515;
  --border-strong: #504030;
  --text: #ede0cc;
  --text-secondary: #a07845;
  --text-muted: #684828;
  --primary: #b56420;
  --primary-bg: rgba(181, 100, 32, 0.12);
  --danger: #e05555;
  --success: #38a868;
  --radius: 8px;
  --inset: rgba(255,255,255,0.04);
  --border-soft: #362515;
}
:root[data-theme="aurora"] {
  --bg: #070610;
  --surface: #0f0c1e;
  --card: #15122c;
  --border: #201c3c;
  --border-strong: #302858;
  --text: #ddd8f8;
  --text-secondary: #7864b0;
  --text-muted: #3c3070;
  --primary: #7050c0;
  --primary-bg: rgba(112, 80, 192, 0.12);
  --danger: #e05555;
  --success: #38a868;
  --radius: 8px;
  --inset: rgba(255,255,255,0.04);
  --border-soft: #201c3c;
}
:root[data-theme="rose"] {
  --bg: #0e0608;
  --surface: #180c10;
  --card: #201018;
  --border: #301824;
  --border-strong: #482438;
  --text: #edd8e4;
  --text-secondary: #9c6880;
  --text-muted: #5c3048;
  --primary: #a84070;
  --primary-bg: rgba(168, 64, 112, 0.12);
  --danger: #e05555;
  --success: #38a868;
  --radius: 8px;
  --inset: rgba(255,255,255,0.04);
  --border-soft: #301824;
}
:root[data-theme="nord"] {
  --bg: #2e3440;
  --surface: #3b4252;
  --card: #434c5e;
  --border: #4c566a;
  --border-strong: #5e6a80;
  --text: #eceff4;
  --text-secondary: #8898b0;
  --text-muted: #5a6880;
  --primary: #3d7a8c;
  --primary-bg: rgba(61, 122, 140, 0.14);
  --danger: #bf616a;
  --success: #8aad72;
  --radius: 8px;
  --inset: rgba(255,255,255,0.05);
  --border-soft: #4c566a;
}
* { box-sizing: border-box; }
.hw, .hw * { font-family: var(--font-sans); letter-spacing: normal; line-height: 1.5; }
.hw { background: var(--bg); color: var(--text); min-height: 100vh; width: 100%; display: grid; grid-template-columns: 220px 1fr; grid-template-rows: 100vh; overflow: hidden; -webkit-font-smoothing: antialiased; font-size: 13px; transition: grid-template-columns .25s cubic-bezier(.4,0,.2,1); }

/* scrollbars */
.hw ::-webkit-scrollbar { width: 8px; height: 8px; }
.hw ::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 4px; border: 2px solid transparent; background-clip: padding-box; }
.hw ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); background-clip: padding-box; }

/* sidebar */
.side { background: var(--surface); border-right: 1px solid var(--border); display: flex; flex-direction: column; padding: 20px 14px; gap: 6px; min-width: 0; position: relative; z-index: 30; overflow: hidden; transition: padding .2s cubic-bezier(.4,0,.2,1); }
.brand { display: flex; align-items: center; gap: 11px; padding: 6px 8px 18px; }
.brand-mark { width: 28px; height: 28px; border-radius: 50%; background: var(--text); display: grid; place-items: center; flex: none; color: var(--bg); }
.brand-name { font-weight: 500; font-size: 16px; color: var(--text); }
.brand-sub { display: none; }
.nav-label { font-size: 11px; color: var(--text-muted); padding: 14px 10px 8px; font-weight: 500; }
.nav { display: flex; align-items: center; gap: 11px; height: 36px; padding: 0 16px; border-radius: var(--radius); color: var(--text-secondary); cursor: pointer; font-size: 13px; transition: .15s ease; position: relative; }
.nav:hover { background: var(--card); }
.nav.active { background: var(--card); color: var(--text); font-weight: 500; }
.nav .badge { margin-left: auto; background: var(--primary); color: var(--bg); font-size: 10px; font-weight: 500; min-width: 16px; height: 16px; border-radius: 8px; display: grid; place-items: center; padding: 0 4px; }
.nav .unread-dot { margin-left: auto; width: 6px; height: 6px; border-radius: 50%; background: var(--primary); }
.side-foot { margin-top: auto; display: flex; align-items: center; gap: 10px; padding: 10px; border-radius: var(--radius); background: transparent; border: none; }
.avatar { width: 32px; height: 32px; border-radius: 50%; display: grid; place-items: center; font-weight: 500; font-size: 12px; flex: none; background: var(--surface); color: var(--text); border: 1px solid var(--border); }
.avatar.lg { width: 40px; height: 40px; font-size: 14px; }

/* center */
.center { min-width: 0; display: flex; flex-direction: column; overflow: hidden; background: var(--bg); }
.topbar { display: flex; align-items: center; gap: 14px; padding: 16px 24px; border-bottom: 1px solid var(--border); background: var(--bg); z-index: 20; height: 64px; }
.greet { min-width: 0; display: flex; align-items: center; gap: 6px; }
.greet-text { font-size: 18px; color: var(--text-secondary); font-weight: 400; }
.greet-name { font-size: 18px; color: var(--text); font-weight: 500; }
.search { margin-left: auto; display: flex; align-items: center; gap: 9px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 8px 12px; width: 300px; max-width: 34vw; color: var(--text-muted); transition: .15s; }
.search:focus-within { border-color: var(--border-strong); }
.search input { background: none; border: none; outline: none; color: var(--text); font-size: 13px; width: 100%; }
.search input::placeholder { color: var(--text-muted); }
.icon-btn { width: 32px; height: 32px; border-radius: var(--radius); display: grid; place-items: center; flex: none; cursor: pointer; background: transparent; border: 1px solid var(--border); color: var(--text-secondary); transition: .15s; position: relative; }
.icon-btn:hover { color: var(--text); border-color: var(--border-strong); background: var(--surface); }
.scroll { overflow-y: auto; overflow-x: hidden; padding: 24px; flex: 1; overscroll-behavior: contain; }

/* cards / grid */
.grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; align-items: start; }
.card { background: var(--card); border: 0.5px solid var(--border); border-radius: 12px; padding: 16px; min-width: 0; }
.card.expanded { grid-column: span 2; }
.card.minimized .card-b { display: none; }
.card.minimized { padding-bottom: 12px; opacity: 0.65; cursor: pointer; transition: opacity .15s; }
.card.minimized:hover { opacity: 0.9; }
.span2 { grid-column: span 2; }
.card-h { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.card-h .ic { width: 16px; height: 16px; display: grid; place-items: center; flex: none; color: var(--text-secondary); }
.card-h h3 { font-size: 13px; font-weight: 500; color: var(--text-secondary); }
.card-h .right { margin-left: auto; display: flex; align-items: center; gap: 8px; }
.card-b { padding: 0; display: flex; flex-direction: column; }
.link-btn { display: inline-flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 500; color: var(--text); cursor: pointer; padding: 4px 8px; border-radius: 4px; transition: .14s; border: 1px solid transparent; text-decoration: none; }
.link-btn:hover { background: var(--surface); border-color: var(--border); }
.row { display: flex; align-items: center; gap: 12px; padding: 10px 0; cursor: pointer; transition: .14s; border-bottom: 0.5px solid var(--border); }
.row:last-child { border-bottom: none; }
.row:hover { background: var(--primary-bg); }
.row .body { min-width: 0; flex: 1; }
.row .top { display: flex; align-items: center; gap: 8px; }
.row .name { font-size: 13px; font-weight: 400; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.row.unread .name { font-weight: 500; }
.row .time { font-size: 11px; color: var(--text-muted); margin-left: auto; white-space: nowrap; flex: none; }
.row .text { font-size: 11px; color: var(--text-muted); margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.unread-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--primary); flex: none; }
.pill { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; font-weight: 500; padding: 2px 6px; border-radius: 4px; white-space: nowrap; background: var(--surface); color: var(--text-secondary); border: 1px solid var(--border); }

/* empty states */
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 32px 0; text-align: center; gap: 12px; }
.empty-state .ic { color: var(--text-muted); margin-bottom: 4px; }
.empty-state .text { font-size: 13px; color: var(--text-muted); }
.empty-btn { display: inline-flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 500; padding: 6px 12px; border-radius: var(--radius); cursor: pointer; border: 1px solid var(--border); background: transparent; color: var(--text-secondary); }
.empty-btn:hover { background: var(--surface); color: var(--text); }

/* forms / auth */
.auth-wrap { display: grid; place-items: center; min-height: 100vh; padding: 20px; background: var(--bg); color: var(--text); }
.auth-card { width: 100%; max-width: 400px; background: var(--card); border: 0.5px solid var(--border); border-radius: 12px; padding: 32px 28px; }
.auth-header { text-align: center; margin-bottom: 32px; }
.auth-title { font-size: 20px; font-weight: 500; color: var(--text); }
.input-group { margin-bottom: 16px; }
.input-label { color: var(--text); font-size: 13px; font-weight: 500; margin-bottom: 8px; display: block; }
.input-field { width: 100%; height: 36px; background: var(--card); color: var(--text); border: 0.5px solid var(--border); border-radius: var(--radius); padding: 0 12px; font-size: 13px; transition: border-color .15s; outline: none; }
.input-field::placeholder { color: var(--text-muted); }
.input-field:focus { border-color: var(--border-strong); }
.auth-error { color: var(--danger); font-size: 12px; margin-top: 4px; margin-bottom: 16px; text-align: center; }
.auth-tabs { display: flex; margin-bottom: 24px; border-bottom: 1px solid var(--border); }
.auth-tab { flex: 1; text-align: center; padding: 8px 0; font-size: 13px; font-weight: 400; color: var(--text-muted); cursor: pointer; transition: .15s; border: none; background: none; border-bottom: 2px solid transparent; }
.auth-tab.active { color: var(--text); border-bottom: 2px solid var(--primary); font-weight: 500; }
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; font-size: 13px; font-weight: 500; height: 36px; padding: 0 14px; border-radius: var(--radius); cursor: pointer; border: 1px solid var(--border-strong); background: var(--surface); color: var(--text); transition: .15s; white-space: nowrap; }
.btn:hover { background: var(--card); border-color: var(--border-strong); }
.btn.primary { background: var(--primary); border-color: var(--primary); color: #fff; }
.btn.primary:hover { background: color-mix(in srgb, var(--primary) 85%, #000); border-color: color-mix(in srgb, var(--primary) 85%, #000); }
.btn.block { width: 100%; }
.btn.connected { background: color-mix(in srgb, var(--success) 10%, var(--surface)); border-color: color-mix(in srgb, var(--success) 35%, transparent); color: var(--success); }
.btn.connected:hover { background: color-mix(in srgb, var(--success) 16%, var(--surface)); }
.btn.ghost { background: transparent; border-color: var(--border); color: var(--text-secondary); }
.btn.ghost:hover { background: var(--surface); color: var(--text); }
.btn:disabled { opacity: 0.45; cursor: not-allowed; }
.btn.sm { height: 28px; padding: 0 10px; font-size: 12px; border-radius: 6px; }
.conn-card { display: flex; align-items: center; gap: 14px; padding: 16px; background: var(--card); border: 0.5px solid var(--border); border-radius: 12px; }
.conn-ic { width: 42px; height: 42px; border-radius: 10px; display: grid; place-items: center; flex: none; }
.tag-hi { background: color-mix(in srgb, var(--rose) 12%, transparent); color: var(--rose); border-color: color-mix(in srgb, var(--rose) 28%, transparent); }
.tag-md { background: color-mix(in srgb, var(--amber) 12%, transparent); color: var(--amber); border-color: color-mix(in srgb, var(--amber) 28%, transparent); }
.tag-lo { background: color-mix(in srgb, var(--green) 12%, transparent); color: var(--green); border-color: color-mix(in srgb, var(--green) 28%, transparent); }
.tag-imp { background: color-mix(in srgb, var(--primary) 12%, transparent); color: var(--primary); border-color: color-mix(in srgb, var(--primary) 28%, transparent); }

/* hero / countdown */
.hero { grid-column: span 2; background: var(--card); border: 0.5px solid var(--border); border-radius: 12px; padding: 24px; display: flex; align-items: center; gap: 20px; }
.hero .glyph { width: 48px; height: 48px; border-radius: 50%; flex: none; display: grid; place-items: center; background: var(--surface); border: 1px solid var(--border); }
.hero .eyebrow { font-size: 11px; color: var(--text-muted); font-weight: 500; }
.hero h2 { font-size: 18px; font-weight: 500; margin-top: 4px; }
.hero .meta { display: flex; gap: 16px; margin-top: 8px; flex-wrap: wrap; color: var(--text-secondary); font-size: 13px; }
.hero .meta span { display: inline-flex; align-items: center; gap: 6px; }
.count { margin-left: auto; text-align: right; flex: none; }
.count .num { font-size: 32px; font-weight: 500; color: var(--text); }
.count .lbl { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

/* stat strip */
.stats { grid-column: span 2; display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.stat { background: var(--card); border: 0.5px solid var(--border); border-radius: 12px; padding: 16px; }
.stat .n { font-size: 24px; font-weight: 500; }
.stat .l { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
.stat .ic { width: 24px; height: 24px; border-radius: 4px; display: grid; place-items: center; margin-bottom: 8px; color: var(--text-secondary); }

/* live dot */
.live { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text); font-weight: 500; }
.live i { width: 6px; height: 6px; border-radius: 50%; background: var(--success); }

/* assistant panel */
.assist { background: var(--surface); border-left: 1px solid var(--border); display: flex; flex-direction: column; min-width: 0; position: relative; z-index: 30; }
.assist-h { padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 12px; }
.assist-h .who { min-width: 0; }
.assist-h .who .nm { font-weight: 500; font-size: 14px; display: flex; align-items: center; gap: 7px; color: var(--text); }
.assist-h .who .st { font-size: 12px; color: var(--text-muted); display: flex; align-items: center; gap: 5px; margin-top: 2px; }
.chat { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 16px; overscroll-behavior: contain; }
.msg { display: flex; gap: 12px; max-width: 92%; }
.msg.me { align-self: flex-end; flex-direction: row-reverse; }
.bub { padding: 10px 14px; border-radius: 8px; font-size: 13px; line-height: 1.5; white-space: pre-wrap; word-break: break-word; }
.msg.ai .bub { background: var(--card); border: 0.5px solid var(--border); color: var(--text); }
.msg.me .bub { background: var(--primary); color: #fff; }
.typing { display: flex; gap: 4px; padding: 12px; }
.typing i { width: 6px; height: 6px; border-radius: 50%; background: var(--text-muted); }
.quick { display: flex; gap: 8px; flex-wrap: wrap; padding: 0 20px 16px; }
.chip { font-size: 12px; font-weight: 500; color: var(--text-secondary); background: var(--card); border: 1px solid var(--border); border-radius: 4px; padding: 6px 10px; cursor: pointer; transition: .15s; white-space: nowrap; }
.chip:hover { background: var(--surface); border-color: var(--border-strong); color: var(--text); }
.composer { padding: 16px; border-top: 1px solid var(--border); background: var(--bg); }
.composer .box { display: flex; align-items: flex-end; gap: 8px; background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 6px 6px 6px 12px; transition: .15s; }
.composer .box:focus-within { border-color: var(--border-strong); }
.composer textarea { flex: 1; background: none; border: none; outline: none; color: var(--text); font-size: 13px; resize: none; max-height: 110px; line-height: 1.5; padding: 6px 0; font-family: inherit; }
.composer textarea::placeholder { color: var(--text-muted); }
.send-btn { width: 32px; height: 32px; border-radius: 4px; border: none; flex: none; cursor: pointer; display: grid; place-items: center; background: var(--primary); color: #fff; transition: .15s; }
.send-btn:hover { background: color-mix(in srgb, var(--primary) 85%, #000); }
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* modal / onboarding */
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; display: grid; place-items: center; padding: 24px; }
.sheet { width: 100%; max-width: 480px; background: var(--card); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; max-height: calc(100vh - 48px); }
.sheet-h { padding: 20px 24px; border-bottom: 1px solid var(--border); flex: none; }
.sheet-b { padding: 20px 24px; overflow-y: auto; overscroll-behavior: contain; }
.sheet-f { padding: 16px 24px; border-top: 1px solid var(--border); display: flex; gap: 12px; align-items: center; flex: none; }
.steps { display: flex; gap: 8px; }
.steps i { height: 4px; border-radius: 2px; background: var(--border); flex: 1; }
.steps i.on { background: var(--primary); }
.field { margin-bottom: 16px; }
.field label { display: block; font-size: 13px; color: var(--text); margin-bottom: 8px; font-weight: 500; }
.field input, .field select { width: 100%; height: 36px; background: var(--card); border: 1px solid var(--border); border-radius: 4px; padding: 0 12px; color: var(--text); font-size: 13px; outline: none; }
.field input:focus, .field select:focus { border-color: var(--border-strong); }
.copy-link { display: flex; align-items: center; gap: 10px; background: var(--surface); border: 1px solid var(--border); border-radius: 4px; padding: 10px 12px; font-size: 13px; color: var(--text); }

/* responsive */
.mobile-only { display: none !important; }
.scrim { display: none; position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 40; }
.side-close { display: none; }
@media(min-width:861px){.hw.sidebar-collapsed{grid-template-columns:0px 1fr}.hw.sidebar-collapsed .side{padding:0;border-right-color:transparent}}
@media(max-width:860px){.hw{grid-template-columns:1fr}.hw.sidebar-collapsed{grid-template-columns:1fr}.side{position:fixed;top:0;left:0;bottom:0;width:272px;z-index:50;transform:translateX(-100%);transition:transform .3s cubic-bezier(.4,0,.2,1);box-shadow:4px 0 24px rgba(0,0,0,0.3);overflow-y:auto;overflow-x:hidden;padding:20px 14px}.side.open{transform:translateX(0)}.grid{grid-template-columns:1fr}.span2,.hero,.stats{grid-column:span 1}.stats{grid-template-columns:repeat(2,1fr)}.hero{flex-wrap:wrap}.count{margin-left:0}.search{width:auto;flex:1}.mobile-only{display:grid!important}.scrim{display:block}.side-close{display:grid}}`;

/* ---------------------------- Mascot SVG ---------------------------- */
function Mascot({ size = 24 }) {
  return (
    <div className="mascot-wrap" style={{ width: size, height: size, background: "var(--text)", color: "var(--bg)", borderRadius: "50%", display: "grid", placeItems: "center" }}>
      <Sparkles size={size * 0.6} />
    </div>
  );
}

/* ---------------------------- Data ---------------------------- */
function buildData(userName = "User") {
  const now = new Date();
  const at = (h, m, dayOffset = 0) => {
    const d = new Date(now); d.setDate(d.getDate() + dayOffset); d.setHours(h, m, 0, 0); return d;
  };
  const inMin = (m) => new Date(now.getTime() + m * 60000);

  return {
    slack: {
      mentions: [
        { id: 1, channel: "#product", from: "Ahmed Raza", text: `@${userName.split(' ')[0]} can you review the new onboarding flow before the 3pm sync?`, time: "8m", unread: true },
        { id: 2, channel: "#engineering", from: "Sara Khan", text: `@${userName.split(' ')[0]} the API rate-limit fix is deployed to staging`, time: "41m", unread: true },
        { id: 3, channel: "#design", from: "Bilal", text: `@${userName.split(' ')[0]} loved the new dashboard mocks — shipping today?`, time: "2h", unread: false },
      ],
      dms: [
        { id: 4, from: "Ayesha Malik", text: "Are we still on for the 1:1 later today?", time: "15m", unread: true },
        { id: 5, from: "Usman", text: "Sent over the contract draft, take a look when free.", time: "1h", unread: false },
      ],
    },
    calendar: [
      { id: "c1", title: "Daily Standup", start: at(9, 30), end: at(9, 45), priority: "low", location: "Google Meet", done: true },
      { id: "c2", title: "Design Review", start: inMin(25), end: inMin(70), priority: "high", location: "Google Meet", attendees: 5, meet: true },
      { id: "c3", title: "1:1 with Ayesha", start: at(15, 0), end: at(15, 30), priority: "medium", location: "Google Meet", attendees: 2, meet: true },
      { id: "c4", title: "Product Sync", start: at(17, 30), end: at(18, 0), priority: "high", location: "Conference Room B", attendees: 8 },
      { id: "c5", title: "Roadmap Planning", start: at(11, 0, 1), end: at(12, 0, 1), priority: "high", location: "Google Meet", attendees: 6, meet: true },
      { id: "c6", title: "Client Demo — Acme", start: at(14, 0, 1), end: at(14, 45, 1), priority: "high", location: "Zoom", attendees: 4 },
    ],
    github: [
      { id: "g1", actor: "Ali Hassan", action: "pushed 5 commits", repo: "backend-api", message: "feat: add rate limiting + retry logic to integration layer", time: "10m", commits: 5 },
      { id: "g2", actor: "Sara Khan", action: "opened a pull request", repo: "web-dashboard", message: "Dark theme polish & responsive sidebar", time: "38m", commits: 0, pr: true },
      { id: "g3", actor: userName.split(' ')[0], action: "pushed 2 commits", repo: "ai-assistant", message: "chore: refine assistant system prompt", time: "1h", commits: 2 },
      { id: "g4", actor: "Bilal", action: "merged a pull request", repo: "web-dashboard", message: "Improve dashboard card layouts", time: "3h", commits: 0, pr: true },
    ],
    email: [
      { id: "e1", from: "Stripe", subject: "Your invoice for May is ready", preview: "Your subscription invoice of $49.00 has been paid successfully.", time: "12m", unread: true, important: true },
      { id: "e2", from: "Daniel Wright", subject: "Re: Partnership proposal", preview: "Thanks for the deck — the team is excited. Can we lock a call this week?", time: "47m", unread: true, important: true },
      { id: "e3", from: "GitHub", subject: "[web-dashboard] 2 new pull requests", preview: "Sara Khan and Bilal opened pull requests in your repository.", time: "1h", unread: true, important: false },
      { id: "e4", from: "Notion", subject: "Weekly digest: 4 pages updated", preview: "Your team updated the Product Roadmap and 3 other pages.", time: "4h", unread: false, important: false },
      { id: "e5", from: "Ayesha Malik", subject: "1:1 agenda for today", preview: "Adding a couple of items — career growth + Q3 priorities.", time: "5h", unread: false, important: false },
    ],
    integrations: [
      { id: "slack", name: "Slack", connected: true, color: "var(--slack)", desc: "Mentions, DMs & channels" },
      { id: "gcal", name: "Google Calendar", connected: true, color: "var(--gcal)", desc: "Events & Google Meet" },
      { id: "gh", name: "GitHub", connected: true, color: "var(--gh)", desc: "Commits & repo activity" },
      { id: "email", name: "Gmail", connected: true, color: "var(--email)", desc: "Inbox & important mail" },
    ],
  };
}

/* ---------------------------- helpers ---------------------------- */
const fmtTime = (d) => d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
const PRIO = { high: ["High", "tag-hi"], medium: ["Medium", "tag-md"], low: ["Low", "tag-lo"] };
const intIcon = { slack: SlackIcon, gcal: Calendar, gh: Github, email: Mail };

function Initials({ name, ...p }) {
  const i = name.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase();
  return <div className="avatar" {...p}>{i}</div>;
}

/* live countdown to next upcoming meeting */
function useCountdown(events) {
  const [, force] = useState(0);
  useEffect(() => { const t = setInterval(() => force((x) => x + 1), 1000); return () => clearInterval(t); }, []);
  const now = Date.now();
  const next = events
    .filter((e) => e.start.getTime() > now)
    .sort((a, b) => a.start - b.start)[0];
  if (!next) return { next: null, text: "—" };
  const diff = next.start.getTime() - now;
  const h = Math.floor(diff / 3600000), m = Math.floor((diff % 3600000) / 60000), s = Math.floor((diff % 60000) / 1000);
  const text = h > 0 ? `${h}h ${m}m` : m > 0 ? `${m}m ${s}s` : `${s}s`;
  return { next, text, h, m };
}

/* =========================================================================
   API LAYER — talks to the FastAPI backend; falls back to demo data offline
   ========================================================================= */
const API_BASE =
  (typeof import.meta !== "undefined" && import.meta.env && import.meta.env.VITE_API_BASE) ||
  "/api";   // relative path → routes through the Vite dev server proxy to localhost:8000

const ICOLOR = { slack: "var(--slack)", gcal: "var(--gcal)", github: "var(--gh)", gh: "var(--gh)", email: "var(--email)" };
const IDMAP = { github: "gh" };   // API id -> internal id

const THEMES = [
  { id: "dark",     label: "Dark",     bg: "#0a0a0a", surface: "#161616", accent: "#4f8ef7" },
  { id: "light",    label: "Light",    bg: "#f0f0f0", surface: "#ffffff", accent: "#2563eb" },
  { id: "midnight", label: "Midnight", bg: "#060d1a", surface: "#102030", accent: "#3d72d4" },
  { id: "forest",   label: "Forest",   bg: "#060d08", surface: "#112016", accent: "#1e8a4c" },
  { id: "sunset",   label: "Sunset",   bg: "#0d0a06", surface: "#201a10", accent: "#b56420" },
  { id: "aurora",   label: "Aurora",   bg: "#070610", surface: "#15122c", accent: "#7050c0" },
  { id: "rose",     label: "Rose",     bg: "#0e0608", surface: "#201018", accent: "#a84070" },
  { id: "nord",     label: "Nord",     bg: "#2e3440", surface: "#434c5e", accent: "#3d7a8c" },
];

/* Convert the backend /dashboard payload into the shape the UI already uses. */
function adaptPayload(p) {
  const now = Date.now();
  return {
    slack: p.slack,
    calendar: (p.calendar || []).map((e) => ({
      ...e, start: new Date(e.start), end: new Date(e.end),
      done: new Date(e.end).getTime() < now,
    })),
    github: p.github,
    email: p.email,
    integrations: (p.integrations || []).map((it) => {
      const id = IDMAP[it.id] || it.id;
      return { id, name: it.name, connected: it.connected,
               color: ICOLOR[id] || "var(--primary)", desc: it.description };
    }),
  };
}

async function fetchDashboard() {
  const r = await fetch(`${API_BASE}/dashboard`, {
    headers: { Accept: "application/json" },
    credentials: "include",   // send session cookie for cross-origin requests
  });
  if (!r.ok) throw new Error("dashboard " + r.status);
  return adaptPayload(await r.json());
}

/* =========================================================================
   AUTH VIEW
   ========================================================================= */
function AuthView({ onAuthSuccess }) {
  const [mode, setMode] = useState("login"); // "login" | "signup"
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    const fd = new FormData(e.target);
    const data = Object.fromEntries(fd.entries());
    
    if (mode === "signup" && data.password !== data.confirm_password) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }
    
    try {
      const res = await fetch(`${API_BASE}/auth/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      
      const payload = await res.json();
      if (!res.ok) {
        if (payload.detail?.error === "email_taken") throw new Error("Email is already registered.");
        if (payload.detail?.error === "invalid_credentials") throw new Error("Incorrect email or password.");
        if (payload.detail?.reason === "password_too_short") throw new Error("Password must be at least 8 characters.");
        throw new Error("An error occurred. Please try again.");
      }
      
      onAuthSuccess(payload);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrap">
      
        <div className="auth-header">
          <Logo size={32} />
          <div className="auth-title">Workspace</div>
        </div>
        
        <div className="auth-card">
          <div>
            
            <div className="auth-tabs">
              <button 
                type="button" 
                className={`auth-tab ${mode === "login" ? "active" : ""}`} 
                onClick={() => { setMode("login"); setError(null); }}
              >
                Log in
              </button>
              <button 
                type="button" 
                className={`auth-tab ${mode === "signup" ? "active" : ""}`} 
                onClick={() => { setMode("signup"); setError(null); }}
              >
                Sign up
              </button>
            </div>
            
            {error && <div className="auth-error">{error}</div>}
            
            <form onSubmit={submit}>
              {mode === "signup" && (
                <div className="input-group">
                  <label className="input-label">Full Name</label>
                  <input name="full_name" required placeholder="Jane Doe" className="input-field" />
                </div>
              )}
              
              <div className="input-group">
                <label className="input-label">Email</label>
                <input name="email" type="email" required placeholder="jane@example.com" className="input-field" />
              </div>
              
              <div className="input-group">
                <label className="input-label">Password</label>
                <input name="password" type="password" required className="input-field" />
              </div>
              
              {mode === "signup" && (
                <div className="input-group">
                  <label className="input-label">Confirm Password</label>
                  <input name="confirm_password" type="password" required className="input-field" />
                </div>
              )}
              
              <button type="submit" disabled={loading} className="btn primary block">
                {loading ? "Please wait..." : mode === "login" ? "Log in to workspace" : "Create account"}
              </button>
            </form>
        </div>
      </div>
    </div>
  );
}

/* ---------------------------- Fonts ---------------------------- */
/* All fonts are pre-loaded via @font-face in the CSS string above — no CDN needed */
const FONTS = [
  { name: "Satoshi",         value: "Satoshi"         },
  { name: "General Sans",    value: "General Sans"    },
  { name: "Cabinet Grotesk", value: "Cabinet Grotesk" },
  { name: "Switzer",         value: "Switzer"         },
  { name: "Clash Display",   value: "Clash Display"   },
  { name: "Synonym",         value: "Synonym"         },
  { name: "Chillax",         value: "Chillax"         },
  { name: "Inter",           value: "Inter"           },
];

function applyPreferences(preferences) {
  if (preferences.theme) {
    document.documentElement.setAttribute("data-theme", preferences.theme);
    localStorage.setItem("theme", preferences.theme);
  }
  if (preferences.font) {
    const font = FONTS.find(f => f.value === preferences.font);
    if (font) {
      document.documentElement.style.setProperty("--font-sans", `"${font.value}", system-ui, sans-serif`);
      localStorage.setItem("workspace-font", font.value);
    }
  }
}

/* ---------------------------- Theme Picker ---------------------------- */
function ThemePicker({ current, onChange }) {
  const [open, setOpen] = useState(false);
  const [activeFont, setActiveFont] = useState(
    () => localStorage.getItem("workspace-font") || "Inter"
  );
  const btnRef = useRef(null);
  const panelRef = useRef(null);

  const toggle = () => setOpen(o => !o);

  useEffect(() => {
    if (!open) return;
    const handler = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target) && !btnRef.current.contains(e.target))
        setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  const handleFontSelect = (font) => {
    applyPreferences({ font: font.value });
    setActiveFont(font.value);
    if (API_BASE) {
      fetch(`${API_BASE}/preferences`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        credentials: "include", body: JSON.stringify({ font: font.value })
      }).catch(() => {});
    }
  };

  return (
    <div style={{ position: "relative" }}>
      <button ref={btnRef} className="icon-btn" onClick={toggle} title="Change theme" style={{ background: open ? "var(--surface)" : undefined }}>
        <Palette size={16} />
      </button>
      {open && (
        <div ref={panelRef} style={{
          position: "absolute", top: "calc(100% + 8px)", left: 0, right: "auto",
          background: "var(--card)", border: "1px solid var(--border-strong)",
          borderRadius: 14, padding: "16px 14px", zIndex: 1000, width: 280,
          boxShadow: "0 16px 40px rgba(0,0,0,0.5)",
        }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: ".1em", marginBottom: 14 }}>
            Theme
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8, marginBottom: 16 }}>
            {THEMES.map(t => {
              const active = current === t.id;
              const isLight = t.id === "light";
              return (
                <button key={t.id} onClick={() => { onChange(t.id); }}
                  title={t.label}
                  style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 7, background: "none", border: "none", cursor: "pointer", padding: "4px 2px", borderRadius: 8 }}>
                  <div style={{
                    width: 42, height: 42, borderRadius: 11, background: t.bg,
                    position: "relative", overflow: "hidden", flexShrink: 0,
                    border: active
                      ? "2.5px solid var(--primary)"
                      : isLight
                        ? "2px solid rgba(0,0,0,0.15)"
                        : "2px solid rgba(255,255,255,0.12)",
                    boxShadow: active ? `0 0 0 3px var(--primary-bg), inset 0 0 0 1px rgba(255,255,255,0.08)` : "inset 0 0 0 1px rgba(255,255,255,0.06)",
                    transition: "border .15s, box-shadow .15s",
                  }}>
                    <div style={{
                      position: "absolute", inset: 0,
                      background: t.surface,
                      clipPath: "polygon(0 60%, 100% 40%, 100% 100%, 0 100%)",
                    }} />
                    <div style={{
                      position: "absolute", bottom: 6, right: 6,
                      width: 10, height: 10, borderRadius: "50%",
                      background: t.accent,
                      boxShadow: `0 0 5px ${t.accent}99`,
                    }} />
                    {active && (
                      <div style={{
                        position: "absolute", top: 5, left: 5, width: 12, height: 12,
                        borderRadius: "50%", background: "var(--primary)",
                        display: "grid", placeItems: "center",
                        boxShadow: "0 1px 4px rgba(0,0,0,0.4)",
                      }}>
                        <Check size={7} color="#fff" strokeWidth={3.5} />
                      </div>
                    )}
                  </div>
                  <span style={{
                    fontSize: 10, letterSpacing: "-.01em",
                    color: active ? "var(--text)" : "var(--text-secondary)",
                    fontWeight: active ? 600 : 400,
                  }}>
                    {t.label}
                  </span>
                </button>
              );
            })}
          </div>
          <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: ".1em", marginBottom: 10 }}>
            Font
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {FONTS.map(font => {
              const active = activeFont === font.value;
              return (
                <button
                  key={font.value}
                  onClick={() => handleFontSelect(font)}
                  style={{
                    fontFamily: `"${font.value}", system-ui, sans-serif`,
                    fontSize: 12,
                    padding: "5px 10px",
                    borderRadius: 6,
                    border: active ? "1.5px solid var(--primary)" : "1px solid var(--border)",
                    background: active ? "var(--primary-bg)" : "var(--surface)",
                    color: active ? "var(--primary)" : "var(--text-secondary)",
                    cursor: "pointer",
                    transition: "border .15s, background .15s, color .15s",
                    whiteSpace: "nowrap",
                  }}
                >
                  {font.name}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

/* =========================================================================
   APP
   ========================================================================= */
const initTheme = localStorage.getItem('theme') || 'dark';
document.documentElement.setAttribute('data-theme', initTheme);
const initFont = localStorage.getItem('workspace-font');
if (initFont) {
  const fontObj = FONTS.find(f => f.value === initFont);
  if (fontObj) document.documentElement.style.setProperty("--font-sans", `"${fontObj.value}", system-ui, sans-serif`);
}

export default function App() {
  const [theme, setTheme] = useState(initTheme);
  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
    applyPreferences({ theme: newTheme });
    if (API_BASE) {
      fetch(`${API_BASE}/preferences`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        credentials: "include", body: JSON.stringify({ theme: newTheme })
      }).catch(() => {});
    }
  };
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const [user, setUser] = useState(null);
  const [connections, setConnections] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  const [data, setData] = useState(() => buildData());
  const [mode, setMode] = useState("demo");      // "demo" | "live" | "loading"
  const [view, setView] = useState("dashboard");
  const [onboard, setOnboard] = useState(false);
  const [navOpen, setNavOpen] = useState(false);
  const [assistOpen, setAssistOpen] = useState(false);
  const [newEvent, setNewEvent] = useState(false);
  const [events, setEvents] = useState(data.calendar);

  const checkAuth = async () => {
    setAuthLoading(true);
    if (!API_BASE) {
      setAuthLoading(false);
      return;
    }
    try {
      const r = await fetch(`${API_BASE}/me`, { credentials: "include" });
      const payload = await r.json();
      if (payload.authenticated) {
        if (payload.preferences) {
          applyPreferences(payload.preferences);
          if (payload.preferences.theme) setTheme(payload.preferences.theme);
        }
        if (payload.connections) setConnections(payload.connections);
        setUser(payload);
        fetchDashboardData();
      } else {
        setUser(null);
        setConnections(null);
        setOnboard(false);
        setAuthLoading(false);
      }
    } catch (e) {
      setAuthLoading(false);
    }
  };

  const fetchDashboardData = () => {
    let alive = true;
    setMode("loading");
    fetchDashboard()
      .then((live) => { if (!alive) return; setData(live); setEvents(live.calendar); setMode("live"); setAuthLoading(false); })
      .catch(() => { if (alive) { setMode("demo"); setAuthLoading(false); } });
    return () => { alive = false; };
  };

  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    if (user) {
      document.title = `${user.full_name}'s Workspace`;
      const done = localStorage.getItem(`onboarding_done_${user.id}`);
      setOnboard(!done);
    } else {
      document.title = "Workspace";
      setOnboard(false);
    }
  }, [user]);

  const finishOnboarding = () => {
    if (user?.id) localStorage.setItem(`onboarding_done_${user.id}`, "1");
    setOnboard(false);
  };

  // Auth → Dashboard (with onboarding overlay for first-time users)
  if (authLoading) {
    return (
      <>
        <style>{CSS}</style>
        <div style={{ display: "grid", placeItems: "center", height: "100vh", color: "var(--text-secondary)", background: "var(--bg)" }}>Loading…</div>
      </>
    );
  }

  if (!user) {
    return (
      <>
        <style>{CSS}</style>
        <AuthView onAuthSuccess={(payload) => {
          if (payload && payload.authenticated) {
            if (payload.preferences) {
              applyPreferences(payload.preferences);
              if (payload.preferences.theme) setTheme(payload.preferences.theme);
            }
            if (payload.connections) setConnections(payload.connections);
            setUser(payload);
            fetchDashboardData();
          } else {
            checkAuth();
          }
        }} />
      </>
    );
  }

  const getInitials = (name) => {
    if (!name) return "";
    return name.split(" ").map(p => p[0]).join("").substring(0, 2).toUpperCase();
  };


  const liveConnect = (internalId) => {
    const path = { gh: "github", gcal: "google", email: "google", slack: "slack" }[internalId];
    if (path && API_BASE) window.location.href = `${API_BASE}/auth/${path}/login`;
  };

  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
  const dateStr = new Date().toLocaleDateString([], { weekday: "long", month: "long", day: "numeric" });

  const unreadSlack = data.slack.mentions.filter((m) => m.unread).length + data.slack.dms.filter((m) => m.unread).length;
  const unreadEmail = data.email.filter((e) => e.unread).length;
  const todayEvents = events.filter((e) => e.start.toDateString() === new Date().toDateString());

  const nav = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "calendar", label: "Calendar", icon: Calendar, badge: todayEvents.length },
    { id: "messages", label: "Slack", icon: MessageSquare, badge: unreadSlack },
    { id: "github", label: "GitHub", icon: Github },
    { id: "email", label: "Email", icon: Mail, badge: unreadEmail },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  const go = (id) => { setView(id); setNavOpen(false); };

  const addEvent = (ev) => {
    setEvents((p) => [...p, ev].sort((a, b) => a.start - b.start));   // optimistic
    if (mode === "live" && API_BASE) {
      fetch(`${API_BASE}/calendar/events`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        credentials: "include",   // send session cookie for cross-origin requests
        body: JSON.stringify({
          title: ev.title, start: ev.start.toISOString(), end: ev.end.toISOString(),
          priority: ev.priority || "medium", add_meet: !!ev.meet,
        }),
      }).catch(() => {});
    }
  };

  return (
    <div className={`hw ${sidebarCollapsed ? "sidebar-collapsed" : ""}`}>
      <style>{CSS}</style>

      {/* ============ SIDEBAR ============ */}
      {navOpen && <div className="scrim" onClick={() => setNavOpen(false)} />}
      <aside className={`side ${navOpen ? "open" : ""}`}>
        <div className="brand">
          <Logo size={32} />
          <div>
            <div className="brand-name hw-display">Workspace</div>
            <div className="brand-sub">{user.full_name.split(' ')[0]}'s command center</div>
          </div>
          <button className="icon-btn side-close" style={{ marginLeft: "auto" }} onClick={() => setNavOpen(false)}><X size={16} /></button>
        </div>
        <div className="nav-label">Menu</div>
        {nav.map((n) => (
          <div key={n.id} className={`nav ${view === n.id ? "active" : ""}`} onClick={() => go(n.id)}>
            <n.icon size={17} />
            <span>{n.label}</span>
            {n.badge ? <span className="badge">{n.badge}</span> : null}
          </div>
        ))}
        <div className="side-foot" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", gap: 10, alignItems: "center", minWidth: 0 }}>
            <Initials name={user.full_name} className="avatar lg" />
            <div style={{ minWidth: 0 }}>
              <div style={{ fontWeight: 650, fontSize: 13, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{user.full_name}</div>
              <div style={{ fontSize: 11, color: "var(--text-muted)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{user.email}</div>
            </div>
          </div>
          <button 
            className="icon-btn" 
            title="Log out"
            onClick={async () => {
              if (API_BASE) {
                await fetch(`${API_BASE}/auth/logout`, { method: "POST", credentials: "include" });
                window.location.reload();
              }
            }}
          >
            <X size={15} />
          </button>
        </div>
      </aside>

      {/* ============ CENTER ============ */}
      <main className="center">
        <header className="topbar">
          <button className="icon-btn" onClick={() => window.innerWidth <= 860 ? setNavOpen(true) : setSidebarCollapsed(c => !c)} title="Toggle sidebar"><Menu size={18} /></button>

          <ThemePicker current={theme} onChange={handleThemeChange} />
          { <div className="greet">
            <div className="greet"><span className="greet-text">{greeting},</span> <span className="greet-name">{user.full_name.split(' ')[0]}</span></div>
            {/* { <p>{dateStr} · Here's everything across your workspace</p>} */}
          </div> }
          <div className="search">
            <Search size={15} />
            <input placeholder="Search messages, events, repos…" />
          </div>
          <div title={mode === "live" ? "Connected to your backend — showing live data"
              : mode === "loading" ? "Connecting to backend…"
              : "Backend not reachable — showing demo data"}
            style={{ display: "flex", alignItems: "center", gap: 7, padding: "8px 12px",
              borderRadius: 11, border: "1px solid var(--border)", background: "var(--inset)",
              fontSize: 12, fontWeight: 600, flex: "none",
              color: mode === "live" ? "var(--success)" : mode === "loading" ? "var(--danger)" : "var(--text-muted)" }}>
            <span style={{ width: 8, height: 8, borderRadius: "50%",
              background: mode === "live" ? "var(--success)" : mode === "loading" ? "var(--danger)" : "var(--text-muted)" }}
              className={mode === "live" ? "" : ""} />
            {/* {mode === "live" ? "Live" : mode === "loading" ? "Syncing" : "Demo"} */}
          </div>
          <button className="icon-btn"><Bell size={17} /><span className="dot" /></button>
        </header>

        <div className="scroll">
          {view === "dashboard" && <Dashboard data={data} events={events} todayEvents={todayEvents}
            unreadSlack={unreadSlack} unreadEmail={unreadEmail} onNewEvent={() => setNewEvent(true)} go={go} onConnect={liveConnect} connections={connections} />}
          {view === "calendar" && <CalendarView events={events} onNew={() => setNewEvent(true)} />}
          {view === "messages" && <MessagesView slack={data.slack} slackConnected={connections?.slack?.connected} onConnect={liveConnect} onDisconnect={() => {
            if (API_BASE && mode === "live") {
              fetch(`${API_BASE}/auth/slack/disconnect`, { method: "POST", credentials: "include" })
                .then(() => setConnections(p => ({ ...p, slack: { connected: false } })));
            }
          }} />}
          {view === "github" && <GithubView github={data.github} connections={connections} setConnections={setConnections} />}
          {view === "email" && <EmailView email={data.email} connections={connections} setConnections={setConnections} />}
          {view === "settings" && (
            <SettingsErrorBoundary>
              <SettingsView integrations={data.integrations} mode={mode} onConnect={liveConnect} connections={connections} setConnections={setConnections} />
            </SettingsErrorBoundary>
          )}
        </div>
      </main>

      {/* ============ ASSISTANT FLOATING BUBBLE ============ */}
      {!assistOpen && (
        <button
          onClick={() => setAssistOpen(true)}
          title="Open assistant"
          style={{
            position: "fixed", bottom: 24, right: 24, zIndex: 1000,
            width: 48, height: 48, borderRadius: "50%",
            background: "var(--primary)", border: "none", cursor: "pointer",
            display: "grid", placeItems: "center",
            boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
            color: "#fff", transition: "transform .15s, box-shadow .15s",
          }}
          onMouseEnter={e => { e.currentTarget.style.transform = "scale(1.08)"; e.currentTarget.style.boxShadow = "0 6px 20px rgba(0,0,0,0.4)"; }}
          onMouseLeave={e => { e.currentTarget.style.transform = "scale(1)"; e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.3)"; }}
        >
          <MessageCircle size={22} />
        </button>
      )}
      {assistOpen && (
        <div style={{
          position: "fixed", bottom: 24, right: 24, zIndex: 1000,
          width: 360, maxHeight: 500,
          background: "var(--surface)", border: "1px solid var(--border)",
          borderRadius: 16, display: "flex", flexDirection: "column",
          boxShadow: "0 20px 60px rgba(0,0,0,0.5)", overflow: "hidden",
        }}>
          <AssistantPanel
            onClose={() => setAssistOpen(false)}
            data={data} events={events} addEvent={addEvent} mode={mode}
            unreadSlack={unreadSlack} unreadEmail={unreadEmail} todayEvents={todayEvents}
            user={user}
          />
        </div>
      )}

      {/* ============ ONBOARDING ============ */}
      {onboard && (
        <Onboarding
          user={user}
          integrations={data.integrations}
          mode={mode}
          onConnect={liveConnect}
          onDone={finishOnboarding}
        />
      )}
      {newEvent && <NewEventModal onClose={() => setNewEvent(false)} onAdd={addEvent} />}
    </div>
  );
}

/* ---------------------------- Dashboard ---------------------------- */
function Dashboard({ data, events, todayEvents, unreadSlack, unreadEmail, onNewEvent, go, onConnect, connections }) {
  const { next, text } = useCountdown(events);
  const [expandedCard, setExpandedCard] = useState(null);
  const toggleExpand = (id) => setExpandedCard(prev => prev === id ? null : id);
  const slackConnected = connections?.slack?.connected;
  const gcalConnected = connections?.calendar?.connected || data.calendar?.length > 0;
  const ghConnected = connections?.github?.connected;
  const emailConnected = connections?.email?.connected;
  const stats = [
    { n: unreadSlack, l: "Slack mentions", ic: AtSign, c: "var(--slack)" },
    { n: todayEvents.length, l: "Meetings today", ic: Calendar, c: "var(--gcal)" },
    { n: unreadEmail, l: "Unread emails", ic: Mail, c: "var(--email)" },
    { n: data.github.length, l: "Repo updates", ic: GitCommit, c: "var(--teal)" },
  ];
  return (
    <div className="grid">
      {/* hero countdown */}
      <div className="hero" style={{ justifyContent: "center" }}>
        <div className="glyph"><Clock size={26} color="currentColor" /></div>
        <div style={{ minWidth: 0 }}>
          <div className="eyebrow">Next up</div>
          <h2>{next ? next.title : "You're all clear"}</h2>
          <div className="meta">
            {next && <span><Clock size={14} /> {fmtTime(next.start)}</span>}
            {next?.location && <span><Video size={14} /> {next.location}</span>}
            {next?.attendees && <span><Users size={14} /> {next.attendees} people</span>}
          </div>
        </div>
        {next && (
          <div className="count">
            <div className="num hw-display">{text}</div>
            <div className="lbl">until it starts</div>
          </div>
        )}
      </div>

      {/* stat strip */}
      <div className="stats">
        {stats.map((s, i) => (
          <div className="stat" key={i} style={{ animationDelay: `${i * 0.05}s` }}>
            <div className="ic" style={{ background: `color-mix(in srgb, ${s.c} 16%, transparent)` }}><s.ic size={15} color={s.c} /></div>
            <div className="n hw-display">{s.n}</div>
            <div className="l">{s.l}</div>
          </div>
        ))}
      </div>

      {/* Slack */}
      <Card icon={SlackIcon} color="var(--slack)" title="Slack" sub={slackConnected ? "Mentions & messages" : "Not connected"}
        cardId="slack" expandedCard={expandedCard} onExpand={toggleExpand}
        action={slackConnected
          ? <a className="link-btn" href="https://slack.com" target="_blank" rel="noreferrer">Open <ExternalLink size={12} /></a>
          : <button type="button" className="btn sm" onClick={() => onConnect("slack")}>Connect</button>}>
        {slackConnected && data.slack.mentions && data.slack.mentions.length > 0 ? data.slack.mentions.slice(0, 3).map((m) => (
          <div className="row" key={m.id}>
            <Initials name={m.from} />
            <div className="body">
              <div className="top">
                {m.unread && <span className="unread-dot" />}
                <span className="name">{m.from}</span>
                <span className="pill" style={{ background: "var(--inset)", color: "var(--text-muted)", border: "1px solid var(--border)" }}>{m.channel}</span>
                <span className="time">{m.time}</span>
              </div>
              <div className="text">{m.text}</div>
            </div>
          </div>
        )) : (
          <div className="empty-state">
            <div className="text">{slackConnected ? "No recent mentions" : "Connect Slack to see your mentions here"}</div>
            {!slackConnected && <button className="btn sm" onClick={() => onConnect("slack")}>Connect Slack</button>}
          </div>
        )}
      </Card>

      {/* Calendar */}
      <Card icon={Calendar} color="var(--gcal)" title="Today's schedule"
        cardId="calendar" expandedCard={expandedCard} onExpand={toggleExpand}
        sub={gcalConnected ? (todayEvents.length > 0 ? `${todayEvents.length} event${todayEvents.length !== 1 ? "s" : ""}` : "No events today") : "Not connected"}
        action={gcalConnected
          ? <button type="button" className="btn sm" onClick={onNewEvent}><Plus size={12} /> New event</button>
          : <button type="button" className="btn sm primary" onClick={() => onConnect("gcal")}>Connect</button>}>
        {gcalConnected ? (todayEvents.length > 0 ? todayEvents.map((e) => (
          <div className="row" key={e.id} style={{ opacity: e.done ? 0.5 : 1 }}>
            <div style={{ textAlign: "center", flex: "none", width: 52 }}>
              <div style={{ fontSize: 13, fontWeight: 700 }}>{fmtTime(e.start)}</div>
              <div style={{ fontSize: 10, color: "var(--text-muted)" }}>{e.done ? "done" : fmtTime(e.end)}</div>
            </div>
            <div className="body">
              <div className="top">
                <span className="name">{e.title}</span>
                <span className={`pill ${PRIO[e.priority][1]}`} style={{ marginLeft: "auto" }}>{PRIO[e.priority][0]}</span>
              </div>
              <div className="text" style={{ display: "flex", gap: 12, color: "var(--text-secondary)" }}>
                {e.meet ? <span style={{ display: "inline-flex", gap: 5, alignItems: "center" }}><Video size={12} /> Google Meet</span>
                  : <span>{e.location}</span>}
              </div>
            </div>
          </div>
        )) : (
          <div className="empty-state"><div className="text">No events today</div></div>
        )) : (
          <div className="empty-state">
            <Calendar size={28} color="var(--text-muted)" />
            <div className="text">Connect Google Calendar to see your schedule</div>
            <button className="btn sm primary" onClick={() => onConnect("gcal")}><Calendar size={12} /> Connect Google Calendar</button>
          </div>
        )}
      </Card>

      {/* GitHub */}
      <Card icon={Github} color="var(--gh)" title="GitHub activity" sub={ghConnected ? "Recent commits & PRs" : "Not connected"}
        cardId="github" expandedCard={expandedCard} onExpand={toggleExpand}
        action={ghConnected
          ? <a className="link-btn" href="https://github.com" target="_blank" rel="noreferrer">Open <ExternalLink size={12} /></a>
          : <button type="button" className="btn sm" onClick={() => onConnect("gh")}>Connect</button>}>
        {ghConnected && data.github.length > 0 ? data.github.slice(0, 4).map((g) => (
          <div className="row" key={g.id}>
            <Initials name={g.actor} />
            <div className="body">
              <div className="top">
                <span className="name"><b>{g.actor}</b></span>
                <span className="time">{g.time} ago</span>
              </div>
              <div className="text">{g.action} to <b>{g.repo}</b> — {g.message}</div>
            </div>
          </div>
        )) : (
          <div className="empty-state">
            <div className="text">{ghConnected ? "No recent activity" : "Connect GitHub to see your activity here"}</div>
            {!ghConnected && <button className="btn sm" onClick={() => onConnect("gh")}>Connect GitHub</button>}
          </div>
        )}
      </Card>

      {/* Email */}
      <Card icon={Mail} color="var(--email)" title="Inbox"
        cardId="email" expandedCard={expandedCard} onExpand={toggleExpand}
        sub={emailConnected ? `${data.email.filter((e) => e.unread).length} unread` : "Not connected"}
        action={emailConnected
          ? <a className="link-btn" href="https://mail.google.com" target="_blank" rel="noreferrer">Open <ExternalLink size={12} /></a>
          : <button type="button" className="btn sm" onClick={() => onConnect("email")}>Connect</button>}>
        {emailConnected && data.email.length > 0 ? data.email.slice(0, 4).map((e) => (
          <div className="row" key={e.id}>
            <Initials name={e.from} />
            <div className="body">
              <div className="top">
                {e.unread && <span className="unread-dot" />}
                <span className="name">{e.from}</span>
                {e.important && <span className="pill tag-imp">Important</span>}
                <span className="time">{e.time}</span>
              </div>
              <div className="text"><b>{e.subject}</b> — {e.preview}</div>
            </div>
          </div>
        )) : (
          <div className="empty-state">
            <div className="text">{emailConnected ? "No new emails" : "Connect Gmail to see your inbox here"}</div>
            {!emailConnected && <button className="btn sm" onClick={() => onConnect("email")}>Connect Gmail</button>}
          </div>
        )}
      </Card>
    </div>
  );
}

function Card({ icon: Ic, color, title, sub, action, children, className = "", cardId, expandedCard, onExpand }) {
  const isExpanded = !!onExpand && expandedCard === cardId;
  const isMinimized = !!onExpand && expandedCard !== null && expandedCard !== cardId;
  const cardClass = `card${className ? ` ${className}` : ""}${isExpanded ? " expanded" : ""}${isMinimized ? " minimized" : ""}`;

  return (
    <section className={cardClass} onClick={isMinimized ? () => onExpand(cardId) : undefined}>
      <div className="card-h">
        <div className="ic" style={{ background: `color-mix(in srgb, ${color} 18%, transparent)`, border: `1px solid color-mix(in srgb, ${color} 30%, transparent)` }}>
          <Ic size={16} color={color} />
        </div>
        <div>
          <h3>{title}</h3>
          <div className="sub">{sub}</div>
        </div>
        {(action || onExpand) && (
          <div className="right">
            {action}
            {onExpand && (
              <button
                className="icon-btn"
                style={{ width: 24, height: 24, border: "none", flexShrink: 0 }}
                onClick={(e) => { e.stopPropagation(); onExpand(cardId); }}
                title={isExpanded ? "Collapse" : "Expand"}
              >
                {isExpanded ? <Minimize2 size={12} /> : <Maximize2 size={12} />}
              </button>
            )}
          </div>
        )}
      </div>
      <div className="card-b">{children}</div>
    </section>
  );
}


/* ---------------------------- Calendar view ---------------------------- */
function CalendarView({ events, onNew }) {
  const today = new Date();
  const [viewDate, setViewDate] = useState(new Date(today.getFullYear(), today.getMonth(), 1));
  const [selectedDate, setSelectedDate] = useState(today);

  const year = viewDate.getFullYear();
  const month = viewDate.getMonth();

  const byDate = useMemo(() => {
    const m = {};
    events.forEach((e) => { const k = e.start.toDateString(); (m[k] = m[k] || []).push(e); });
    return m;
  }, [events]);

  const firstDow = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const cells = [];
  for (let i = 0; i < firstDow; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(new Date(year, month, d));

  const selEvents = (byDate[selectedDate.toDateString()] || []).sort((a, b) => a.start - b.start);
  const monthLabel = viewDate.toLocaleDateString([], { month: "long", year: "numeric" });
  const DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  const isToday = (d) => d && d.toDateString() === today.toDateString();
  const isSel = (d) => d && d.toDateString() === selectedDate.toDateString();

  return (
    <div>
      <ViewHead title="Calendar" sub={monthLabel}
        action={<button className="btn primary" onClick={onNew}><Plus size={15} /> New event</button>} />

      {/* Month grid */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ padding: "18px 20px 14px" }}>
          {/* Nav header */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
            <button className="btn" style={{ padding: "4px 8px", minWidth: 0, height: "auto" }}
              onClick={() => setViewDate(new Date(year, month - 1, 1))}>
              <ChevronLeft size={16} />
            </button>
            <span style={{ fontWeight: 700, fontSize: 14, color: "var(--text)" }}>{monthLabel}</span>
            <button className="btn" style={{ padding: "4px 8px", minWidth: 0, height: "auto" }}
              onClick={() => setViewDate(new Date(year, month + 1, 1))}>
              <ChevronRight size={16} />
            </button>
          </div>

          {/* Day-of-week headers */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 2, marginBottom: 4 }}>
            {DOW.map((d) => (
              <div key={d} style={{ textAlign: "center", fontSize: 11, fontWeight: 600, color: "var(--text-muted)", padding: "2px 0" }}>{d}</div>
            ))}
          </div>

          {/* Day cells */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 2 }}>
            {cells.map((day, i) => {
              const hasDot = day && byDate[day.toDateString()]?.length > 0;
              const sel = isSel(day);
              const tod = isToday(day);
              return (
                <div key={i} onClick={() => day && setSelectedDate(day)}
                  style={{
                    textAlign: "center", padding: "6px 2px 4px", borderRadius: 8, fontSize: 13,
                    cursor: day ? "pointer" : "default",
                    background: sel ? "var(--primary)" : tod ? "color-mix(in srgb, var(--primary) 14%, transparent)" : "transparent",
                    color: sel ? "#fff" : tod ? "var(--primary)" : day ? "var(--text)" : "transparent",
                    fontWeight: tod || sel ? 700 : 400,
                    transition: "background .12s",
                  }}>
                  {day?.getDate()}
                  {hasDot && (
                    <div style={{ width: 4, height: 4, borderRadius: "50%", margin: "2px auto 0",
                      background: sel ? "rgba(255,255,255,0.7)" : "var(--gcal)" }} />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Events for selected date */}
      <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: ".08em", marginBottom: 12 }}>
        {isToday(selectedDate) ? "Today · " : ""}
        {selectedDate.toLocaleDateString([], { weekday: "long", month: "long", day: "numeric" })}
      </div>

      {selEvents.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "32px 20px", color: "var(--text-muted)", fontSize: 13 }}>
          No events scheduled for this day
        </div>
      ) : (
        <div className="card"><div className="card-b">
          {selEvents.map((e) => (
            <div className="row" key={e.id} style={{ opacity: e.done ? 0.5 : 1 }}>
              <div style={{ width: 4, alignSelf: "stretch", borderRadius: 4,
                background: `var(--${e.priority === "high" ? "rose" : e.priority === "medium" ? "amber" : "green"})` }} />
              <div style={{ textAlign: "center", width: 56, flex: "none" }}>
                <div style={{ fontWeight: 700, fontSize: 13 }}>{fmtTime(e.start)}</div>
                <div style={{ fontSize: 10, color: "var(--text-muted)" }}>{fmtTime(e.end)}</div>
              </div>
              <div className="body">
                <div className="top">
                  <span className="name" style={{ fontSize: 14 }}>{e.title}</span>
                  <span className={`pill ${PRIO[e.priority][1]}`} style={{ marginLeft: "auto" }}>{PRIO[e.priority][0]}</span>
                </div>
                <div className="text" style={{ display: "flex", gap: 12 }}>
                  {e.meet
                    ? <span style={{ display: "inline-flex", gap: 5, alignItems: "center" }}><Video size={12} /> Google Meet</span>
                    : e.location && <span style={{ display: "inline-flex", gap: 5, alignItems: "center" }}><Calendar size={12} /> {e.location}</span>}
                  {e.attendees > 0 && <span style={{ display: "inline-flex", gap: 5, alignItems: "center" }}><Users size={12} /> {e.attendees}</span>}
                </div>
              </div>
              {e.meet && <a className="btn" style={{ alignSelf: "center" }} href="https://meet.google.com" target="_blank" rel="noreferrer"><Video size={14} /> Join</a>}
            </div>
          ))}
        </div></div>
      )}
    </div>
  );
}

/* ---------------------------- Messages (Slack) ---------------------------- */
function MessagesView({ slack, slackConnected, onConnect, onDisconnect }) {
  if (!slackConnected) {
    return (
      <div>
        <ViewHead title="Slack" sub="Slack mentions & direct messages" />
        <div style={{ textAlign: "center", padding: "60px 20px", background: "var(--card)", borderRadius: "var(--radius)", border: "1px solid var(--border)", marginTop: 20 }}>
          <SlackIcon size={48} color="var(--text-muted)" style={{ margin: "0 auto 16px" }} />
          <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8, color: "var(--text)" }}>Connect your Slack</h2>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, marginBottom: 24, maxWidth: 400, margin: "0 auto" }}>View your recent mentions and direct messages directly on your dashboard.</p>
          <button className="btn" style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--text)", width: "auto", margin: "0 auto" }} onClick={() => onConnect("slack")}><SlackIcon size={14} /> Connect Slack</button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <ViewHead title="Slack" sub="Slack mentions & direct messages"
        action={
          <div style={{ display: "flex", gap: 10 }}>
            <button className="btn" style={{ color: "var(--danger)", borderColor: "var(--border)" }} onClick={onDisconnect}>Disconnect</button>
            <a className="btn primary" href="https://slack.com" target="_blank" rel="noreferrer"><ExternalLink size={14} /> Open in Slack</a>
          </div>
        } />
      <div className="grid">
        <Card icon={AtSign} color="var(--slack)" title="Mentions" sub="People who tagged you"
          action={<a className="link-btn" href="https://slack.com" target="_blank" rel="noreferrer">Open <ExternalLink size={12} /></a>}>
          {slack.mentions && slack.mentions.length > 0 ? slack.mentions.map((m) => (
            <div className={`row ${(m.id).unread || (m.id).isUnread ? "unread" : ""}`} key={m.id}>
              <Initials name={m.from} />
              <div className="body">
                <div className="top">{m.unread && <span className="unread-dot" />}<span className="name">{m.from}</span>
                  <span className="pill" style={{ background: "var(--inset)", color: "var(--text-muted)", border: "1px solid var(--border)" }}>{m.channel}</span>
                  <span className="time">{m.time}</span></div>
                <div className="text">{m.text}</div>
              </div>
              <a className="link-btn" style={{ alignSelf: "center" }} href="https://slack.com" target="_blank" rel="noreferrer">Reply <ArrowUpRight size={12} /></a>
            </div>
          )) : (
            <div style={{ color: "var(--text-muted)", fontSize: 13, textAlign: "center", padding: "10px 0" }}>No mentions</div>
          )}
        </Card>
        <Card icon={MessageSquare} color="var(--blue)" title="Direct messages" sub="Recent conversations">
          {slack.dms && slack.dms.length > 0 ? slack.dms.map((m) => (
            <div className={`row ${(m.id).unread || (m.id).isUnread ? "unread" : ""}`} key={m.id}>
              <Initials name={m.from} />
              <div className="body">
                <div className="top">{m.unread && <span className="unread-dot" />}<span className="name">{m.from}</span><span className="time">{m.time}</span></div>
                <div className="text">{m.text}</div>
              </div>
              <a className="link-btn" style={{ alignSelf: "center" }} href="https://slack.com" target="_blank" rel="noreferrer">Open <ArrowUpRight size={12} /></a>
            </div>
          )) : (
            <div style={{ color: "var(--text-muted)", fontSize: 13, textAlign: "center", padding: "10px 0" }}>No direct messages</div>
          )}
        </Card>
      </div>
    </div>
  );
}

/* ---------------------------- GitHub view ---------------------------- */
function GithubView({ connections, setConnections }) {
  const connected = connections?.github?.connected;
  const [status, setStatus] = useState(connected ? "loading" : "disconnected"); // loading, connected, disconnected, rate_limited, error
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!API_BASE) return;
    let alive = true;
    if (connected) {
      setStatus("loading");
      fetch(`${API_BASE}/github/summary`, { credentials: "include" })
        .then(r => {
          if (!alive) return null;
          if (r.status === 401) { setStatus("disconnected"); setConnections(p => ({ ...p, github: { connected: false } })); return null; }
          if (r.status === 429) { setStatus("rate_limited"); return null; }
          if (!r.ok) throw new Error("bad status");
          return r.json();
        })
        .then(summary => {
          if (alive && summary) { setData(summary); setStatus("connected"); }
        })
        .catch(() => { if (alive) setStatus("error"); });
    } else {
      setStatus("disconnected");
    }
    return () => { alive = false; };
  }, [connected, setConnections]);

  const disconnect = () => {
    setStatus("loading");
    fetch(`${API_BASE}/auth/github/disconnect`, { method: "POST", credentials: "include" })
      .then(() => setConnections(p => ({ ...p, github: { connected: false } })))
      .catch(() => setConnections(p => ({ ...p, github: { connected: false } })));
  };
  const connect = () => {
    window.location.href = `${API_BASE}/auth/github/login`;
  };

  const timeAgo = (ds) => {
    if (!ds) return "";
    const m = Math.floor((Date.now() - new Date(ds).getTime()) / 60000);
    if (m < 60) return `${Math.max(0, m)}m ago`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h ago`;
    return `${Math.floor(h / 24)}d ago`;
  };

  const renderList = (items, title, icon, emptyText, renderItem) => (
    <div style={{ marginBottom: 24 }}>
      <h3 style={{ fontSize: 14, fontWeight: 650, marginBottom: 12, display: "flex", alignItems: "center", gap: 8 }}>
        {icon} {title} <span style={{ fontSize: 11, color: "var(--text-secondary)", fontWeight: 500, background: "var(--inset)", padding: "2px 6px", borderRadius: 10 }}>{items?.length || 0}</span>
      </h3>
      <div className="card"><div className="card-b" style={{ padding: items?.length ? "8px" : "16px 20px" }}>
        {items && items.length > 0 ? items.map(renderItem) : (
          <div style={{ color: "var(--text-muted)", fontSize: 13, textAlign: "center", padding: "10px 0" }}>{emptyText}</div>
        )}
      </div></div>
    </div>
  );

  return (
    <div>
      <ViewHead title="GitHub" sub="Notifications, PRs, Issues & Activity"
        action={
          status === "connected" ? (
            <button className="link-btn" onClick={disconnect} style={{ color: "var(--text-muted)", background: "transparent", border: "none" }}>Disconnect</button>
          ) : status === "disconnected" ? (
            <button className="btn primary" onClick={connect}><Github size={14} /> Connect GitHub</button>
          ) : null
        } />
      
      {status === "loading" && <div style={{ color: "var(--text-secondary)", fontSize: 14, padding: "20px 0" }}>Loading...</div>}
      
      {status === "rate_limited" && <div style={{ color: "var(--danger)", fontSize: 14, padding: "16px 20px", background: "rgba(245,181,68,0.1)", border: "1px solid rgba(245,181,68,0.2)", borderRadius: 12, marginBottom: 20 }}>GitHub rate limit reached, try again later.</div>}
      
      {status === "error" && <div style={{ color: "var(--rose)", fontSize: 14, padding: "16px 20px", background: "rgba(255,107,138,0.1)", border: "1px solid rgba(255,107,138,0.2)", borderRadius: 12, marginBottom: 20 }}>An error occurred while fetching GitHub data.</div>}
      
      {status === "disconnected" && (
        <div style={{ textAlign: "center", padding: "60px 20px", background: "var(--card)", borderRadius: "var(--radius)", border: "1px solid var(--border-soft)", marginTop: 20 }}>
          <Github size={48} color="var(--text-muted)" style={{ margin: "0 auto 16px" }} />
          <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>Connect your GitHub</h2>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, marginBottom: 24, maxWidth: 400, margin: "0 auto" }}>View your notifications, review requests, assigned issues, and recent activity right from your dashboard.</p>
          <button className="btn primary" onClick={connect}><Github size={14} /> Connect GitHub</button>
        </div>
      )}

      {status === "connected" && data && (
        <div className="grid" style={{ marginTop: 20 }}>
          <div style={{ display: "flex", flexDirection: "column" }}>
            {renderList(data.notifications, "Notifications", <Bell size={15} color="var(--danger)" />, "No new notifications", (n) => (
              <a href={n.url} target="_blank" rel="noreferrer" className={`row ${(n.id).unread || (n.id).isUnread ? "unread" : ""}`} key={n.id} style={{ textDecoration: "none", color: "inherit", display: "flex" }}>
                <div className="ic" style={{ width: 34, height: 34, borderRadius: 10, background: "var(--inset)", border: "1px solid var(--border)", display: "grid", placeItems: "center", flex: "none" }}>
                  <Bell size={15} color="var(--danger)" />
                </div>
                <div className="body">
                  <div className="top">
                    {n.unread && <span className="unread-dot" />}
                    <span className="name"><b>{n.repo}</b></span>
                    <span className="time">{timeAgo(n.updated_at)}</span>
                  </div>
                  <div className="text">{n.title} <span style={{ color: "var(--text-muted)" }}>({n.reason})</span></div>
                </div>
              </a>
            ))}
            
            {renderList(data.pull_requests, "Pull requests awaiting review", <GitCommit size={15} color="var(--teal)" />, "No PRs waiting for your review", (pr) => (
              <a href={pr.url} target="_blank" rel="noreferrer" className={`row ${(pr.id).unread || (pr.id).isUnread ? "unread" : ""}`} key={pr.id} style={{ textDecoration: "none", color: "inherit", display: "flex" }}>
                <div className="ic" style={{ width: 34, height: 34, borderRadius: 10, background: "var(--inset)", border: "1px solid var(--border)", display: "grid", placeItems: "center", flex: "none" }}>
                  <GitCommit size={15} color="var(--teal)" />
                </div>
                <div className="body">
                  <div className="top"><span className="name"><b>{pr.repo}</b></span><span className="time">{timeAgo(pr.updated_at)}</span></div>
                  <div className="text">{pr.title}</div>
                </div>
              </a>
            ))}
          </div>
          
          <div style={{ display: "flex", flexDirection: "column" }}>
            {renderList(data.assigned_issues, "Assigned issues", <CheckCircle2 size={15} color="var(--rose)" />, "No open issues assigned to you", (iss) => (
              <a href={iss.url} target="_blank" rel="noreferrer" className={`row ${(iss.id).unread || (iss.id).isUnread ? "unread" : ""}`} key={iss.id} style={{ textDecoration: "none", color: "inherit", display: "flex" }}>
                <div className="ic" style={{ width: 34, height: 34, borderRadius: 10, background: "var(--inset)", border: "1px solid var(--border)", display: "grid", placeItems: "center", flex: "none" }}>
                  <CheckCircle2 size={15} color="var(--rose)" />
                </div>
                <div className="body">
                  <div className="top"><span className="name"><b>{iss.repo}</b></span><span className="time">{timeAgo(iss.updated_at)}</span></div>
                  <div className="text">{iss.title}</div>
                </div>
              </a>
            ))}

            {renderList(data.recent_activity, "Recent activity", <Github size={15} color="var(--gh)" />, "No recent activity", (act, i) => (
              <div className={`row ${(i).unread || (i).isUnread ? "unread" : ""}`} key={i} style={{ display: "flex" }}>
                <div className="ic" style={{ width: 34, height: 34, borderRadius: 10, background: "var(--inset)", border: "1px solid var(--border)", display: "grid", placeItems: "center", flex: "none" }}>
                  <Github size={15} color="var(--gh)" />
                </div>
                <div className="body">
                  <div className="top"><span className="name"><b>{act.repo}</b></span><span className="time">{timeAgo(act.created_at)}</span></div>
                  <div className="text">{act.summary}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/* ---------------------------- Email view ---------------------------- */
function EmailView({ connections, setConnections }) {
  const connected = connections?.email?.connected;
  const emailAddress = connections?.email?.email_address;
  const [status, setStatus] = useState(connected ? "loading" : "disconnected"); // loading, connected, disconnected, error
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!API_BASE) return;
    let alive = true;
    if (connected) {
      setStatus("loading");
      fetch(`${API_BASE}/email/messages`, { credentials: "include" })
        .then(r => {
          if (!alive) return null;
          if (r.status === 401) { setStatus("disconnected"); setConnections(p => ({ ...p, email: { connected: false } })); return null; }
          if (!r.ok) throw new Error("bad status");
          return r.json();
        })
        .then(payload => {
          if (alive && payload) { setData(payload); setStatus("connected"); }
        })
        .catch(() => { if (alive) setStatus("error"); });
    } else {
      setStatus("disconnected");
    }
    return () => { alive = false; };
  }, [connected, setConnections]);

  const disconnect = () => {
    setStatus("loading");
    fetch(`${API_BASE}/auth/google/disconnect`, { method: "POST", credentials: "include" })
      .then(() => setConnections(p => ({ ...p, email: { connected: false } })))
      .catch(() => setConnections(p => ({ ...p, email: { connected: false } })));
  };

  const connect = () => {
    window.location.href = `${API_BASE}/auth/google/login`;
  };

  const timeAgo = (ds) => {
    if (!ds) return "";
    const m = Math.floor((Date.now() - new Date(ds).getTime()) / 60000);
    if (m < 60) return `${Math.max(0, m)}m ago`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h ago`;
    return `${Math.floor(h / 24)}d ago`;
  };

  return (
    <div>
      <ViewHead title="Inbox" sub={emailAddress ? `Connected as ${emailAddress}` : "Recent emails"}
        action={
          status === "connected" ? (
            <button className="link-btn" onClick={disconnect} style={{ color: "var(--text-muted)", background: "transparent", border: "none" }}>Disconnect</button>
          ) : status === "disconnected" ? (
            <button className="btn primary" onClick={connect}><Mail size={14} /> Connect Gmail</button>
          ) : null
        } />
      
      {status === "loading" && <div style={{ color: "var(--text-secondary)", fontSize: 14, padding: "20px 0" }}>Loading...</div>}
      
      {status === "error" && <div style={{ color: "var(--rose)", fontSize: 14, padding: "16px 20px", background: "rgba(255,107,138,0.1)", border: "1px solid rgba(255,107,138,0.2)", borderRadius: 12, marginBottom: 20 }}>An error occurred while fetching emails.</div>}
      
      {status === "disconnected" && (
        <div style={{ textAlign: "center", padding: "60px 20px", background: "var(--card)", borderRadius: "var(--radius)", border: "1px solid var(--border-soft)", marginTop: 20 }}>
          <Mail size={48} color="var(--text-muted)" style={{ margin: "0 auto 16px" }} />
          <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>Connect your Gmail</h2>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, marginBottom: 24, maxWidth: 400, margin: "0 auto" }}>View your recent inbox messages directly on your dashboard.</p>
          <button className="btn primary" onClick={connect}><Mail size={14} /> Connect Gmail</button>
        </div>
      )}

      {status === "connected" && data && (
        <div className="card" style={{ marginTop: 20 }}><div className="card-b" style={{ padding: data.messages?.length ? "8px" : "16px 20px" }}>
          {data.messages && data.messages.length > 0 ? data.messages.map((e) => (
            <div className={`row ${(e.id).unread || (e.id).isUnread ? "unread" : ""}`} key={e.id}>
              <Initials name={e.sender} />
              <div className="body">
                <div className="top">
                  {e.unread && <span className="unread-dot" />}
                  <span className="name" >{e.sender}</span>
                  <span className="time">{timeAgo(e.received_at)}</span>
                </div>
                <div className="text" >
                  <b >{e.subject}</b> — {e.snippet}
                </div>
              </div>
              <div style={{ display: "flex", gap: 6, alignSelf: "center" }}>
                <a className="icon-btn" style={{ width: 34, height: 34 }} href={`https://mail.google.com/mail/u/0/#inbox/${e.id}`} target="_blank" rel="noreferrer"><ExternalLink size={15} /></a>
              </div>
            </div>
          )) : (
            <div style={{ color: "var(--text-muted)", fontSize: 13, textAlign: "center", padding: "10px 0" }}>No new emails</div>
          )}
        </div></div>
      )}
    </div>
  );
}

/* ---------------------------- Settings Error Boundary ---------------------------- */
class SettingsErrorBoundary extends React.Component {
  state = { hasError: false };
  static getDerivedStateFromError() { return { hasError: true }; }
  render() {
    if (this.state.hasError)
      return (
        <div style={{ padding: 24, color: "var(--danger)" }}>
          Settings failed to load. Try refreshing.
        </div>
      );
    return this.props.children;
  }
}

/* ---------------------------- Settings ---------------------------- */
function SettingsView({ integrations, mode, onConnect, connections, setConnections }) {
  const [activeFont, setActiveFont] = useState(
    () => localStorage.getItem("workspace-font") || "Inter"
  );
  const live = mode === "live";
  const oauthIds = ["gh", "gcal", "email", "slack"];

  const handleDisconnect = (itId) => {
    const internalToApi = { gh: "github", gcal: "google", email: "google", slack: "slack" };
    const internalToConnections = { gh: "github", gcal: "calendar", email: "email", slack: "slack" };
    
    if (!live) {
      setConnections((p) => ({ ...p, [internalToConnections[itId]]: { connected: false } }));
      return;
    }
    const path = internalToApi[itId];
    if (path && API_BASE) {
      fetch(`${API_BASE}/auth/${path}/disconnect`, { method: "POST", credentials: "include" })
        .then(() => setConnections((p) => ({ ...p, [internalToConnections[itId]]: { connected: false } })))
        .catch(() => {});
    } else {
      setConnections((p) => ({ ...p, [internalToConnections[itId]]: { connected: false } }));
    }
  };

  const handleFontSelect = (font) => {
    applyPreferences({ font: font.value });
    setActiveFont(font.value);
    if (API_BASE) {
      fetch(`${API_BASE}/preferences`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        credentials: "include", body: JSON.stringify({ font: font.value })
      }).catch(() => {});
    }
  };

  return (
    <div>
      <ViewHead title="Settings" sub="Manage your connected tools & workspace" />

      {/* Appearance section */}
      <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: ".08em", margin: "4px 0 14px" }}>Appearance</div>
      <div className="card" style={{ marginBottom: 24, padding: 20 }}>
        <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text)", marginBottom: 12 }}>Font</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {FONTS.map(font => {
            const active = activeFont === font.value;
            return (
              <button
                key={font.value}
                onClick={() => handleFontSelect(font)}
                style={{
                  fontFamily: `"${font.value}", system-ui, sans-serif`,
                  fontSize: 13,
                  padding: "7px 14px",
                  borderRadius: 8,
                  border: active ? "1.5px solid var(--primary)" : "1px solid var(--border)",
                  background: active ? "var(--primary-bg)" : "var(--surface)",
                  color: active ? "var(--primary)" : "var(--text-secondary)",
                  cursor: "pointer",
                  transition: "border .15s, background .15s, color .15s",
                  whiteSpace: "nowrap",
                }}
              >
                {font.name}
              </button>
            );
          })}
        </div>
      </div>

      {/* Integrations section */}
      <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: ".08em", margin: "4px 0 14px" }}>Integrations</div>
      <div style={{ display: "grid", gap: 12 }}>
        {integrations.map((it) => {
          const internalToConnections = { gh: "github", gcal: "calendar", email: "email", slack: "slack" };
          const Ic = intIcon[it.id]; 
          const on = connections?.[internalToConnections[it.id]]?.connected;
          const isOauth = oauthIds.includes(it.id);
          const handleConnect = () => {
            if (live && isOauth) { onConnect(it.id); return; }   // → /api/auth/{provider}/login
            setConnections((p) => ({ ...p, [internalToConnections[it.id]]: { connected: true } }));
          };
          return (
            <div className="conn-card" key={it.id}>
              <div className="conn-ic" style={{ background: `color-mix(in srgb, ${it.color} 16%, transparent)`, border: `1px solid color-mix(in srgb, ${it.color} 30%, transparent)` }}>
                <Ic size={20} color={it.color} />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 650, fontSize: 14 }}>{it.name}</div>
                <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>{it.desc}{live && it.id === "slack" ? " · OAuth" : ""}</div>
              </div>
              {on
                ? <button className="btn connected" onClick={() => handleDisconnect(it.id)}><CheckCircle2 size={15} /> Connected</button>
                : <button className="btn primary" onClick={handleConnect}>{live && isOauth ? "Connect" : "Connect"}</button>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ViewHead({ title, sub, action }) {
  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 14, marginBottom: 20 }}>
      <div>
        <h2 className="hw-display" style={{ fontSize: 24, fontWeight: 700, letterSpacing: "-.5px" }}>{title}</h2>
        <p style={{ color: "var(--text-secondary)", fontSize: 13, marginTop: 4 }}>{sub}</p>
      </div>
      {action && <div style={{ marginLeft: "auto" }}>{action}</div>}
    </div>
  );
}

/* ---------------------------- Assistant Panel (floating) ---------------------------- */
function AssistantPanel({ onClose, data, events, addEvent, mode, unreadSlack, unreadEmail, todayEvents, user }) {
  const name = `${user.full_name.split(' ')[0]}'s Assistant`;
  const [msgs, setMsgs] = useState([
    { role: "assistant", content: `Hi ${user.full_name.split(' ')[0]}! I'm your assistant. I keep an eye on your Slack, Calendar, GitHub and inbox so you don't have to tab-hop. Ask me what's happening today, or to create a meeting.` },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => { scrollRef.current?.scrollTo({ top: 9e9, behavior: "smooth" }); }, [msgs, busy]);

  const context = () => {
    const next = events.filter((e) => e.start > new Date()).sort((a, b) => a.start - b.start)[0];
    return {
      user: user.full_name, now: new Date().toString(),
      slack: { unread: unreadSlack, mentions: data.slack.mentions.map((m) => ({ from: m.from, channel: m.channel, text: m.text, when: m.time })) },
      calendar_today: todayEvents.map((e) => ({ title: e.title, time: fmtTime(e.start), priority: e.priority, location: e.location })),
      calendar_tomorrow: events.filter((e) => { const t = new Date(); t.setDate(t.getDate() + 1); return e.start.toDateString() === t.toDateString(); }).map((e) => ({ title: e.title, time: fmtTime(e.start) })),
      next_meeting: next ? { title: next.title, time: fmtTime(next.start) } : null,
      email: { unread: unreadEmail, important: data.email.filter((e) => e.important).map((e) => ({ from: e.from, subject: e.subject })) },
      github: data.github.map((g) => ({ who: g.actor, what: g.action, repo: g.repo, when: g.time })),
    };
  };

  /* offline fallback so the assistant always answers */
  const localAnswer = (q) => {
    const t = q.toLowerCase(); const c = context();
    if (/(urgent|important).*(email|mail)|email.*(urgent|important)/.test(t) || (/email|mail|inbox/.test(t) && /urgent|important/.test(t)))
      return `You have ${c.email.important.length} important email${c.email.important.length !== 1 ? "s" : ""}:\n${c.email.important.map((e) => `• ${e.from} — ${e.subject}`).join("\n")}`;
    if (/email|mail|inbox/.test(t))
      return `You've got ${c.email.unread} unread emails, ${c.email.important.length} marked important — most notably from ${c.email.important.map((e) => e.from).join(" and ")}.`;
    if (/commit|repo|github|push/.test(t))
      return `Recent GitHub activity:\n${c.github.slice(0, 3).map((g) => `• ${g.who} ${g.what} to ${g.repo} (${g.when} ago)`).join("\n")}`;
    if (/tomorrow/.test(t))
      return c.calendar_tomorrow.length ? `Tomorrow you have ${c.calendar_tomorrow.length} meetings:\n${c.calendar_tomorrow.map((e) => `• ${e.time} — ${e.title}`).join("\n")}` : "Your calendar is clear tomorrow — nice";
    if (/slack|mention|tagged/.test(t))
      return `You were mentioned by ${c.slack.mentions.map((m) => m.from).join(", ")}.\nMost recent: ${c.slack.mentions[0].from} in ${c.slack.mentions[0].channel} — "${c.slack.mentions[0].text}"`;
    if (/create|schedule|set up|add.*(meeting|event|call)|meeting.*tomorrow/.test(t)) {
      const m = t.match(/(\d{1,2})\s*(am|pm)/);
      let hh = 17; if (m) { hh = parseInt(m[1]); if (m[2] === "pm" && hh < 12) hh += 12; if (m[2] === "am" && hh === 12) hh = 0; }
      const tomorrow = /tomorrow/.test(t); const d = new Date(); if (tomorrow) d.setDate(d.getDate() + 1); d.setHours(hh, 0, 0, 0);
      const ev = { id: "ai" + Date.now(), title: "New Meeting", start: d, end: new Date(d.getTime() + 30 * 60000), priority: "medium", location: "Google Meet", meet: true };
      addEvent(ev);
      return `Done I've added "New Meeting" to your calendar for ${tomorrow ? "tomorrow" : "today"} at ${fmtTime(d)} with a Google Meet link. You can rename it from the Calendar tab.`;
    }
    if (/today|happening|summary|catch.*up|brief/.test(t) || t.length < 4) {
      const ghLine = c.github.length
        ? `• ${c.github[0].who} pushed updates to ${c.github[0].repo}`
        : "• No recent GitHub activity";
      return `Good ${new Date().getHours() < 12 ? "morning" : "afternoon"} ${user.full_name.split(' ')[0]}\nHere's your snapshot:\n• ${c.slack.unread} new Slack mentions\n• ${c.calendar_today.length} meetings today\n• ${c.email.unread} new emails (${c.email.important.length} important)\n${ghLine}\n${c.next_meeting ? `\nYour next meeting is ${c.next_meeting.title} at ${c.next_meeting.time}.` : ""}`;
    }
    return `I can summarize your day, check Slack mentions, urgent emails, GitHub activity, or tomorrow's meetings — and I can create events for you. Try "What's happening today?"`;
  };

  const send = async (text) => {
    const q = (text ?? input).trim(); if (!q || busy) return;
    const history = msgs.filter((m) => m.role !== "system").map((m) => ({ role: m.role, content: m.content }));
    setInput(""); setMsgs((p) => [...p, { role: "user", content: q }]); setBusy(true);

    // Demo create-event intent: real side-effect on the local calendar.
    if (mode !== "live" && /\b(create|schedule|set up|add)\b.*(meeting|event|call)/i.test(q)) {
      const reply = localAnswer(q);
      setTimeout(() => { setMsgs((p) => [...p, { role: "assistant", content: reply }]); setBusy(false); }, 400);
      return;
    }

    // Live: route through the backend assistant (OpenRouter / Gemma).
    if (mode === "live") {
      try {
        const res = await fetch(`${API_BASE}/assistant/query`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          credentials: "include",   // send session cookie for cross-origin requests
          body: JSON.stringify({ message: q, history }),
        });
        const json = await res.json();
        setMsgs((p) => [...p, { role: "assistant", content: json.reply || localAnswer(q) }]);
      } catch {
        setMsgs((p) => [...p, { role: "assistant", content: localAnswer(q) }]);
      } finally { setBusy(false); }
      return;
    }

    // Demo: built-in local engine (no backend reachable).
    setTimeout(() => { setMsgs((p) => [...p, { role: "assistant", content: localAnswer(q) }]); setBusy(false); }, 400);
  };

  const quick = ["What's happening today?", "Any urgent emails?", "Who committed today?", "Meetings tomorrow?"];

  return (
    <>
      {/* Panel header */}
      <div style={{
        padding: "14px 16px",
        borderBottom: "1px solid var(--border)",
        display: "flex", alignItems: "center", gap: 10,
        flex: "none",
      }}>
        <Mascot size={34} />
        <div style={{ minWidth: 0, flex: 1 }}>
          <div style={{ fontWeight: 500, fontSize: 14, display: "flex", alignItems: "center", gap: 6, color: "var(--text)" }}>
            {name} <Sparkles size={13} color="var(--primary-2)" />
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", display: "flex", alignItems: "center", gap: 5, marginTop: 2 }}>
            <span className="live"><i /></span> Online · synced just now
          </div>
        </div>
        <button
          onClick={onClose}
          style={{
            width: 28, height: 28, border: "1px solid var(--border)", borderRadius: 6,
            background: "transparent", cursor: "pointer", display: "grid", placeItems: "center",
            color: "var(--text-secondary)", flex: "none",
          }}
        >
          <X size={15} />
        </button>
      </div>

      {/* Messages area — scrollable */}
      <div className="chat" ref={scrollRef} style={{ flex: 1, overflowY: "auto", maxHeight: 300 }}>
        {msgs.map((m, i) => (
          <div key={i} className={`msg ${m.role === "user" ? "me" : "ai"}`}>
            {m.role === "assistant" && <div className="mini-mascot"><Mascot size={30} /></div>}
            <div className="bub">{m.content}</div>
          </div>
        ))}
        {busy && <div className="msg ai"><div className="mini-mascot"><Mascot size={30} /></div>
          <div className="bub" style={{ padding: 0 }}><div className="typing"><i /><i /><i /></div></div></div>}
      </div>

      <div className="quick" style={{ flex: "none" }}>
        {quick.map((q) => <button key={q} className="chip" onClick={() => send(q)} disabled={busy}>{q}</button>)}
      </div>

      <div className="composer" style={{ flex: "none" }}>
        <div className="box">
          <textarea rows={1} value={input} placeholder={`Ask ${name}…`}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }} />
          <button className="send-btn" onClick={() => send()} disabled={busy || !input.trim()}><Send size={16} /></button>
        </div>
      </div>
    </>
  );
}

/* ---------------------------- Onboarding ---------------------------- */
function Onboarding({ user, integrations, mode, onConnect, onDone }) {
  const [step, setStep] = useState(0);
  const [conn, setConn] = useState(Object.fromEntries(integrations.map((i) => [i.id, false])));
  const connectedCount = Object.values(conn).filter(Boolean).length;

  const steps = ["Welcome", "Connect apps", "Permissions", "All set"];
  const next = () => setStep((s) => Math.min(s + 1, 3));

  return (
    <div className="overlay">
      <div className="sheet">
        <div className="sheet-h">
          <div className="steps" style={{ marginBottom: 18 }}>{steps.map((_, i) => <i key={i} className={i <= step ? "on" : ""} />)}</div>
          {step === 0 && <>
            <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
              <Mascot size={52} />
              <div>
                <h2 className="hw-display" style={{ fontSize: 22, fontWeight: 700 }}>Welcome, {user.full_name.split(' ')[0]}</h2>
                <p style={{ color: "var(--text-secondary)", fontSize: 13.5, marginTop: 4 }}>Let's set up your command center.</p>
              </div>
            </div>
          </>}
          {step === 1 && <h2 className="hw-display" style={{ fontSize: 21, fontWeight: 700 }}>Connect your tools</h2>}
          {step === 2 && <h2 className="hw-display" style={{ fontSize: 21, fontWeight: 700 }}>Grant permissions</h2>}
          {step === 3 && <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <Logo size={32} />
            <h2 className="hw-display" style={{ fontSize: 22, fontWeight: 700 }}>You're all set!</h2>
          </div>}
        </div>

        <div className="sheet-b">
          {step === 0 && <p style={{ color: "var(--text-secondary)", fontSize: 14, lineHeight: 1.6 }}>
            Stop tab-hopping between Slack, Calendar, GitHub and email. Connect them once and get a single, intelligent overview — plus an AI assistant that summarizes your whole day in seconds.
          </p>}

          {step === 1 && <div style={{ display: "grid", gap: 10 }}>
            {integrations.map((it) => {
              const Ic = intIcon[it.id]; const on = conn[it.id] || (mode === "live" && it.connected);
              const isOauth = ["gh", "gcal", "email", "slack"].includes(it.id);
              return (
                <div className="conn-card" key={it.id} style={{ padding: 13 }}>
                  <div className="conn-ic" style={{ width: 38, height: 38, background: `color-mix(in srgb, ${it.color} 16%, transparent)`, border: `1px solid color-mix(in srgb, ${it.color} 30%, transparent)` }}><Ic size={18} color={it.color} /></div>
                  <div style={{ flex: 1, minWidth: 0 }}><div style={{ fontWeight: 600, fontSize: 13.5 }}>{it.name}</div><div style={{ fontSize: 11.5, color: "var(--text-secondary)" }}>{it.desc}</div></div>
                  <button className={on ? "btn connected" : "btn primary"} style={{ padding: "7px 13px", fontSize: 12.5 }}
                    onClick={() => { if (mode === "live" && isOauth) { onConnect(it.id); return; } setConn((p) => ({ ...p, [it.id]: !on })); }}>
                    {on ? <><Check size={13} /> Connected</> : "Connect"}
                  </button>
                </div>
              );
            })}
          </div>}

          {step === 2 && <div style={{ display: "grid", gap: 10 }}>
            {["Read your messages & mentions", "View calendar & create events", "Read repository activity", "Read your inbox & flag important mail"].map((p, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 11, padding: "11px 13px", background: "var(--inset)", border: "1px solid var(--border)", borderRadius: 11, fontSize: 13 }}>
                <CheckCircle2 size={17} color="var(--success)" /> {p}
              </div>
            ))}
            <p style={{ fontSize: 11.5, color: "var(--text-muted)", marginTop: 2 }}>You can revoke access anytime from Settings. We never post on your behalf.</p>
          </div>}

          {step === 3 && <p style={{ color: "var(--text-secondary)", fontSize: 14, lineHeight: 1.6 }}>
            {connectedCount > 0 ? `${connectedCount} ${connectedCount === 1 ? "tool" : "tools"} connected. ` : ""}
            Your dashboard is ready. Your assistant is standing by on the right — try asking <b style={{ color: "var(--text)" }}>"What's happening today?"</b>
          </p>}
        </div>

        <div className="sheet-f">
          {step > 0 && step < 3 && <button className="btn ghost" onClick={() => setStep((s) => s - 1)}>Back</button>}
          {step === 0 && <button className="btn ghost" onClick={onDone}>Skip</button>}
          <div style={{ marginLeft: "auto", display: "flex", gap: 10 }}>
            {step < 3
              ? <button className="btn primary" onClick={next}>{step === 0 ? "Get started" : "Continue"} <ChevronRight size={15} /></button>
              : <button className="btn primary" onClick={onDone}>Enter workspace <ArrowUpRight size={15} /></button>}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ---------------------------- New event modal ---------------------------- */
function NewEventModal({ onClose, onAdd }) {
  const [title, setTitle] = useState("");
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [time, setTime] = useState("15:00");
  const [priority, setPriority] = useState("medium");
  const [meet, setMeet] = useState(true);

  const save = () => {
    const [h, m] = time.split(":").map(Number);
    const start = new Date(date); start.setHours(h, m, 0, 0);
    onAdd({ id: "ev" + Date.now(), title: title || "Untitled meeting", start, end: new Date(start.getTime() + 30 * 60000), priority, location: meet ? "Google Meet" : "In person", meet });
    onClose();
  };

  return (
    <div className="overlay" onClick={onClose}>
      <div className="sheet" style={{ maxWidth: 440 }} onClick={(e) => e.stopPropagation()}>
        <div className="sheet-h" style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div className="conn-ic" style={{ width: 38, height: 38, background: "color-mix(in srgb, var(--gcal) 16%, transparent)", border: "1px solid color-mix(in srgb, var(--gcal) 30%, transparent)" }}><Calendar size={18} color="var(--gcal)" /></div>
          <h2 className="hw-display" style={{ fontSize: 18, fontWeight: 700 }}>New event</h2>
          <button className="icon-btn" style={{ marginLeft: "auto", width: 34, height: 34 }} onClick={onClose}><X size={16} /></button>
        </div>
        <div className="sheet-b">
          <div className="field"><label>Title</label><input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Team sync" autoFocus /></div>
          <div style={{ display: "flex", gap: 12 }}>
            <div className="field" style={{ flex: 1 }}><label>Date</label><input type="date" value={date} onChange={(e) => setDate(e.target.value)} /></div>
            <div className="field" style={{ width: 130 }}><label>Time</label><input type="time" value={time} onChange={(e) => setTime(e.target.value)} /></div>
          </div>
          <div className="field"><label>Priority</label>
            <select value={priority} onChange={(e) => setPriority(e.target.value)}>
              <option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option>
            </select>
          </div>
          <label style={{ display: "flex", alignItems: "center", gap: 9, fontSize: 13, color: "var(--text-secondary)", cursor: "pointer" }}>
            <input type="checkbox" checked={meet} onChange={(e) => setMeet(e.target.checked)} style={{ width: 16, height: 16, accentColor: "var(--primary)" }} />
            <Video size={15} /> Add a Google Meet link
          </label>
        </div>
        <div className="sheet-f">
          <button className="btn ghost" onClick={onClose} style={{ marginLeft: "auto" }}>Cancel</button>
          <button className="btn primary" onClick={save}><Plus size={15} /> Create event</button>
        </div>
      </div>
    </div>
  );
}
