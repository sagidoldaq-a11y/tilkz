-- 004: Ересек пайдаланушылардың тіркелуі («Мемлекеттік қызметтегі қазақ тілі» тренажері).
-- Google арқылы (OAuth) не email + құпиясөз арқылы (role = learner) тіркелген адам өткізіледі.
-- Оқушылар кестесіне жазылмайды; нәтижелері бұрынғыдай attempts/answers кестелеріне түседі.
-- Мұғалім (шақырылған пошта) мен оқушы (кодпен не кодсыз) ережелері 003-тегідей.

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

  -- Ересек пайдаланушы: Google арқылы не email арқылы (role = learner)
  if coalesce(new.raw_app_meta_data->>'provider', 'email') <> 'email' or m->>'role' = 'learner' then
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
