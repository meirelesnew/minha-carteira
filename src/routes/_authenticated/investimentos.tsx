import { createFileRoute } from "@tanstack/react-router";
import { useServerFn } from "@tanstack/react-start";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listInvestments, upsertInvestment, deleteInvestment } from "@/lib/finance.functions";
import { useState } from "react";
import { formatBRL } from "@/lib/format";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Plus, Trash2, Pencil } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";

export const Route = createFileRoute("/_authenticated/investimentos")({
  head: () => ({ meta: [{ title: "Investimentos — Carteira Muth" }] }),
  component: Page,
});

type Form = { id?: string; ticker: string; asset_type: string; quantity: string; avg_price: string; current_price: string; monthly_dividend: string; notes: string };
const empty: Form = { ticker: "", asset_type: "FII", quantity: "", avg_price: "", current_price: "", monthly_dividend: "", notes: "" };

function Page() {
  const listFn = useServerFn(listInvestments);
  const upsertFn = useServerFn(upsertInvestment);
  const delFn = useServerFn(deleteInvestment);
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ["investments"], queryFn: () => listFn() });
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<Form>(empty);

  const save = useMutation({
    mutationFn: () => upsertFn({ data: {
      id: form.id,
      ticker: form.ticker,
      asset_type: form.asset_type || "FII",
      quantity: Number(form.quantity) || 0,
      avg_price: Number(form.avg_price) || 0,
      current_price: form.current_price ? Number(form.current_price) : null,
      monthly_dividend: form.monthly_dividend ? Number(form.monthly_dividend) : null,
      notes: form.notes || null,
    }}),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["investments"] }); setOpen(false); setForm(empty); toast.success("Investimento salvo"); },
    onError: (e: Error) => toast.error(e.message),
  });

  const del = useMutation({
    mutationFn: (id: string) => delFn({ data: { id } }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["investments"] }),
  });

  const patrimonio = (q.data ?? []).reduce((s, i) => s + Number(i.quantity) * Number(i.current_price ?? i.avg_price), 0);
  const dividendos = (q.data ?? []).reduce((s, i) => s + Number(i.quantity) * Number(i.monthly_dividend ?? 0), 0);
  const mxrf = (q.data ?? []).find((i) => i.ticker?.toUpperCase() === "MXRF11");
  const mxrfQty = mxrf ? Number(mxrf.quantity) : 0;
  const mxrfPrice = mxrf ? Number(mxrf.current_price ?? mxrf.avg_price) : 10;
  const cotasFaltam = Math.max(0, 100 - mxrfQty);
  const valorFalta = cotasFaltam * mxrfPrice;

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Investimentos</h1>
          <p className="text-muted-foreground">Sua carteira e progresso para 100 cotas do MXRF11.</p>
        </div>
        <Dialog open={open} onOpenChange={(v) => { setOpen(v); if (!v) setForm(empty); }}>
          <DialogTrigger asChild><Button><Plus className="mr-1 h-4 w-4" /> Novo ativo</Button></DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>{form.id ? "Editar" : "Novo"} ativo</DialogTitle></DialogHeader>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div><Label>Ticker</Label><Input value={form.ticker} onChange={(e) => setForm({ ...form, ticker: e.target.value.toUpperCase() })} placeholder="MXRF11" /></div>
                <div><Label>Tipo</Label><Input value={form.asset_type} onChange={(e) => setForm({ ...form, asset_type: e.target.value })} placeholder="FII / Ação" /></div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div><Label>Quantidade</Label><Input type="number" step="1" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} /></div>
                <div><Label>Preço médio (R$)</Label><Input type="number" step="0.01" value={form.avg_price} onChange={(e) => setForm({ ...form, avg_price: e.target.value })} /></div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div><Label>Cotação atual (R$)</Label><Input type="number" step="0.01" value={form.current_price} onChange={(e) => setForm({ ...form, current_price: e.target.value })} /></div>
                <div><Label>Dividendo/cota (R$)</Label><Input type="number" step="0.0001" value={form.monthly_dividend} onChange={(e) => setForm({ ...form, monthly_dividend: e.target.value })} /></div>
              </div>
              <div><Label>Anotações</Label><Input value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></div>
            </div>
            <DialogFooter><Button onClick={() => save.mutate()} disabled={save.isPending}>Salvar</Button></DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Patrimônio</div><div className="text-2xl font-bold">{formatBRL(patrimonio)}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Dividendos/mês</div><div className="text-2xl font-bold">{formatBRL(dividendos)}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Ativos</div><div className="text-2xl font-bold">{(q.data ?? []).length}</div></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle>🎯 Meta: 100 cotas MXRF11</CardTitle></CardHeader>
        <CardContent>
          <div className="mb-2 flex items-center justify-between text-sm"><span>{mxrfQty} cotas</span><span className="text-muted-foreground">100 cotas</span></div>
          <Progress value={Math.min(100, mxrfQty)} />
          <div className="mt-3 text-sm text-muted-foreground">
            Faltam <strong className="text-foreground">{cotasFaltam} cotas</strong> · estimativa de aporte: <strong className="text-foreground">{formatBRL(valorFalta)}</strong>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Carteira</CardTitle></CardHeader>
        <CardContent>
          {(q.data ?? []).length === 0 ? (
            <p className="text-sm text-muted-foreground">Adicione seu primeiro ativo. Comece pelo MXRF11.</p>
          ) : (
            <div className="space-y-2">
              {(q.data ?? []).map((i) => {
                const qty = Number(i.quantity);
                const price = Number(i.current_price ?? i.avg_price);
                return (
                  <div key={i.id} className="flex items-center justify-between rounded-md border border-border p-3">
                    <div>
                      <div className="font-semibold">{i.ticker} <span className="ml-1 text-xs font-normal text-muted-foreground">{i.asset_type}</span></div>
                      <div className="text-xs text-muted-foreground">{qty} cotas × {formatBRL(price)} = {formatBRL(qty * price)}</div>
                    </div>
                    <div className="flex gap-1">
                      <Button size="icon" variant="ghost" onClick={() => { setForm({ id: i.id, ticker: i.ticker, asset_type: i.asset_type, quantity: String(i.quantity), avg_price: String(i.avg_price), current_price: i.current_price ? String(i.current_price) : "", monthly_dividend: i.monthly_dividend ? String(i.monthly_dividend) : "", notes: i.notes ?? "" }); setOpen(true); }}><Pencil className="h-4 w-4" /></Button>
                      <Button size="icon" variant="ghost" onClick={() => del.mutate(i.id)}><Trash2 className="h-4 w-4" /></Button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}