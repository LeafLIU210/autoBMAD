"""Run basedpyright analysis and save results."""
import subprocess
import json

result = subprocess.run(
    ['python', '-m', 'basedpyright', 'autoBMAD/docuswarm', '--outputjson'],
    capture_output=True
)

output = result.stderr.decode('utf-8', errors='ignore') if result.stderr else ""
if not output:
    output = result.stdout.decode('utf-8', errors='ignore') if result.stdout else ""
json_start = output.find('{')
if json_start >= 0:
    json_str = output[json_start:]
    data = json.loads(json_str)
    with open('docs/research/basedpyright_raw.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    diagnostics = data.get("generalDiagnostics", [])
    errors = sum(1 for d in diagnostics if d.get("severity") == "error")
    warnings = sum(1 for d in diagnostics if d.get("severity") == "warning")
    print(f"Saved {len(diagnostics)} diagnostics ({errors} errors, {warnings} warnings)")
else:
    print("No JSON found in output")
    print("Output preview:", output[:500] if output else "(empty)")
