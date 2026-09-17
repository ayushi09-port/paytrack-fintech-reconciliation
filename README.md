# 💳 PayTrack - QR Payment Record & Reconciliation System

PayTrack is a lightweight, offline-first payment reconciliation and management system designed to help local merchants and small businesses track, audit, and analyze incoming UPI and QR code payments.

*Developed as part of the Blackbucks-NASSCOM FinTech Virtual Internship.*

---

## 🚀 Features

* **Instant Transaction Recording:** Dedicated form with automatic timestamping to record payment references, amounts, customer identifiers, and status.
* **Duplicate Entry Prevention:** Built-in SQLite database constraints to block duplicate Reference IDs and ensure data integrity.
* **Audit Ledger & Search:** Real-time search across Reference IDs, Customer Names, or Order IDs, alongside status-based filtering.
* **Record Management:** Easily update payment details or permanently delete erroneous entries.
* **Daily Metrics:** Real-time totals for verified daily revenue, total entries, pending checks, and mismatched records.
* **Visual Analytics:** Interactive Plotly charts showing daily collection trends, UPI app distribution shares, and payment status breakdowns.

---

## 🛠️ Project Structure

```text
paytrack/
│
├── app.py           # Main Streamlit UI, navigation tabs, and dashboard layout
├── database.py      # SQLite database initialization, schema, and CRUD functions
├── requirements.txt # Python package dependencies
└── README.md        # Project setup and running instructions
