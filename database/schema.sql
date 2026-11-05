-- Users profile table that links to Supabase Auth
create table profiles (
  id uuid references auth.users on delete cascade not null primary key,
  updated_at timestamp with time zone,
  username text unique,
  full_name text,
  avatar_url text,
  website text,
  tier text default 'free' check (tier in ('free', 'pro')),

  constraint username_length check (char_length(username) >= 3)
);

-- Enable Row Level Security (RLS)
alter table profiles enable row level security;

create policy "Public profiles are viewable by everyone." on profiles
  for select using (true);

create policy "Users can insert their own profile." on profiles
  for insert with check (auth.uid() = id);

create policy "Users can update own profile." on profiles
  for update using (auth.uid() = id);

-- Trigger to create profile on signup
create function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, full_name, avatar_url)
  values (new.id, new.raw_user_meta_data->>'full_name', new.raw_user_meta_data->>'avatar_url');
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- Job Description Analyses table
create table analyses (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users not null,
  jd_text text not null,
  analysis_json jsonb not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table analyses enable row level security;

create policy "Users can view their own analyses." on analyses
  for select using (auth.uid() = user_id);

create policy "Users can insert their own analyses." on analyses
  for insert with check (auth.uid() = user_id);

-- Saved Projects table
create table saved_projects (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) not null,
  title text not null,
  description text,
  tech_stack text,
  implementation_plan jsonb,
  is_favorite boolean default false,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table saved_projects enable row level security;

create policy "Users can view their own projects." on saved_projects
  for select using (auth.uid() = user_id);

create policy "Users can manage their own projects." on saved_projects
  for all using (auth.uid() = user_id);
