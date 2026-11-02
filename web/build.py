# Тапсырмалар банкін веб-прототипке енгізеді
import json, pathlib
here = pathlib.Path(__file__).parent
bank = json.loads((here.parent/"content"/"bank_v1.json").read_text(encoding="utf-8"))
tpl = (here/"app.template.html").read_text(encoding="utf-8")
out = tpl.replace("/*__BANK__*/null", json.dumps(bank, ensure_ascii=False).replace("</", "<\\/"))
bank2 = json.loads((here.parent/"content"/"bank_l2_v1.json").read_text(encoding="utf-8"))
out = out.replace("/*__BANK_L2__*/null", json.dumps(bank2, ensure_ascii=False).replace("</", "<\\/"))
bank3 = json.loads((here.parent/"content"/"bank_l2_v2.json").read_text(encoding="utf-8"))
out = out.replace("/*__BANK_L2_V2__*/null", json.dumps(bank3, ensure_ascii=False).replace("</", "<\\/"))
(here/"oqylym.html").write_text(out, encoding="utf-8")
print("ok", len(out))
