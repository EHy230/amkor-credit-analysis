# Amkor AI financial spreading

Python and Google Colab workflow for 58 annual financial-statement fields across FY2023-FY2025 (174 field/year observations). It complements the existing Excel credit model; it does not make a lending decision or overwrite that model.

## Start in Colab

1. Visit https://colab.research.google.com/ and choose **File > Upload notebook**. Open `Amkor_AI_Financial_Spreading.ipynb`.
2. Run the installation and definitions cells. No API key is needed yet.
3. Run the PDF-download cell. If blocked, use the upload cell to select `Amkor_FY2025_10K.pdf` and `Amkor_FY2024_10K.pdf` from the project's `sources` folder. The notebook is self-contained: you do not need to upload the Python code or benchmark separately.
4. Run the source checks and offline tests. These are engineering checks, **not Claude extraction results**.
5. Add a Colab Secret named `ANTHROPIC_API_KEY` using the key icon in the left sidebar. Enable notebook access for that secret. Never paste a key into code, screenshots, GitHub or chat.
6. Confirm your Anthropic account has API credits and confirm the model and price settings. Set `RUN_LIVE_API = True` in the live-run cell when ready. Run that cell once. It makes six streamed API calls; automatic retries are disabled. Re-running the cell creates another paid run.
7. Run evaluation and export. Download the results ZIP. Inspect `ai_spread_staging.csv`, `human_review.csv`, `reconciliation_checks.csv`, `evaluation_summary.json`, and `run_log.json`.
8. Open `human_review.csv` in Excel. Check the source row, year, unit, sign and field meaning. Set `reviewer_decision` to `Approve` or `Reject`, and enter a reviewer name and source-review note. Save as CSV. Upload the reviewed CSV using the notebook's optional approval cell. Failed machine checks cannot be approved through this shortcut; correct the extracted record with a separate documented amendment and re-evaluate first.

An approved CSV is a staged import file. It does not change the Excel workbook automatically; any update to the workbook is made by hand after checking the results.

## Local Python use

Install `requirements.txt`, set `ANTHROPIC_API_KEY` privately in your environment, then run:

```text
python credit_spreading.py --sources ../sources --benchmark benchmark_verified.json --output ../results/live_run_001 --confirm-paid
python -m unittest -v test_credit_spreading
```

Use a fresh output folder for each live run. No paid calls occur on import or during unit tests.

## Source and accounting scope

- FY2025 10-K: PDF page 54 / printed 53 income statement, PDF 56 / printed 55 balance sheet, PDF 58 / printed 57 cash flow, PDF 59 / printed 58 cash-interest supplement.
- FY2024 10-K: PDF 56 / printed 55 supplies the 2023 balance sheet. Latest available comparative statements take precedence. Earlier FY2023 PDF is a cross-check, not required for this run.
- SEC filings are authoritative references. Existing local copies are AnnualReports.com mirror PDFs; report identity, financial page markers and units are checked. Each run records PDF SHA-256 hashes.
- The June 2026 interim statements, debt-note instrument details, maturity schedule, capex guidance and forecast assumptions already in Excel are **outside this first AI evaluation scope** and remain manually verified. No automatic refresh of those inputs is claimed.
- Amounts remain signed as printed in the raw AI response. Python converts USD thousands to millions. Specified outflows and the NCI deduction use positive magnitudes to match the existing model. Net investing/financing cash flows and other income/expense retain their sign.
- Missing values stay missing; only explicit printed dashes on a verified row/year are zero. Cash-flow cash includes restricted cash; available cash does not. GAAP debt carrying value is not gross debt principal. EBITDA remains an Excel analyst proxy, not a directly extracted reported line.
- `benchmark_verified.json` is derived from the independently checked workbook Raw Spread, with workbook cell references and file hash. It is never supplied to Claude. Schema compliance and exact quote matching do not prove semantic correctness, so all 174 records require human review.

## Evaluation and honest portfolio claims

Numeric accuracy uses **all 174 planned observations**, including missing fields in the denominator. The evaluation also reports coverage, source/year/unit/evidence checks and accounting reconciliations. This is a one-company pilot with repeated comparative disclosures, not an independent generalization test. Add another issuer and a held-out reporting period before making broader reliability claims.

API responses, token counts, returned model, wall time and estimated token cost are preserved. Default model is Claude Sonnet 5.5 at reference prices of $2/$10 per million input/output tokens (Haiku 4.5 comparison run: $1/$5), with a 32,000 output-token cap per call; verify current pricing before a paid run. Cost is an estimate, not an invoice. No prompt caching, web-search tools or retries are requested. Failed API runs may still be billed, and a transport failure may prevent recovering token counts; check provider billing.

Manual baseline and analyst review time start as **not measured**. Measure at least two comparable paired trials, including setup, corrections and review, before claiming time savings. No live extraction accuracy or productivity result is included in the delivered notebook.

## Design and controls

PDF text is treated as untrusted data. The model has no tool access. Output uses a constrained JSON schema; local checks reject unexpected/duplicate keys, fabricated page quotes, wrong columns, units, truncation and missing amounts. CSV text is escaped to reduce Excel formula-injection risk. The pipeline retains raw responses and never writes API keys or modifies the Excel credit workbook.

## Primary technical references

- [Anthropic structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [Anthropic Python Messages API](https://platform.claude.com/docs/en/api/python/messages/create)
- [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [pypdf text extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)
