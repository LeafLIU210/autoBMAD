"""View specific errors from basedpyright output."""
import json

with open('docs/research/basedpyright_raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for d in data.get('generalDiagnostics', []):
    if 'update_context.py' in d['file'] and d['severity'] == 'error':
        print(f"Line {d['range']['start']['line']}: {d['message']}")
