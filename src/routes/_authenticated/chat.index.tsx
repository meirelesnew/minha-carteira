import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useServerFn } from "@tanstack/react-start";
import { useMutation, useQuery } from "@tanstack/react-query";
import { listThreads, createThread } from "@/lib/chat.functions";
import { useEffect } from "react";
import { Loader2 } from "lucide-react";

export const Route = createFileRoute("/_authenticated/chat/")({
  head: () => ({ meta: [{ title: "Agente IA — Carteira Muth" }] }),
  component: Page,
});

function Page() {
  const navigate = useNavigate();
  const listFn = useServerFn(listThreads);
  const createFn = useServerFn(createThread);
  const q = useQuery({ queryKey: ["threads"], queryFn: () => listFn() });
  const create = useMutation({
    mutationFn: () => createFn(),
    onSuccess: (t) => navigate({ to: "/chat/$threadId", params: { threadId: t.id } }),
  });

  useEffect(() => {
    if (q.isSuccess) {
      if ((q.data ?? []).length === 0) create.mutate();
      else navigate({ to: "/chat/$threadId", params: { threadId: q.data![0].id }, replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q.isSuccess]);

  return (
    <div className="flex h-full items-center justify-center">
      <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
    </div>
  );
}