create extension if not exists "pgcrypto";

create function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = timezone('utc', now());
  return new;
end;
$$;

create table public.clients (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name_or_business text not null,
  identificacion text not null,
  contact text,
  notes text,
  payment_state text not null check (payment_state in ('pendiente', 'pagado')),
  payment_amount numeric(14,2),
  tags text[] not null default '{}',
  documents jsonb not null default '[]'::jsonb,
  tax_profile jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create trigger set_clients_updated_at
before update on public.clients
for each row
execute procedure public.set_updated_at();

create index clients_user_id_idx on public.clients(user_id);
create index clients_identificacion_idx on public.clients(identificacion);
create index clients_search_idx on public.clients using gin (to_tsvector('spanish', name_or_business || ' ' || coalesce(notes, '')));

alter table public.clients enable row level security;

create policy clients_select on public.clients
for select using (auth.uid() = user_id);

create policy clients_modify on public.clients
for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table public.tasks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  description text,
  status text not null check (status in ('sin_iniciar', 'en_proceso', 'finalizado')),
  labels text[] not null default '{}',
  due_date timestamptz,
  add_to_calendar boolean not null default false,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now()),
  "order" double precision not null default 0
);

create trigger set_tasks_updated_at
before update on public.tasks
for each row
execute procedure public.set_updated_at();

create index tasks_user_id_idx on public.tasks(user_id);
create index tasks_status_idx on public.tasks(status);
create index tasks_due_date_idx on public.tasks(due_date);
create index tasks_labels_gin_idx on public.tasks using gin(labels);

alter table public.tasks enable row level security;

create policy tasks_select on public.tasks
for select using (auth.uid() = user_id);

create policy tasks_modify on public.tasks
for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
