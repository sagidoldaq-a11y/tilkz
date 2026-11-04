# Тапсырмалар банкін веб-прототипке енгізеді
import json, pathlib
here = pathlib.Path(__file__).parent
bank = json.loads((here.parent/"content"/"bank_v1.json").read_text(encoding="utf-8"))
tpl = (here/"app.template.html").read_text(encoding="utf-8")
out = tpl.replace("/*__BANK__*/null", json.dumps(bank, ensure_ascii=False).replace("</", "<\\/"))
bank2 = json.loads((here.parent/"content"/"bank_l2_v1.json").read_text(encoding="utf-8"))
out = out.replace("/*__BANK_L2__*/null", json.dumps(bank2, ensure_ascii=False).replace("</", "<\\/"))
bank5 = json.loads((here.parent/"content"/"bank_l1_v3.json").read_text(encoding="utf-8"))
out = out.replace("/*__BANK_L1_V3__*/null", json.dumps(bank5, ensure_ascii=False).replace("</", "<\\/"))
bank4 = json.loads((here.parent/"content"/"bank_l1_v2.json").read_text(encoding="utf-8"))
out = out.replace("/*__BANK_L1_V2__*/null", json.dumps(bank4, ensure_ascii=False).replace("</", "<\\/"))
bank3 = json.loads((here.parent/"content"/"bank_l2_v2.json").read_text(encoding="utf-8"))
out = out.replace("/*__BANK_L2_V2__*/null", json.dumps(bank3, ensure_ascii=False).replace("</", "<\\/"))
EXTRA = [("L1_V4", "bank_l1_v4.json"), ("L1_V5", "bank_l1_v5.json"), ("L2_V3", "bank_l2_v3.json"), ("L2_V4", "bank_l2_v4.json"), ("L2_V5", "bank_l2_v5.json")]
extra = {}
for slot, fn in EXTRA:   # 4-нұсқадан бастап: файл бар болса ғана қосылады
    f = (here.parent/"content") / fn
    extra[slot] = json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    out = out.replace(f"/*__BANK_{slot}__*/null", json.dumps(extra[slot], ensure_ascii=False).replace("</", "<\\/") if extra[slot] else "null")
(here/"oqylym.html").write_text(out, encoding="utf-8")
print("ok", len(out))
