"""Build the data used by the portfolio's interactive charts.

Reads real project outputs (no numbers are typed in by hand) and injects them
as JSON into site/portfolio.html between the VIZDATA markers.

Run with a Python that has `markdown` installed, e.g.
  ../05-typology-reports/.venv/bin/python tools/build_viz_data.py
"""
import csv
import json
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
SCR = ROOT / "01-sanctions-screening" / "output"
TM = ROOT / "03-transaction-monitoring"


def rows(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(v):
    try:
        f = float(v)
        return int(f) if f.is_integer() else f
    except (TypeError, ValueError):
        return v


# ---------- FC-01 sanctions screening ----------
tuning = {
    "with": [{k: num(v) for k, v in r.items()} for r in rows(SCR / "threshold_tuning.csv")],
    "without": [{k: num(v) for k, v in r.items()} for r in rows(SCR / "threshold_tuning_no_arabic.csv")],
}
screen = []
for r in rows(SCR / "screening_results.csv"):
    screen.append({
        "id": r["customer_id"], "name": r["name"], "type": r["type"],
        "alert": r["alert"] == "Y", "disp": r["disposition"] or "No alert",
        "score": num(r["top_score"]) if r["top_score"] else None,
        "matched": r["matched_name"], "entry": r["list_entry"], "list": r["list"],
        "programs": r["programs"], "hits": num(r["n_hits"]) if r["n_hits"] else 0,
        "why": r["disposition_reason"], "own": r["ownership_note"],
        "reasons": [x.strip() for x in (r["top_reasons"] or "").split("|") if x.strip()],
    })

# ---------- FC-02 transaction monitoring ----------
metrics = json.loads((TM / "outputs" / "metrics.json").read_text())
rules = [{k: num(v) for k, v in r.items()} for r in rows(TM / "outputs" / "rule_metrics.csv")]

disp_files = sorted((TM / "dispositions").glob("ALT-*.md"))
alerts = {r["alert_id"]: r for r in rows(TM / "outputs" / "alerts.csv")}
customers = {r["customer_id"]: r for r in rows(TM / "data" / "customers.csv")}
case_ids = {}
for p in disp_files:
    aid = p.name.split("_")[0]
    case_ids[aid] = p

wanted = {alerts[a]["customer_id"] for a in case_ids}
txns = {c: [] for c in wanted}
for r in rows(TM / "data" / "transactions.csv"):
    c = r["customer_id"]
    if c in txns:
        txns[c].append([r["txn_id"], r["timestamp"][:16], r["txn_type"], r["direction"],
                        round(float(r["amount"]), 2), r["counterparty_name"],
                        r["counterparty_country"], r["branch_state"]])

cases = []
for aid, p in case_ids.items():
    a = alerts[aid]
    c = customers[a["customer_id"]]
    md = p.read_text(encoding="utf-8")
    title = md.splitlines()[0].lstrip("# ").strip()
    m = re.search(r"\| \*\*Decision\*\* \| \*\*(.+?)\*\* \|", md)
    body = "\n".join(md.splitlines()[1:])
    body = re.sub(r"\.\./04-sar-narratives/", "", body)
    html = markdown.markdown(body, extensions=["tables"])
    cases.append({
        "alert": aid, "rule": a["rule_id"], "ruleName": a["rule_name"], "date": a["alert_date"][:10],
        "amount": float(a["amount_involved"] or 0), "details": a["details"],
        "flagged": [t for t in a["txn_ids"].split(";") if t],
        "outcome": "Escalate" if "escalate" in p.name else "Close",
        "decision": m.group(1) if m else "", "title": title, "html": html,
        "customer": {k: c[k] for k in ["customer_id", "name", "customer_type", "occupation", "age",
                                       "nationality", "home_state", "account_open_date",
                                       "expected_monthly_volume_usd", "expected_cash_activity",
                                       "expected_international", "expected_countries",
                                       "kyc_risk_rating", "pep_flag"]},
        "txns": sorted(txns[a["customer_id"]], key=lambda t: t[1]),
    })
cases.sort(key=lambda x: (x["outcome"] != "Escalate", x["alert"]))

data = {
    "tuning": tuning, "screen": screen,
    "tm": {"overall": metrics["overall"], "iforest": metrics["isolation_forest"],
           "presets": metrics["presets"], "pak": metrics.get("precision_at_k", []),
           "rules": rules},
    "cases": cases,
}

page = SITE / "portfolio.html"
s = page.read_text(encoding="utf-8")
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
new = f'<script id="vizdata" type="application/json">{blob}</script>'
s, n = re.subn(r'<script id="vizdata" type="application/json">.*?</script>', lambda _: new, s, flags=re.S)
if n != 1:
    raise SystemExit("VIZDATA marker not found in portfolio.html")
page.write_text(s, encoding="utf-8")
print(f"Injected {len(blob)/1024:.0f} KB: {len(screen)} screened customers, {len(cases)} cases, "
      f"{sum(len(c['txns']) for c in cases)} transactions")
