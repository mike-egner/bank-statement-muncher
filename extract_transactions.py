import pdfplumber
import pandas as pd
import re
import sys
from datetime import datetime
from categories_rules import rules

def categorize(description):
    desc = description.lower().strip()

    # Special rule: starts with #
    if desc.startswith("#"):
        return "Bank Fees"

    for keyword, category in rules.items():
        if keyword in desc:
            return category
    return "Uncategorized"


pdf_path = sys.argv[1] if len(sys.argv) > 1 else "PRIVATE_CLIENTS_CREDIT_CARD_109.pdf"

transactions = []
unmatched_lines = []

# Regexes
statement_date_regex = re.compile(r"Statement Date\s*(\d{2} \w{3} \d{4})")
line_regex = re.compile(r"^(\d{2} \w{3}) (.+?) (\d{1,3}(?:[ \xa0]?\d{3})*\.\d{2})(?: ?Cr)?$")

statement_year = None
statement_month = None

with pdfplumber.open(pdf_path) as pdf:
    # Step 1: Extract the statement date
    first_page_text = pdf.pages[0].extract_text()
    match = statement_date_regex.search(first_page_text)
    if match:
        full_date_str = match.group(1)  # e.g., "08 Jan 2024"
        parsed_statement_date = datetime.strptime(full_date_str, "%d %b %Y")
        statement_year = parsed_statement_date.year
        statement_month = parsed_statement_date.month
    else:
        print("⚠️ Could not detect statement date. Defaulting to March 2024.")
        statement_year = 2024
        statement_month = 3

    # Step 2: Parse all pages
    for page in pdf.pages:
        text = page.extract_text()
        lines = text.split('\n')
        for line in lines:
            stripped_line = line.strip()
            match = line_regex.match(stripped_line)
            if match:
                date_str, description, amount_str = match.groups()
                is_credit = stripped_line.endswith("Cr")

                # Clean amount
                amount_str = amount_str.replace(" ", "").replace("\xa0", "")
                amount = float(amount_str)
                if is_credit:
                    amount *= -1

                # Parse transaction month
                try:
                    dt_temp = datetime.strptime(f"{date_str} {statement_year}", "%d %b %Y")
                    transaction_month = dt_temp.month
                    transaction_year = statement_year

                    # Adjust year backwards if month loops (e.g., Dec on Jan statement)
                    if transaction_month > statement_month:
                        transaction_year -= 1

                    date = datetime.strptime(f"{date_str} {transaction_year}", "%d %b %Y").date()
                except ValueError:
                    date = date_str  # Fallback

                transactions.append({
                    "date": date,
                    "description": description.strip(),
                    "amount": round(amount, 2),
                    "category": categorize(description.strip()),
                    "amount_review": ""
                })
            else:
                unmatched_lines.append(stripped_line)

# Save to CSV
df = pd.DataFrame(transactions)

# --- Extract balances from the first page ---
opening_balance_match = re.search(r"Opening Balance ([\d\s]+\.\d{2})", first_page_text)
closing_balance_match = re.search(r"Closing Balance ([\d\s]+\.\d{2})", first_page_text)

if opening_balance_match and closing_balance_match:
    opening_balance = float(opening_balance_match.group(1).replace(" ", ""))
    closing_balance = float(closing_balance_match.group(1).replace(" ", ""))
    
    net_change = closing_balance - opening_balance
    total_txns = df['amount'].sum()

    print(f"\n📘 Opening Balance: R{opening_balance:,.2f}")
    print(f"📙 Closing Balance: R{closing_balance:,.2f}")
    print(f"📊 Net Change: R{net_change:,.2f}")
    print(f"💰 Total value of transactions: R{total_txns:,.2f}")

    if abs(total_txns - net_change) < 0.01:
        print("✅ Reconciles")
    else:
        print("❌ Does not reconcile")
else:
    print("⚠️ Could not find Opening or Closing Balance for reconciliation.")

df.to_csv("extracted_transactions.csv", index=False)

print(f"\n✅ Done! Extracted {len(df)} transactions.")
print(f"📅 Statement date: {statement_month}/{statement_year}")
print(f"💰 Total value of transactions: R{df['amount'].sum():,.2f}")
print("📄 Output written to extracted_transactions.csv")

if unmatched_lines:
    with open("unmatched_lines.txt", "w", encoding="utf-8") as f:
        for line in unmatched_lines:
            f.write(line + "\n")
    print(f"🧐 {len(unmatched_lines)} unmatched lines. See unmatched_lines.txt.")
else:
    print("✅ All lines matched successfully.")

summary = df.groupby("category")["amount"].sum().sort_values(ascending=False)
print("📂 Category summary:")
print(summary.to_string())

