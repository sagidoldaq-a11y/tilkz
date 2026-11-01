# Тапсырмалар банкін веб-прототипке енгізеді
import json, pathlib
here = pathlib.Path(__file__).parent
bank = json.loads((here.parent/"content"/"bank_v1.json").read_text(encoding="utf-8"))
tpl = (here/"app.template.html").read_text(encoding="utf-8")
out = tpl.replace("/*__BANK__*/null", json.dumps(bank, ensure_ascii=False).replace("</", "<\\/"))
(here/"oqylym.html").write_text(out, encoding="utf-8")
print("ok", len(out))
