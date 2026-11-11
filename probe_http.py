"""Run the requested external curl checks without redirects or cookie reuse."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('base_url')
parser.add_argument('--phase', default='awake')
parser.add_argument('--prefix', default='')
args = parser.parse_args()
base = args.base_url.rstrip('/')
output = Path(__file__).resolve().parent / 'results' / args.phase
output.mkdir(parents=True, exist_ok=True)
rows = []
for name, path, headers in (
    ('health', '/api/karte/v1/health', []),
    ('echo', '/api/karte/v1/echo', ['Authorization: Bearer test-test-test', 'If-Match: "e1"', 'Range: bytes=0-9']),
    ('streamlit-health', '/_stcore/health', []),
):
    url = base + args.prefix + path
    command = ['curl', '--silent', '--show-error', '-i', '--max-time', '30']
    for header in headers:
        command.extend(['-H', header])
    command.append(url)
    started = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(command, capture_output=True)
    (output / (name + '.curl.txt')).write_bytes(result.stdout)
    (output / (name + '.stderr.txt')).write_bytes(result.stderr)
    raw_headers, separator, body = result.stdout.partition(b'\r\n\r\n')
    if not separator:
        raw_headers, separator, body = result.stdout.partition(b'\n\n')
    lines = raw_headers.decode('utf-8', errors='replace').splitlines()
    fields = {}
    for line in lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            fields[key.lower()] = value.strip()
    status = int(lines[0].split()[1]) if lines and lines[0].startswith('HTTP/') else None
    row = {'case': name, 'url': url, 'utc': started, 'curl_exit': result.returncode,
           'status': status, 'content_type': fields.get('content-type'),
           'location': fields.get('location'), 'body_first_200': body.decode('utf-8', errors='replace')[:200],
           'body_bytes': len(body)}
    if name == 'echo':
        try:
            row['header_presence'] = json.loads(body)
        except (ValueError, UnicodeError):
            row['header_presence'] = None
    rows.append(row)
(output / 'summary.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(rows, ensure_ascii=False, indent=2))
