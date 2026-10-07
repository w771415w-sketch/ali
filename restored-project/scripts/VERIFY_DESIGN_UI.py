from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
app=(root/'desktop/src/App.jsx').read_text(encoding='utf-8')
main=(root/'desktop/src/main.jsx').read_text(encoding='utf-8')
css=(root/'desktop/src/styles.css').read_text(encoding='utf-8')
checks={
 'rtl_document': "document.documentElement.dir = 'rtl';" in main,
 'auto_direction_input': 'dir="auto" spellCheck={true}' in app,
 'in_chat_web_button': 'البحث عبر الإنترنت داخل المحادثة' in app,
 'clean_control_chars': 'replace(/[\\u0000-\\u0008' in app,
 'professional_trace_css': '.workingTrace' in css,
 'web_sources_css': '.webSources' in css,
 'design_selector': 'data-ali-design' in css,
 'electron_entry': (root/'desktop/electron/main.cjs').exists(),
 'backend_entry': (root/'backend/scripts/desktop_server.py').exists(),
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(f'{k}: {"PASS" if v else "FAIL"}')
if bad:
    print('FAILED:', ', '.join(bad)); sys.exit(1)
print('DESIGN UI VERIFY: PASS')
