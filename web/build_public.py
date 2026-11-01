# Көмекшісіз, кез келген хостингте жұмыс істейтін нұсқа (А кезеңі)
import json, pathlib, re
here = pathlib.Path(__file__).parent
bank = json.loads((here.parent/"content"/"bank_v1.json").read_text(encoding="utf-8"))
tpl = (here/"app.template.html").read_text(encoding="utf-8")
body = tpl.replace("/*__BANK__*/null", json.dumps(bank, ensure_ascii=False).replace("</", "<\\/"))
# Көмекші батырмасын жасыру: window.claude жоқ ортада ол қажет емес
body = body.replace("</style>", "body.no-ai [data-act=help]{display:none}\n</style>", 1)
body = body.replace("renderAll();\n</script>", "if(!window.claude) document.body.classList.add('no-ai');\nrenderAll();\n</script>")
assert "no-ai');" in body
head = ('<!doctype html><html lang="kk"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<meta name="description" content="TilKz AI — қазақ тілі оқу сауаттылығы: НЗМ, БИЛ емтихандарына дайындық">'
        '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>'
        '</head><body>')
out_dir = here.parent
(out_dir/"index.html").write_text(head + body + "</body></html>", encoding="utf-8")
print("ok", out_dir/"index.html")
