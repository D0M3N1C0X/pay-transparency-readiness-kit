"""
Article 7: the answer to a worker who asks how their pay compares.

A worker can ask, in writing, for their own pay level and the average pay levels, broken down by sex, of the
workers doing the same work or work of equal value; the employer answers in writing within two months (Directive
2023/970, Art. 7(1) and (4)). The categories the screen uses are those workers, so the answer comes from the same
data. Where one sex has fewer than MIN_CELL workers in the category, an average could reveal a colleague's pay:
the letter says so and names who can still see them where national law uses the option in Article 12(3).

answer() gives the figures; letter() writes the reply in English or Italian. docs/article7-response.md holds two
generated examples, one with the figures and one held back.
"""
from datetime import date, timedelta

import pandas as pd

from config import ENTITIES, MIN_CELL, ROOT

EXAMPLES = ROOT / "docs" / "article7-response.md"
ANSWER_DAYS = 61        # "no later than two months": the earliest date two months can end, kept safe


def answer(w: pd.DataFrame, worker_id: str, received: date) -> dict:
    me = w.loc[w["worker_id"] == worker_id]
    if len(me) != 1:
        raise KeyError(f"{worker_id}: not one worker in the payroll")
    me = me.iloc[0]
    peers = w[(w["country"] == me["country"]) & (w["category"] == me["category"])]
    f, m = peers[peers["gender"] == "F"], peers[peers["gender"] == "M"]
    shown = min(len(f), len(m)) >= MIN_CELL
    out = {"worker_id": worker_id, "employer": ENTITIES[me["country"]], "category": me["category"],
           "received": received, "answer_by": received + timedelta(days=ANSWER_DAYS),
           "own_annual": float(me["total_pay"]), "own_hourly": float(me["hourly_total"]),
           "women": len(f), "men": len(m), "shown": shown}
    if shown:
        out |= {"women_annual": float(f["total_pay"].mean()), "men_annual": float(m["total_pay"].mean()),
                "women_hourly": float(f["hourly_total"].mean()), "men_hourly": float(m["hourly_total"].mean())}
    return out


def _eur(x: float, lang: str) -> str:
    s = f"{x:,.2f}"
    return "€ " + s.replace(",", "X").replace(".", ",").replace("X", ".") if lang == "it" else "€" + s


def _day(d: date, lang: str) -> str:
    months = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre",
              "ottobre", "novembre", "dicembre"]
    if lang == "it":
        return f"{'1°' if d.day == 1 else d.day} {months[d.month - 1]} {d.year}"
    return f"{d.day} {d:%B %Y}"


def letter(a: dict, lang: str = "en") -> str:
    e, d = (lambda x: _eur(x, lang)), (lambda x: _day(x, lang))
    if lang == "it":
        lines = [f"**Oggetto:** risposta alla richiesta di informazioni retributive ricevuta il {d(a['received'])}",
                 "",
                 f"Gentile collega ({a['worker_id']}),",
                 "",
                 "in risposta alla sua richiesta, ai sensi dell'articolo 7 della Direttiva (UE) 2023/970 come "
                 "recepito nel diritto nazionale, le comunichiamo quanto segue.",
                 "",
                 f"**Il suo livello retributivo.** Retribuzione lorda annua {e(a['own_annual'])}; retribuzione lorda "
                 f"oraria {e(a['own_hourly'])}.",
                 "",
                 f"**La sua categoria di lavoratori.** {a['category']} presso {a['employer']}: le persone che "
                 "svolgono lo stesso lavoro o un lavoro di pari valore secondo la valutazione dei ruoli, "
                 f"{a['women']} donne e {a['men']} uomini."]
        if a["shown"]:
            lines += ["",
                      "| | Donne | Uomini |", "|---|---:|---:|",
                      f"| Retribuzione lorda annua media | {e(a['women_annual'])} | {e(a['men_annual'])} |",
                      f"| Retribuzione lorda oraria media | {e(a['women_hourly'])} | {e(a['men_hourly'])} |"]
        else:
            lines += ["",
                      f"Nella sua categoria uno dei due sessi conta meno di {MIN_CELL} persone: una media "
                      "renderebbe riconoscibile la retribuzione di singoli colleghi, e per questo non la indichiamo "
                      "qui. Dove la legge nazionale lo prevede, le medie restano accessibili ai rappresentanti dei "
                      "lavoratori, all'ispettorato del lavoro o all'organismo per la parità, che possono valutarle "
                      "per suo conto (articolo 12, paragrafo 3, della Direttiva)."]
        lines += ["",
                  "La retribuzione comprende la paga base e tutte le componenti complementari e variabili; la "
                  "retribuzione oraria è calcolata sulle ore contrattuali. Può chiedere chiarimenti o dettagli "
                  "aggiuntivi, e ha diritto a ricevere questa risposta entro due mesi dalla richiesta "
                  f"(entro il {d(a['answer_by'])}). Nessuna clausola contrattuale le impedisce di rendere nota la "
                  "propria retribuzione per far valere la parità retributiva.",
                  "", "Cordiali saluti,", "", "Ufficio Risorse Umane"]
    else:
        lines = [f"**Subject:** your request for pay information, received {d(a['received'])}",
                 "",
                 f"Dear colleague ({a['worker_id']}),",
                 "",
                 "In answer to your request under Article 7 of Directive (EU) 2023/970, as transposed into national "
                 "law, here is the information you asked for.",
                 "",
                 f"**Your pay level.** Gross annual pay {e(a['own_annual'])}; gross hourly pay {e(a['own_hourly'])}.",
                 "",
                 f"**Your category of workers.** {a['category']} at {a['employer']}: the workers doing the same work "
                 f"or work of equal value under the job evaluation, {a['women']} women and {a['men']} men."]
        if a["shown"]:
            lines += ["",
                      "| | Women | Men |", "|---|---:|---:|",
                      f"| Average gross annual pay | {e(a['women_annual'])} | {e(a['men_annual'])} |",
                      f"| Average gross hourly pay | {e(a['women_hourly'])} | {e(a['men_hourly'])} |"]
        else:
            lines += ["",
                      f"In your category one sex has fewer than {MIN_CELL} workers, so an average would reveal "
                      "individual colleagues' pay, so it is not given here. Where national law provides for it, the "
                      "averages remain available to workers' representatives, the labour inspectorate or the "
                      "equality body, who can assess them on your behalf (Article 12(3) of the Directive)."]
        lines += ["",
                  "Pay includes base pay and every complementary and variable component; hourly pay is computed on "
                  "contractual hours. You can ask for clarification or further detail, and you are entitled to this "
                  f"answer within two months of your request (by {d(a['answer_by'])}). No term of your contract "
                  "prevents you from disclosing your own pay to enforce equal pay.",
                  "", "Kind regards,", "", "Human Resources"]
    return "\n".join(lines) + "\n"


def write_examples(w: pd.DataFrame, received: date = date(2027, 7, 1)) -> None:
    """Two letters on the sample payroll: a worker in a category with figures, and one where they are held back."""
    counts = w.groupby(["country", "category", "gender"]).size().unstack(fill_value=0)
    small = counts[counts.min(axis=1) < MIN_CELL].index[0]
    big = ("IT", "Cat B")
    pick = lambda key: sorted(w.loc[(w["country"] == key[0]) & (w["category"] == key[1]), "worker_id"])[0]
    shown, held = answer(w, pick(big), received), answer(w, pick(small), received)
    text = ["# Article 7: answering a worker's request for pay information",
            "",
            "Generated by `src/article7.py` from the synthetic payroll, so the figures are the kit's own. A worker "
            "asks in writing for their pay level and the average pay levels, by sex, of the workers doing the same "
            "work or work of equal value; the employer answers in writing within two months (Directive 2023/970, "
            "Art. 7(1) and (4); verification register V06). The category is the one the Article 10 screen uses.",
            "",
            "Before sending: check the worker's figures against payroll, have the categories agreed with workers' "
            "representatives, and adapt the legal references to the national act. The letter states the right to "
            "disclose one's own pay (Art. 7(5)).",
            "",
            f"## A category with figures ({shown['employer']}, {shown['category']}), in Italian",
            "", letter(shown, "it"),
            "## The same letter in English", "", letter(shown, "en"),
            f"## A category where the averages are held back ({held['employer']}, {held['category']})",
            "", letter(held, "en")]
    EXAMPLES.write_text("\n".join(text), encoding="utf-8")
