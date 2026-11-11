-- Apply once in Supabase SQL Editor BEFORE deploying the new API.
-- This migration preserves existing user data and adds atomic cross-instance quotas.
begin;

create table if not exists public.api_usage (
    user_id uuid not null references auth.users(id) on delete cascade,
    feature text not null check (feature in ('analyse', 'recommend', 'implement', 'upgrade')),
    window_start date not null,
    used integer not null default 0 check (used >= 0),
    primary key (user_id, feature, window_start)
);

alter table public.api_usage enable row level security;

-- No policies allow the browser's anon/authenticated roles to mutate quotas.
revoke all on table public.api_usage from anon, authenticated;

create or replace function public.consume_api_quota(
    p_user_id uuid,
    p_feature text,
    p_limit integer,
    p_window_start date
)
returns boolean
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
    updated_count integer;
begin
    if p_user_id is null
       or p_feature not in ('analyse', 'recommend', 'implement', 'upgrade')
       or p_limit < 1 or p_limit > 100000 or p_limit is null
       or p_window_start is null then
        raise exception 'Invalid quota parameters';
    end if;

    insert into public.api_usage as usage (user_id, feature, window_start, used)
    values (p_user_id, p_feature, p_window_start, 1)
    on conflict (user_id, feature, window_start)
    do update set used = usage.used + 1
    where usage.used < p_limit
    returning used into updated_count;

    return updated_count is not null;
end;
$$;

-- Only the trusted server may use the SECURITY DEFINER function.
revoke all on function public.consume_api_quota(uuid,text,integer,date) from public, anon, authenticated;
grant execute on function public.consume_api_quota(uuid,text,integer,date) to service_role;

-- Protect the "tier" column from client-side self-upgrades.
-- Profiles are created by the existing auth.users SECURITY DEFINER trigger.
revoke insert, update on table public.profiles from anon, authenticated;
grant update (username, full_name, avatar_url, website, updated_at)
  on table public.profiles to authenticated;

drop policy if exists "Public profiles are viewable by everyone." on public.profiles;
drop policy if exists "Users can view own profile." on public.profiles;
create policy "Users can view own profile." on public.profiles
  for select to authenticated using (auth.uid() = id);

commit;
