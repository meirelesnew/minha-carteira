"""
gerar.py — Gerador da vitrine financeira responsiva
Uso: python gerar.py
Le dados.json e gera index.html — mobile, tablet e desktop.
"""
import json

with open("dados.json","r",encoding="utf-8") as f:
    d=json.load(f)

perfil=d["perfil"]; caixinha=d["caixinha"]; fiis=d["carteira_fiis"]
acoes=d["carteira_acoes"]; acoes_res=d["acoes_resumo"]
orcamento=d["orcamento"]; freelas=d["freelas"]
historico=d["historico"]; atualizado=d["ultima_atualizacao"]

def brl(v): return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")
def pct(v): return f"{v:.1f}%"

patrimonio_total=acoes_res["valor_total"]+sum(f["qtd"]*f["preco_medio"] for f in fiis)
dividendos_mes=sum(f["dividendo_mes"] for f in fiis)
caixinha_pct=min((caixinha["saldo"]/caixinha["meta"])*100,100)
mxrf=next((f for f in fiis if f["ticker"]=="MXRF11"),None)
mxrf_cotas=mxrf["qtd"] if mxrf else 0
mxrf_meta=mxrf["meta_cotas"] if mxrf else 100
mxrf_pct=min((mxrf_cotas/mxrf_meta)*100,100)
sobra=orcamento["renda_escolar"]+orcamento["renda_freelas"]-orcamento["gastos_cartao"]-perfil["aporte_mensal"]

def rows_fiis():
    out=""
    for f in fiis:
        meta=f"{f['qtd']}/{f['meta_cotas']}" if f["meta_cotas"] else "Manter"
        cor='class="amarelo"' if f["meta_cotas"] else ""
        out+=f'<tr><td data-label="Ativo"><span class="ticker">{f["ticker"]}</span></td><td data-label="Qtd">{f["qtd"]}</td><td data-label="P.Medio">{brl(f["preco_medio"])}</td><td data-label="Dividendos" class="positivo">~{brl(f["dividendo_mes"])}</td><td data-label="Meta"><span {cor}>{meta}</span></td></tr>'
    return out

def rows_acoes():
    out=""
    for a in acoes:
        out+=f'<tr><td data-label="Ativo"><span class="ticker">{a["ticker"]}</span></td><td data-label="Qtd">{a["qtd"]}</td><td data-label="P.Medio">{brl(a["preco_medio"])}</td><td data-label="Setor"><span class="badge">{a["setor"]}</span></td></tr>'
    return out

def rows_hist():
    out=""
    for h in reversed(historico):
        out+=f'<tr><td data-label="Mes"><strong>{h["mes"]}</strong></td><td data-label="Deposito">{brl(h["caixinha_deposito"])}</td><td data-label="Saldo" class="positivo">{brl(h["caixinha_saldo"])}</td><td data-label="MXRF11">{h["mxrf11_cotas"]} cotas</td><td data-label="Freelas">{brl(h["freelas_valor"])}</td><td data-label="Nota" class="nota">{h.get("nota","")}</td></tr>'
    return out

sobra_class="verde" if sobra>=0 else "vermelho"
freela_class="verde" if orcamento["renda_freelas"]>0 else ""
freela_sub="este mes" if orcamento["renda_freelas"]>0 else "em construcao"
apo_pct=min((patrimonio_total/120000)*100,100)

HTML=f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,viewport-fit=cover">
<meta name="description" content="Jornada financeira real de Meireles — Duque de Caxias/RJ.">
<meta name="theme-color" content="#090E0C">
<title>Meireles — Jornada Financeira</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@300;400&display=swap" rel="stylesheet">
<style>
:root{{
  --g:#00C896;--gd:#00A07A;--am:#FFD166;--vm:#FF6B6B;
  --f:#090E0C;--f2:#111816;--f3:#1A2520;
  --b:rgba(0,200,150,.12);--bh:rgba(0,200,150,.35);
  --t:#E8F5F0;--t2:#6B9E8C;--t3:#3D6B5A;
  --TT:'Syne',sans-serif;--MM:'DM Mono',monospace;
  --r:8px;--rs:4px;
  --gap:clamp(12px,3vw,24px);
  --pad:clamp(16px,4vw,32px);
  --ps:clamp(12px,2vw,20px);
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{font-size:16px;scroll-behavior:smooth;-webkit-text-size-adjust:100%}}
body{{background:var(--f);color:var(--t);font-family:var(--MM);overflow-x:hidden;line-height:1.6}}
body::before{{content:'';position:fixed;inset:0;
  background-image:linear-gradient(rgba(0,200,150,.025) 1px,transparent 1px),
  linear-gradient(90deg,rgba(0,200,150,.025) 1px,transparent 1px);
  background-size:clamp(24px,5vw,40px) clamp(24px,5vw,40px);pointer-events:none;z-index:0}}
body::after{{content:'';position:fixed;top:-30vh;left:50%;transform:translateX(-50%);
  width:min(700px,120vw);height:50vh;
  background:radial-gradient(ellipse,rgba(0,200,150,.07) 0%,transparent 70%);
  pointer-events:none;z-index:0}}
.wrap{{max-width:960px;margin:0 auto;padding:0 var(--pad);position:relative;z-index:1}}
section{{padding:clamp(32px,6vw,56px) 0;border-bottom:1px solid var(--b)}}
section:last-of-type{{border-bottom:none}}
h1{{font-family:var(--TT);font-size:clamp(38px,9vw,80px);font-weight:800;line-height:.95;letter-spacing:-.03em;margin-bottom:clamp(12px,2vw,20px)}}
h1 .g{{color:var(--g)}}
h2{{font-family:var(--TT);font-size:clamp(18px,3.5vw,26px);font-weight:700;letter-spacing:-.01em}}
h3{{font-size:clamp(11px,2vw,13px);color:var(--t2);letter-spacing:.1em;text-transform:uppercase;font-weight:400;margin-bottom:clamp(4px,1vw,8px)}}
header{{padding:clamp(40px,8vw,80px) 0 clamp(28px,5vw,48px);border-bottom:1px solid var(--b)}}
.tag{{display:inline-flex;align-items:center;gap:8px;font-size:clamp(10px,2vw,12px);color:var(--g);
  letter-spacing:.15em;text-transform:uppercase;border:1px solid var(--b);
  padding:5px 14px;border-radius:2px;margin-bottom:clamp(16px,4vw,28px)}}
.sub{{font-size:clamp(13px,2.5vw,15px);color:var(--t2);line-height:1.75;max-width:520px;margin-bottom:clamp(16px,3vw,24px)}}
.chips{{display:flex;flex-wrap:wrap;gap:clamp(6px,1.5vw,10px);margin-bottom:clamp(12px,2vw,20px)}}
.chip{{font-size:clamp(10px,2vw,12px);color:var(--t2);border:1px solid var(--b);padding:4px 12px;border-radius:2px;letter-spacing:.04em;white-space:nowrap}}
.chip.on{{color:var(--g);border-color:rgba(0,200,150,.3)}}
.live{{display:inline-flex;align-items:center;gap:8px;font-size:clamp(10px,2vw,12px);color:var(--t2)}}
.dot{{width:7px;height:7px;border-radius:50%;background:var(--g);flex-shrink:0;animation:pulse 2.2s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:1;box-shadow:0 0 0 0 rgba(0,200,150,.4)}}50%{{opacity:.5;box-shadow:0 0 0 5px rgba(0,200,150,0)}}}}
.sh{{display:flex;align-items:center;gap:clamp(8px,2vw,14px);margin-bottom:clamp(20px,4vw,36px)}}
.sn{{font-size:clamp(10px,2vw,12px);color:var(--g);letter-spacing:.1em;flex-shrink:0}}
/* GRIDS NUMERICOS */
.ng{{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:var(--b);border:1px solid var(--b);border-radius:var(--r);overflow:hidden}}
@media(min-width:640px){{.ng{{grid-template-columns:repeat(4,1fr)}}}}
.ni{{background:var(--f2);padding:var(--pad);transition:background .25s}}
.ni:hover{{background:var(--f3)}}
.nv{{font-family:var(--TT);font-size:clamp(22px,5vw,36px);font-weight:800;letter-spacing:-.03em;line-height:1;margin-bottom:6px}}
.nv.verde{{color:var(--g)}}.nv.amarelo{{color:var(--am)}}.nv.vermelho{{color:var(--vm)}}
.ns{{font-size:clamp(10px,2vw,12px);color:var(--t2)}}
/* METAS */
.mg{{display:grid;grid-template-columns:1fr;gap:var(--gap)}}
@media(min-width:480px){{.mg{{grid-template-columns:repeat(2,1fr)}}}}
.mc{{background:var(--f2);border:1px solid var(--b);border-radius:var(--r);padding:var(--pad);
  position:relative;overflow:hidden;transition:border-color .25s,transform .25s,box-shadow .25s;
  display:flex;flex-direction:column}}
.mc:hover{{border-color:var(--bh);transform:translateY(-2px);box-shadow:0 4px 24px rgba(0,0,0,.4)}}
.mc::after{{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,var(--gd),var(--g));
  transform:scaleX(0);transform-origin:left;transition:transform .4s}}
.mc:hover::after{{transform:scaleX(1)}}
.mi{{font-size:clamp(24px,5vw,32px);margin-bottom:12px}}
.mt{{font-family:var(--TT);font-size:clamp(14px,2.5vw,17px);font-weight:700;margin-bottom:6px}}
.md{{font-size:clamp(11px,2vw,13px);color:var(--t2);line-height:1.65;margin-bottom:16px;flex:1}}
.bl{{display:flex;justify-content:space-between;font-size:clamp(10px,2vw,12px);color:var(--t2);margin-bottom:6px}}
.bl span:last-child{{color:var(--g)}}
.bar{{height:5px;background:var(--f3);border-radius:99px;overflow:hidden}}
.bf{{height:100%;background:linear-gradient(90deg,var(--gd),var(--g));border-radius:99px}}
/* CAIXINHA */
.cc{{background:var(--f2);border:1px solid var(--b);border-radius:var(--r);padding:var(--pad);
  display:grid;grid-template-columns:1fr;gap:var(--gap)}}
@media(min-width:600px){{.cc{{grid-template-columns:1fr 1fr;align-items:center}}}}
.cv{{font-family:var(--TT);font-size:clamp(40px,10vw,64px);font-weight:800;color:var(--g);letter-spacing:-.04em;line-height:1}}
.cm{{font-size:clamp(11px,2vw,13px);color:var(--t2);margin-top:8px}}
.blg{{height:10px;background:var(--f3);border-radius:99px;overflow:hidden;margin:14px 0 8px}}
.blgf{{height:100%;background:linear-gradient(90deg,var(--gd),var(--g));border-radius:99px;width:{caixinha_pct:.1f}%}}
.cp{{font-family:var(--TT);font-size:clamp(13px,2.5vw,15px);color:var(--g)}}
.ci{{font-size:clamp(12px,2vw,14px);color:var(--t2);line-height:1.9}}
.ci .dest{{color:var(--g)}}
/* TABELAS */
.tw{{background:var(--f2);border:1px solid var(--b);border-radius:var(--r);overflow:hidden;margin-bottom:var(--gap)}}
table{{width:100%;border-collapse:collapse}}
thead{{background:var(--f3)}}
th{{font-size:clamp(9px,1.5vw,11px);letter-spacing:.12em;color:var(--t2);text-transform:uppercase;
  padding:clamp(10px,2vw,14px) clamp(12px,2.5vw,18px);text-align:left;font-weight:400;white-space:nowrap}}
td{{font-size:clamp(12px,2vw,14px);padding:clamp(12px,2vw,16px) clamp(12px,2.5vw,18px);
  border-top:1px solid var(--b);transition:background .2s}}
tr:hover td{{background:rgba(0,200,150,.04)}}
@media(max-width:600px){{
  table,thead,tbody,tr,th,td{{display:block}}
  thead{{display:none}}
  tr{{border:1px solid var(--b);border-radius:var(--rs);margin-bottom:8px;background:var(--f3);overflow:hidden}}
  td{{display:flex;justify-content:space-between;align-items:center;
    border-top:1px solid var(--b);padding:10px 14px;font-size:13px}}
  td:first-child{{border-top:none}}
  td::before{{content:attr(data-label);font-size:10px;color:var(--t2);letter-spacing:.1em;
    text-transform:uppercase;flex-shrink:0;margin-right:12px}}
  .tw{{border-radius:0;border-left:none;border-right:none}}
}}
.ticker{{font-family:var(--TT);font-weight:700;font-size:clamp(13px,2.5vw,15px);color:var(--g)}}
.badge{{font-size:clamp(9px,1.8vw,11px);padding:3px 9px;border-radius:2px;
  background:var(--f3);color:var(--t2);border:1px solid var(--b);white-space:nowrap}}
.positivo{{color:var(--g)}}.amarelo{{color:var(--am)}}.nota{{color:var(--t2);font-size:11px}}
/* ORCAMENTO */
.og{{display:grid;grid-template-columns:1fr;gap:var(--gap)}}
@media(min-width:480px){{.og{{grid-template-columns:repeat(2,1fr)}}}}
@media(min-width:800px){{.og{{grid-template-columns:repeat(4,1fr)}}}}
.oc{{background:var(--f2);border:1px solid var(--b);border-radius:var(--r);
  padding:var(--ps) var(--pad);transition:border-color .25s}}
.oc:hover{{border-color:var(--bh)}}
/* FREELAS */
.fg{{display:grid;grid-template-columns:repeat(2,1fr);gap:var(--gap)}}
@media(min-width:640px){{.fg{{grid-template-columns:repeat(4,1fr)}}}}
.fc{{background:var(--f2);border:1px solid var(--b);border-radius:var(--r);padding:var(--ps);
  transition:border-color .25s,transform .25s}}
.fc:hover{{border-color:var(--bh);transform:translateY(-2px)}}
.fl{{font-size:clamp(9px,1.8vw,11px);color:var(--t2);letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px}}
.fv{{font-family:var(--TT);font-size:clamp(18px,4vw,26px);font-weight:700;color:var(--am);line-height:1}}
.fd{{font-size:clamp(10px,2vw,12px);color:var(--t2);margin-top:8px;line-height:1.6}}
/* TIMELINE */
.tl{{display:flex;flex-direction:column}}
.ti{{display:flex;gap:clamp(14px,3vw,22px)}}
.tll{{display:flex;flex-direction:column;align-items:center;width:18px;flex-shrink:0}}
.td{{width:10px;height:10px;border-radius:50%;background:var(--g);flex-shrink:0;margin-top:4px}}
.td.v{{background:transparent;border:1.5px solid var(--t3)}}
.tln{{width:1px;flex:1;min-height:20px;background:var(--b);margin:4px 0}}
.tr{{padding-bottom:clamp(20px,4vw,32px);flex:1}}
.tf{{font-size:clamp(9px,2vw,11px);color:var(--g);letter-spacing:.1em;text-transform:uppercase;margin-bottom:4px}}
.tt{{font-family:var(--TT);font-size:clamp(15px,3vw,18px);font-weight:700;margin-bottom:4px}}
.tdsc{{font-size:clamp(11px,2vw,13px);color:var(--t2);line-height:1.7}}
/* NAV MOBILE */
.nm{{display:none;position:fixed;bottom:0;left:0;right:0;
  background:rgba(9,14,12,.95);backdrop-filter:blur(12px);
  border-top:1px solid var(--b);
  padding:10px var(--pad) calc(10px + env(safe-area-inset-bottom));
  z-index:100;justify-content:space-around}}
@media(max-width:640px){{.nm{{display:flex}}footer{{padding-bottom:80px}}}}
.na{{display:flex;flex-direction:column;align-items:center;gap:3px;
  font-size:9px;color:var(--t2);letter-spacing:.05em;text-transform:uppercase;
  text-decoration:none;padding:4px 8px;border-radius:4px;transition:color .2s;cursor:pointer}}
.na:hover,.na.on{{color:var(--g)}}
.ni2{{font-size:18px;line-height:1}}
/* FOOTER */
footer{{padding:clamp(28px,5vw,48px) 0;text-align:center;
  font-size:clamp(11px,2vw,13px);color:var(--t2);line-height:1.9}}
footer a{{color:var(--g);text-decoration:none}}
footer a:hover{{text-decoration:underline}}
.fl2{{font-size:10px;opacity:.4;margin-top:14px}}
/* ANIMS */
.fade{{opacity:0;transform:translateY(18px);transition:opacity .55s,transform .55s}}
.fade.on{{opacity:1;transform:translateY(0)}}
.mc:nth-child(1){{transition-delay:0s}}.mc:nth-child(2){{transition-delay:.08s}}
.mc:nth-child(3){{transition-delay:.16s}}.mc:nth-child(4){{transition-delay:.24s}}
::-webkit-scrollbar{{width:6px;height:6px}}
::-webkit-scrollbar-track{{background:var(--f)}}
::-webkit-scrollbar-thumb{{background:var(--t3);border-radius:3px}}
::-webkit-scrollbar-thumb:hover{{background:var(--gd)}}
::selection{{background:rgba(0,200,150,.25);color:var(--t)}}
</style>
</head>
<body>
<nav class="nm" role="navigation">
  <a class="na" href="#visao"><span class="ni2">📊</span>Visao</a>
  <a class="na" href="#metas"><span class="ni2">🎯</span>Metas</a>
  <a class="na" href="#carteira"><span class="ni2">📈</span>Carteira</a>
  <a class="na" href="#freelas"><span class="ni2">⚡</span>Freelas</a>
  <a class="na" href="#historico"><span class="ni2">📅</span>Historico</a>
</nav>
<div class="wrap">
<header class="fade">
  <div class="tag"><span class="dot"></span>jornada financeira real</div>
  <h1>{perfil['nome']}<br><span class="g">Construindo</span><br>Patrimonio</h1>
  <p class="sub">{perfil['profissao']}.<br>{brl(perfil['aporte_mensal'])}/mes com consistencia.<br>{perfil['familia']} — casa propria quitada.<br>Numeros reais, sem filtro.</p>
  <div class="chips">
    <span class="chip">{perfil['cidade']}</span>
    <span class="chip on">⚡ Em transicao de carreira</span>
    <span class="chip">Desde {perfil['inicio']}</span>
  </div>
  <div class="live"><span class="dot"></span>Atualizado em {atualizado} · orientado pelo Claude (Anthropic)</div>
</header>

<section class="fade" id="visao">
  <div class="sh"><span class="sn">01 —</span><h2>Visao Geral</h2></div>
  <div class="ng">
    <div class="ni"><h3>Patrimonio total</h3><div class="nv verde">{brl(patrimonio_total)}</div><div class="ns">acoes + FIIs</div></div>
    <div class="ni"><h3>Rentabilidade</h3><div class="nv verde">+{pct(acoes_res['rentabilidade_pct'])}</div><div class="ns">carteira de acoes</div></div>
    <div class="ni"><h3>Dividendos/mes</h3><div class="nv amarelo">{brl(dividendos_mes)}</div><div class="ns">renda passiva atual</div></div>
    <div class="ni"><h3>Aporte mensal</h3><div class="nv">{brl(perfil['aporte_mensal'])}</div><div class="ns">todo mes sem falta</div></div>
  </div>
</section>

<section class="fade" id="metas">
  <div class="sh"><span class="sn">02 —</span><h2>Metas</h2></div>
  <div class="mg">
    <div class="mc fade"><div class="mi">🚗</div><div class="mt">Reserva do Carro</div><div class="md">Proteger a ferramenta de trabalho. Sem carro, sem renda.</div><div class="bl"><span>{brl(caixinha['saldo'])}</span><span>{brl(caixinha['meta'])}</span></div><div class="bar"><div class="bf" style="width:{caixinha_pct:.1f}%"></div></div></div>
    <div class="mc fade"><div class="mi">📈</div><div class="mt">100 cotas MXRF11</div><div class="md">FII com dividendos mensais. Base da renda passiva.</div><div class="bl"><span>{mxrf_cotas} cotas</span><span>{mxrf_meta} cotas</span></div><div class="bar"><div class="bf" style="width:{mxrf_pct:.1f}%"></div></div></div>
    <div class="mc fade"><div class="mi">👨‍👩‍👧‍👦</div><div class="mt">Estabilidade Familiar</div><div class="md">{perfil['familia']}. Casa propria quitada. Construindo seguranca.</div><div class="bl"><span>Em construcao</span><span>Longo prazo</span></div><div class="bar"><div class="bf" style="width:15%"></div></div></div>
    <div class="mc fade"><div class="mi">🏖️</div><div class="mt">Aposentadoria</div><div class="md">R$ 1.000/mes em dividendos. Alvo: R$ 120.000.</div><div class="bl"><span>{brl(patrimonio_total)}</span><span>R$ 120.000</span></div><div class="bar"><div class="bf" style="width:{apo_pct:.1f}%"></div></div></div>
  </div>
</section>

<section class="fade" id="caixinha">
  <div class="sh"><span class="sn">03 —</span><h2>Caixinha do Carro</h2></div>
  <div class="cc">
    <div><div class="cv">{brl(caixinha['saldo'])}</div><div class="cm">Meta: {brl(caixinha['meta'])} — {caixinha['onde']}</div><div class="blg"><div class="blgf"></div></div><div class="cp">{pct(caixinha_pct)} concluido</div></div>
    <div class="ci">Protege contra manutencoes inesperadas.<br>Todo freela vai direto aqui<br>ate completar {brl(caixinha['meta'])}.<br><br><span class="dest">Previsao: {caixinha['previsao']}</span></div>
  </div>
</section>

<section class="fade" id="carteira">
  <div class="sh"><span class="sn">04 —</span><h2>Carteira</h2></div>
  <h3 style="margin-bottom:12px">FIIs — Fundos Imobiliarios</h3>
  <div class="tw"><table><thead><tr><th>Ativo</th><th>Qtd</th><th>P.Medio</th><th>Dividendos/mes</th><th>Meta</th></tr></thead><tbody>{rows_fiis()}</tbody></table></div>
  <h3 style="margin:20px 0 12px">Acoes — manter, nao aportar</h3>
  <div class="tw"><table><thead><tr><th>Ativo</th><th>Qtd</th><th>P.Medio</th><th>Setor</th></tr></thead><tbody>{rows_acoes()}</tbody></table></div>
  <p style="font-size:12px;color:var(--t2);margin-top:10px">Rentabilidade: <span class="positivo">+{pct(acoes_res['rentabilidade_pct'])}</span> &nbsp;|&nbsp; Valor: {brl(acoes_res['valor_total'])}</p>
</section>

<section class="fade" id="orcamento">
  <div class="sh"><span class="sn">05 —</span><h2>Orcamento Mensal</h2></div>
  <div class="og">
    <div class="oc"><h3>Renda escolar</h3><div class="nv" style="font-size:clamp(20px,4vw,28px)">{brl(orcamento['renda_escolar'])}</div><div class="ns">mensal</div></div>
    <div class="oc"><h3>Freelas eletrica</h3><div class="nv {freela_class}" style="font-size:clamp(20px,4vw,28px)">{brl(orcamento['renda_freelas'])}</div><div class="ns">{freela_sub}</div></div>
    <div class="oc"><h3>Gastos (cartao)</h3><div class="nv" style="font-size:clamp(20px,4vw,28px)">{brl(orcamento['gastos_cartao'])}</div><div class="ns">pago total todo mes</div></div>
    <div class="oc"><h3>Sobra real</h3><div class="nv {sobra_class}" style="font-size:clamp(20px,4vw,28px)">{brl(sobra)}</div><div class="ns">apos investimento</div></div>
  </div>
</section>

<section class="fade" id="freelas">
  <div class="sh"><span class="sn">06 —</span><h2>Freelas de Eletrica</h2></div>
  <div class="fg">
    <div class="fc"><div class="fl">Faturado 2026</div><div class="fv">{brl(freelas['faturado_2026'])}</div><div class="fd">Canal: {freelas['canal']}.<br>Meta: 2 servicos/fim de semana.</div></div>
    <div class="fc"><div class="fl">Potencial mensal</div><div class="fv">R$ 400+</div><div class="fd">Com 2-4 servicos.<br>Tecnico formado.</div></div>
    <div class="fc"><div class="fl">Servicos realizados</div><div class="fv">{freelas['servicos_realizados']}</div><div class="fd">Primeiro freela vai<br>100% na caixinha.</div></div>
    <div class="fc"><div class="fl">Impacto no plano</div><div class="fv" style="color:var(--g);font-size:clamp(16px,3.5vw,22px)">3x mais rapido</div><div class="fd">Com R$ 400 extra/mes<br>metas chegam antes.</div></div>
  </div>
</section>

<section class="fade" id="plano">
  <div class="sh"><span class="sn">07 —</span><h2>Plano de Fases</h2></div>
  <div class="tl">
    <div class="ti"><div class="tll"><div class="td"></div><div class="tln"></div></div><div class="tr"><div class="tf">Fase 1 — Mai a Dez/2026</div><div class="tt">Proteger a renda</div><div class="tdsc">R$ 100/mes na caixinha ate R$ 800. Prioridade absoluta.</div></div></div>
    <div class="ti"><div class="tll"><div class="td v"></div><div class="tln"></div></div><div class="tr"><div class="tf">Fase 2 — Jan/2027</div><div class="tt">100 cotas MXRF11</div><div class="tdsc">R$ 100/mes inteiros em MXRF11 + reinvestir dividendos. ~4 meses.</div></div></div>
    <div class="ti"><div class="tll"><div class="td v"></div><div class="tln"></div></div><div class="tr"><div class="tf">Fase 3 — 2027/2028</div><div class="tt">Diversificar FIIs</div><div class="tdsc">Expandir para outros FIIs de qualidade. Aumentar renda passiva.</div></div></div>
    <div class="ti"><div class="tll"><div class="td v"></div></div><div class="tr"><div class="tf">Fase 4 — Longo prazo</div><div class="tt">Aposentadoria</div><div class="tdsc">R$ 1.000/mes em dividendos. Com freelas: ~13 anos.</div></div></div>
  </div>
</section>

<section class="fade" id="historico">
  <div class="sh"><span class="sn">08 —</span><h2>Historico</h2></div>
  <div class="tw"><table><thead><tr><th>Mes</th><th>Deposito</th><th>Saldo</th><th>MXRF11</th><th>Freelas</th><th>Nota</th></tr></thead><tbody>{rows_hist()}</tbody></table></div>
</section>

<footer class="fade">
  <p>Jornada real — sem filtro, sem perfumaria.</p>
  <p style="margin-top:6px">Orientado pelo <a href="https://claude.ai" target="_blank">Claude</a> (Anthropic) &nbsp;·&nbsp; {perfil['cidade']} &nbsp;·&nbsp; <a href="https://github.com/meirelesnew/minha-carteira" target="_blank">GitHub</a></p>
  <p class="fl2">Nao e recomendacao de investimento. Sao escolhas pessoais documentadas publicamente.</p>
</footer>
</div>
<script>
const io=new IntersectionObserver(entries=>{{entries.forEach((e,i)=>{{if(e.isIntersecting){{setTimeout(()=>e.target.classList.add('on'),i*60);io.unobserve(e.target)}}}})}},{{threshold:.08}});
document.querySelectorAll('.fade').forEach(el=>io.observe(el));
const secs=document.querySelectorAll('section[id],header');
const navs=document.querySelectorAll('.na');
const sio=new IntersectionObserver(entries=>{{entries.forEach(e=>{{if(e.isIntersecting)navs.forEach(n=>n.classList.toggle('on',n.getAttribute('href')==='#'+e.target.id))}}))}},{{threshold:.4}});
secs.forEach(s=>sio.observe(s));
</script>
</body>
</html>"""

with open("index.html","w",encoding="utf-8") as f:
    f.write(HTML)

print("Vitrine responsiva gerada!")
print(f"  Patrimonio: {brl(patrimonio_total)}")
print(f"  Dividendos: {brl(dividendos_mes)}/mes")
print(f"  Caixinha:   {brl(caixinha['saldo'])} / {brl(caixinha['meta'])} ({pct(caixinha_pct)})")
print(f"  MXRF11:     {mxrf_cotas}/{mxrf_meta} cotas")
print(f"  Sobra:      {brl(sobra)}/mes")
