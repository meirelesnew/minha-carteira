import { createFileRoute, Link } from "@tanstack/react-router";
import { useServerFn } from "@tanstack/react-start";
import { useQuery } from "@tanstack/react-query";
import { listDebts, listInvestments, listGoals, getProfile } from "@/lib/finance.functions";
import { formatBRL } from "@/lib/format";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/_authenticated/dashboard")({
  head: () => ({ meta: [{ title: "Painel — Carteira Muth" }] }),
  component: Dashboard,
});

function Dashboard() {
  const debtsFn = useServerFn(listDebts);
  const invFn = useServerFn(listInvestments);
  const goalsFn = useServerFn(listGoals);
  const profFn = useServerFn(getProfile);

  const debts = useQuery({ queryKey: ["debts"], queryFn: () => debtsFn() });
  const inv = useQuery({ queryKey: ["investments"], queryFn: () => invFn() });
  const goals = useQuery({ queryKey: ["goals"], queryFn: () => goalsFn() });
  const profile = useQuery({ queryKey: ["profile"], queryFn: () => profFn() });

  const totalDebt = (debts.data ?? []).reduce((s, d) => s + Number(d.balance), 0);
  const patrimonio = (inv.data ?? []).reduce((s, i) => s + Number(i.quantity) * Number(i.current_price ?? i.avg_price), 0);
  const dividendos = (inv.data ?? []).reduce((s, i) => s + Number(i.quantity) * Number(i.monthly_dividend ?? 0), 0);
  const mxrf = (inv.data ?? []).find((i) => i.ticker?.toUpperCase() === "MXRF11");
  const mxrfQty = mxrf ? Number(mxrf.quantity) : 0;

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Olá{profile.data?.display_name ? `, ${profile.data.display_name}` : ""} 👋</h1>
        <p className="text-muted-foreground">Visão geral da sua vida financeira.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Stat label="Patrimônio" value={formatBRL(patrimonio)} hint="ações + FIIs" />
        <Stat label="Dividendos/mês" value={formatBRL(dividendos)} hint="renda passiva" />
        <Stat label="Dívidas" value={formatBRL(totalDebt)} hint={`${(debts.data ?? []).length} cadastradas`} tone={totalDebt > 0 ? "danger" : undefined} />
        <Stat label="MXRF11" value={`${mxrfQty} / 100`} hint={`faltam ${Math.max(0, 100 - mxrfQty)} cotas`} />
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Metas</CardTitle>
          <Link to="/metas"><Button size="sm" variant="outline">Editar</Button></Link>
        </CardHeader>
        <CardContent className="space-y-4">
          {(goals.data ?? []).map((g) => {
            const pct = g.target_amount > 0 ? Math.min(100, (Number(g.current_amount) / Number(g.target_amount)) * 100) : 0;
            const isCotas = g.title.toLowerCase().includes("mxrf");
            const current = isCotas ? mxrfQty : Number(g.current_amount);
            const target = Number(g.target_amount);
            const fmt = (v: number) => isCotas ? `${v} cotas` : formatBRL(v);
            const realPct = isCotas && target > 0 ? Math.min(100, (current / target) * 100) : pct;
            return (
              <div key={g.id}>
                <div className="mb-1 flex items-center justify-between text-sm">
                  <span className="font-medium">{g.icon} {g.title}</span>
                  <span className="text-muted-foreground">{fmt(current)} / {fmt(target)}</span>
                </div>
                <Progress value={realPct} />
                {g.description && <p className="mt-1 text-xs text-muted-foreground">{g.description}</p>}
              </div>
            );
          })}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Próximas ações</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm">
          {totalDebt > 0 && <div>💳 Cadastre/atualize suas <Link to="/dividas" className="text-primary underline">dívidas</Link> para receber o plano de quitação.</div>}
          {(inv.data ?? []).length === 0 && <div>📈 Cadastre suas posições na <Link to="/investimentos" className="text-primary underline">página de investimentos</Link>.</div>}
          <div>🧠 Converse com o <Link to="/chat" className="text-primary underline">agente IA</Link> para receber um plano semanal personalizado.</div>
        </CardContent>
      </Card>
    </div>
  );
}

function Stat({ label, value, hint, tone }: { label: string; value: string; hint?: string; tone?: "danger" }) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="text-xs uppercase tracking-wide text-muted-foreground">{label}</div>
        <div className={`mt-1 text-2xl font-bold ${tone === "danger" ? "text-destructive" : ""}`}>{value}</div>
        {hint && <div className="mt-1 text-xs text-muted-foreground">{hint}</div>}
      </CardContent>
    </Card>
  );
}