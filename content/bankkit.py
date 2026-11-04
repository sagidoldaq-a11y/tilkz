# Нұсқа банктерін құрастыруға арналған ортақ құралдар (3-нұсқадан бастап).
# Әр build_*.py файлы тек мазмұнды (мәтін, сұрақ, аударма) береді; тексеріс пен құжат осында.
import json, re, pathlib
from collections import Counter

ROOT = pathlib.Path(__file__).parent

SKILLS = {
    "A1": "Нақты деректі табу", "A2": "Себеп пен салдарды табу", "A3": "Ақпараттың орнын табу",
    "B1": "Сілтемені анықтау", "B2": "Сөздің мәтіндегі мағынасы", "B3": "Тұжырымды мәтінмен салыстыру",
    "B4": "Кейіпкердің сезімі мен мінезі", "C1": "Негізгі ой, тақырып, атау", "C2": "Астарлы ойды түсіндіру",
    "C3": "Түйін, кеңес, тағылым", "C4": "Мәтін құрылымы мен логикасы", "D1": "Мәтін үлгісі мен жанры",
    "D2": "Автордың мақсаты мен көзқарасы",
}
TWO_L1 = ["екеуі де бұрыс", "екеуі де дұрыс", "тек біріншісі", "тек екіншісі"]   # НЗМ бірінші тіл үлгісіндегі рет
TWO_L2 = ["тек біріншісі", "тек екіншісі", "екеуі де дұрыс", "екеуі де бұрыс"]   # НЗМ екінші тіл үлгісіндегі рет

strip_loc = lambda e: re.sub(r"\s*\([^)]*(азатжол|бөлім)[^)]*\)$", "", e)


class Bank:
    def __init__(self, prefix, bank_id, track, source, ru=False):
        self.prefix, self.bank_id, self.track, self.source, self.ru = prefix, bank_id, track, source, ru
        self.texts, self.items, self.changes, self.evid_ru = [], [], {}, {}

    def text(self, i, title, paras, src, numbered=False, changes=""):
        tid = f"{self.prefix}-t{i}"
        self.texts.append({"id": tid, "title": title, "source_note": src, "numbered_paragraphs": numbered, "paragraphs": paras})
        if changes: self.changes[tid] = changes

    def q(self, n, t, stem, opts, key, skill, level, ev, expl, kw_ok, notes, fixed=False, negative=False, expl_ru="", kw_ok_ru=None):
        """L1: notes = {L: (kk, [ev], [kw])};  L2 (ru=True): notes = {L: (kk, ru, [ev], [kw kk], [kw ru])}"""
        tid = f"{self.prefix}-t{t}"
        it = {"id": f"{self.prefix}-q{n}", "number": n, "text_id": tid, "stem": stem,
              "options": dict(zip("ABCD", opts)), "key": key, "skill": skill, "skill_name": SKILLS[skill],
              "level": level, "negative": negative, "fixed_order": fixed, "evidence": ev, "explanation": expl,
              "editor_changes": self.changes.get(tid, "") if not any(x["text_id"] == tid and x["editor_changes"] for x in self.items) else ""}
        if self.ru:
            it["explanation_ru"] = expl_ru
            it["distractor_notes"] = {k: v[0] for k, v in notes.items()}
            it["distractor_notes_ru"] = {k: v[1] for k, v in notes.items()}
            it["distractor_evidence"] = {k: [strip_loc(e) for e in v[2]] for k, v in notes.items()}
            it["keywords"] = dict({"ok": {"kk": kw_ok, "ru": kw_ok_ru or []}}, **{k: {"kk": v[3], "ru": v[4]} for k, v in notes.items() if v[2]})
        else:
            it["distractor_notes"] = {k: v[0] for k, v in notes.items()}
            it["distractor_evidence"] = {k: [strip_loc(e) for e in v[1]] for k, v in notes.items()}
            it["keywords"] = dict({"ok": {"kk": kw_ok, "ru": []}}, **{k: {"kk": v[2], "ru": []} for k, v in notes.items() if v[1]})
        self.items.append(it)

    # ---------- тексеріс ----------
    def check(self, official_keys=None):
        errs = 0
        for x in self.items:
            assert x["key"] in "ABCD" and len(x["options"]) == 4, x["id"]
            assert set(x["distractor_notes"]) == set("ABCD") - {x["key"]}, x["id"]
            body = " ".join(next(t for t in self.texts if t["id"] == x["text_id"])["paragraphs"]).replace("**", "")
            groups = [("ok", x["evidence"])] + [(k, v) for k, v in x["distractor_evidence"].items() if v]
            for k, evs in groups:
                for e in evs:
                    for frag in [f.strip(" .") for f in strip_loc(e).split("...")]:
                        if frag and frag not in body: print("ДӘЛЕЛ ТАБЫЛМАДЫ:", x["id"], k, "|", frag); errs += 1
                    if self.ru and strip_loc(e) not in self.evid_ru: print("АУДАРМА ЖОҚ:", x["id"], k, "|", strip_loc(e)); errs += 1
                kw = x["keywords"].get(k, {"kk": [], "ru": []})
                kk_all = " ".join(strip_loc(e) for e in evs).lower()
                for w in kw["kk"]:
                    if w.lower() not in kk_all: print("КІЛТ СӨЗ (kk) ЖОҚ:", x["id"], k, "|", w); errs += 1
                if self.ru:
                    ru_all = " ".join(self.evid_ru.get(strip_loc(e), "") for e in evs).lower()
                    for w in kw["ru"]:
                        if w.lower() not in ru_all: print("КІЛТ СӨЗ (ru) ЖОҚ:", x["id"], k, "|", w); errs += 1
            if self.ru:
                assert x["explanation_ru"], x["id"]
                assert set(x["distractor_notes_ru"]) == set(x["distractor_notes"]), x["id"]
            if not x["fixed_order"]:
                kl = len(x["options"][x["key"]]); short = [l for l, o in x["options"].items() if l != x["key"] and len(o) < kl]
                if len(short) > 1: print("НҰСҚАЛАР ҚЫСҚА:", x["id"], {l: len(o) for l, o in x["options"].items()}, "кілт", kl); errs += 1
        for t in self.texts: assert t["source_note"], t["id"]
        assert [x["number"] for x in self.items] == list(range(1, 21)), [x["number"] for x in self.items]
        if official_keys: assert [x["key"] for x in self.items] == official_keys
        assert not errs, f"{errs} қате"

    # ---------- жазу ----------
    def write(self, json_name, doc_name, title):
        bank = {"bank_id": self.bank_id, "track": self.track, "source": self.source, "skills": SKILLS,
                "evidence_ru": self.evid_ru, "style_notes": [], "texts": self.texts, "items": self.items}
        (ROOT / json_name).write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding="utf-8")
        md = [f"# {title}", "", f"Дереккөз: {self.source}.", ""]
        for t in self.texts:
            md += [f"## {t['id'].split('-t')[1]}-мәтін" + (f": {t['title']}" if t["title"] else ""), "", f"*Дереккөз:* {t['source_note']}", ""]
            if t["id"] in self.changes: md += [f"*Редакциялық түзету:* {self.changes[t['id']]}", ""]
            for i, p in enumerate(t["paragraphs"], 1):
                md += [(f"{i}. " if t["numbered_paragraphs"] else "") + p.replace("**", ""), ""]
            for x in [x for x in self.items if x["text_id"] == t["id"]]:
                md += [f"### {x['number']}. " + x["stem"].replace("\n", "  \n"), ""]
                md += [f"- **{k})** {v}" + ("  ✅" if k == x["key"] else "") for k, v in x["options"].items()]
                md += ["", f"*Дағды:* {x['skill']} – {x['skill_name']} · *Деңгей:* {x['level']}", "", "**Мәтіндегі дәлел:**"]
                md += [f"> {e}" for e in x["evidence"]]
                md += ["", f"**Түсініктеме:** {x['explanation']}"] + ([f"*Орысша:* {x['explanation_ru']}"] if self.ru else []) + ["", "**Қалған нұсқалар неге қате:**"]
                for k in sorted(x["distractor_notes"]):
                    v = x["distractor_notes"][k]; ev = x["distractor_evidence"][k]
                    md.append(f"- {k}) {v[:1].upper()+v[1:]}" + (" Дәлел: «" + "», «".join(ev) + "»" if ev else ""))
                    if self.ru: md.append(f"  - *Орысша:* {x['distractor_notes_ru'][k]}")
                md += ["", "---", ""]
        (ROOT.parent / "docs" / doc_name).write_text("\n".join(md), encoding="utf-8")
        print(self.bank_id, "items", len(self.items), "keys", dict(Counter(x["key"] for x in self.items)),
              "skills", dict(Counter(x["skill"][0] for x in self.items)), "levels", dict(Counter(x["level"] for x in self.items)))
        for t in self.texts: print(" ", t["id"], len(" ".join(t["paragraphs"]).split()), "сөз")
