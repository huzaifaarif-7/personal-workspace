import re

def process_file():
    with open('src/Workspace.jsx', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace the entire CSS string
    new_css = """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

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
}
* { box-sizing: border-box; }
.hw, .hw * { font-family: 'Inter', system-ui, -apple-system, sans-serif; letter-spacing: normal; line-height: 1.5; }
.hw { background: var(--bg); color: var(--text); min-height: 100vh; width: 100%; display: grid; grid-template-columns: 220px 1fr 372px; grid-template-rows: 100vh; overflow: hidden; -webkit-font-smoothing: antialiased; font-size: 13px; }

/* scrollbars */
.hw ::-webkit-scrollbar { width: 8px; height: 8px; }
.hw ::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 4px; border: 2px solid transparent; background-clip: padding-box; }
.hw ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); background-clip: padding-box; }

/* sidebar */
.side { background: var(--surface); border-right: 1px solid var(--border); display: flex; flex-direction: column; padding: 20px 14px; gap: 6px; min-width: 0; position: relative; z-index: 30; }
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
.scroll { overflow-y: auto; padding: 24px; flex: 1; }

/* cards / grid */
.grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; align-items: start; }
.card { background: var(--card); border: 0.5px solid var(--border); border-radius: 12px; padding: 16px; }
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
.auth-wrap { display: grid; place-items: center; min-height: 100vh; padding: 20px; background: var(--bg); }
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
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; font-size: 13px; font-weight: 500; height: 36px; padding: 0 14px; border-radius: var(--radius); cursor: pointer; border: 1px solid var(--border); background: transparent; color: var(--text); transition: .15s; }
.btn:hover { background: var(--surface); }
.btn.primary { background: var(--primary); border: none; color: #fff; width: 100%; }
.btn.primary:hover { background: color-mix(in srgb, var(--primary) 85%, #000); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }

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
.chat { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 16px; }
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
.sheet { width: 100%; max-width: 480px; background: var(--card); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
.sheet-h { padding: 20px 24px; border-bottom: 1px solid var(--border); }
.sheet-b { padding: 20px 24px; }
.sheet-f { padding: 16px 24px; border-top: 1px solid var(--border); display: flex; gap: 12px; align-items: center; }
.steps { display: flex; gap: 8px; }
.steps i { height: 4px; border-radius: 2px; background: var(--border); flex: 1; }
.steps i.on { background: var(--primary); }
.field { margin-bottom: 16px; }
.field label { display: block; font-size: 13px; color: var(--text); margin-bottom: 8px; font-weight: 500; }
.field input, .field select { width: 100%; height: 36px; background: var(--card); border: 1px solid var(--border); border-radius: 4px; padding: 0 12px; color: var(--text); font-size: 13px; outline: none; }
.field input:focus, .field select:focus { border-color: var(--border-strong); }
.copy-link { display: flex; align-items: center; gap: 10px; background: var(--surface); border: 1px solid var(--border); border-radius: 4px; padding: 10px 12px; font-size: 13px; color: var(--text); }

/* responsive */
@media(max-width:1200px) { .hw{grid-template-columns:220px 1fr} .assist{position:fixed;top:0;right:0;bottom:0;width:380px;max-width:90vw;transform:translateX(105%);transition:transform .2s;box-shadow:-20px 0 60px -20px rgba(0,0,0,0.5)} .assist.open{transform:none} .assist-close{display:grid!important} }
@media(max-width:860px) { .hw{grid-template-columns:1fr} .side{position:fixed;top:0;left:0;bottom:0;width:248px;transform:translateX(-105%);transition:transform .2s;box-shadow:20px 0 60px -20px rgba(0,0,0,0.5)} .side.open{transform:none} .grid{grid-template-columns:1fr} .span2,.hero,.stats{grid-column:span 1} .stats{grid-template-columns:repeat(2,1fr)} .hero{flex-wrap:wrap}.count{margin-left:0} .search{width:auto;flex:1} .mobile-only{display:grid} .scrim{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:25;} }
.assist-close { display: none; position: absolute; top: 16px; right: 16px; }"""

    content = re.sub(r'const CSS = `.*?`;', f'const CSS = `{new_css}`;', content, flags=re.DOTALL)

    # Clean up hardcoded hex values in inline styles
    content = re.sub(r'style=\{\{\s*width: \d+,\s*height: \d+,\s*borderLeft: "[^"]+",\s*borderRight: "[^"]+",\s*borderBottom: "[^"]+"[^\}]*\}\}', 'className="brand-mark"', content)
    content = content.replace('<div className="brand-mark"></div>', '<div className="brand-mark">W</div>')
    
    # 5. Auth screen overhaul
    auth_old = r'<div style=\{\{ display: "grid", placeItems: "center", minHeight: "100vh", padding: 20 \}\}>'
    content = re.sub(r'<div style=\{\{ display: "grid", placeItems: "center", minHeight: "100vh", padding: 20 \}\}>', '<div className="auth-wrap">', content)
    
    content = re.sub(r'<div style=\{\{ width: "100%", maxWidth: 360 \}\}>', '', content)
    
    content = re.sub(r'<div style=\{\{ display: "flex", alignItems: "center", gap: 11, marginBottom: 32, justifyContent: "center" \}\}>', '<div className="auth-header">', content)
    
    content = re.sub(r'<div className="brand-name" style=\{\{ fontSize: 24, color: "var\(--text\)" \}\}>Workspace</div>', '<div className="auth-title">Workspace</div>', content)
    content = re.sub(r'<div className="brand-name" style=\{\{ fontSize: 22, color: "var\(--text\)" \}\}>Workspace</div>', '<div className="auth-title">Workspace</div>', content)
    
    content = re.sub(r'<div className="card" style=\{\{ maxWidth: 380, width: "100%", margin: "0 auto" \}\}>', '<div className="auth-card">', content)
    
    content = re.sub(r'<div className="card-b" style=\{\{ padding: "32px 28px" \}\}>', '<div>', content)
    
    content = re.sub(r'<button type="submit" disabled=\{loading\} className="btn primary" style=\{\{ width: "100%", padding: 12, marginTop: 12, justifyContent: "center", height: "auto" \}\}>', '<button type="submit" disabled={loading} className="btn primary">', content)

    # 4. Top bar Greeting overhaul
    greeting_old = r'<h1 className="hw-display">\{greeting\}, \{user\.full_name\.split\(\' \'\)\[0\]\}</h1>'
    greeting_new = r'<div className="greet"><span className="greet-text">{greeting},</span> <span className="greet-name">{user.full_name.split(\' \')[0]}</span></div>'
    content = re.sub(greeting_old, greeting_new, content)
    content = content.replace('<h1 className="hw-display">', '<h1>')
    content = content.replace('<h2 className="hw-display">', '<h2>')
    content = content.replace('<div className="brand-name" style={{ color: "var(--text)" }}>Workspace</div>', '<div className="brand-name">Workspace</div>')

    # Remove extra closing div from auth layout cleanup
    content = content.replace('</form>\n          </div>\n        </div>\n      </div>\n    </div>', '</form>\n        </div>\n      </div>\n    </div>')

    # "Connect" buttons in unconnected states (Calendar, Slack etc)
    # The current empty state for email:
    # <div style={{ color: "var(--faint)", fontSize: 13, textAlign: "center", padding: "10px 0" }}>Connect Gmail in Settings to see your inbox here</div>
    email_empty = r'<div style=\{\{ color: "var\(--faint\)", fontSize: 13, textAlign: "center", padding: "10px 0" \}\}>Connect Gmail in Settings to see your inbox here</div>'
    email_empty_new = r'<div className="empty-state"><Mail size={24} className="ic" /><div className="text">Connect Gmail in Settings to see your inbox here</div><button className="empty-btn" onClick={() => setView("settings")}>Connect</button></div>'
    content = re.sub(email_empty, email_empty_new, content)

    # Calendar empty state is handled by c.calendar_today.length check? No, calendar UI has renderList:
    # There is no empty state except the one in the renderList generic function
    content = content.replace('var(--dim)', 'var(--text-secondary)')
    content = content.replace('var(--faint)', 'var(--text-muted)')
    content = content.replace('var(--green)', 'var(--success)')
    content = content.replace('var(--amber)', 'var(--danger)') # Danger used for warnings/errors

    # Row unread classes
    content = re.sub(r'<div className="row" key=\{e\.id\}\s+onClick=\{.*?\}>', r'<div className={`row ${e.unread ? "unread" : ""}`} key={e.id}>', content)
    # We must be careful because e.id is dynamic. We'll just replace `className="row"` with conditional
    # Actually, the prompt says "Unread items title in 500 font weight". The CSS covers `.row.unread .name { font-weight: 500; }`.
    # Let's just use regex to add the `unread` class if e.unread is true for emails/slack.
    content = re.sub(r'className="row" key=\{([^\}]+)\}', r'className={`row ${(\1).unread || (\1).isUnread ? "unread" : ""}`} key={\1}', content)
    content = re.sub(r'className="row" key=\{([a-zA-Z0-9_\.]+)\}', r'className={`row ${(\1).unread ? "unread" : ""}`} key={\1}', content)

    # Remove all hardcoded `#fff` `#000` from inline styles
    content = content.replace('color: "#fff"', 'color: "var(--bg)"')
    content = content.replace('color="#fff"', 'color="currentColor"')
    content = content.replace('background: "#111"', 'background: "var(--surface)"')

    # Remove the SVGs we injected previously if they conflict or just let them inherit currentColor
    content = content.replace('fill="#E01E5A"', 'fill="currentColor"')
    content = content.replace('fill="#36C5F0"', 'fill="currentColor"')
    content = content.replace('fill="#2EB67D"', 'fill="currentColor"')
    content = content.replace('fill="#ECB22E"', 'fill="currentColor"')
    content = content.replace('stroke="#EA4335"', 'stroke="currentColor"')
    content = content.replace('fill="#EA4335"', 'fill="currentColor"')

    with open('src/Workspace.jsx', 'w', encoding='utf-8') as f:
        f.write(content)

process_file()
