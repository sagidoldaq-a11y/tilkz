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
bank3 = json.loads((root / "content" / "bank_l2_v2.json").read_text(encoding="utf-8"))
body = body.replace("/*__BANK_L2_V2__*/null", json.dumps(bank3, ensure_ascii=False).replace("</", "<\\/"))
assert "/*__BANK" not in body
# «TilKz AI» атауы визиткаға апаратын сілтеме болады
brand_old = '<div class="brand"><b>TilKz <span class="ai">AI</span></b>'
assert brand_old in body
body = body.replace(brand_old, '<div class="brand"><a href="../" class="home" title="Басты бет">TilKz <span class="ai">AI</span></a>')
body = body.replace("</style>", ".brand a.home{font-family:var(--f-text);font-weight:700;font-size:22px;letter-spacing:.2px;text-decoration:none;color:var(--ink)}\n"
                                 ".brand a.home .ai{color:var(--accent);font-family:var(--f-ui);font-weight:700;letter-spacing:.5px;font-size:inherit}\n"
                                 "@media (max-width:880px){.brand a.home{font-size:19px}}\n@media (orientation:landscape) and (max-height:520px){.brand a.home{font-size:18px}}\n</style>", 1)
body = body.replace("<title>TilKz AI</title>", "<title>НЗМ, БИЛ. Қазақ тілі – TilKz AI</title>", 1)
head = ('<!doctype html><html lang="kk"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<meta name="description" content="НЗМ, БИЛ емтихандарына дайындық: қазақ тілі, оқу сауаттылығы. Мәтін, тест, түсініктеме, дағдылар бойынша есеп.">'
        '<meta property="og:title" content="НЗМ, БИЛ. Қазақ тілі – TilKz AI">'
        '<meta property="og:description" content="Оқу сауаттылығы бойынша онлайн жаттықтырғыш. Автор: Қазбек Сағидолда">'
        '<meta property="og:image" content="https://sagidoldaq-a11y.github.io/tilkz/img/og.jpg">'
        '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>'
        '</head><body>')
out = root / "nzm-bil"
out.mkdir(exist_ok=True)
(out / "index.html").write_text(head + body + "</body></html>", encoding="utf-8")
print("ok", root / "index.html", out / "index.html")
