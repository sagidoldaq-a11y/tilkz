-- TilKz AI – деректер қоры, 2-қадам: мұғалімнің құралдары.
-- Мұғалім өз сыныбындағы оқушының құпиясөзін ауыстыра алады және оқушыны (барлық деректерімен) өшіре алады.
-- Supabase → SQL Editor → New query → осы файлдың бәрін қойып → Run.

-- Оқушының құпиясөзін ауыстыру (тек осы оқушы оқитын сыныптың мұғалімі)
create or replace function public.teacher_set_password(p_student uuid, p_password text) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  if not public.teaches(p_student) then
    raise exception 'NOT_ALLOWED';
  end if;
  if p_password is null or length(p_password) < 6 then
    raise exception 'PASSWORD_TOO_SHORT';
  end if;
  update auth.users
     set encrypted_password = extensions.crypt(p_password, extensions.gen_salt('bf')),
         updated_at = now()
   where id = p_student;
end $$;

-- Оқушыны өшіру: аккаунты, профилі, тест әрекеттері мен жауаптары толық өшіріледі
create or replace function public.teacher_delete_student(p_student uuid) returns void
language plpgsql security definer set search_path = public as $$
begin
  if not public.teaches(p_student) then
    raise exception 'NOT_ALLOWED';
  end if;
  delete from auth.users where id = p_student;
end $$;

revoke all on function public.teacher_set_password(uuid, text) from public, anon;
revoke all on function public.teacher_delete_student(uuid) from public, anon;
grant execute on function public.teacher_set_password(uuid, text) to authenticated;
grant execute on function public.teacher_delete_student(uuid) to authenticated;

select 'Дайын: мұғалімнің құралдары қосылды' as "Нәтиже";
