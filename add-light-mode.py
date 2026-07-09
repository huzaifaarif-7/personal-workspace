import re

with open('src/Workspace.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Sun and Moon to lucide-react imports
if 'Sun, Moon' not in content:
    content = content.replace('Users, ArrowUpRight, CheckCircle2, Slack as SlackIcon, Zap, Bell', 'Users, ArrowUpRight, CheckCircle2, Slack as SlackIcon, Zap, Bell, Sun, Moon')

# 2. Add light theme CSS
light_theme_css = '''
:root[data-theme="light"]{
  --bg:#FFFFFF; --panel:#F7F7F7; --card:#FFFFFF; --card-2:#F0F0F0;
  --inset:#F7F7F7; --border:#EAEAEA; --border-soft:#F5F5F5;
  --text:#111111; --dim:#666666; --faint:#999999;
  --primary:#111111; --primary-2:#000000; --teal:#0055FF; --blue:#0070F3;
  --amber:#F5A623; --rose:#FF0080; --green:#0070F3;
  --danger:var(--rose);
  --slack:#000000; --gcal:#000000; --cly:#000000; --gh:#000000; --email:#000000;
  --input-bg:#FFFFFF; --input-border:#EAEAEA; --input-text:#111111; --input-placeholder:#999999;
  --shadow:0 0 0 1px #EAEAEA, 0 4px 12px rgba(0,0,0,0.05);
}
'''
if 'data-theme="light"' not in content:
    content = content.replace('*{box-sizing:border-box}', light_theme_css + '*{box-sizing:border-box}')

# 3. Add theme state to App and provide it
app_state_add = '''export default function App() {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');
  useEffect(() => {
    localStorage.setItem('theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);
  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark');
'''
if 'const [theme, setTheme] = useState' not in content:
    content = content.replace('export default function App() {', app_state_add)

# 4. Insert toggle button into topbar
toggle_btn = '''
          <button className="icon-btn" onClick={toggleTheme}>
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
          </button>
'''
if '<button className="icon-btn" onClick={toggleTheme}>' not in content:
    content = content.replace('<header className="topbar">', '<header className="topbar">' + toggle_btn)

with open('src/Workspace.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Light mode added successfully")
