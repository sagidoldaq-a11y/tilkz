# Сайтты құрастырады (GitHub Pages):
#   index.html         – визитка (web/home.html)
#   nzm-bil/index.html – «НЗМ, БИЛ. Қазақ тілі» курсы (тест)
import json, pathlib, shutil
here = pathlib.Path(__file__).parent
root = here.parent

# 1) Визитка
shutil.copyfile(here / "home.html", root / "index.html")

# 2) Тест беті
bank = json.loads((root / "content" / "bank_v1.json").read_text(encoding="utf-8"))
tpl = (here / "app.template.html").read_text(encoding="utf-8")
body = tpl.replace("/*__BANK__*/null", json.dumps(bank, ensure_ascii=False).replace("</", "<\\/"))
bank2 = json.loads((root / "content" / "bank_l2_v1.json").read_text(encoding="utf-8"))
body = body.replace("/*__BANK_L2__*/null", json.dumps(bank2, ensure_ascii=False).replace("</", "<\\/"))
bank5 = json.loads((root / "content" / "bank_l1_v3.json").read_text(encoding="utf-8"))
body = body.replace("/*__BANK_L1_V3__*/null", json.dumps(bank5, ensure_ascii=False).replace("</", "<\\/"))
bank4 = json.loads((root / "content" / "bank_l1_v2.json").read_text(encoding="utf-8"))
body = body.replace("/*__BANK_L1_V2__*/null", json.dumps(bank4, ensure_ascii=False).replace("</", "<\\/"))
bank3 = json.loads((root / "content" / "bank_l2_v2.json").read_text(encoding="utf-8"))
body = body.replace("/*__BANK_L2_V2__*/null", json.dumps(bank3, ensure_ascii=False).replace("</", "<\\/"))
EXTRA = [("L1_V4", "bank_l1_v4.json"), ("L1_V5", "bank_l1_v5.json"), ("L2_V3", "bank_l2_v3.json"), ("L2_V4", "bank_l2_v4.json"), ("L2_V5", "bank_l2_v5.json")]
extra = {}
for slot, fn in EXTRA:   # 4-нұсқадан бастап: файл бар болса ғана қосылады
    f = (root / "content") / fn
    extra[slot] = json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    body = body.replace(f"/*__BANK_{slot}__*/null", json.dumps(extra[slot], ensure_ascii=False).replace("</", "<\\/") if extra[slot] else "null")
assert "/*__BANK" not in body
# Тіркелу мен нәтижелерді сақтау (Supabase). Ашық (publishable) кілт – сайттың кодында тұруға арналған;
# деректерді деректер қорындағы RLS ережелері қорғайды (supabase/001_init.sql).
SUPABASE = {"url": "https://yqfepngubehrupkitklr.supabase.co", "key": "sb_publishable_R_DvPrvev24GFHUtyGwhRw_r5CopZYH"}
assert body.count("/*__SUPABASE__*/null") == 1
body = body.replace("/*__SUPABASE__*/null", json.dumps(SUPABASE))
# «aitil» логотипі визиткаға апаратын сілтеме болады
brand_old = '<div class="brand"><b><span class="ai">ai</span>til</b>'
assert brand_old in body
body = body.replace(brand_old, '<div class="brand"><a href="../" class="home" title="Басты бет"><span class="ai">ai</span>til</a>')
body = body.replace("</style>", ".brand a.home{font-family:var(--f-ui);font-weight:800;font-size:22px;letter-spacing:-.3px;text-decoration:none;color:var(--ink)}\n"
                                 ".brand a.home .ai{color:var(--accent);font:inherit;letter-spacing:inherit}\n"
                                 "@media (max-width:880px){.brand a.home{font-size:19px}}\n@media (orientation:landscape) and (max-height:520px){.brand a.home{font-size:18px}}\n</style>", 1)
assert "<title>aitil</title>" in body
body = body.replace("<title>aitil</title>", "<title>НЗМ, БИЛ. Қазақ тілі – aitil</title>", 1)
head = ('<!doctype html><html lang="kk" translate="no"><head><meta charset="utf-8"><meta name="google" content="notranslate">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<meta name="description" content="НЗМ, БИЛ емтихандарына дайындық: қазақ тілі, оқу сауаттылығы. Мәтін, тест, түсініктеме, дағдылар бойынша есеп.">'
        '<meta property="og:title" content="НЗМ, БИЛ. Қазақ тілі – aitil">'
        '<meta property="og:description" content="Оқу сауаттылығы бойынша онлайн жаттықтырғыш. Автор: Қазбек Сағидолда">'
        '<meta property="og:image" content="https://aitil.kz/img/og.jpg">'
        '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js"></script>'
        '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>'
        '</head><body>')
out = root / "nzm-bil"
out.mkdir(exist_ok=True)
(out / "index.html").write_text(head + body + "</body></html>", encoding="utf-8")
# 2б) Құпиялық саясаты
(root / "privacy").mkdir(exist_ok=True)
shutil.copyfile(here / "privacy.html", root / "privacy" / "index.html")

# 3) Мұғалім кабинеті
banks_all = [bank, bank4, bank5, bank2, bank3] + [extra[s] for s in ("L1_V4","L1_V5","L2_V3","L2_V4","L2_V5") if extra[s]]   # бірінші тіл: 1, 2, 3-нұсқа; екінші тіл: 1, 2-нұсқа
tt = (here / "teacher.template.html").read_text(encoding="utf-8")
assert tt.count("/*__BANKS__*/[]") == 1 and tt.count("/*__SUPABASE__*/null") == 1
tt = tt.replace("/*__BANKS__*/[]", json.dumps(banks_all, ensure_ascii=False).replace("</", "<\\/"))
tt = tt.replace("/*__SUPABASE__*/null", json.dumps(SUPABASE))
assert tt.count("/*__BANKS__*/") == 0
tout = root / "mugalim"
tout.mkdir(exist_ok=True)
(tout / "index.html").write_text(tt, encoding="utf-8")
# 4) «Мемлекеттік қызметтегі қазақ тілі» тренажері: сабақтың мазмұны JSON-нан өзгеріссіз енгізіледі
gov_lesson = json.loads((root / "content" / "gov-kz-L1-refusal-v1.json").read_text(encoding="utf-8"))
gt = (here / "gov.template.html").read_text(encoding="utf-8")
assert gt.count("/*__LESSON__*/null") == 1 and gt.count("/*__SUPABASE__*/null") == 1
gt = gt.replace("/*__LESSON__*/null", json.dumps(gov_lesson, ensure_ascii=False).replace("</", "<\\/"))
gt = gt.replace("/*__SUPABASE__*/null", json.dumps(SUPABASE))
gout = root / "gov"
gout.mkdir(exist_ok=True)
(gout / "index.html").write_text(gt, encoding="utf-8")
print("ok", root / "index.html", out / "index.html", tout / "index.html", gout / "index.html")
