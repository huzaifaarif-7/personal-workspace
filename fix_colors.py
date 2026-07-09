import re

with open('src/Workspace.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the broken inline style setting color to var(--bg)
content = content.replace('style={{ color: "var(--bg)" }}', '')
content = content.replace('<b >', '<b>')

# Remove the broken conditional color for email sender
content = content.replace('style={{ color: e.unread ? "#fff" : "inherit" }}', '')
content = content.replace('style={{ color: e.unread ? "var(--bg)" : "inherit" }}', '')
content = content.replace('style={{ color: e.unread ? "inherit" : "inherit" }}', '')
content = re.sub(r'style=\{\{\s*color:\s*e\.unread\s*\?\s*\"[^\"]+\"\s*:\s*\"[^\"]+\"\s*\}\}', '', content)

with open('src/Workspace.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Colors fixed.")
