import { createFileRoute, Link, useNavigate, useParams } from "@tanstack/react-router";
import { useServerFn } from "@tanstack/react-start";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listThreads, createThread, deleteThread, getThreadMessages } from "@/lib/chat.functions";
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport, type UIMessage } from "ai";
import { supabase } from "@/integrations/supabase/client";
import { useEffect, useMemo, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Trash2, Send, Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { toast } from "sonner";

export const Route = createFileRoute("/_authenticated/chat/$threadId")({
  head: () => ({ meta: [{ title: "Conversa — Carteira Muth" }] }),
  component: Page,
});

function Page() {
  const { threadId } = useParams({ from: "/_authenticated/chat/$threadId" });
  const navigate = useNavigate();
  const qc = useQueryClient();

  const listFn = useServerFn(listThreads);
  const createFn = useServerFn(createThread);
  const delFn = useServerFn(deleteThread);
  const getMsgsFn = useServerFn(getThreadMessages);

  const threads = useQuery({ queryKey: ["threads"], queryFn: () => listFn() });
  const msgs = useQuery({
    queryKey: ["thread-messages", threadId],
    queryFn: () => getMsgsFn({ data: { threadId } }),
  });

  const create = useMutation({
    mutationFn: () => createFn(),
    onSuccess: (t) => {
      qc.invalidateQueries({ queryKey: ["threads"] });
      navigate({ to: "/chat/$threadId", params: { threadId: t.id } });
    },
  });
  const del = useMutation({
    mutationFn: (id: string) => delFn({ data: { id } }),
    onSuccess: async (_d, id) => {
      qc.invalidateQueries({ queryKey: ["threads"] });
      if (id === threadId) {
        const remaining = (threads.data ?? []).filter((t) => t.id !== id);
        if (remaining[0]) navigate({ to: "/chat/$threadId", params: { threadId: remaining[0].id } });
        else navigate({ to: "/chat" });
      }
    },
  });

  if (msgs.isLoading) {
    return <div className="flex h-full items-center justify-center"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>;
  }

  return (
    <div className="flex h-[calc(100vh-9rem)] gap-4 md:h-[calc(100vh-4rem)]">
      <aside className="hidden w-64 shrink-0 flex-col rounded-lg border border-border bg-card p-3 md:flex">
        <Button size="sm" className="mb-3" onClick={() => create.mutate()} disabled={create.isPending}>
          <Plus className="mr-1 h-4 w-4" /> Nova conversa
        </Button>
        <div className="flex-1 space-y-1 overflow-auto">
          {(threads.data ?? []).map((t) => (
            <div key={t.id} className={`group flex items-center gap-1 rounded-md px-2 py-1.5 text-sm ${t.id === threadId ? "bg-primary text-primary-foreground" : "hover:bg-accent"}`}>
              <Link to="/chat/$threadId" params={{ threadId: t.id }} className="flex-1 truncate">{t.title}</Link>
              <button onClick={() => del.mutate(t.id)} className="opacity-0 transition-opacity group-hover:opacity-100"><Trash2 className="h-3.5 w-3.5" /></button>
            </div>
          ))}
        </div>
      </aside>
      <ChatWindow key={threadId} threadId={threadId} initial={(msgs.data ?? []) as unknown as UIMessage[]} />
    </div>
  );
}

function ChatWindow({ threadId, initial }: { threadId: string; initial: UIMessage[] }) {
  const transport = useMemo(
    () =>
      new DefaultChatTransport({
        api: "/api/chat",
        body: { threadId },
        fetch: async (input, init) => {
          const { data } = await supabase.auth.getSession();
          const token = data.session?.access_token;
          const headers = new Headers(init?.headers);
          if (token) headers.set("Authorization", `Bearer ${token}`);
          return fetch(input, { ...init, headers });
        },
      }),
    [threadId],
  );

  const { messages, sendMessage, status } = useChat({
    id: threadId,
    messages: initial,
    transport,
    onError: (e) => toast.error(e.message),
  });

  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  useEffect(() => { inputRef.current?.focus(); }, [threadId]);

  const busy = status === "submitted" || status === "streaming";

  async function submit() {
    const text = input.trim();
    if (!text || busy) return;
    setInput("");
    await sendMessage({ text });
    inputRef.current?.focus();
  }

  return (
    <div className="flex flex-1 flex-col rounded-lg border border-border bg-card">
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-auto p-4">
        {messages.length === 0 && (
          <div className="mx-auto mt-12 max-w-md text-center text-sm text-muted-foreground">
            <p className="mb-2 text-2xl">🧠</p>
            <p>Olá! Sou seu agente financeiro. Posso te ajudar a montar plano de quitação de dívidas, calcular quanto falta para 100 cotas do MXRF11 e simular sua aposentadoria.</p>
            <p className="mt-3 text-xs">Tente: <em>"Monte meu plano para os próximos 6 meses"</em></p>
          </div>
        )}
        {messages.map((m) => {
          const text = m.parts.map((p) => (p.type === "text" ? p.text : "")).join("");
          const isUser = m.role === "user";
          return (
            <div key={m.id} className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[85%] rounded-lg px-4 py-2 text-sm ${isUser ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                {isUser ? text : <div className="prose prose-sm max-w-none dark:prose-invert"><ReactMarkdown>{text}</ReactMarkdown></div>}
              </div>
            </div>
          );
        })}
        {status === "submitted" && (
          <div className="flex justify-start"><div className="rounded-lg bg-muted px-4 py-2 text-sm"><Loader2 className="h-4 w-4 animate-spin" /></div></div>
        )}
      </div>
      <div className="border-t border-border p-3">
        <form onSubmit={(e) => { e.preventDefault(); submit(); }} className="flex gap-2">
          <Textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); } }}
            placeholder="Pergunte algo sobre suas finanças..."
            rows={2}
            className="resize-none"
            autoFocus
          />
          <Button type="submit" disabled={busy || !input.trim()} size="icon"><Send className="h-4 w-4" /></Button>
        </form>
      </div>
    </div>
  );
}