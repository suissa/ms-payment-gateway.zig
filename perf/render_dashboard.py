#!/usr/bin/env python3
import json, sys
from pathlib import Path
indir = Path(sys.argv[1] if len(sys.argv)>1 else 'perf/results')
out = Path(sys.argv[2] if len(sys.argv)>2 else 'docs/performance-dashboard.html')
rows=[]
for p in sorted(indir.glob('*.json')):
    try: rows.append(json.loads(p.read_text()))
    except Exception: pass
html_rows=''.join(f"<tr><td>{r.get('target')}</td><td>{r.get('profile')}</td><td>{r.get('requests')}</td><td>{r.get('concurrency')}</td><td>{r.get('success')}</td><td>{r.get('failures')}</td><td>{r.get('requests_per_second',0):.2f}</td><td>{r.get('latency_ms',{}).get('mean',0):.2f}</td><td>{r.get('latency_ms',{}).get('p95',0):.2f}</td><td>{r.get('latency_ms',{}).get('p99',0):.2f}</td></tr>" for r in rows)
data=json.dumps(rows)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(f'''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Dashboard de performance</title><style>body{{font-family:Arial,sans-serif;margin:2rem;background:#f8fafc;color:#0f172a}}table{{border-collapse:collapse;width:100%;background:white}}td,th{{border:1px solid #cbd5e1;padding:.6rem;text-align:right}}td:first-child,td:nth-child(2),th:first-child,th:nth-child(2){{text-align:left}}th{{background:#1e293b;color:white}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}}.card{{background:white;border:1px solid #cbd5e1;border-radius:12px;padding:1rem}}</style><h1>Dashboard de resultados - ms-payment-gateway</h1><p>Perfis: carga, stress e benchmark para Laravel/Docker e Zig.</p><div class="cards"><div class="card"><strong>Execuções</strong><br>{len(rows)}</div><div class="card"><strong>Dados</strong><br>Gerados a partir de <code>perf/results/*.json</code></div></div><h2>Resumo</h2><table><thead><tr><th>Alvo</th><th>Perfil</th><th>Req.</th><th>Conc.</th><th>OK</th><th>Falhas</th><th>Req/s</th><th>Média ms</th><th>p95 ms</th><th>p99 ms</th></tr></thead><tbody>{html_rows}</tbody></table><script type="application/json" id="results">{data}</script></html>''', encoding='utf-8')
print(out)
