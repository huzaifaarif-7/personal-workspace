import re

with open('src/Workspace.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. CSS Refactor (Vercel/Github style, no gradients)
new_css = '''
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Geist:wght@500;600;700&display=swap');

:root{
  --bg:#000000; --panel:#0A0A0A; --card:#000000; --card-2:#111111;
  --inset:#0A0A0A; --border:#333333; --border-soft:#222222;
  --text:#EDEDED; --dim:#A1A1AA; --faint:#71717A;
  --primary:#EDEDED; --primary-2:#FFFFFF; --teal:#3291FF; --blue:#0070F3;
  --amber:#F5A623; --rose:#FF0080; --green:#50E3C2;
  --danger:var(--rose);
  --slack:#FFFFFF; --gcal:#FFFFFF; --cly:#FFFFFF; --gh:#FFFFFF; --email:#FFFFFF;
  --input-bg:#000000; --input-border:#333; --input-text:#EDEDED; --input-placeholder:#71717A;
  --radius:6px; --radius-sm:4px;
  --shadow:0 0 0 1px #333, 0 4px 12px rgba(0,0,0,0.5);
}
*{box-sizing:border-box}
.hw, .hw *{font-family:'Inter',system-ui,-apple-system,sans-serif}
.hw-display{font-family:'Geist','Inter',sans-serif; letter-spacing:-0.04em}
.hw{ background:var(--bg); color:var(--text); min-height:100vh; width:100%;
  display:grid; grid-template-columns:240px 1fr 372px; grid-template-rows:100vh;
  overflow:hidden; -webkit-font-smoothing:antialiased;
}

/* ---------- scrollbars ---------- */
.hw ::-webkit-scrollbar{width:8px;height:8px}
.hw ::-webkit-scrollbar-thumb{background:#333;border-radius:4px;border:2px solid transparent;background-clip:padding-box}
.hw ::-webkit-scrollbar-thumb:hover{background:#444;background-clip:padding-box}

/* ---------- sidebar ---------- */
.side{background:var(--bg); border-right:1px solid var(--border);
  display:flex; flex-direction:column; padding:20px 14px; gap:6px; min-width:0; position:relative; z-index:30}
.brand{display:flex;align-items:center;gap:11px;padding:6px 8px 18px}
.brand-mark{width:28px;height:28px;border-radius:50%;background:var(--text);display:grid;place-items:center;flex:none;color:var(--bg)}
.brand-name{font-weight:600;font-size:14px;letter-spacing:-.2px;line-height:1.1}
.brand-sub{font-size:11px;color:var(--faint);letter-spacing:.3px}
.nav-label{font-size:11px;letter-spacing:.05em;color:var(--faint);padding:14px 10px 8px;font-weight:500}
.nav{display:flex;align-items:center;gap:11px;padding:8px 11px;border-radius:6px;color:var(--dim);
  cursor:pointer;font-size:13px;font-weight:500;border:1px solid transparent;transition:.15s ease;position:relative}
.nav:hover{background:var(--card-2);color:var(--text)}
.nav.active{background:#222;color:#fff;}
.nav .badge{margin-left:auto;background:var(--text);color:var(--bg);font-size:10.5px;font-weight:600;
  min-width:18px;height:18px;border-radius:9px;display:grid;place-items:center;padding:0 5px}
.side-foot{margin-top:auto;display:flex;align-items:center;gap:10px;padding:10px;border-radius:6px;
  background:var(--bg);border:1px solid var(--border)}
.avatar{width:32px;height:32px;border-radius:50%;display:grid;place-items:center;font-weight:600;font-size:12px;flex:none;
  background:#222;color:var(--text);border:1px solid var(--border)}
.avatar.lg{width:40px;height:40px;font-size:14px}

/* ---------- center ---------- */
.center{min-width:0;display:flex;flex-direction:column;overflow:hidden;background:var(--bg)}
.topbar{display:flex;align-items:center;gap:14px;padding:16px 24px;border-bottom:1px solid var(--border);
  background:var(--bg);z-index:20}
.greet{min-width:0}
.greet h1{font-size:16px;font-weight:600;letter-spacing:-.2px;line-height:1.2}
.greet p{font-size:13px;color:var(--dim);margin-top:2px}
.search{margin-left:auto;display:flex;align-items:center;gap:9px;background:var(--bg);border:1px solid var(--border);
  border-radius:6px;padding:8px 12px;width:300px;max-width:34vw;color:var(--dim);transition:.15s}
.search:focus-within{border-color:var(--text)}
.search input{background:none;border:none;outline:none;color:var(--text);font-size:13px;width:100%}
.search input::placeholder{color:var(--faint)}
.icon-btn{width:36px;height:36px;border-radius:6px;display:grid;place-items:center;flex:none;cursor:pointer;
  background:var(--bg);border:1px solid var(--border);color:var(--dim);transition:.15s;position:relative}
.icon-btn:hover{color:var(--text);border-color:#555;background:var(--card-2)}
.icon-btn .dot{position:absolute;top:8px;right:9px;width:7px;height:7px;border-radius:50%;background:var(--rose);border:2px solid var(--bg)}
.scroll{overflow-y:auto;padding:24px;flex:1}

/* ---------- cards / grid ---------- */
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;align-items:start}
.card{background:var(--bg);border:1px solid var(--border);
  border-radius:var(--radius);overflow:hidden;}
.card:hover{border-color:#444}
.span2{grid-column:span 2}
.card-h{display:flex;align-items:center;gap:11px;padding:14px 16px;border-bottom:1px solid var(--border-soft)}
.card-h .ic{width:28px;height:28px;border-radius:4px;display:grid;place-items:center;flex:none}
.card-h h3{font-size:14px;font-weight:600;letter-spacing:-.2px}
.card-h .sub{font-size:12px;color:var(--faint)}
.card-h .right{margin-left:auto;display:flex;align-items:center;gap:8px}
.card-b{padding:8px}
.link-btn{display:inline-flex;align-items:center;gap:5px;font-size:12px;font-weight:500;color:var(--text);
  cursor:pointer;padding:4px 8px;border-radius:4px;transition:.14s;border:1px solid transparent;text-decoration:none}
.link-btn:hover{background:#222;border-color:#333}
.row{display:flex;align-items:flex-start;gap:12px;padding:10px 12px;border-radius:6px;cursor:pointer;transition:.14s}
.row:hover{background:#111}
.row .body{min-width:0;flex:1}
.row .top{display:flex;align-items:center;gap:8px}
.row .name{font-size:13px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.row .time{font-size:12px;color:var(--faint);margin-left:auto;white-space:nowrap;flex:none}
.row .text{font-size:13px;color:var(--dim);margin-top:3px;line-height:1.5;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.row .text b{color:var(--text);font-weight:500}
.unread-dot{width:6px;height:6px;border-radius:50%;background:var(--text);flex:none}
.pill{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:500;padding:2px 6px;border-radius:4px;white-space:nowrap}
.tag-hi{background:#222;color:#EDEDED;border:1px solid #444}
.tag-md{background:#222;color:#EDEDED;border:1px solid #444}
.tag-lo{background:#222;color:#EDEDED;border:1px solid #444}
.tag-imp{background:#300;color:var(--rose);border:1px solid #500}

/* ---------- forms / auth ---------- */
.input-group{margin-bottom:16px}
.input-label{color:var(--text);font-size:13px;font-weight:500;margin-bottom:8px;display:block}
.input-field{width:100%;background:var(--input-bg);color:var(--input-text);border:1px solid var(--input-border);
  border-radius:var(--radius-sm);padding:10px 12px;font-size:14px;transition:border-color .15s;outline:none}
.input-field::placeholder{color:var(--input-placeholder)}
.input-field:focus{border-color:var(--text);}
.auth-error{color:var(--rose);background:#200;border:1px solid #500;
  padding:10px 12px;border-radius:4px;font-size:13px;margin-bottom:16px}
.auth-tabs{display:flex;background:#111;border:1px solid #333;border-radius:6px;padding:3px;margin-bottom:24px}
.auth-tab{flex:1;text-align:center;padding:6px 0;font-size:13px;font-weight:500;color:var(--dim);
  border-radius:4px;cursor:pointer;transition:.15s;border:none;background:none}
.auth-tab.active{background:#333;color:var(--text);}
.btn:disabled{opacity:.6;cursor:not-allowed}

/* ---------- hero / countdown ---------- */
.hero{grid-column:span 2;background:var(--bg);
  border:1px solid var(--border);border-radius:var(--radius);padding:24px;
  display:flex;align-items:center;gap:20px;}
.hero .glyph{width:48px;height:48px;border-radius:50%;flex:none;display:grid;place-items:center;
  background:#111;border:1px solid #333;}
.hero .eyebrow{font-size:11px;letter-spacing:.05em;color:var(--faint);font-weight:500}
.hero h2{font-size:20px;font-weight:600;letter-spacing:-.4px;margin-top:4px}
.hero .meta{display:flex;gap:16px;margin-top:8px;flex-wrap:wrap;color:var(--dim);font-size:13px}
.hero .meta span{display:inline-flex;align-items:center;gap:6px}
.count{margin-left:auto;text-align:right;flex:none}
.count .num{font-family:'Geist';font-size:32px;font-weight:600;letter-spacing:-1px;color:var(--text)}
.count .lbl{font-size:11px;color:var(--faint);letter-spacing:.05em;margin-top:2px}

/* ---------- stat strip ---------- */
.stats{grid-column:span 2;display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.stat{background:var(--bg);border:1px solid var(--border);
  border-radius:6px;padding:16px;}
.stat .n{font-family:'Geist';font-size:24px;font-weight:600;letter-spacing:-.5px}
.stat .l{font-size:13px;color:var(--dim);margin-top:4px}
.stat .ic{width:24px;height:24px;border-radius:4px;display:grid;place-items:center;margin-bottom:8px;color:var(--text)}

/* ---------- live dot ---------- */
.live{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:var(--text);font-weight:500}
.live i{width:6px;height:6px;border-radius:50%;background:var(--text);}

/* ---------- assistant panel ---------- */
.assist{background:var(--bg);border-left:1px solid var(--border);
  display:flex;flex-direction:column;min-width:0;position:relative;z-index:30}
.assist-h{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px}
.assist-h .who{min-width:0}
.assist-h .who .nm{font-weight:600;font-size:14px;letter-spacing:-.2px;display:flex;align-items:center;gap:7px}
.assist-h .who .st{font-size:12px;color:var(--dim);display:flex;align-items:center;gap:5px;margin-top:2px}
.chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:16px}
.msg{display:flex;gap:12px;max-width:92%;}
.msg.me{align-self:flex-end;flex-direction:row-reverse}
.bub{padding:10px 14px;border-radius:6px;font-size:14px;line-height:1.5;white-space:pre-wrap;word-break:break-word}
.msg.ai .bub{background:#111;border:1px solid #333;}
.msg.me .bub{background:#EDEDED;color:#000;}
.mini-mascot{width:28px;height:28px;flex:none;align-self:flex-end;background:#222;border-radius:50%;display:grid;place-items:center;border:1px solid #444}
.typing{display:flex;gap:4px;padding:12px}
.typing i{width:6px;height:6px;border-radius:50%;background:#555;}
.quick{display:flex;gap:8px;flex-wrap:wrap;padding:0 20px 16px}
.chip{font-size:12px;font-weight:500;color:var(--text);background:var(--bg);border:1px solid var(--border);
  border-radius:4px;padding:6px 10px;cursor:pointer;transition:.15s;white-space:nowrap}
.chip:hover{background:#111;border-color:#555}
.composer{padding:16px;border-top:1px solid var(--border)}
.composer .box{display:flex;align-items:flex-end;gap:8px;background:var(--bg);border:1px solid var(--border);
  border-radius:6px;padding:6px 6px 6px 12px;transition:.15s}
.composer .box:focus-within{border-color:#555;}
.composer textarea{flex:1;background:none;border:none;outline:none;color:var(--text);font-size:14px;
  resize:none;max-height:110px;line-height:1.5;padding:6px 0;font-family:inherit}
.composer textarea::placeholder{color:var(--faint)}
.send-btn{width:32px;height:32px;border-radius:4px;border:none;flex:none;cursor:pointer;display:grid;place-items:center;
  background:#EDEDED;color:#000;transition:.15s}
.send-btn:hover{background:#FFF}
.send-btn:disabled{opacity:.4;cursor:not-allowed;}

/* ---------- mascot ---------- */
.mascot-wrap{display:grid;place-items:center}

/* ---------- settings / lists ---------- */
.conn-card{display:flex;align-items:center;gap:16px;padding:16px;border:1px solid var(--border);
  border-radius:6px;background:var(--bg);transition:.15s}
.conn-card:hover{border-color:#555}
.conn-ic{width:40px;height:40px;border-radius:50%;display:grid;place-items:center;flex:none;border:1px solid #333;background:#111}
.btn{display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:500;padding:8px 14px;border-radius:4px;
  cursor:pointer;border:1px solid var(--border);background:var(--bg);color:var(--text);transition:.15s}
.btn:hover{background:#111;border-color:#555}
.btn.primary{background:#EDEDED;border:none;color:#000}
.btn.primary:hover{background:#FFF}
.btn.ghost{background:transparent;border-color:transparent}
.btn.connected{color:var(--text);border-color:#333;background:#111}

/* ---------- modal / onboarding ---------- */
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:100;
  display:grid;place-items:center;padding:24px;}
.sheet{width:100%;max-width:480px;background:#000;
  border:1px solid #333;border-radius:8px;overflow:hidden;}
.sheet-h{padding:20px 24px;border-bottom:1px solid #333}
.sheet-b{padding:20px 24px}
.sheet-f{padding:16px 24px;border-top:1px solid #333;display:flex;gap:12px;align-items:center}
.steps{display:flex;gap:8px}
.steps i{height:4px;border-radius:2px;background:#333;flex:1;}
.steps i.on{background:#EDEDED}
.field{margin-bottom:16px}
.field label{display:block;font-size:13px;color:var(--text);margin-bottom:8px;font-weight:500}
.field input,.field select{width:100%;background:#000;border:1px solid #333;border-radius:4px;
  padding:10px 12px;color:var(--text);font-size:14px;outline:none;}
.field input:focus,.field select:focus{border-color:#666}
.copy-link{display:flex;align-items:center;gap:10px;background:#000;border:1px solid #333;
  border-radius:4px;padding:10px 12px;font-size:13px;color:var(--text)}
.copy-link .url{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-family:ui-monospace,monospace;}

/* ---------- floating assistant button (mobile) ---------- */
.fab{display:none;position:fixed;right:20px;bottom:20px;z-index:60;width:50px;height:50px;border-radius:25px;
  border:none;cursor:pointer;background:#EDEDED;color:#000;place-items:center}
.mobile-only{display:none}

/* ---------- responsive ---------- */
@media(max-width:1200px){
  .hw{grid-template-columns:240px 1fr}
  .assist{position:fixed;top:0;right:0;bottom:0;width:380px;max-width:90vw;transform:translateX(105%);
    transition:transform .2s;box-shadow:-20px 0 60px -20px #000}
  .assist.open{transform:none}
  .fab{display:grid}
  .assist-close{display:grid!important}
}
@media(max-width:860px){
  .hw{grid-template-columns:1fr}
  .side{position:fixed;top:0;left:0;bottom:0;width:248px;transform:translateX(-105%);
    transition:transform .2s;box-shadow:20px 0 60px -20px #000}
  .side.open{transform:none}
  .grid{grid-template-columns:1fr}
  .span2,.hero,.stats{grid-column:span 1}
  .stats{grid-template-columns:repeat(2,1fr)}
  .hero{flex-wrap:wrap}.count{margin-left:0}
  .search{width:auto;flex:1}
  .mobile-only{display:grid}
  .scrim{position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:25;}
}
.assist-close{display:none;position:absolute;top:16px;right:16px}
'''

content = re.sub(r'const CSS = `.*?`;', f'const CSS = `{new_css}`;', content, flags=re.DOTALL)

# 2. Mascot SVG replacement
new_mascot = '''function Mascot({ size = 24 }) {
  return (
    <div className="mascot-wrap" style={{ width: size, height: size, background: "var(--text)", color: "var(--bg)", borderRadius: "50%", display: "grid", placeItems: "center" }}>
      <Sparkles size={size * 0.6} />
    </div>
  );
}'''
content = re.sub(r'function Mascot.*?return.*?</svg>\s*</div>\s*\);\s*}', new_mascot, content, flags=re.DOTALL)

# 3. Remove Emojis
emojis = ['🎉', '👋', '✅']
for e in emojis:
    content = content.replace(f' {e}', '')
    content = content.replace(e, '')

# 4. Login Brand Mark & Workspace Readable
triangle_logo = '<div style={{ width: 0, height: 0, borderLeft: "8px solid transparent", borderRight: "8px solid transparent", borderBottom: "14px solid var(--text)" }}></div>'
content = re.sub(r'<div className=\"brand-mark\"><Sparkles size=\{18\} color=\"#fff\" /></div>', triangle_logo, content)

content = content.replace(r'<div className="brand-name" style={{ fontSize: 20 }}>Workspace</div>', r'<div className="brand-name" style={{ fontSize: 24, color: "var(--text)" }}>Workspace</div>')

content = re.sub(r'<div className=\"brand-mark\"><Sparkles size=\{20\} color=\"#fff\" /></div>', triangle_logo, content)
content = re.sub(r'<div className=\"brand-name\">Huzaifa\'s Workspace</div>', r'<div className=\"brand-name\" style={{ color: "var(--text)" }}>Workspace</div>', content)

with open('src/Workspace.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
