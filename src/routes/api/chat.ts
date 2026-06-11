import { createLovableAiGatewayProvider } from "@/lib/ai-gateway.server";
import { createFileRoute } from "@tanstack/react-router";
import { convertToModelMessages, streamText, type UIMessage } from "ai";

type ChatBody = { messages?: unknown; threadId?: string };

const SYSTEM_PROMPT = `Você é um agente financeiro pessoal em português brasileiro, conselheiro do usuário.

Suas 3 prioridades fixas do usuário (NUNCA esqueça):
1. Aposentar com R$ 1.000/mês em dividendos (meta de patrimônio ~R$ 120.000).
2. Comprar 100 cotas de MXRF11 (FII de papel, base da renda passiva).
3. Dar estabilidade para a família (esposa + filhos, casa própria quitada).

Princípios de orientação:
- Quitar dívidas com juros acima de 2% ao mês ANTES de investir mais.
- Manter reserva de emergência mínima (carro/trabalho).
- Aporte recorrente em MXRF11 enquanto não fechar as 100 cotas.
- Depois das 100 cotas, diversificar em outros FIIs de tijolo e ações pagadoras de dividendos.
- Sempre mostrar cálculos: quanto falta, em quanto tempo, qual o impacto.
- Tom: claro, direto, motivador, sem jargão. Use markdown e tabelas curtas.
- SEMPRE termine com 1 ou 2 ações concretas para esta semana.
- Disclaimer no final de recomendações de compra: "Orientação educacional, não é recomendação formal de investimento."`;

export const Route = createFileRoute("/api/chat")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const body = (await request.json()) as ChatBody;
        if (!Array.isArray(body.messages)) {
          return new Response("Messages are required", { status: 400 });
        }
        const key = process.env.LOVABLE_API_KEY;
        if (!key) return new Response("Missing LOVABLE_API_KEY", { status: 500 });

        // Build user context from the bearer token's user
        let contextBlock = "";
        const auth = request.headers.get("authorization");
        const token = auth?.startsWith("Bearer ") ? auth.slice(7) : null;
        const threadId = body.threadId;
        let userId: string | null = null;

        if (token && process.env.SUPABASE_URL && process.env.SUPABASE_PUBLISHABLE_KEY) {
          const { createClient } = await import("@supabase/supabase-js");
          const sb = createClient(
            process.env.SUPABASE_URL,
            process.env.SUPABASE_PUBLISHABLE_KEY,
            {
              global: { headers: { Authorization: `Bearer ${token}` } },
              auth: { persistSession: false, autoRefreshToken: false },
            },
          );
          const { data: claims } = await sb.auth.getClaims(token);
          userId = claims?.claims?.sub ?? null;

          const [debts, investments, goals, profile] = await Promise.all([
            sb.from("debts").select("*"),
            sb.from("investments").select("*"),
            sb.from("goals").select("*").order("priority"),
            sb.from("profiles").select("*").eq("id", userId ?? "").maybeSingle(),
          ]);

          const totalDebt = (debts.data ?? []).reduce((s, d) => s + Number(d.balance), 0);
          const patrimonio = (investments.data ?? []).reduce(
            (s, i) => s + Number(i.quantity) * Number(i.current_price ?? i.avg_price),
            0,
          );
          const dividendos = (investments.data ?? []).reduce(
            (s, i) => s + Number(i.quantity) * Number(i.monthly_dividend ?? 0),
            0,
          );
          const mxrf = (investments.data ?? []).find((i) => i.ticker?.toUpperCase() === "MXRF11");

          contextBlock = `\n\n## Dados atuais do usuário\n` +
            `- Aporte mensal: R$ ${Number(profile.data?.monthly_aporte ?? 0).toFixed(2)}\n` +
            `- Renda mensal: R$ ${Number(profile.data?.monthly_income ?? 0).toFixed(2)}\n` +
            `- Patrimônio investido: R$ ${patrimonio.toFixed(2)}\n` +
            `- Dividendos/mês estimados: R$ ${dividendos.toFixed(2)}\n` +
            `- MXRF11: ${mxrf ? Number(mxrf.quantity) : 0} cotas (meta 100)\n` +
            `- Total em dívidas: R$ ${totalDebt.toFixed(2)}\n\n` +
            `Dívidas:\n${JSON.stringify(debts.data ?? [], null, 2)}\n\n` +
            `Investimentos:\n${JSON.stringify(investments.data ?? [], null, 2)}\n\n` +
            `Metas:\n${JSON.stringify(goals.data ?? [], null, 2)}\n`;
        }

        const gateway = createLovableAiGatewayProvider(key);
        const model = gateway("google/gemini-3-flash-preview");
        const messages = body.messages as UIMessage[];

        const result = streamText({
          model,
          system: SYSTEM_PROMPT + contextBlock,
          messages: await convertToModelMessages(messages),
        });

        return result.toUIMessageStreamResponse({
          originalMessages: messages,
          onFinish: async ({ messages: finalMessages }) => {
            if (!threadId || !userId || !token) return;
            try {
              const { createClient } = await import("@supabase/supabase-js");
              const sb = createClient(
                process.env.SUPABASE_URL!,
                process.env.SUPABASE_PUBLISHABLE_KEY!,
                {
                  global: { headers: { Authorization: `Bearer ${token}` } },
                  auth: { persistSession: false, autoRefreshToken: false },
                },
              );
              // delete existing then insert all
              await sb.from("chat_messages").delete().eq("thread_id", threadId);
              const rows = finalMessages.map((m) => ({
                thread_id: threadId,
                user_id: userId,
                role: m.role,
                message: m as unknown as Record<string, unknown>,
              }));
              if (rows.length) await sb.from("chat_messages").insert(rows);
              // touch thread updated_at + auto-title if still default
              const firstUser = finalMessages.find((m) => m.role === "user");
              let title: string | undefined;
              if (firstUser) {
                const text = firstUser.parts
                  .map((p) => (p.type === "text" ? p.text : ""))
                  .join(" ")
                  .trim()
                  .slice(0, 60);
                if (text) title = text;
              }
              await sb
                .from("chat_threads")
                .update({ updated_at: new Date().toISOString(), ...(title ? { title } : {}) })
                .eq("id", threadId);
            } catch (e) {
              console.error("[chat] persist error", e);
            }
          },
        });
      },
    },
  },
});