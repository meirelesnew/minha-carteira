"""
gerar.py — Vitrine financeira com sinais de mercado e carteira balanceada
Uso: python gerar.py
"""
import json

with open("dados.json","r",encoding="utf-8") as f:
    d=json.load(f)

perfil=d["perfil"]; caixinha=d["caixinha"]; fiis=d["carteira_fiis"]
acoes=d["carteira_acoes"]; acoes_res=d["acoes_resumo"]
orcamento=d["orcamento"]; freelas_d=d["freelas"]
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
sobra_class="verde" if sobra>=0 else "vermelho"
freela_class="verde" if orcamento["renda_freelas"]>0 else ""
freela_sub="este mes" if orcamento["renda_freelas"]>0 else "em construcao"
apo_pct=min((patrimonio_total/120000)*100,100)

# Sinais de mercado baseados no cenário Mai/2026
sinais = [
    {"ativo":"MXRF11","tipo":"FII Papel","sinal":"COMPRAR","cor":"verde","motivo":"FIIs descontados vs VP. Selic em queda favorece. Yield ~10% atrativo."},
    {"ativo":"GARE11","tipo":"FII Logística","sinal":"MANTER","cor":"amarelo","motivo":"Bom ativo mas aguardar queda de juros para forte valorização."},
    {"ativo":"ITSA4","tipo":"Ação","sinal":"MANTER","cor":"amarelo","motivo":"Holding Itaú sólida. Aguardar preço mais atrativo para novo aporte."},
    {"ativo":"BBAS3","tipo":"Ação","sinal":"MANTER","cor":"amarelo","motivo":"Banco do Brasil paga bons dividendos. Risco político monitorar."},
    {"ativo":"EGIE3","tipo":"Ação","sinal":"COMPRAR","cor":"verde","motivo":"Energia elétrica defensiva. Dividendos consistentes. Bom para longo prazo."},
    {"ativo":"TAEE11","tipo":"Ação","sinal":"COMPRAR","cor":"verde","motivo":"Transmissão elétrica com receita previsível. Ótimo pagador de dividendos."},
    {"ativo":"BBSE3","tipo":"Ação","sinal":"MANTER","cor":"amarelo","motivo":"BB Seguridade sólida. Carteira já tem exposição adequada."},
    {"ativo":"KLBN4","tipo":"Ação","sinal":"MANTER","cor":"amarelo","motivo":"Papel/celulose sensível ao câmbio. Aguardar momento mais claro."},
    {"ativo":"WEGE3","tipo":"Ação","sinal":"MANTER","cor":"amarelo","motivo":"WEG é excelente empresa mas negocia a múltiplos elevados. Paciência."},
]

# Carteira balanceada ideal (10% cada ativo = 10 ativos)
carteira_ideal = [
    {"ticker":"MXRF11","tipo":"FII Papel","pct":10,"motivo":"Dividendos mensais, defensivo"},
    {"ticker":"GARE11","tipo":"FII Logística","pct":10,"motivo":"Imóveis de logística, crescimento"},
    {"ticker":"HGLG11","tipo":"FII Logística","pct":10,"motivo":"Um dos maiores FIIs do Brasil"},
    {"ticker":"XPLG11","tipo":"FII Logística","pct":10,"motivo":"Alta qualidade, bem gerido"},
    {"ticker":"ITSA4","tipo":"Ação","pct":10,"motivo":"Holding Itaú, sólida e defensiva"},
    {"ticker":"BBAS3","tipo":"Ação","pct":10,"motivo":"Banco do Brasil, bons dividendos"},
    {"ticker":"EGIE3","tipo":"Ação","pct":10,"motivo":"Energia elétrica, receita previsível"},
    {"ticker":"TAEE11","tipo":"Ação","pct":10,"motivo":"Transmissão, dividendos robustos"},
    {"ticker":"WEGE3","tipo":"Ação","pct":10,"motivo":"Crescimento de longo prazo"},
    {"ticker":"KLBN4","tipo":"Ação","pct":10,"motivo":"Papel/celulose, exportações"},
]

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

def cards_sinais():
    out=""
    for s in sinais:
        if s["sinal"]=="COMPRAR":
            sc="sinal-comprar"; ic="▲ COMPRAR"
        elif s["sinal"]=="VENDER":
            sc="sinal-vender"; ic="▼ VENDER"
        else:
            sc="sinal-manter"; ic="● MANTER"
        out+=f'''<div class="sinal-card">
  <div class="sinal-top">
    <div>
      <div class="sinal-ticker">{s["ativo"]}</div>
      <div class="sinal-tipo">{s["tipo"]}</div>
    </div>
    <div class="sinal-badge {sc}">{ic}</div>
  </div>
  <div class="sinal-motivo">{s["motivo"]}</div>
</div>'''
    return out

def rows_ideal():
    out=""
    for c in carteira_ideal:
        tipo_class = "badge-fii" if "FII" in c["tipo"] else "badge-acao"
        out+=f'''<tr>
  <td data-label="Ativo"><span class="ticker">{c["ticker"]}</span></td>
  <td data-label="Tipo"><span class="badge {tipo_class}">{c["tipo"]}</span></td>
  <td data-label="Peso">
    <div class="peso-wrap">
      <div class="peso-bar"><div class="peso-fill" style="width:{c["pct"]}%"></div></div>
      <span class="peso-num">{c["pct"]}%</span>
    </div>
  </td>
  <td data-label="Por que" class="nota">{c["motivo"]}</td>
</tr>'''
    return out

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
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
/* ── TOKENS ── */
:root{{
  --g:#00C896;--gd:#009973;--am:#FFD166;--vm:#FF6B6B;--az:#60A5FA;
  --f:#090E0C;--f2:#111816;--f3:#1A2520;--f4:#0F1A17;
  --b:rgba(0,200,150,.1);--bh:rgba(0,200,150,.3);
  --t:#E8F5F0;--t2:#7AA898;--t3:#3D6B5A;
  --TT:'Playfair Display',serif;
  --MM:'Inter',sans-serif;
  --r:10px;--rs:6px;
  --gap:clamp(12px,3vw,24px);
  --pad:clamp(16px,4vw,32px);
  --ps:clamp(12px,2vw,20px);
  --sh:0 2px 20px rgba(0,0,0,.3);
}}

/* ── RESET ── */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth;-webkit-text-size-adjust:100%}}
body{{
  background:var(--f);
  color:var(--t);
  font-family:var(--MM);
  font-size:16px;
  line-height:1.7;
  overflow-x:hidden;
  font-weight:400;
  -webkit-font-smoothing:antialiased;
}}

/* ── FUNDO ── */
body::before{{
  content:'';position:fixed;inset:0;
  background-image:linear-gradient(rgba(0,200,150,.02) 1px,transparent 1px),
    linear-gradient(90deg,rgba(0,200,150,.02) 1px,transparent 1px);
  background-size:clamp(24px,5vw,48px) clamp(24px,5vw,48px);
  pointer-events:none;z-index:0;
}}
body::after{{
  content:'';position:fixed;top:-40vh;left:50%;transform:translateX(-50%);
  width:min(800px,150vw);height:60vh;
  background:radial-gradient(ellipse,rgba(0,200,150,.06) 0%,transparent 65%);
  pointer-events:none;z-index:0;
}}

/* ── LAYOUT ── */
.wrap{{max-width:980px;margin:0 auto;padding:0 var(--pad);position:relative;z-index:1}}
section{{padding:clamp(36px,7vw,64px) 0;border-bottom:1px solid var(--b)}}
section:last-of-type{{border-bottom:none}}

/* ── TIPOGRAFIA ── */
h1{{
  font-family:var(--TT);
  font-size:clamp(42px,10vw,88px);
  font-weight:800;
  line-height:1.0;
  letter-spacing:-.01em;
  margin-bottom:clamp(14px,2.5vw,24px);
}}
h1 .g{{color:var(--g)}}

h2{{
  font-family:var(--TT);
  font-size:clamp(22px,4vw,32px);
  font-weight:700;
  letter-spacing:-.01em;
  line-height:1.2;
}}

h3{{
  font-family:var(--MM);
  font-size:clamp(10px,1.8vw,12px);
  font-weight:600;
  color:var(--t2);
  letter-spacing:.12em;
  text-transform:uppercase;
  margin-bottom:clamp(4px,1vw,8px);
}}

p{{font-size:clamp(14px,2vw,16px);color:var(--t2);line-height:1.8}}

/* ── HEADER ── */
header{{
  padding:clamp(48px,10vw,96px) 0 clamp(32px,6vw,56px);
  border-bottom:1px solid var(--b);
}}

.tag{{
  display:inline-flex;align-items:center;gap:10px;
  font-family:var(--MM);
  font-size:clamp(10px,1.8vw,12px);
  font-weight:600;
  color:var(--g);
  letter-spacing:.18em;
  text-transform:uppercase;
  border:1px solid rgba(0,200,150,.25);
  background:rgba(0,200,150,.05);
  padding:6px 16px;
  border-radius:99px;
  margin-bottom:clamp(20px,4vw,32px);
}}

.sub{{
  font-size:clamp(14px,2.5vw,18px);
  color:var(--t2);
  line-height:1.8;
  max-width:560px;
  margin-bottom:clamp(20px,4vw,32px);
  font-weight:300;
}}

.chips{{display:flex;flex-wrap:wrap;gap:clamp(6px,1.5vw,10px);margin-bottom:clamp(16px,3vw,28px)}}
.chip{{
  font-size:clamp(11px,1.8vw,13px);
  font-weight:500;
  color:var(--t2);
  border:1px solid var(--b);
  padding:5px 14px;
  border-radius:99px;
  letter-spacing:.03em;
  white-space:nowrap;
  background:rgba(255,255,255,.02);
}}
.chip.on{{color:var(--g);border-color:rgba(0,200,150,.3);background:rgba(0,200,150,.06)}}

.live{{display:inline-flex;align-items:center;gap:10px;font-size:clamp(11px,1.8vw,13px);color:var(--t2);font-weight:400}}
.dot{{width:7px;height:7px;border-radius:50%;background:var(--g);flex-shrink:0;animation:pulse 2s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:1;box-shadow:0 0 0 0 rgba(0,200,150,.5)}}60%{{opacity:.5;box-shadow:0 0 0 6px rgba(0,200,150,0)}}}}

/* ── SECTION HEADER ── */
.sh{{display:flex;align-items:baseline;gap:clamp(10px,2vw,16px);margin-bottom:clamp(24px,5vw,40px)}}
.sn{{font-size:clamp(11px,1.8vw,13px);color:var(--g);letter-spacing:.1em;font-weight:600;font-family:var(--MM);flex-shrink:0}}
.sc{{font-size:clamp(12px,2vw,14px);color:var(--t2);font-weight:400;margin-left:auto;text-align:right;line-height:1.4}}

/* ── GRID NÚMEROS ── */
.ng{{
  display:grid;
  grid-template-columns:repeat(2,1fr);
  gap:1px;
  background:var(--b);
  border:1px solid var(--b);
  border-radius:var(--r);
  overflow:hidden;
  box-shadow:var(--sh);
}}
@media(min-width:640px){{.ng{{grid-template-columns:repeat(4,1fr)}}}}

.ni{{background:var(--f2);padding:var(--pad);transition:background .2s}}
.ni:hover{{background:var(--f3)}}
.nv{{
  font-family:var(--TT);
  font-size:clamp(24px,5.5vw,40px);
  font-weight:700;
  line-height:1;
  margin-bottom:6px;
  letter-spacing:-.01em;
}}
.nv.verde{{color:var(--g)}}.nv.amarelo{{color:var(--am)}}.nv.vermelho{{color:var(--vm)}}
.ns{{font-size:clamp(11px,1.8vw,13px);color:var(--t2);font-weight:400}}

/* ── METAS ── */
.mg{{display:grid;grid-template-columns:1fr;gap:var(--gap)}}
@media(min-width:500px){{.mg{{grid-template-columns:repeat(2,1fr)}}}}

.mc{{
  background:var(--f2);
  border:1px solid var(--b);
  border-radius:var(--r);
  padding:var(--pad);
  position:relative;overflow:hidden;
  transition:border-color .25s,transform .3s,box-shadow .3s;
  display:flex;flex-direction:column;
  box-shadow:var(--sh);
}}
.mc:hover{{border-color:var(--bh);transform:translateY(-3px);box-shadow:0 8px 32px rgba(0,0,0,.4)}}
.mc::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--gd),var(--g),var(--am));
  transform:scaleX(0);transform-origin:left;transition:transform .45s ease;
}}
.mc:hover::before{{transform:scaleX(1)}}
.mi{{font-size:clamp(28px,5vw,36px);margin-bottom:14px;line-height:1}}
.mt{{font-family:var(--TT);font-size:clamp(16px,2.5vw,20px);font-weight:700;margin-bottom:8px;line-height:1.2}}
.md{{font-size:clamp(12px,2vw,14px);color:var(--t2);line-height:1.7;margin-bottom:20px;flex:1;font-weight:400}}
.bl{{display:flex;justify-content:space-between;font-size:clamp(11px,1.8vw,12px);color:var(--t2);margin-bottom:8px;font-weight:500}}
.bl span:last-child{{color:var(--g)}}
.bar{{height:6px;background:var(--f3);border-radius:99px;overflow:hidden}}
.bf{{height:100%;background:linear-gradient(90deg,var(--gd),var(--g));border-radius:99px;transition:width 1.8s cubic-bezier(.4,0,.2,1)}}

/* ── CAIXINHA ── */
.cc{{
  background:var(--f2);border:1px solid var(--b);
  border-radius:var(--r);padding:var(--pad);
  display:grid;grid-template-columns:1fr;gap:var(--gap);
  box-shadow:var(--sh);
}}
@media(min-width:600px){{.cc{{grid-template-columns:1fr 1fr;align-items:center}}}}
.cv{{font-family:var(--TT);font-size:clamp(44px,11vw,72px);font-weight:700;color:var(--g);line-height:1}}
.cm{{font-size:clamp(12px,2vw,14px);color:var(--t2);margin-top:10px;font-weight:400}}
.blg{{height:12px;background:var(--f3);border-radius:99px;overflow:hidden;margin:18px 0 10px}}
.blgf{{height:100%;background:linear-gradient(90deg,var(--gd),var(--g),#7DF4DC);border-radius:99px;width:{caixinha_pct:.1f}%}}
.cp{{font-family:var(--MM);font-size:clamp(14px,2.5vw,16px);color:var(--g);font-weight:600}}
.ci{{font-size:clamp(13px,2vw,15px);color:var(--t2);line-height:2;font-weight:300}}
.ci .dest{{color:var(--g);font-weight:600}}

/* ── TABELAS ── */
.tw{{
  background:var(--f2);border:1px solid var(--b);
  border-radius:var(--r);overflow:hidden;
  margin-bottom:var(--gap);box-shadow:var(--sh);
}}
table{{width:100%;border-collapse:collapse}}
thead{{background:var(--f4)}}
th{{
  font-size:clamp(9px,1.5vw,11px);
  letter-spacing:.14em;color:var(--t2);
  text-transform:uppercase;
  padding:clamp(10px,2vw,14px) clamp(14px,2.5vw,20px);
  text-align:left;font-weight:600;white-space:nowrap;
}}
td{{
  font-size:clamp(13px,2vw,15px);
  padding:clamp(12px,2vw,16px) clamp(14px,2.5vw,20px);
  border-top:1px solid var(--b);
  transition:background .2s;
  font-weight:400;
}}
tr:hover td{{background:rgba(0,200,150,.03)}}

@media(max-width:600px){{
  table,thead,tbody,tr,th,td{{display:block}}
  thead{{display:none}}
  tr{{border:1px solid var(--b);border-radius:var(--rs);margin-bottom:10px;background:var(--f3);overflow:hidden}}
  td{{
    display:flex;justify-content:space-between;align-items:center;
    border-top:1px solid var(--b);padding:11px 16px;font-size:14px;
  }}
  td:first-child{{border-top:none}}
  td::before{{
    content:attr(data-label);font-size:10px;color:var(--t2);
    letter-spacing:.1em;text-transform:uppercase;
    flex-shrink:0;margin-right:12px;font-weight:600;
  }}
  .tw{{border-radius:0;border-left:none;border-right:none}}
}}

.ticker{{font-family:var(--TT);font-weight:700;font-size:clamp(14px,2.5vw,16px);color:var(--g)}}
.badge{{font-size:clamp(10px,1.8vw,12px);padding:4px 10px;border-radius:99px;white-space:nowrap;font-weight:500}}
.badge-fii{{background:rgba(96,165,250,.12);color:#60A5FA;border:1px solid rgba(96,165,250,.25)}}
.badge-acao{{background:rgba(0,200,150,.08);color:var(--g);border:1px solid rgba(0,200,150,.2)}}
.badge-setor{{background:var(--f3);color:var(--t2);border:1px solid var(--b);font-size:clamp(10px,1.8vw,11px);padding:3px 10px;border-radius:99px}}
.positivo{{color:var(--g);font-weight:500}}.amarelo{{color:var(--am)}}.nota{{color:var(--t2);font-size:clamp(11px,1.8vw,13px)}}

/* ── SINAIS DE MERCADO ── */
.cenario-box{{
  background:var(--f2);border:1px solid var(--b);
  border-radius:var(--r);padding:var(--pad);
  margin-bottom:var(--gap);box-shadow:var(--sh);
}}
.cenario-titulo{{font-family:var(--TT);font-size:clamp(16px,3vw,22px);font-weight:700;margin-bottom:8px}}
.cenario-desc{{font-size:clamp(13px,2vw,15px);color:var(--t2);line-height:1.8;font-weight:300}}
.cenario-tags{{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}}
.ctag{{font-size:11px;font-weight:600;padding:4px 12px;border-radius:99px;letter-spacing:.05em}}
.ctag.positivo{{background:rgba(0,200,150,.12);color:var(--g);border:1px solid rgba(0,200,150,.25)}}
.ctag.atencao{{background:rgba(255,209,102,.12);color:var(--am);border:1px solid rgba(255,209,102,.25)}}
.ctag.negativo{{background:rgba(255,107,107,.12);color:var(--vm);border:1px solid rgba(255,107,107,.25)}}

.sinais-grid{{
  display:grid;
  grid-template-columns:1fr;
  gap:var(--gap);
}}
@media(min-width:480px){{.sinais-grid{{grid-template-columns:repeat(2,1fr)}}}}
@media(min-width:800px){{.sinais-grid{{grid-template-columns:repeat(3,1fr)}}}}

.sinal-card{{
  background:var(--f2);border:1px solid var(--b);
  border-radius:var(--r);padding:var(--ps);
  transition:border-color .25s,transform .25s;
  box-shadow:var(--sh);
}}
.sinal-card:hover{{border-color:var(--bh);transform:translateY(-2px)}}
.sinal-top{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px}}
.sinal-ticker{{font-family:var(--TT);font-size:clamp(18px,3vw,22px);font-weight:700;color:var(--g)}}
.sinal-tipo{{font-size:11px;color:var(--t2);font-weight:500;letter-spacing:.05em;margin-top:2px}}
.sinal-motivo{{font-size:clamp(12px,1.8vw,13px);color:var(--t2);line-height:1.7;font-weight:400}}

.sinal-badge{{
  font-size:clamp(9px,1.5vw,11px);
  font-weight:700;
  padding:5px 12px;
  border-radius:99px;
  letter-spacing:.08em;
  white-space:nowrap;
  flex-shrink:0;
}}
.sinal-comprar{{background:rgba(0,200,150,.15);color:var(--g);border:1px solid rgba(0,200,150,.35)}}
.sinal-manter{{background:rgba(255,209,102,.12);color:var(--am);border:1px solid rgba(255,209,102,.3)}}
.sinal-vender{{background:rgba(255,107,107,.15);color:var(--vm);border:1px solid rgba(255,107,107,.35)}}

/* ── CARTEIRA IDEAL ── */
.peso-wrap{{display:flex;align-items:center;gap:10px}}
.peso-bar{{flex:1;height:6px;background:var(--f3);border-radius:99px;overflow:hidden}}
.peso-fill{{height:100%;background:linear-gradient(90deg,var(--gd),var(--g));border-radius:99px}}
.peso-num{{font-size:13px;font-weight:600;color:var(--g);width:34px;text-align:right;flex-shrink:0}}

/* ── ORÇAMENTO ── */
.og{{display:grid;grid-template-columns:1fr;gap:var(--gap)}}
@media(min-width:480px){{.og{{grid-template-columns:repeat(2,1fr)}}}}
@media(min-width:800px){{.og{{grid-template-columns:repeat(4,1fr)}}}}
.oc{{background:var(--f2);border:1px solid var(--b);border-radius:var(--r);padding:var(--ps) var(--pad);transition:border-color .25s;box-shadow:var(--sh)}}
.oc:hover{{border-color:var(--bh)}}

/* ── FREELAS ── */
.fg{{display:grid;grid-template-columns:repeat(2,1fr);gap:var(--gap)}}
@media(min-width:640px){{.fg{{grid-template-columns:repeat(4,1fr)}}}}
.fc{{background:var(--f2);border:1px solid var(--b);border-radius:var(--r);padding:var(--ps);transition:border-color .25s,transform .25s;box-shadow:var(--sh)}}
.fc:hover{{border-color:var(--bh);transform:translateY(-2px)}}
.fl{{font-size:clamp(9px,1.8vw,11px);color:var(--t2);letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px;font-weight:600}}
.fv{{font-family:var(--TT);font-size:clamp(20px,4vw,28px);font-weight:700;color:var(--am);line-height:1}}
.fd{{font-size:clamp(11px,1.8vw,13px);color:var(--t2);margin-top:8px;line-height:1.6;font-weight:400}}

/* ── TIMELINE ── */
.tl{{display:flex;flex-direction:column}}
.ti{{display:flex;gap:clamp(16px,3vw,24px)}}
.tll{{display:flex;flex-direction:column;align-items:center;width:20px;flex-shrink:0}}
.tdot{{width:12px;height:12px;border-radius:50%;background:var(--g);flex-shrink:0;margin-top:5px;box-shadow:0 0 10px rgba(0,200,150,.5)}}
.tdot.v{{background:transparent;border:2px solid var(--t3);box-shadow:none}}
.tln{{width:1px;flex:1;min-height:24px;background:linear-gradient(to bottom,var(--g),var(--b));margin:4px 0}}
.tr{{padding-bottom:clamp(24px,5vw,36px);flex:1}}
.tf{{font-size:clamp(10px,1.8vw,12px);color:var(--g);letter-spacing:.1em;text-transform:uppercase;margin-bottom:5px;font-weight:600}}
.tt{{font-family:var(--TT);font-size:clamp(16px,3vw,20px);font-weight:700;margin-bottom:5px}}
.tdsc{{font-size:clamp(12px,2vw,14px);color:var(--t2);line-height:1.8;font-weight:400}}

/* ── NAV MOBILE ── */
.nm{{
  display:none;position:fixed;bottom:0;left:0;right:0;
  background:rgba(9,14,12,.97);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border-top:1px solid var(--b);
  padding:10px var(--pad) calc(10px + env(safe-area-inset-bottom));
  z-index:100;justify-content:space-around;
}}
@media(max-width:640px){{.nm{{display:flex}}footer{{padding-bottom:90px}}}}
.na{{
  display:flex;flex-direction:column;align-items:center;gap:4px;
  font-size:9px;color:var(--t2);letter-spacing:.06em;text-transform:uppercase;
  text-decoration:none;padding:4px 8px;border-radius:8px;
  transition:color .2s,background .2s;cursor:pointer;font-weight:600;
}}
.na:hover,.na.on{{color:var(--g);background:rgba(0,200,150,.08)}}
.ni2{{font-size:20px;line-height:1}}

/* ── FOOTER ── */
footer{{
  padding:clamp(32px,6vw,56px) 0;
  text-align:center;
  font-size:clamp(12px,2vw,14px);
  color:var(--t2);line-height:2;font-weight:400;
}}
footer a{{color:var(--g);text-decoration:none;font-weight:500}}
footer a:hover{{text-decoration:underline}}
.fl2{{font-size:11px;opacity:.4;margin-top:16px}}

/* ── ANIMAÇÕES ── */
.fade{{opacity:0;transform:translateY(22px);transition:opacity .6s ease,transform .6s ease}}
.fade.on{{opacity:1;transform:translateY(0)}}
.mc:nth-child(1){{transition-delay:.0s}}.mc:nth-child(2){{transition-delay:.1s}}
.mc:nth-child(3){{transition-delay:.2s}}.mc:nth-child(4){{transition-delay:.3s}}
.sinal-card:nth-child(1){{transition-delay:.0s}}.sinal-card:nth-child(2){{transition-delay:.07s}}
.sinal-card:nth-child(3){{transition-delay:.14s}}.sinal-card:nth-child(4){{transition-delay:.21s}}
.sinal-card:nth-child(5){{transition-delay:.28s}}.sinal-card:nth-child(6){{transition-delay:.35s}}

/* ── UTILS ── */
::-webkit-scrollbar{{width:5px;height:5px}}
::-webkit-scrollbar-track{{background:var(--f)}}
::-webkit-scrollbar-thumb{{background:var(--t3);border-radius:3px}}
::-webkit-scrollbar-thumb:hover{{background:var(--gd)}}
::selection{{background:rgba(0,200,150,.2);color:var(--t)}}
</style>
</head>
<body>

<!-- NAV MOBILE -->
<nav class="nm" role="navigation" aria-label="Menu">
  <a class="na" href="#visao"><span class="ni2">📊</span>Visao</a>
  <a class="na" href="#metas"><span class="ni2">🎯</span>Metas</a>
  <a class="na" href="#sinais"><span class="ni2">📡</span>Sinais</a>
  <a class="na" href="#carteira"><span class="ni2">📈</span>Carteira</a>
  <a class="na" href="#historico"><span class="ni2">📅</span>Hist.</a>
</nav>

<div class="wrap">

<!-- HEADER -->
<header class="fade">
  <div class="tag"><span class="dot"></span>jornada financeira real</div>
  <h1>{perfil['nome']}<br><span class="g">Construindo</span><br>Patrimônio</h1>
  <p class="sub">{perfil['profissao']}.<br>{brl(perfil['aporte_mensal'])}/mês com consistência.<br>{perfil['familia']} — casa própria quitada.</p>
  <div class="chips">
    <span class="chip">{perfil['cidade']}</span>
    <span class="chip on">⚡ Em transição de carreira</span>
    <span class="chip">Desde {perfil['inicio']}</span>
  </div>
  <div class="live">
    <span class="dot"></span>
    Atualizado em {atualizado} · orientado pelo Claude (Anthropic)
  </div>
</header>

<!-- 01 VISÃO GERAL -->
<section class="fade" id="visao">
  <div class="sh"><span class="sn">01 —</span><h2>Visão Geral</h2></div>
  <div class="ng">
    <div class="ni"><h3>Patrimônio total</h3><div class="nv verde">{brl(patrimonio_total)}</div><div class="ns">ações + FIIs</div></div>
    <div class="ni"><h3>Rentabilidade</h3><div class="nv verde">+{pct(acoes_res['rentabilidade_pct'])}</div><div class="ns">carteira de ações</div></div>
    <div class="ni"><h3>Dividendos/mês</h3><div class="nv amarelo">{brl(dividendos_mes)}</div><div class="ns">renda passiva atual</div></div>
    <div class="ni"><h3>Aporte mensal</h3><div class="nv">{brl(perfil['aporte_mensal'])}</div><div class="ns">todo mês sem falta</div></div>
  </div>
</section>

<!-- 02 METAS -->
<section class="fade" id="metas">
  <div class="sh"><span class="sn">02 —</span><h2>Metas</h2></div>
  <div class="mg">
    <div class="mc fade"><div class="mi">🚗</div><div class="mt">Reserva do Carro</div><div class="md">Ferramenta de trabalho protegida. Sem carro, sem renda.</div><div class="bl"><span>{brl(caixinha['saldo'])}</span><span>{brl(caixinha['meta'])}</span></div><div class="bar"><div class="bf" style="width:{caixinha_pct:.1f}%"></div></div></div>
    <div class="mc fade"><div class="mi">📈</div><div class="mt">100 cotas MXRF11</div><div class="md">FII com dividendos mensais. Base da renda passiva futura.</div><div class="bl"><span>{mxrf_cotas} cotas</span><span>{mxrf_meta} cotas</span></div><div class="bar"><div class="bf" style="width:{mxrf_pct:.1f}%"></div></div></div>
    <div class="mc fade"><div class="mi">👨‍👩‍👧‍👦</div><div class="mt">Estabilidade Familiar</div><div class="md">{perfil['familia']}. Casa própria quitada. Segurança em construção.</div><div class="bl"><span>Em construção</span><span>Longo prazo</span></div><div class="bar"><div class="bf" style="width:15%"></div></div></div>
    <div class="mc fade"><div class="mi">🏖️</div><div class="mt">Aposentadoria</div><div class="md">R$ 1.000/mês em dividendos. Patrimônio alvo: R$ 120.000.</div><div class="bl"><span>{brl(patrimonio_total)}</span><span>R$ 120.000</span></div><div class="bar"><div class="bf" style="width:{apo_pct:.1f}%"></div></div></div>
  </div>
</section>

<!-- 03 CAIXINHA -->
<section class="fade" id="caixinha">
  <div class="sh"><span class="sn">03 —</span><h2>Caixinha do Carro</h2></div>
  <div class="cc">
    <div>
      <div class="cv">{brl(caixinha['saldo'])}</div>
      <div class="cm">Meta: {brl(caixinha['meta'])} — {caixinha['onde']}</div>
      <div class="blg"><div class="blgf"></div></div>
      <div class="cp">{pct(caixinha_pct)} concluído</div>
    </div>
    <div class="ci">
      Protege contra manutenções inesperadas.<br>
      Todo freela vai direto aqui<br>
      até completar {brl(caixinha['meta'])}.<br><br>
      <span class="dest">Previsão: {caixinha['previsao']}</span>
    </div>
  </div>
</section>

<!-- 04 SINAIS DE MERCADO -->
<section class="fade" id="sinais">
  <div class="sh">
    <span class="sn">04 —</span>
    <h2>Sinais de Mercado</h2>
    <span class="sc">Cenário Mai/2026<br>Atualizado mensalmente</span>
  </div>

  <div class="cenario-box fade">
    <div class="cenario-titulo">📡 Cenário Brasil — Maio/2026</div>
    <div class="cenario-desc">
      Bolsa brasileira subiu +32% em 2025, uma das maiores altas do mundo. Em 2026 o mercado segue com volatilidade mas com perspectiva positiva. Expectativa de queda gradual da Selic favorece FIIs e ações de dividendos. Cenário eleitoral gera incerteza no segundo semestre.
    </div>
    <div class="cenario-tags">
      <span class="ctag positivo">✅ Selic em queda gradual</span>
      <span class="ctag positivo">✅ FIIs abaixo do valor patrimonial</span>
      <span class="ctag positivo">✅ Ações de dividendos atrativas</span>
      <span class="ctag atencao">⚠️ Volatilidade elevada</span>
      <span class="ctag atencao">⚠️ Ano eleitoral — incerteza política</span>
      <span class="ctag negativo">❌ Juros ainda altos no curto prazo</span>
    </div>
  </div>

  <div class="sinais-grid">
    {cards_sinais()}
  </div>

  <p style="margin-top:16px;font-size:12px;opacity:.5;font-style:italic">
    * Sinais baseados no cenário macroeconômico. Não é recomendação de investimento. Consulte um profissional antes de decisões.
  </p>
</section>

<!-- 05 CARTEIRA IDEAL BALANCEADA -->
<section class="fade" id="ideal">
  <div class="sh"><span class="sn">05 —</span><h2>Carteira Ideal Balanceada</h2></div>
  <p style="margin-bottom:var(--gap)">
    Distribuição sugerida com 10% em cada ativo — 4 FIIs + 6 ações. 
    Equilibra renda passiva (FIIs) com crescimento (ações). 
    Construir gradualmente conforme aportes chegarem.
  </p>
  <div class="tw">
    <table>
      <thead><tr><th>Ativo</th><th>Tipo</th><th>Peso ideal</th><th>Por que</th></tr></thead>
      <tbody>{rows_ideal()}</tbody>
    </table>
  </div>
  <div class="cenario-box fade" style="margin-top:0">
    <div class="cenario-titulo" style="font-size:clamp(14px,2.5vw,18px)">💡 Como chegar lá com R$ 100/mês</div>
    <div class="cenario-desc">
      Você já tem ITSA4, BBAS3, EGIE3, TAEE11, BBSE3, KLBN4, WEGE3, MXRF11 e GARE11 — 9 dos 10 ativos!<br>
      Falta apenas: <strong style="color:var(--g)">HGLG11 ou XPLG11</strong> (FII de logística) para completar a carteira ideal.<br><br>
      Após a caixinha atingir R$ 800, direcione os aportes para equilibrar os pesos — 
      compre mais do que está abaixo de 10% da carteira.
    </div>
  </div>
</section>

<!-- 06 CARTEIRA ATUAL -->
<section class="fade" id="carteira">
  <div class="sh"><span class="sn">06 —</span><h2>Carteira Atual</h2></div>
  <h3 style="margin-bottom:14px">FIIs — Fundos Imobiliários</h3>
  <div class="tw">
    <table>
      <thead><tr><th>Ativo</th><th>Qtd</th><th>P.Médio</th><th>Dividendos/mês</th><th>Meta</th></tr></thead>
      <tbody>{rows_fiis()}</tbody>
    </table>
  </div>
  <h3 style="margin:24px 0 14px">Ações — manter, não aportar agora</h3>
  <div class="tw">
    <table>
      <thead><tr><th>Ativo</th><th>Qtd</th><th>P.Médio</th><th>Setor</th></tr></thead>
      <tbody>{rows_acoes()}</tbody>
    </table>
  </div>
  <p style="font-size:13px;color:var(--t2);margin-top:12px;font-weight:400">
    Rentabilidade: <span class="positivo">+{pct(acoes_res['rentabilidade_pct'])}</span>
    &nbsp;·&nbsp; Valor total ações: {brl(acoes_res['valor_total'])}
  </p>
</section>

<!-- 07 ORÇAMENTO -->
<section class="fade" id="orcamento">
  <div class="sh"><span class="sn">07 —</span><h2>Orçamento Mensal</h2></div>
  <div class="og">
    <div class="oc"><h3>Renda escolar</h3><div class="nv" style="font-size:clamp(20px,4vw,30px)">{brl(orcamento['renda_escolar'])}</div><div class="ns">mensal</div></div>
    <div class="oc"><h3>Freelas elétrica</h3><div class="nv {freela_class}" style="font-size:clamp(20px,4vw,30px)">{brl(orcamento['renda_freelas'])}</div><div class="ns">{freela_sub}</div></div>
    <div class="oc"><h3>Gastos (cartão)</h3><div class="nv" style="font-size:clamp(20px,4vw,30px)">{brl(orcamento['gastos_cartao'])}</div><div class="ns">pago total todo mês ✅</div></div>
    <div class="oc"><h3>Sobra real</h3><div class="nv {sobra_class}" style="font-size:clamp(20px,4vw,30px)">{brl(sobra)}</div><div class="ns">após investimento</div></div>
  </div>
</section>

<!-- 08 FREELAS -->
<section class="fade" id="freelas">
  <div class="sh"><span class="sn">08 —</span><h2>Freelas de Elétrica ⚡</h2></div>
  <div class="fg">
    <div class="fc"><div class="fl">Faturado 2026</div><div class="fv">{brl(freelas_d['faturado_2026'])}</div><div class="fd">Canal: {freelas_d['canal']}.<br>Meta: 2 serviços/fim de semana.</div></div>
    <div class="fc"><div class="fl">Potencial mensal</div><div class="fv">R$ 400+</div><div class="fd">Com 2–4 serviços.<br>Técnico formado.</div></div>
    <div class="fc"><div class="fl">Serviços realizados</div><div class="fv">{freelas_d['servicos_realizados']}</div><div class="fd">Primeiro freela →<br>100% na caixinha.</div></div>
    <div class="fc"><div class="fl">Impacto no plano</div><div class="fv" style="color:var(--g);font-size:clamp(16px,3vw,22px)">3× mais rápido</div><div class="fd">Com R$ 400 extra/mês<br>metas chegam antes.</div></div>
  </div>
</section>

<!-- 09 PLANO -->
<section class="fade" id="plano">
  <div class="sh"><span class="sn">09 —</span><h2>Plano de Fases</h2></div>
  <div class="tl">
    <div class="ti"><div class="tll"><div class="tdot"></div><div class="tln"></div></div><div class="tr"><div class="tf">Fase 1 — Mai a Dez/2026 · EM ANDAMENTO</div><div class="tt">Proteger a renda</div><div class="tdsc">R$ 100/mês na caixinha até R$ 800. Prioridade absoluta. Sem isso, qualquer imprevisto vira dívida cara.</div></div></div>
    <div class="ti"><div class="tll"><div class="tdot v"></div><div class="tln"></div></div><div class="tr"><div class="tf">Fase 2 — Jan/2027</div><div class="tt">100 cotas MXRF11</div><div class="tdsc">R$ 100/mês inteiros em MXRF11. Reinvestir dividendos. Faltam {mxrf_meta - mxrf_cotas} cotas — ~4 meses.</div></div></div>
    <div class="ti"><div class="tll"><div class="tdot v"></div><div class="tln"></div></div><div class="tr"><div class="tf">Fase 3 — 2027/2028</div><div class="tt">Carteira balanceada</div><div class="tdsc">Adicionar HGLG11 ou XPLG11. Equilibrar pesos para 10% cada ativo. Aumentar renda passiva mensal.</div></div></div>
    <div class="ti"><div class="tll"><div class="tdot v"></div></div><div class="tr"><div class="tf">Fase 4 — Longo prazo</div><div class="tt">Aposentadoria</div><div class="tdsc">R$ 1.000/mês em dividendos. Com freelas de elétrica: ~13 anos. Sem freelas: ~35 anos.</div></div></div>
  </div>
</section>

<!-- 10 HISTÓRICO -->
<section class="fade" id="historico">
  <div class="sh"><span class="sn">10 —</span><h2>Histórico</h2></div>
  <div class="tw">
    <table>
      <thead><tr><th>Mês</th><th>Depósito</th><th>Saldo</th><th>MXRF11</th><th>Freelas</th><th>Nota</th></tr></thead>
      <tbody>{rows_hist()}</tbody>
    </table>
  </div>
</section>

<!-- FOOTER -->
<footer class="fade">
  <p>Jornada real — sem filtro, sem perfumaria.</p>
  <p style="margin-top:8px">
    Orientado pelo <a href="https://claude.ai" target="_blank">Claude</a> (Anthropic)
    &nbsp;·&nbsp; {perfil['cidade']}
    &nbsp;·&nbsp; <a href="https://github.com/meirelesnew/minha-carteira" target="_blank">GitHub</a>
  </p>
  <p class="fl2">Não é recomendação de investimento. São escolhas pessoais documentadas publicamente.</p>
</footer>

</div><!-- /wrap -->

<script>
const io=new IntersectionObserver(entries=>{{
  entries.forEach((e,i)=>{{
    if(e.isIntersecting){{setTimeout(()=>e.target.classList.add('on'),i*55);io.unobserve(e.target);}}
  }});
}},{{threshold:.07}});
document.querySelectorAll('.fade').forEach(el=>io.observe(el));

const secs=document.querySelectorAll('section[id],header');
const navs=document.querySelectorAll('.na');
const sio=new IntersectionObserver(entries=>{{
  entries.forEach(e=>{{
    if(e.isIntersecting)navs.forEach(n=>n.classList.toggle('on',n.getAttribute('href')==='#'+e.target.id));
  }});
}},{{threshold:.35}});
secs.forEach(s=>sio.observe(s));
</script>
</body>
</html>"""

with open("index.html","w",encoding="utf-8") as f:
    f.write(HTML)

print("Vitrine gerada com sucesso!")
print(f"  Patrimonio: {brl(patrimonio_total)}")
print(f"  Sinais:     {len(sinais)} ativos analisados")
print(f"  Carteira:   {len(carteira_ideal)} ativos na carteira ideal")
print(f"  Dividendos: {brl(dividendos_mes)}/mes")
