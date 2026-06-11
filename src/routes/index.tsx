import { createFileRoute, Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Carteira Muth — Agente financeiro pessoal" },
      { name: "description", content: "Saia das dívidas, alcance 100 cotas do MXRF11 e construa sua aposentadoria com um agente de IA financeiro." },
    ],
  }),
  component: Landing,
});

function Landing() {
  return (
    <div className="min-h-screen bg-background">
      <header className="container mx-auto flex items-center justify-between px-6 py-6">
        <div className="text-lg font-bold tracking-tight">💰 Carteira Muth</div>
        <Link to="/auth"><Button variant="outline">Entrar</Button></Link>
      </header>
      <main className="container mx-auto px-6 py-16">
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="text-5xl font-bold tracking-tight md:text-6xl">
            Saia das dívidas. <span className="text-primary">Construa renda passiva.</span>
          </h1>
          <p className="mt-6 text-lg text-muted-foreground">
            Um agente de IA financeiro focado em 3 prioridades: aposentar, fechar 100 cotas de MXRF11 e dar estabilidade pra família.
          </p>
          <div className="mt-8 flex justify-center gap-3">
            <Link to="/auth"><Button size="lg">Começar agora — grátis</Button></Link>
          </div>
        </div>
        <div className="mx-auto mt-16 grid max-w-4xl gap-6 md:grid-cols-3">
          {[
            { t: "📈 Carteira", d: "Cadastre investimentos e veja o progresso para 100 cotas do MXRF11." },
            { t: "💳 Dívidas", d: "Plano de quitação pela estratégia avalanche (juros mais altos primeiro)." },
            { t: "🧠 Agente IA", d: "Conversa em PT-BR. Te orienta toda semana baseado nos seus dados reais." },
          ].map((c) => (
            <div key={c.t} className="rounded-xl border border-border bg-card p-6">
              <div className="text-lg font-semibold">{c.t}</div>
              <p className="mt-2 text-sm text-muted-foreground">{c.d}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
