## Análise rápida da sua situação atual (com base no carteira-01.web.app)

| Item | Hoje | Meta |
|---|---|---|
| Patrimônio (ações + FIIs) | R$ 1.312,15 | R$ 120.000 (aposentadoria) |
| Dividendos/mês | R$ 10 | R$ 1.000 |
| MXRF11 | 66 cotas | 100 cotas (faltam 34 ≈ R$ 340) |
| Aporte mensal | R$ 100 | — |
| Reserva carro | R$ 100 | R$ 800 |
| Renda extra | Transporte escolar + freelas elétrica (R$ 400+/mês potencial) | — |
| Dívidas | **não cadastradas** no site | quitar |

Diagnóstico: o site atual é um painel estático/leitura. Faltam três coisas para destravar suas 3 prioridades: (1) cadastro e plano de quitação de dívidas, (2) priorização de aporte para fechar as 100 cotas de MXRF11 antes da meta de aposentadoria, (3) um agente que cruze esses dados e te oriente toda semana. É isso que vamos construir.

## O que vou construir

Um app novo (não substitui o carteira-01, complementa) com:

1. **Login** (e-mail/senha + Google) via Lovable Cloud — seus dados privados, só você acessa.
2. **Dashboard da carteira**: patrimônio, dividendos/mês, progresso das 4 metas (Carro, 100 MXRF11, Estabilidade Familiar, Aposentadoria), receitas extras.
3. **Módulo de dívidas**: cadastrar cada dívida (credor, saldo, juros, parcela), ver custo total, e a estratégia recomendada (avalanche por juros vs. bola de neve por saldo).
4. **Módulo de investimentos**: cadastrar posições (ticker, qtd, preço médio), com foco no MXRF11 e cálculo de quanto falta para 100 cotas.
5. **Agente de IA financeiro (chat)** — várias conversas (threads), cada uma com URL própria. O agente:
   - lê suas dívidas, investimentos e metas em tempo real;
   - responde priorizando suas 3 metas (aposentar, 100 MXRF11, estabilidade familiar);
   - sugere plano mensal: quanto vai para dívida, quanto para MXRF11, quanto para reserva;
   - simula cenários ("e se eu aportar R$ 300?", "quanto tempo para 100 cotas?", "vale antecipar dívida ou comprar FII?").
6. **Disclaimer**: o agente dá orientação educacional, não recomendação formal de investimento.

## Telas

```text
/auth              login / cadastro
/                  dashboard (resumo + metas)
/dividas           lista + cadastro de dívidas, plano de quitação
/investimentos     lista de posições, foco MXRF11
/metas             editar as 4 metas e prazos
/chat              lista de conversas com o agente
/chat/$threadId    conversa individual (URL própria)
```

## Detalhes técnicos

- TanStack Start + Tailwind + shadcn (stack já configurada).
- Lovable Cloud (Supabase gerenciado) com RLS por `auth.uid()`. Tabelas: `profiles`, `debts`, `investments`, `goals`, `chat_threads`, `chat_messages`.
- Auth: e-mail/senha + Google (via `lovable.auth.signInWithOAuth`).
- Rotas protegidas em `src/routes/_authenticated/`; `/auth` pública.
- Agente: AI SDK + Lovable AI Gateway, modelo `google/gemini-3-flash-preview`, streaming via rota `src/routes/api/chat.ts`. System prompt em PT-BR com suas 3 prioridades fixas e contexto carregado das tabelas (dívidas + investimentos + metas) a cada mensagem.
- Threads persistidas no banco (`chat_threads` + `chat_messages` com `UIMessage[]` salvo em `onFinish`).
- Cotação do MXRF11: campo manual no começo (você atualiza); integração com API de cotações pode vir depois se quiser.

## O que NÃO entra agora

- Importação automática da B3 / corretora.
- Cotações ao vivo via API paga.
- Sinais de IA de compra/venda como no carteira-01 (rede Muth) — não é o foco das suas 3 prioridades.
- Módulos de transporte escolar e freelas elétrica (posso adicionar depois se quiser).

Confirma que pode seguir assim?
