"""
gerar.py — Gerador da vitrine financeira
Uso: python gerar.py
Lê dados.json e gera index.html atualizado.
Não precisa instalar nada — Python puro.
"""

import json
from datetime import datetime

# ─── LER DADOS ───────────────────────────────────────────────────────────────

with open("dados.json", "r", encoding="utf-8") as f:
    d = json.load(f)

perfil       = d["perfil"]
caixinha     = d["caixinha"]
fiis         = d["carteira_fiis"]
acoes        = d["carteira_acoes"]
acoes_res    = d["acoes_resumo"]
orcamento    = d["orcamento"]
freelas      = d["freelas"]
historico    = d["historico"]
atualizado   = d["ultima_atualizacao"]

# ─── CÁLCULOS ────────────────────────────────────────────────────────────────

dividendos_mes   = sum(f["dividendo_mes"] for f in fiis)
patrimonio_total = acoes_res["valor_total"] + sum(
    f["qtd"] * f["preco_medio"] for f in fiis
)
caixinha_pct     = (caixinha["saldo"] / caixinha["meta"]) * 100

mxrf = next((f for f in fiis if f["ticker"] == "MXRF11"), None)
mxrf_cotas       = mxrf["qtd"] if mxrf else 0
mxrf_meta        = mxrf["meta_cotas"] if mxrf else 100
mxrf_pct         = (mxrf_cotas / mxrf_meta) * 100

renda_total      = orcamento["renda_escolar"] + orcamento["renda_freelas"]
sobra            = renda_total - orcamento["gastos_cartao"] - perfil["aporte_mensal"]

# ─── HELPERS HTML ────────────────────────────────────────────────────────────

def brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def pct(valor):
    return f"{valor:.1f}%"

def linhas_fiis():
    html = ""
    for f in fiis:
        meta_txt = f"{f['qtd']}/{f['meta_cotas']}" if f["meta_cotas"] else "Manter"
        cor = 'style="color:var(--amarelo)"' if f["meta_cotas"] else ""
        html += f"""
          <tr>
            <td><span class="ticker">{f['ticker']}</span></td>
            <td>{f['qtd']}</td>
            <td>{brl(f['preco_medio'])}</td>
            <td class="positivo">~{brl(f['dividendo_mes'])}</td>
            <td><span {cor}>{meta_txt}</span></td>
          </tr>"""
    return html

def linhas_acoes():
    html = ""
    for a in acoes:
        html += f"""
          <tr>
            <td><span class="ticker">{a['ticker']}</span></td>
            <td>{a['qtd']}</td>
            <td>{brl(a['preco_medio'])}</td>
            <td><span class="badge-setor">{a['setor']}</span></td>
          </tr>"""
    return html

def linhas_historico():
    html = ""
    for h in reversed(historico):
        html += f"""
          <tr>
            <td>{h['mes']}</td>
            <td>{brl(h['caixinha_deposito'])}</td>
            <td>{brl(h['caixinha_saldo'])}</td>
            <td>{h['mxrf11_cotas']} cotas</td>
            <td>{brl(h['freelas_valor'])}</td>
            <td style="color:var(--texto2);font-size:11px">{h.get('nota','—')}</td>
          </tr>"""
    return html

# ─── TEMPLATE HTML ───────────────────────────────────────────────────────────

html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Meireles — Jornada Financeira</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root {{
  --verde:#00C896; --verde-escuro:#00A07A; --amarelo:#FFD166;
  --fundo:#0A0F0D; --fundo2:#111816; --fundo3:#182420;
  --borda:rgba(0,200,150,0.15); --texto:#E8F5F0; --texto2:#7AA898;
  --fonte-titulo:'Syne',sans-serif; --fonte-mono:'DM Mono',monospace;
}}
*{{margin:0;padding:0;box-sizing:border-box;}} html{{scroll-behavior:smooth;}}
body{{background:var(--fundo);color:var(--texto);font-family:var(--fonte-mono);overflow-x:hidden;}}
body::before{{content:'';position:fixed;inset:0;
  background-image:linear-gradient(rgba(0,200,150,0.03) 1px,transparent 1px),
  linear-gradient(90deg,rgba(0,200,150,0.03) 1px,transparent 1px);
  background-size:40px 40px;pointer-events:none;z-index:0;}}
body::after{{content:'';position:fixed;top:-200px;left:50%;transform:translateX(-50%);
  width:600px;height:400px;
  background:radial-gradient(ellipse,rgba(0,200,150,0.08) 0%,transparent 70%);
  pointer-events:none;z-index:0;}}
.container{{max-width:900px;margin:0 auto;padding:0 20px;position:relative;z-index:1;}}
header{{padding:60px 0 40px;border-bottom:1px solid var(--borda);}}
.tag{{display:inline-block;font-size:11px;letter-spacing:0.15em;color:var(--verde);
  text-transform:uppercase;border:1px solid var(--borda);padding:4px 12px;
  border-radius:2px;margin-bottom:24px;}}
h1{{font-family:var(--fonte-titulo);font-size:clamp(36px,8vw,72px);font-weight:800;
  line-height:1;letter-spacing:-0.02em;margin-bottom:16px;}}
h1 span{{color:var(--verde);}}
.subtitulo{{font-size:14px;color:var(--texto2);line-height:1.7;max-width:500px;}}
.meta-chips{{display:flex;flex-wrap:wrap;gap:8px;margin-top:24px;}}
.chip{{font-size:11px;color:var(--texto2);border:1px solid var(--borda);
  padding:4px 10px;border-radius:2px;letter-spacing:0.05em;}}
.chip.ativo{{color:var(--verde);border-color:rgba(0,200,150,0.3);}}
section{{padding:48px 0;border-bottom:1px solid var(--borda);}}
section:last-child{{border-bottom:none;}}
.section-header{{display:flex;align-items:center;gap:12px;margin-bottom:32px;}}
.section-num{{font-size:11px;color:var(--verde);letter-spacing:0.1em;}}
h2{{font-family:var(--fonte-titulo);font-size:22px;font-weight:700;letter-spacing:-0.01em;}}
.numeros-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
  gap:1px;background:var(--borda);border:1px solid var(--borda);border-radius:4px;overflow:hidden;}}
.numero-item{{background:var(--fundo2);padding:28px 24px;}}
.numero-label{{font-size:11px;color:var(--texto2);letter-spacing:0.08em;margin-bottom:8px;}}
.numero-valor{{font-family:var(--fonte-titulo);font-size:32px;font-weight:800;
  letter-spacing:-0.02em;line-height:1;}}
.numero-valor.verde{{color:var(--verde);}} .numero-valor.amarelo{{color:var(--amarelo);}}
.numero-sub{{font-size:11px;color:var(--texto2);margin-top:6px;}}
.metas-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;}}
.meta-card{{background:var(--fundo2);border:1px solid var(--borda);border-radius:4px;
  padding:24px;position:relative;overflow:hidden;transition:border-color 0.3s;}}
.meta-card:hover{{border-color:rgba(0,200,150,0.4);}}
.meta-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:var(--verde);transform:scaleX(0);transform-origin:left;transition:transform 0.4s;}}
.meta-card:hover::before{{transform:scaleX(1);}}
.meta-icone{{font-size:28px;margin-bottom:12px;}}
.meta-titulo{{font-family:var(--fonte-titulo);font-size:15px;font-weight:700;margin-bottom:8px;}}
.meta-desc{{font-size:12px;color:var(--texto2);line-height:1.6;margin-bottom:16px;}}
.barra-labels{{display:flex;justify-content:space-between;font-size:11px;
  color:var(--texto2);margin-bottom:6px;}}
.barra-labels span:last-child{{color:var(--verde);}}
.barra{{height:4px;background:var(--fundo3);border-radius:2px;overflow:hidden;}}
.barra-fill{{height:100%;background:linear-gradient(90deg,var(--verde-escuro),var(--verde));
  border-radius:2px;}}
.caixinha-card{{background:var(--fundo2);border:1px solid var(--borda);border-radius:4px;
  padding:32px;display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:center;}}
@media(max-width:600px){{.caixinha-card{{grid-template-columns:1fr;}}}}
.caixinha-valor{{font-family:var(--fonte-titulo);font-size:48px;font-weight:800;
  color:var(--verde);letter-spacing:-0.03em;line-height:1;}}
.caixinha-meta{{font-size:12px;color:var(--texto2);margin-top:8px;}}
.barra-grande{{height:8px;background:var(--fundo3);border-radius:4px;overflow:hidden;margin:16px 0 8px;}}
.barra-grande-fill{{height:100%;background:linear-gradient(90deg,var(--verde-escuro),var(--verde));
  border-radius:4px;width:{caixinha_pct:.1f}%;}}
.caixinha-pct{{font-family:var(--fonte-titulo);font-size:13px;color:var(--verde);}}
.caixinha-info{{font-size:12px;color:var(--texto2);line-height:1.8;}}
.table-wrap{{background:var(--fundo2);border:1px solid var(--borda);border-radius:4px;overflow:hidden;}}
table{{width:100%;border-collapse:collapse;}}
thead{{background:var(--fundo3);}}
th{{font-size:10px;letter-spacing:0.12em;color:var(--texto2);text-transform:uppercase;
  padding:12px 16px;text-align:left;font-weight:400;}}
td{{font-size:13px;padding:14px 16px;border-top:1px solid var(--borda);color:var(--texto);}}
tr:hover td{{background:rgba(0,200,150,0.03);}}
.ticker{{font-family:var(--fonte-titulo);font-weight:700;font-size:14px;color:var(--verde);}}
.badge-setor{{font-size:10px;padding:2px 8px;border-radius:2px;background:var(--fundo3);
  color:var(--texto2);border:1px solid var(--borda);}}
.positivo{{color:var(--verde);}}
.freelas-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;}}
@media(max-width:600px){{.freelas-grid{{grid-template-columns:1fr;}}}}
.freela-card{{background:var(--fundo2);border:1px solid var(--borda);border-radius:4px;padding:20px;}}
.freela-titulo{{font-size:11px;color:var(--texto2);letter-spacing:0.08em;margin-bottom:8px;}}
.freela-valor{{font-family:var(--fonte-titulo);font-size:24px;font-weight:700;color:var(--amarelo);}}
.freela-desc{{font-size:11px;color:var(--texto2);margin-top:6px;line-height:1.6;}}
.atualizado{{display:inline-flex;align-items:center;gap:6px;font-size:11px;
  color:var(--texto2);margin-top:16px;}}
.dot-live{{width:6px;height:6px;border-radius:50%;background:var(--verde);animation:pulse 2s infinite;}}
@keyframes pulse{{0%,100%{{opacity:1;transform:scale(1);}}50%{{opacity:0.4;transform:scale(0.8);}}}}
footer{{padding:40px 0;text-align:center;font-size:12px;color:var(--texto2);line-height:1.8;}}
footer a{{color:var(--verde);text-decoration:none;}}
.fade-in{{opacity:0;transform:translateY(20px);transition:opacity 0.6s,transform 0.6s;}}
.fade-in.visivel{{opacity:1;transform:translateY(0);}}
.sobra-positivo{{color:var(--verde);}} .sobra-negativo{{color:#ff6b6b;}}
</style>
</head>
<body>
<div class="container">

<header class="fade-in">
  <div class="tag">// jornada financeira real</div>
  <h1>{perfil['nome']}<br><span>Construindo</span><br>Patrimônio</h1>
  <p class="subtitulo">
    {perfil['profissao']}.<br>
    {brl(perfil['aporte_mensal'])}/mês investidos com consistência. {perfil['familia']}. Casa própria quitada.
    Sem enrolação — números reais, metas reais.
  </p>
  <div class="meta-chips">
    <span class="chip">{perfil['cidade']}</span>
    <span class="chip ativo">⚡ Em transição de carreira</span>
    <span class="chip">Iniciado {perfil['inicio']}</span>
  </div>
  <div class="atualizado">
    <div class="dot-live"></div>
    Atualizado em {atualizado} — orientado pelo Claude (Anthropic)
  </div>
</header>

<section class="fade-in">
  <div class="section-header"><span class="section-num">01 —</span><h2>Visão Geral</h2></div>
  <div class="numeros-grid">
    <div class="numero-item">
      <div class="numero-label">Patrimônio total</div>
      <div class="numero-valor verde">{brl(patrimonio_total)}</div>
      <div class="numero-sub">ações + FIIs</div>
    </div>
    <div class="numero-item">
      <div class="numero-label">Rentabilidade ações</div>
      <div class="numero-valor verde">+{pct(acoes_res['rentabilidade_pct'])}</div>
      <div class="numero-sub">carteira consolidada</div>
    </div>
    <div class="numero-item">
      <div class="numero-label">Dividendos / mês</div>
      <div class="numero-valor amarelo">{brl(dividendos_mes)}</div>
      <div class="numero-sub">renda passiva atual</div>
    </div>
    <div class="numero-item">
      <div class="numero-label">Aporte mensal</div>
      <div class="numero-valor">{brl(perfil['aporte_mensal'])}</div>
      <div class="numero-sub">consistente todo mês</div>
    </div>
  </div>
</section>

<section class="fade-in">
  <div class="section-header"><span class="section-num">02 —</span><h2>Metas</h2></div>
  <div class="metas-grid">
    <div class="meta-card">
      <div class="meta-icone">🚗</div>
      <div class="meta-titulo">Reserva do Carro</div>
      <div class="meta-desc">Proteger minha ferramenta de trabalho. Sem carro, sem renda.</div>
      <div class="barra-labels"><span>{brl(caixinha['saldo'])}</span><span>{brl(caixinha['meta'])}</span></div>
      <div class="barra"><div class="barra-fill" style="width:{min(caixinha_pct,100):.1f}%"></div></div>
    </div>
    <div class="meta-card">
      <div class="meta-icone">📈</div>
      <div class="meta-titulo">100 cotas MXRF11</div>
      <div class="meta-desc">FII de papel com dividendos mensais. Base da renda passiva.</div>
      <div class="barra-labels"><span>{mxrf_cotas} cotas</span><span>{mxrf_meta} cotas</span></div>
      <div class="barra"><div class="barra-fill" style="width:{min(mxrf_pct,100):.1f}%"></div></div>
    </div>
    <div class="meta-card">
      <div class="meta-icone">👨‍👩‍👧‍👦</div>
      <div class="meta-titulo">Estabilidade Familiar</div>
      <div class="meta-desc">{perfil['familia']}. Casa própria quitada. Construindo segurança.</div>
      <div class="barra-labels"><span>Em construção</span><span>Longo prazo</span></div>
      <div class="barra"><div class="barra-fill" style="width:15%"></div></div>
    </div>
    <div class="meta-card">
      <div class="meta-icone">🏖️</div>
      <div class="meta-titulo">Aposentadoria</div>
      <div class="meta-desc">R$ 1.000/mês em dividendos. Patrimônio necessário: R$ 120.000.</div>
      <div class="barra-labels"><span>{brl(patrimonio_total)}</span><span>R$ 120.000</span></div>
      <div class="barra"><div class="barra-fill" style="width:{min((patrimonio_total/120000)*100,100):.1f}%"></div></div>
    </div>
  </div>
</section>

<section class="fade-in">
  <div class="section-header"><span class="section-num">03 —</span><h2>Caixinha do Carro</h2></div>
  <div class="caixinha-card">
    <div>
      <div class="caixinha-valor">{brl(caixinha['saldo'])}</div>
      <div class="caixinha-meta">Meta: {brl(caixinha['meta'])} — {caixinha['onde']}</div>
      <div class="barra-grande"><div class="barra-grande-fill"></div></div>
      <div class="caixinha-pct">{pct(caixinha_pct)} concluído</div>
    </div>
    <div class="caixinha-info">
      Protege contra manutenções inesperadas.<br>
      Todo freela de elétrica vai direto aqui<br>
      até fechar {brl(caixinha['meta'])}.<br><br>
      <span style="color:var(--verde)">Previsão: {caixinha['previsao']}</span>
    </div>
  </div>
</section>

<section class="fade-in">
  <div class="section-header"><span class="section-num">04 —</span><h2>Carteira</h2></div>
  <p style="font-size:12px;color:var(--texto2);margin-bottom:16px">FIIs — Fundos Imobiliários</p>
  <div class="table-wrap" style="margin-bottom:24px">
    <table>
      <thead><tr><th>Ativo</th><th>Qtd</th><th>P. Médio</th><th>Dividendos/mês</th><th>Meta</th></tr></thead>
      <tbody>{linhas_fiis()}</tbody>
    </table>
  </div>
  <p style="font-size:12px;color:var(--texto2);margin-bottom:16px">Ações — Status: manter, não aportar</p>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Ativo</th><th>Qtd</th><th>P. Médio</th><th>Setor</th></tr></thead>
      <tbody>{linhas_acoes()}</tbody>
    </table>
  </div>
  <p style="font-size:11px;color:var(--texto2);margin-top:12px">
    Rentabilidade: <span class="positivo">+{pct(acoes_res['rentabilidade_pct'])}</span>
    &nbsp;|&nbsp; Valor: {brl(acoes_res['valor_total'])}
  </p>
</section>

<section class="fade-in">
  <div class="section-header"><span class="section-num">05 —</span><h2>Orçamento Mensal</h2></div>
  <div class="numeros-grid">
    <div class="numero-item">
      <div class="numero-label">Renda escolar</div>
      <div class="numero-valor">{brl(orcamento['renda_escolar'])}</div>
      <div class="numero-sub">mensal</div>
    </div>
    <div class="numero-item">
      <div class="numero-label">Freelas elétrica</div>
      <div class="numero-valor {'verde' if orcamento['renda_freelas'] > 0 else ''}">{brl(orcamento['renda_freelas'])}</div>
      <div class="numero-sub">{'Este mês' if orcamento['renda_freelas'] > 0 else 'Em construção'}</div>
    </div>
    <div class="numero-item">
      <div class="numero-label">Gastos (cartão)</div>
      <div class="numero-valor">{brl(orcamento['gastos_cartao'])}</div>
      <div class="numero-sub">pago total todo mês ✅</div>
    </div>
    <div class="numero-item">
      <div class="numero-label">Sobra real</div>
      <div class="numero-valor {'verde' if sobra >= 0 else ''}" style="{'color:#ff6b6b' if sobra < 0 else ''}">{brl(sobra)}</div>
      <div class="numero-sub">após investimento</div>
    </div>
  </div>
</section>

<section class="fade-in">
  <div class="section-header"><span class="section-num">06 —</span><h2>Freelas de Elétrica ⚡</h2></div>
  <div class="freelas-grid">
    <div class="freela-card">
      <div class="freela-titulo">FATURADO EM 2026</div>
      <div class="freela-valor">{brl(freelas['faturado_2026'])}</div>
      <div class="freela-desc">Canal: {freelas['canal']}.<br>Meta: 2 serviços/fim de semana.</div>
    </div>
    <div class="freela-card">
      <div class="freela-titulo">POTENCIAL MENSAL</div>
      <div class="freela-valor">R$ 400+</div>
      <div class="freela-desc">Com 2-4 serviços/mês.<br>Técnico em Eletrotécnica formado.</div>
    </div>
    <div class="freela-card">
      <div class="freela-titulo">SERVIÇOS REALIZADOS</div>
      <div class="freela-valor">{freelas['servicos_realizados']}</div>
      <div class="freela-desc">Primeiro serviço vai direto<br>para a caixinha do carro.</div>
    </div>
    <div class="freela-card">
      <div class="freela-titulo">IMPACTO NO PLANO</div>
      <div class="freela-valor" style="font-size:18px;color:var(--verde)">3× mais rápido</div>
      <div class="freela-desc">Com R$ 400/mês extra,<br>metas chegam 3x antes.</div>
    </div>
  </div>
</section>

<section class="fade-in">
  <div class="section-header"><span class="section-num">07 —</span><h2>Histórico</h2></div>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Mês</th><th>Caixinha</th><th>Saldo</th>
          <th>MXRF11</th><th>Freelas</th><th>Nota</th>
        </tr>
      </thead>
      <tbody>{linhas_historico()}</tbody>
    </table>
  </div>
</section>

<footer class="fade-in">
  <p>Esta é uma jornada real — sem filtro, sem perfumaria.</p>
  <p style="margin-top:8px">
    Orientado pelo <a href="https://claude.ai" target="_blank">Claude</a> (Anthropic)
    &nbsp;·&nbsp; {perfil['cidade']}
    &nbsp;·&nbsp; <a href="https://github.com/meirelesnew/minha-carteira" target="_blank">GitHub</a>
  </p>
  <p style="margin-top:16px;font-size:10px;opacity:0.5">
    Não é recomendação de investimento. São escolhas pessoais documentadas publicamente.
  </p>
</footer>

</div>
<script>
const obs = new IntersectionObserver(entries => {{
  entries.forEach((e,i) => {{
    if(e.isIntersecting) setTimeout(()=>e.target.classList.add('visivel'), i*80);
  }});
}}, {{threshold:0.1}});
document.querySelectorAll('.fade-in').forEach(el=>obs.observe(el));
</script>
</body>
</html>"""

# ─── SALVAR ──────────────────────────────────────────────────────────────────

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ index.html gerado com sucesso!")
print(f"   Patrimônio total: {brl(patrimonio_total)}")
print(f"   Dividendos/mês:   {brl(dividendos_mes)}")
print(f"   Caixinha:         {brl(caixinha['saldo'])} / {brl(caixinha['meta'])} ({pct(caixinha_pct)})")
print(f"   MXRF11:           {mxrf_cotas}/{mxrf_meta} cotas ({pct(mxrf_pct)})")
print(f"   Sobra mensal:     {brl(sobra)}")
print()
print("👉 Próximo passo: suba o index.html no GitHub")
