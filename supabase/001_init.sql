-- TilKz AI – деректер қоры, 1-қадам: мұғалім, сынып, оқушы, тест әрекеттері мен жауаптар.
-- Supabase → SQL Editor → New query → осы файлдың бәрін қойып → Run.
-- Қайта іске қосуға болады: бар нысандар қайта жасалмайды.

-- ============ Кестелер ============

-- Мұғалім болып тіркелуге рұқсат етілген пошталар (тек осы тізімдегі адам мұғалім бола алады)
create table if not exists public.teacher_invites (
  email text primary key
);

create table if not exists public.teachers (
  user_id    uuid primary key references auth.users on delete cascade,
  email      text not null,
  created_at timestamptz not null default now()
);

-- Сынып (топ). Оқушы тек осы кодпен тіркеле алады.
create table if not exists public.classes (
  id         uuid primary key default gen_random_uuid(),
  code       text unique not null check (code ~ '^[A-Z0-9]{6}$'),
  name       text not null,
  teacher_id uuid references public.teachers(user_id) on delete set null,
  active     boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.students (
  user_id    uuid primary key references auth.users on delete cascade,
  class_id   uuid not null references public.classes(id),
  login      text unique not null check (login ~ '^[a-z0-9._-]{3,20}$'),
  first_name text not null check (length(first_name) between 1 and 60),
  last_name  text not null check (length(last_name) between 1 and 60),
  grade      smallint not null check (grade between 1 and 11),
  city       text not null check (length(city) between 1 and 80),
  school     text not null check (length(school) between 1 and 120),
  consent_at timestamptz not null,
  created_at timestamptz not null default now()
);

-- Тест әрекеті: бір оқушының бір нұсқаны бір рет орындауы
create table if not exists public.attempts (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null default auth.uid() references auth.users on delete cascade,
  bank_id       text not null,
  mode          text not null default 'practice' check (mode in ('practice', 'exam', 'review')),
  started_at    timestamptz not null default now(),
  finished_at   timestamptz,
  first_correct integer,
  total         integer
);
create index if not exists attempts_user_idx on public.attempts (user_id, started_at desc);

-- Әр сұраққа берілген жауап. Қателер банкі осы кестеден құрылады (first_correct = false).
create table if not exists public.answers (
  attempt_id    uuid not null references public.attempts(id) on delete cascade,
  user_id       uuid not null default auth.uid() references auth.users on delete cascade,
  bank_id       text not null,
  item_id       text not null,
  skill         text,
  level         smallint,
  tries         text[] not null default '{}',
  status        text not null check (status in ('ok', 'wrong1', 'retry', 'revealed')),
  first_correct boolean not null default false,
  updated_at    timestamptz not null default now(),
  primary key (attempt_id, item_id)
);
create index if not exists answers_user_idx on public.answers (user_id, first_correct);

-- ============ Көмекші функциялар ============

create or replace function public.is_teacher() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from teachers where user_id = auth.uid());
$$;

-- Оқушы осы мұғалімнің сыныбында ма
create or replace function public.teaches(student uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from students s join classes c on c.id = s.class_id
                 where s.user_id = student and c.teacher_id = auth.uid());
$$;

-- Тіркелу алдында: сынып коды дұрыс па (дұрыс болса – сыныптың атауы)
create or replace function public.check_class_code(p_code text) returns text
language sql stable security definer set search_path = public as $$
  select name from classes where code = upper(trim(p_code)) and active;
$$;

-- Тіркелу алдында: логин бос па
create or replace function public.login_available(p_login text) returns boolean
language sql stable security definer set search_path = public as $$
  select not exists (select 1 from students where login = lower(trim(p_login)));
$$;

-- Жаңа пайдаланушы: мұғалім (шақырылған пошта) не оқушы (дұрыс сынып коды + келісім). Басқаларға тіркелуге болмайды.
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
declare
  m   jsonb := coalesce(new.raw_user_meta_data, '{}'::jsonb);
  cid uuid;
begin
  if exists (select 1 from teacher_invites where lower(email) = lower(new.email)) then
    insert into teachers (user_id, email) values (new.id, new.email) on conflict do nothing;
    update classes set teacher_id = new.id where teacher_id is null;
    return new;
  end if;

  if m->>'role' is distinct from 'student' then
    raise exception 'SIGNUP_NOT_ALLOWED';
  end if;
  select id into cid from classes where code = upper(trim(m->>'class_code')) and active;
  if cid is null then
    raise exception 'INVALID_CLASS_CODE';
  end if;
  if coalesce(m->>'consent', '') <> 'true' then
    raise exception 'NO_CONSENT';
  end if;

  insert into students (user_id, class_id, login, first_name, last_name, grade, city, school, consent_at)
  values (new.id, cid, lower(trim(m->>'login')), trim(m->>'first_name'), trim(m->>'last_name'),
          (m->>'grade')::smallint, trim(m->>'city'), trim(m->>'school'), now());
  return new;
end $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- ============ Қорғау ережелері (RLS) ============
-- Оқушы тек өз деректерін көреді; мұғалім тек өз сыныптарының оқушыларын көреді.

alter table public.teacher_invites enable row level security;  -- ешкімге ашық емес
alter table public.teachers        enable row level security;
alter table public.classes         enable row level security;
alter table public.students        enable row level security;
alter table public.attempts        enable row level security;
alter table public.answers         enable row level security;

drop policy if exists teachers_self on public.teachers;
create policy teachers_self on public.teachers for select using (user_id = auth.uid());

drop policy if exists classes_teacher on public.classes;
create policy classes_teacher on public.classes for all
  using (teacher_id = auth.uid()) with check (teacher_id = auth.uid());

drop policy if exists classes_student on public.classes;
create policy classes_student on public.classes for select
  using (id = (select class_id from public.students where user_id = auth.uid()));

drop policy if exists students_read on public.students;
create policy students_read on public.students for select
  using (user_id = auth.uid() or public.teaches(user_id));

drop policy if exists attempts_read on public.attempts;
create policy attempts_read on public.attempts for select
  using (user_id = auth.uid() or public.teaches(user_id));
drop policy if exists attempts_insert on public.attempts;
create policy attempts_insert on public.attempts for insert with check (user_id = auth.uid());
drop policy if exists attempts_update on public.attempts;
create policy attempts_update on public.attempts for update
  using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists answers_read on public.answers;
create policy answers_read on public.answers for select
  using (user_id = auth.uid() or public.teaches(user_id));
drop policy if exists answers_insert on public.answers;
create policy answers_insert on public.answers for insert
  with check (user_id = auth.uid() and exists (select 1 from public.attempts a where a.id = attempt_id and a.user_id = auth.uid()));
drop policy if exists answers_update on public.answers;
create policy answers_update on public.answers for update
  using (user_id = auth.uid()) with check (user_id = auth.uid());

revoke all on function public.handle_new_user() from public, anon, authenticated;
grant execute on function public.check_class_code(text) to anon, authenticated;
grant execute on function public.login_available(text) to anon, authenticated;

-- ============ Бастапқы деректер ============

-- Мұғалімнің поштасы (осы поштамен тіркелген адам – мұғалім)
insert into public.teacher_invites (email) values ('sagidolda.q@gmail.com') on conflict do nothing;

-- Алғашқы сынып. Код автоматты түрде жасалады; оны төмендегі нәтижеден көресіз.
insert into public.classes (code, name)
select upper(substr(translate(encode(gen_random_bytes(9), 'base64'), '+/=0O1ILoil', ''), 1, 6)), 'НЗМ, БИЛ – 1-топ'
where not exists (select 1 from public.classes);

select code as "Сынып коды", name as "Сынып" from public.classes order by created_at;
