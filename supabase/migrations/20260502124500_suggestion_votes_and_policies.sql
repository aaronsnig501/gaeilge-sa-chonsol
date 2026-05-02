create table if not exists public.suggestion_votes (
  id             uuid primary key default gen_random_uuid(),
  suggestion_id  uuid not null references public.suggestions(id) on delete cascade,
  user_id        uuid not null references auth.users(id) on delete cascade,
  created_at     timestamptz not null default now(),
  unique (suggestion_id, user_id)
);

create index if not exists suggestion_votes_suggestion_id_idx
  on public.suggestion_votes (suggestion_id);

create index if not exists suggestion_votes_user_id_idx
  on public.suggestion_votes (user_id);

alter table public.suggestion_votes enable row level security;

create or replace function public.sync_suggestion_upvotes()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  if tg_op = 'INSERT' then
    update public.suggestions
    set upvotes = upvotes + 1
    where id = new.suggestion_id;
    return new;
  elsif tg_op = 'DELETE' then
    update public.suggestions
    set upvotes = greatest(upvotes - 1, 0)
    where id = old.suggestion_id;
    return old;
  end if;

  return null;
end;
$$;

drop trigger if exists suggestion_votes_sync_upvotes on public.suggestion_votes;

create trigger suggestion_votes_sync_upvotes
after insert or delete on public.suggestion_votes
for each row
execute function public.sync_suggestion_upvotes();

create policy "suggestion votes are public"
  on public.suggestion_votes
  for select
  using (true);

create policy "authenticated users can vote on suggestions"
  on public.suggestion_votes
  for insert
  with check (auth.role() = 'authenticated' and user_id = auth.uid());

create policy "users can remove their own suggestion votes"
  on public.suggestion_votes
  for delete
  using (user_id = auth.uid());

create policy "contributors can update suggestions"
  on public.suggestions
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
