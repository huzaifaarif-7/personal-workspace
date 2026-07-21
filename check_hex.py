import re
with open('src/Workspace.jsx', encoding='utf-8') as f:
    content = f.read()

hexes = set(re.findall(r'#[0-9a-fA-F]{3,6}', content))
# Filter out valid CSS vars from :root definitions that are allowed
allowed = {'#0a0a0a', '#111111', '#161616', '#272727', '#333333', '#ededed', '#888888', '#555555', '#4f8ef7', '#f87171', '#4ade80', '#fafafa', '#f4f4f4', '#ffffff', '#e5e5e5', '#d4d4d4', '#666666', '#999999', '#2563eb', '#dc2626', '#16a34a'}

illegal_hexes = hexes - allowed - {'#fff', '#000'}

print('Hexes (illegal):', illegal_hexes)
