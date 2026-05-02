create extension if not exists pgcrypto;

create table if not exists public.strings (
  id            uuid primary key default gen_random_uuid(),
  game_id       text not null,
  "offset"      text not null,
  english       text not null,
  irish         text,
  budget        integer not null,
  verified      boolean not null default false,
  compromised   boolean not null default false,
  note          text,
  updated_at    timestamptz not null default now(),
  unique (game_id, "offset")
);

create index if not exists strings_game_id_idx on public.strings (game_id);
create index if not exists strings_game_offset_idx on public.strings (game_id, "offset");

create table if not exists public.suggestions (
  id               uuid primary key default gen_random_uuid(),
  game_id          text not null,
  "offset"         text not null,
  suggested        text not null,
  note             text,
  user_id          uuid references auth.users(id) on delete set null,
  github_username  text,
  upvotes          integer not null default 0,
  status           text not null default 'open' check (status in ('open', 'accepted', 'rejected')),
  created_at       timestamptz not null default now()
);

create index if not exists suggestions_game_offset_idx on public.suggestions (game_id, "offset");
create index if not exists suggestions_status_idx on public.suggestions (status);

create table if not exists public.verifications (
  id               uuid primary key default gen_random_uuid(),
  game_id          text not null,
  "offset"         text not null,
  user_id          uuid references auth.users(id) on delete set null,
  github_username  text,
  created_at       timestamptz not null default now()
);

create index if not exists verifications_game_offset_idx on public.verifications (game_id, "offset");

create table if not exists public.contributors (
  user_id          uuid primary key references auth.users(id) on delete cascade,
  github_username  text not null unique,
  added_at         timestamptz not null default now()
);

alter table public.strings enable row level security;
alter table public.suggestions enable row level security;
alter table public.verifications enable row level security;
alter table public.contributors enable row level security;

create policy "strings are public"
  on public.strings
  for select
  using (true);

create policy "contributors can update strings"
  on public.strings
  for update
  using (
    exists (
      select 1
      from public.contributors
      where contributors.user_id = auth.uid()
    )
  )
  with check (
    exists (
      select 1
      from public.contributors
      where contributors.user_id = auth.uid()
    )
  );

create policy "suggestions are public"
  on public.suggestions
  for select
  using (true);

create policy "authenticated users can suggest"
  on public.suggestions
  for insert
  with check (auth.role() = 'authenticated');

create policy "verifications are public"
  on public.verifications
  for select
  using (true);

create policy "contributors can verify"
  on public.verifications
  for insert
  with check (
    exists (
      select 1
      from public.contributors
      where contributors.user_id = auth.uid()
    )
  );

create policy "contributors are public"
  on public.contributors
  for select
  using (true);
