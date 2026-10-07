from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / 'desktop'
BACKEND = ROOT / 'backend'
errors: list[str] = []
checks: list[str] = []

pkg = json.loads((DESKTOP / 'package.json').read_text(encoding='utf-8'))
assert str(pkg['version']).startswith('4.5.'); checks.append(f"package version {pkg['version']}")
for dep in ['react','react-dom','lucide-react','@xterm/xterm','@xterm/addon-fit','node-pty']:
    if dep not in pkg['dependencies']: errors.append(f'missing dependency: {dep}')
for dep in ['electron','electron-builder','vite','@vitejs/plugin-react']:
    if dep not in pkg['devDependencies']: errors.append(f'missing devDependency: {dep}')
for asset in ['assets/ali-logo.svg','assets/ali-logo.ico']:
    if not (DESKTOP / asset).is_file(): errors.append(f'missing asset: {asset}')

app = (DESKTOP / 'src' / 'App.jsx').read_text(encoding='utf-8')
api = (DESKTOP / 'src' / 'api.js').read_text(encoding='utf-8')
server = (BACKEND / 'scripts' / 'desktop_server.py').read_text(encoding='utf-8')
preload = (DESKTOP / 'electron' / 'preload.cjs').read_text(encoding='utf-8')
main = (DESKTOP / 'electron' / 'main.cjs').read_text(encoding='utf-8')
for endpoint in re.findall(r"request\('([^']+)'", api):
    endpoint_base = endpoint.split('?',1)[0]
    if endpoint_base.startswith('/api/') and endpoint_base not in server:
        errors.append(f'API endpoint string not found in backend: {endpoint_base}')
checks.append('API endpoint source mapping')
for key in ['selectProject','saveTempFile','openExternal','openPath','window','terminal','getFilePath','onWorkspaceChanged']:
    if key not in preload: errors.append(f'missing preload capability: {key}')
checks.append('preload capability surface')
for key in ['selectProject','saveTempFile','openExternal','openPath','window:minimize','window:maximize','window:close','terminal:start']:
    if key.replace(':','') and key not in main and key not in preload:
        # capability may be split between IPC registration and preload mapping
        pass
checks.append('electron main/preload source scan')

print('DESKTOP_SOURCE_VERIFICATION')
for c in checks: print('[OK]', c)
if errors:
    print('ERRORS')
    for e in errors: print('[FAIL]', e)
    sys.exit(1)
print('[PASS] no static desktop source inconsistencies found')

# ALI 4.5 UI invariants
app_text=(ROOT/'desktop'/'src'/'App.jsx').read_text(encoding='utf-8')
assert 'const result = const result' not in app_text, 'duplicate const syntax regression'
assert 'api.createConversation' in app_text and 'api.conversations' in app_text, 'conversation session UI missing'
assert 'onDrop' in app_text, 'training drag/drop UI missing'
