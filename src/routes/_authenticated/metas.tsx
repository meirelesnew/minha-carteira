import { createFileRoute } from "@tanstack/react-router";
import { useServerFn } from "@tanstack/react-start";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listGoals, updateGoal, getProfile, updateProfile } from "@/lib/finance.functions";
import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

export const Route = createFileRoute("/_authenticated/metas")({
  head: () => ({ meta: [{ title: "Metas — Carteira Muth" }] }),
  component: Page,
});

function Page() {
  const listFn = useServerFn(listGoals);
  const updFn = useServerFn(updateGoal);
  const profFn = useServerFn(getProfile);
  const updProfFn = useServerFn(updateProfile);
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ["goals"], queryFn: () => listFn() });
  const profile = useQuery({ queryKey: ["profile"], queryFn: () => profFn() });

  const [aporte, setAporte] = useState("");
  const [income, setIncome] = useState("");

  useEffect(() => {
    if (profile.data) {
      setAporte(String(profile.data.monthly_aporte ?? ""));
      setIncome(String(profile.data.monthly_income ?? ""));
    }
  }, [profile.data]);

  const upd = useMutation({
    mutationFn: (vars: { id: string; current_amount: number; target_amount: number }) => updFn({ data: vars }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["goals"] }); toast.success("Meta atualizada"); },
  });
  const updProf = useMutation({
    mutationFn: () => updProfFn({ data: { monthly_aporte: Number(aporte) || 0, monthly_income: Number(income) || 0 } }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["profile"] }); toast.success("Perfil atualizado"); },
  });

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Metas e perfil</h1>
        <p className="text-muted-foreground">Configure os números que o agente usa para te orientar.</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Renda e aporte</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div><Label>Renda mensal (R$)</Label><Input type="number" step="0.01" value={income} onChange={(e) => setIncome(e.target.value)} /></div>
            <div><Label>Aporte mensal (R$)</Label><Input type="number" step="0.01" value={aporte} onChange={(e) => setAporte(e.target.value)} /></div>
          </div>
          <Button onClick={() => updProf.mutate()} disabled={updProf.isPending}>Salvar</Button>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {(q.data ?? []).map((g) => (
          <GoalEditor key={g.id} goal={g} onSave={(cur, tar) => upd.mutate({ id: g.id, current_amount: cur, target_amount: tar })} />
        ))}
      </div>
    </div>
  );
}

function GoalEditor({ goal, onSave }: { goal: { id: string; title: string; description: string | null; icon: string | null; current_amount: number; target_amount: number }; onSave: (cur: number, tar: number) => void }) {
  const [cur, setCur] = useState(String(goal.current_amount));
  const [tar, setTar] = useState(String(goal.target_amount));
  return (
    <Card>
      <CardHeader><CardTitle className="text-base">{goal.icon} {goal.title}</CardTitle></CardHeader>
      <CardContent className="space-y-3">
        {goal.description && <p className="text-sm text-muted-foreground">{goal.description}</p>}
        <div className="grid grid-cols-2 gap-3">
          <div><Label>Atual</Label><Input type="number" step="0.01" value={cur} onChange={(e) => setCur(e.target.value)} /></div>
          <div><Label>Meta</Label><Input type="number" step="0.01" value={tar} onChange={(e) => setTar(e.target.value)} /></div>
        </div>
        <Button size="sm" onClick={() => onSave(Number(cur) || 0, Number(tar) || 0)}>Salvar</Button>
      </CardContent>
    </Card>
  );
}