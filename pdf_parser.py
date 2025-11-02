import re
from typing import Dict, Optional, List
from dateutil import parser as dateparser
import pdfplumber


ISSUERS = ["chase", "bank of america", "citi", "american express", "capital one"]


def extract_text_from_pdf(path: str) -> str:
    texts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            try:
                texts.append(page.extract_text() or "")
            except Exception:
                # fall back to empty for a page if extraction fails
                texts.append("")
    return "\n".join(texts)


def detect_issuer(text: str) -> Optional[str]:
    t = text.lower()
    for issuer in ISSUERS:
        if issuer in t:
            return issuer
    # fallback heuristics
    if "amex" in t or "american express" in t:
        return "american express"
    return None


def first_match(regexes, text):
    for rx in regexes:
        m = re.search(rx, text, re.IGNORECASE | re.DOTALL)
        if m:
            return m
    return None


def parse_amount(s: str) -> Optional[float]:
    if not s:
        return None
    s = s.replace(',', '')
    m = re.search(r"[-+]?[\d]+(?:\.\d{1,2})?", s)
    if not m:
        return None
    try:
        return float(m.group())
    except Exception:
        return None


def parse_date(s: str) -> Optional[str]:
    if not s:
        return None
    try:
        d = dateparser.parse(s, fuzzy=True)
        return d.date().isoformat()
    except Exception:
        return None


def extract_fields_from_text(text: str) -> Dict[str, Optional[str]]:
    # Common fallback regexes
    res = {
        "issuer": None,
        "cardholder_name": None,
        "card_last4": None,
        "statement_period": None,
        "payment_due_date": None,
        "new_balance": None,
    }

    issuer = detect_issuer(text)
    res["issuer"] = issuer

    # Card last 4: common patterns like 'ending in 1234' or '**** 1234' or 'Account ...1234'
    last4_rx = [
        r"ending in\s*(\d{4})", 
        r"ending:\s*(\d{4})", 
        r"\*{2,}\s*(\d{4})", 
        r"(\d{4})\s*\)",
        r"Account\s+\*{3,}(\d{4})",
        r"card\s+ending\s+in\s+(\d{4})",
        r"x+\s*(\d{4})",
    ]
    m = first_match(last4_rx, text)
    if m:
        res["card_last4"] = m.group(1)

    # Cardholder name: look for 'Account holder', 'Account summary for' or line near the top before address lines
    name_rx = [
        r"Account holder[:\s]*([A-Z][A-Za-z\- ,\.]+)",
        r"Account summary for[:\s]*([A-Z][A-Za-z\- ,\.]+)",
        r"Statement for[:\s]*([A-Z][A-Za-z\- ,\.]+)",
        r"Cardholder[:\s]*([A-Z][A-Za-z\- ,\.]+)",
        r"Member Name[:\s]*([A-Z][A-Za-z\- ,\.]+)",
    ]
    m = first_match(name_rx, text)
    if m:
        name = m.group(1).strip()
        # Clean up common noise
        name = re.sub(r'\s+(LLC|INC|CORP|LTD).*', '', name, flags=re.IGNORECASE)
        res["cardholder_name"] = name[:50]  # Limit length
    else:
        # fallback: take first line with two words and capital letters near top
        top_lines = text.strip().splitlines()[:15]
        for line in top_lines:
            line = line.strip()
            if re.match(r"^[A-Z][a-z]+\s+[A-Z][a-z]+", line) and len(line) < 50:
                res["cardholder_name"] = line
                break

    # Statement period / billing cycle: common labels like 'Statement period' or 'Statement date'
    period_rx = [
        r"Statement period[:\s]*([A-Za-z0-9 ,\-/]+)",
        r"Billing period[:\s]*([A-Za-z0-9 ,\-/]+)",
        r"Statement closing date[:\s]*([A-Za-z0-9 ,\-/]+)",
        r"Billing cycle[:\s]*([A-Za-z0-9 ,\-/]+)",
    ]
    m = first_match(period_rx, text)
    if m:
        res["statement_period"] = m.group(1).strip()[:100]
    else:
        # try to capture 'From <date> to <date>' or '<date> - <date>'
        m = re.search(r"From\s+([A-Za-z0-9,\s]+?)\s+to\s+([A-Za-z0-9,\s]+?)\b", text, re.IGNORECASE)
        if m:
            res["statement_period"] = f"{m.group(1).strip()} to {m.group(2).strip()}"
        else:
            m = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4})\s*-\s*(\d{1,2}/\d{1,2}/\d{2,4})", text)
            if m:
                res["statement_period"] = f"{m.group(1)} to {m.group(2)}"

    # Payment due date
    due_rx = [
        r"Payment due date[:\s]*([A-Za-z0-9 ,/\-]+)",
        r"Due date[:\s]*([A-Za-z0-9 ,/\-]+)",
        r"Payment due[:\s]*([A-Za-z0-9 ,/\-]+)",
        r"Pay by[:\s]*([A-Za-z0-9 ,/\-]+)",
    ]
    m = first_match(due_rx, text)
    if m:
        res["payment_due_date"] = parse_date(m.group(1))

    # New balance / Total balance
    balance_rx = [
        r"New balance[:\s]*\$?\s*([\d,]+\.\d{2})",
        r"New account balance[:\s]*\$?\s*([\d,]+\.\d{2})",
        r"Current balance[:\s]*\$?\s*([\d,]+\.\d{2})",
        r"Total balance[:\s]*\$?\s*([\d,]+\.\d{2})",
        r"Amount due[:\s]*\$?\s*([\d,]+\.\d{2})",
        r"Total due[:\s]*\$?\s*([\d,]+\.\d{2})",
    ]
    m = first_match(balance_rx, text)
    if m:
        res["new_balance"] = f"${m.group(1)}"

    # Issuer-specific tweaks
    if issuer == "chase":
        # Chase often shows 'Total due' or 'New balance' near the top
        if not res["new_balance"]:
            m = first_match([r"Total due[:\s]*\$?\s*([\d,]+\.\d{2})", r"Amount due[:\s]*\$?\s*([\d,]+\.\d{2})"], text)
            if m:
                res["new_balance"] = f"${m.group(1)}"
        # Chase sometimes shows 'Statement closing date' or 'Statement period'
        if not res["statement_period"]:
            m = first_match([r"Statement closing date[:\s]*([A-Za-z0-9 ,/\-]+)", r"Statement period[:\s]*([A-Za-z0-9 ,\-/]+)"], text)
            if m:
                res["statement_period"] = m.group(1).strip()

    elif issuer == "american express":
        # Amex uses 'Account ending in' label
        if not res["card_last4"]:
            m = re.search(r"Account ending in[:\s]*(\d{4})", text, re.IGNORECASE)
            if m:
                res["card_last4"] = m.group(1)
        if not res["payment_due_date"]:
            m = first_match([r"Payment due[:\s]*([A-Za-z0-9 ,/\-]+)", r"Due date[:\s]*([A-Za-z0-9 ,/\-]+)"], text)
            if m:
                res["payment_due_date"] = parse_date(m.group(1))
    
    elif issuer == "bank of america":
        # BoA specific patterns
        if not res["card_last4"]:
            m = re.search(r"Account number ending in[:\s]*(\d{4})", text, re.IGNORECASE)
            if m:
                res["card_last4"] = m.group(1)
    
    elif issuer == "citi":
        # Citi specific patterns
        if not res["new_balance"]:
            m = first_match([r"New balance[:\s]*\$?\s*([\d,]+\.\d{2})"], text)
            if m:
                res["new_balance"] = f"${m.group(1)}"
    
    elif issuer == "capital one":
        # Capital One specific patterns
        if not res["card_last4"]:
            m = re.search(r"Account ending in[:\s]*(\d{4})", text, re.IGNORECASE)
            if m:
                res["card_last4"] = m.group(1)

    # Generic fallback parsing for dates and balances if not found
    if not res["payment_due_date"]:
        # find first plausible date labeled near 'Due'
        m = re.search(r"Due[:\s]*([A-Za-z0-9,\-/]+)", text, re.IGNORECASE)
        if m:
            res["payment_due_date"] = parse_date(m.group(1))

    if not res["new_balance"]:
        # search for a currency amount near keywords 'Balance' or 'New Balance'
        m = re.search(r"(New balance|Current balance|Total balance|Amount due|New account balance)[:\s\$]*\s*([\d,]+\.\d{2})", text, re.IGNORECASE)
        if m:
            res["new_balance"] = f"${m.group(2)}"

    return res


def parse_pdf(path: str) -> Dict[str, Optional[str]]:
    text = extract_text_from_pdf(path)
    return extract_fields_from_text(text)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        out = parse_pdf(sys.argv[1])
        for k, v in out.items():
            print(f"{k}: {v}")
    else:
        print("Usage: python pdf_parser.py <file.pdf>")
