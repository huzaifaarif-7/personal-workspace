import re

with open('src/Workspace.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Sun and Moon to lucide-react imports
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
content = content.replace('*{box-sizing:border-box}', light_theme_css + '*{box-sizing:border-box}')

# 3. Add theme state to App and provide it
# Let's see how App is defined.
app_state_add = '''export default function App() {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');
  useEffect(() => {
    localStorage.setItem('theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);
  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark');
'''
content = content.replace('export default function App() {', app_state_add)

# 4. We need to pass toggleTheme down to Dashboard, but wait, Workspace is not in App.
# Wait, let's see how App renders the dashboard.
# Usually it renders <Dashboard ... /> or something.
# But where can we put the toggle? Let's put a global toggle in topbar of the Dashboard.
# Wait, if we use document.documentElement.setAttribute, we can just use a local state in Dashboard or anywhere.
# Actually, the simplest is to put it in topbar.
# Let's search for `<div className="topbar">`
topbar_inject = '''<div className="topbar">
          <button className="icon-btn" onClick={() => {
            const next = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            window.dispatchEvent(new Event('themechange'));
          }}>
            {document.documentElement.getAttribute('data-theme') === 'light' ? <Moon size={18} /> : <Sun size={18} />}
          </button>'''
# Since react re-rendering won't trigger on DOM attribute change unless it's state,
# it's better to add state to the Dashboard component.

with open('src/Workspace.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
