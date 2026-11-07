-- 003: Кодсыз (еркін) тіркелу.
-- Жаңа оқушы аты-жөнін, сыныбын, өзінің және ата-анасының WhatsApp нөмірін жазады, құпиясөз ойлап табады.
-- Логин – оқушының өз нөмірі (7XXXXXXXXXX). Оқушы сыныбына қарай «N-сынып (еркін тіркелу)» тобына түседі.
-- Бұрын код арқылы тіркелгендер өз логин-құпиясөзімен кіре береді; код арқылы тіркелу де жұмыс істей береді.
-- Supabase → SQL Editor → New query: осы файлды толық қойып, Run басыңыз. Қайта іске қосуға болады.

-- 1) Оқушы кестесі: қала мен мектеп енді міндетті емес, WhatsApp нөмірлері қосылады
alter table public.students alter column city drop not null;
alter table public.students alter column school drop not null;
alter table public.students add column if not exists phone text;
alter table public.students add column if not exists parent_phone text;
do $$ begin
  alter table public.students add constraint students_phone_fmt check (phone is null or phone ~ '^7[0-9]{10}$');
exception when duplicate_object then null; end $$;
do $$ begin
  alter table public.students add constraint students_parent_phone_fmt check (parent_phone is null or parent_phone ~ '^7[0-9]{10}$');
exception when duplicate_object then null; end $$;

-- 2) Әр сынып үшін еркін тіркелу тобы (4–11-сынып). Топтар 10B5C4 сыныбының мұғаліміне беріледі.
insert into public.classes (code, name, teacher_id)
select 'OPEN' || lpad(g::text, 2, '0'), g || '-сынып (еркін тіркелу)',
       (select teacher_id from public.classes where code = '10B5C4')
from generate_series(4, 11) as g
on conflict (code) do nothing;

-- 3) Тіркелу: мұғалім (шақырылған пошта), оқушы кодпен (бұрынғыдай) не кодсыз (mode = open)
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
declare
  m   jsonb := coalesce(new.raw_user_meta_data, '{}'::jsonb);
  cid uuid;
  g   smallint;
begin
  if exists (select 1 from teacher_invites where lower(email) = lower(new.email)) then
    insert into teachers (user_id, email) values (new.id, new.email) on conflict do nothing;
    update classes set teacher_id = new.id where teacher_id is null;
    return new;
  end if;

  if m->>'role' is distinct from 'student' then
    raise exception 'SIGNUP_NOT_ALLOWED';
  end if;
  if coalesce(m->>'consent', '') <> 'true' then
    raise exception 'NO_CONSENT';
  end if;

  if m->>'mode' = 'open' then
    g := (m->>'grade')::smallint;
    select id into cid from classes where code = 'OPEN' || lpad(g::text, 2, '0') and active;
    if cid is null then
      raise exception 'INVALID_GRADE';
    end if;
    insert into students (user_id, class_id, login, first_name, last_name, grade, phone, parent_phone, consent_at)
    values (new.id, cid, trim(m->>'phone'), trim(m->>'first_name'), trim(m->>'last_name'), g,
            trim(m->>'phone'), trim(m->>'parent_phone'), now());
    return new;
  end if;

  select id into cid from classes where code = upper(trim(m->>'class_code')) and active;
  if cid is null then
    raise exception 'INVALID_CLASS_CODE';
  end if;
  insert into students (user_id, class_id, login, first_name, last_name, grade, city, school, consent_at)
  values (new.id, cid, lower(trim(m->>'login')), trim(m->>'first_name'), trim(m->>'last_name'),
          (m->>'grade')::smallint, trim(m->>'city'), trim(m->>'school'), now());
  return new;
end $$;

revoke all on function public.handle_new_user() from public, anon, authenticated;
