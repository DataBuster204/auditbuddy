# AuditBuddy — AI-Powered Financial Document Analyser

Built by [Olumide Daramola](https://olumidedaramola.dev) · Powered by GPT-4o-mini & LangChain

## What it does

AuditBuddy lets you upload any financial document — bank statements, audit reports, income statements, Excel sheets — and instantly get:

- **AI Summary** — plain-English breakdown of the key figures and financial position
- **Red Flag Detection** — forensic analysis that spots anomalies, risks, and concerns
- **Q&A Chat** — ask any question about the document and get a grounded answer
- **Audit Memo** — a board-ready formal audit observation memo in one click
- **Custom Reports** — describe the analysis you need and get a structured report

Supported file formats: PDF, Excel (.xlsx / .xls), Word (.docx)

---

## Tech Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| AI / LLM | GPT-4o-mini via LangChain |
| PDF Parsing | pdfplumber |
| Excel Parsing | pandas + openpyxl |
| Word Parsing | python-docx |
| Config | PyYAML (white-label ready) |
| Deployment | Streamlit Cloud |

---

## White-Label Ready

AuditBuddy is built with a white-label config system. Any company name, tagline, logo, and brand colours can be applied by editing a single `config.yaml` file — no code changes required.

---

## Live Demo

[https://auditbuddy-2fcgcbghkoeb97yyqqsfdk.streamlit.app](https://auditbuddy-2fcgcbghkoeb97yyqqsfdk.streamlit.app)

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/DataBuster204/auditbuddy.git
cd auditbuddy

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your OpenAI key
echo OPENAI_API_KEY=your-key-here > .env

# Run the app
streamlit run app.py
```

---

## Use Cases

- Accountants and auditors reviewing client financials
- Finance teams analysing monthly reports
- Businesses wanting a branded AI document tool
- Any professional who works with financial documents regularly

---

*Part of a 12-week AI portfolio build. See all projects at [olumidedaramola.dev](https://olumidedaramola.dev)*