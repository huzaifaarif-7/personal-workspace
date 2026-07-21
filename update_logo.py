import re
with open('src/Workspace.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

logo_comp = '''const Logo = ({ size = 28 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2L22 20H2L12 2Z" />
  </svg>
);
'''
if 'const Logo = ' not in content:
    content = content.replace('/* ---------------------------- Constants ---------------------------- */', '/* ---------------------------- Constants ---------------------------- */\n' + logo_comp)

# In the Auth screen hero
content = content.replace('<div className="hero">', '<div className="hero" style={{ justifyContent: "center" }}>')
content = content.replace('<div className="hero" style={{ justifyContent: "center" }}>\n          <div className="brand-mark">W</div>', '<div className="hero" style={{ justifyContent: "center" }}>\n          <Logo size={48} />')

# Let's fix up the brand-mark generally if we couldn't find the exact match
content = re.sub(r'<div className="brand-mark"[^>]*>.*?</div>', '<Logo size={32} />', content)

# But wait, in the sidebar we probably want the size to be 24
# The brand section in sidebar is:
# <div className="brand">
#   <Logo size={32} />
#   <div>
#     <div className="brand-name">Workspace</div>
content = content.replace('<Logo size={32} />\n            <div>\n              <div className="brand-name">Workspace</div>', '<Logo size={24} />\n            <div>\n              <div className="brand-name">Workspace</div>')

with open('src/Workspace.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
