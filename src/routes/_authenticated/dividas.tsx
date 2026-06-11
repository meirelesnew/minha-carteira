import { createFileRoute } from "@tanstack/react-router";
import { useServerFn } from "@tanstack/react-start";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listDebts, upsertDebt, deleteDebt } from "@/lib/finance.functions";
import { useState } from "react";
import { formatBRL } from "@/lib/format";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Plus, Trash2, Pencil } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/_authenticated/dividas")({
  head: () => ({ meta: [{ title: "Dívidas — Carteira Muth" }] }),
  component: Page,
});

type DebtForm = { id?: string; creditor: string; balance: string; interest_rate_monthly: string; installment: string; notes: string };
const empty: DebtForm = { creditor: "", balance: "", interest_rate_monthly: "", installment: "", notes: "" };

function Page() {
  const listFn = useServerFn(listDebts);
  const upsertFn = useServerFn(upsertDebt);
  const delFn = useServerFn(deleteDebt);
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ["debts"], queryFn: () => listFn() });
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<DebtForm>(empty);

  const save = useMutation({
    mutationFn: () => upsertFn({ data: {
      id: form.id,
      creditor: form.creditor,
      balance: Number(form.balance) || 0,
      interest_rate_monthly: Number(form.interest_rate_monthly) || 0,
      installment: Number(form.installment) || 0,
      notes: form.notes || null,
    }}),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["debts"] }); setOpen(false); setForm(empty); toast.success("Dívida salva"); },
    onError: (e: Error) => toast.error(e.message),
  });

  const del = useMutation({
    mutationFn: (id: string) => delFn({ data: { id } }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["debts"] }); toast.success("Removida"); },
  });

  const total = (q.data ?? []).reduce((s, d) => s + Number(d.balance), 0);
  const totalInst = (q.data ?? []).reduce((s, d) => s + Number(d.installment), 0);

  function edit(d: typeof q.data extends (infer T)[] | undefined ? T : never) {
    setForm({
      id: d.id,
      creditor: d.creditor,
      balance: String(d.balance),
      interest_rate_monthly: String(d.interest_rate_monthly),
      installment: String(d.installment),
      notes: d.notes ?? "",
    });
    setOpen(true);
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dívidas</h1>
          <p className="text-muted-foreground">Quitar com juros mais altos primeiro (estratégia avalanche).</p>
        </div>
        <Dialog open={open} onOpenChange={(v) => { setOpen(v); if (!v) setForm(empty); }}>
          <DialogTrigger asChild><Button><Plus className="mr-1 h-4 w-4" /> Nova dívida</Button></DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>{form.id ? "Editar" : "Nova"} dívida</DialogTitle></DialogHeader>
            <div className="space-y-3">
              <div><Label>Credor</Label><Input value={form.creditor} onChange={(e) => setForm({ ...form, creditor: e.target.value })} placeholder="Ex: Cartão Nubank" /></div>
              <div className="grid grid-cols-2 gap-3">
                <div><Label>Saldo (R$)</Label><Input type="number" step="0.01" value={form.balance} onChange={(e) => setForm({ ...form, balance: e.target.value })} /></div>
                <div><Label>Juros (% ao mês)</Label><Input type="number" step="0.01" value={form.interest_rate_monthly} onChange={(e) => setForm({ ...form, interest_rate_monthly: e.target.value })} /></div>
              </div>
              <div><Label>Parcela mensal (R$)</Label><Input type="number" step="0.01" value={form.installment} onChange={(e) => setForm({ ...form, installment: e.target.value })} /></div>
              <div><Label>Anotações</Label><Input value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></div>
            </div>
            <DialogFooter><Button onClick={() => save.mutate()} disabled={save.isPending}>Salvar</Button></DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Saldo total</div><div className="text-2xl font-bold text-destructive">{formatBRL(total)}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Parcelas/mês</div><div className="text-2xl font-bold">{formatBRL(totalInst)}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Dívidas ativas</div><div className="text-2xl font-bold">{(q.data ?? []).length}</div></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Prioridade de quitação</CardTitle></CardHeader>
        <CardContent>
          {(q.data ?? []).length === 0 ? (
            <p className="text-sm text-muted-foreground">Sem dívidas cadastradas. Se você tem, comece adicionando agora — é o primeiro passo.</p>
          ) : (
            <div className="space-y-2">
              {(q.data ?? []).map((d, i) => (
                <div key={d.id} className="flex items-center justify-between rounded-md border border-border p-3">
                  <div>
                    <div className="text-xs text-muted-foreground">#{i + 1} prioridade</div>
                    <div className="font-semibold">{d.creditor}</div>
                    <div className="text-xs text-muted-foreground">{formatBRL(Number(d.balance))} · {Number(d.interest_rate_monthly)}%/mês · parcela {formatBRL(Number(d.installment))}</div>
                  </div>
                  <div className="flex gap-1">
                    <Button size="icon" variant="ghost" onClick={() => edit(d)}><Pencil className="h-4 w-4" /></Button>
                    <Button size="icon" variant="ghost" onClick={() => del.mutate(d.id)}><Trash2 className="h-4 w-4" /></Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}