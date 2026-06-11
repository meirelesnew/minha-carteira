import { createServerFn } from "@tanstack/react-start";
import { requireSupabaseAuth } from "@/integrations/supabase/auth-middleware";
import { z } from "zod";

// ---------- DEBTS ----------
export const listDebts = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }) => {
    const { data, error } = await context.supabase
      .from("debts").select("*").order("interest_rate_monthly", { ascending: false });
    if (error) throw new Error(error.message);
    return data ?? [];
  });

const debtInput = z.object({
  id: z.string().uuid().optional(),
  creditor: z.string().min(1),
  balance: z.number().min(0),
  interest_rate_monthly: z.number().min(0),
  installment: z.number().min(0),
  notes: z.string().nullable().optional(),
});

export const upsertDebt = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((d: unknown) => debtInput.parse(d))
  .handler(async ({ data, context }) => {
    const row = { ...data, user_id: context.userId };
    const { error } = await context.supabase.from("debts").upsert(row);
    if (error) throw new Error(error.message);
    return { ok: true };
  });

export const deleteDebt = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((d: unknown) => z.object({ id: z.string().uuid() }).parse(d))
  .handler(async ({ data, context }) => {
    const { error } = await context.supabase.from("debts").delete().eq("id", data.id);
    if (error) throw new Error(error.message);
    return { ok: true };
  });

// ---------- INVESTMENTS ----------
export const listInvestments = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }) => {
    const { data, error } = await context.supabase
      .from("investments").select("*").order("ticker");
    if (error) throw new Error(error.message);
    return data ?? [];
  });

const invInput = z.object({
  id: z.string().uuid().optional(),
  ticker: z.string().min(1).max(10),
  asset_type: z.string().default("FII"),
  quantity: z.number().min(0),
  avg_price: z.number().min(0),
  current_price: z.number().min(0).nullable().optional(),
  monthly_dividend: z.number().min(0).nullable().optional(),
  notes: z.string().nullable().optional(),
});

export const upsertInvestment = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((d: unknown) => invInput.parse(d))
  .handler(async ({ data, context }) => {
    const row = { ...data, ticker: data.ticker.toUpperCase(), user_id: context.userId };
    const { error } = await context.supabase.from("investments").upsert(row);
    if (error) throw new Error(error.message);
    return { ok: true };
  });

export const deleteInvestment = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((d: unknown) => z.object({ id: z.string().uuid() }).parse(d))
  .handler(async ({ data, context }) => {
    const { error } = await context.supabase.from("investments").delete().eq("id", data.id);
    if (error) throw new Error(error.message);
    return { ok: true };
  });

// ---------- GOALS ----------
export const listGoals = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }) => {
    const { data, error } = await context.supabase
      .from("goals").select("*").order("priority");
    if (error) throw new Error(error.message);
    return data ?? [];
  });

const goalInput = z.object({
  id: z.string().uuid(),
  current_amount: z.number().min(0),
  target_amount: z.number().min(0),
  title: z.string().min(1).optional(),
  description: z.string().nullable().optional(),
});

export const updateGoal = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((d: unknown) => goalInput.parse(d))
  .handler(async ({ data, context }) => {
    const { id, ...rest } = data;
    const { error } = await context.supabase.from("goals").update(rest).eq("id", id);
    if (error) throw new Error(error.message);
    return { ok: true };
  });

// ---------- PROFILE ----------
export const getProfile = createServerFn({ method: "GET" })
  .middleware([requireSupabaseAuth])
  .handler(async ({ context }) => {
    const { data } = await context.supabase.from("profiles").select("*").eq("id", context.userId).maybeSingle();
    return data;
  });

const profileInput = z.object({
  display_name: z.string().nullable().optional(),
  monthly_income: z.number().min(0).nullable().optional(),
  monthly_aporte: z.number().min(0).nullable().optional(),
});

export const updateProfile = createServerFn({ method: "POST" })
  .middleware([requireSupabaseAuth])
  .inputValidator((d: unknown) => profileInput.parse(d))
  .handler(async ({ data, context }) => {
    const { error } = await context.supabase.from("profiles").update(data).eq("id", context.userId);
    if (error) throw new Error(error.message);
    return { ok: true };
  });