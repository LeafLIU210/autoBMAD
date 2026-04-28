"""Check remaining basedpyright errors."""
import json

with open('docs/research/basedpyright_raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

errors = [d for d in data.get('generalDiagnostics', []) if d['severity'] == 'error']
print(f'Remaining errors: {len(errors)}')
print()

for e in errors:
    file_name = e['file'].split('/')[-1]
    line = e['range']['start']['line']
    rule = e['rule']
    print(f"  {file_name}:{line} - {rule}")
