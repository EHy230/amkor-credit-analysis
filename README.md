# Amkor Technology Credit Analysis and AI Financial Spreading

By Eisen Hy, October 2026. Tools: Excel, Python, Claude API, Google Colab.

This project looks at a hypothetical $100 million, three-year term loan to Amkor Technology (NASDAQ: AMKR) from a lender's point of view. Amkor is a U.S.-based semiconductor packaging and test company with most of its operations in Asia. Using its public filings, I built an Excel credit model, wrote a two-page credit memo, and built a Python pipeline that uses the Claude API to pull figures out of the 10-K financial statements.

Start with the memo: [`memo/Amkor_Credit_Memo_Eisen_Hy.pdf`](memo/Amkor_Credit_Memo_Eisen_Hy.pdf).

## Recommendation

Defer the loan until Amkor shows a fully funded plan for its expansion spending.

Amkor's leverage is low. Gross debt was about 1.9x the EBITDA proxy for the twelve months to June 2026, and earnings cover interest many times over. The concern is cash. The company guides to $2.5–3.0 billion of capital spending in 2026, and free cash flow (operating cash flow minus capex) was about −$172 million over those twelve months. Under my base-case assumptions, liquid assets fall below a $500 million minimum reserve in 2028, and the cumulative funding gap reaches $3.02 billion by 2029. In the combined revenue and interest-rate stress case, the gap grows to $4.24 billion. Making the loan smaller would not close that gap, so the memo asks for a funded expansion plan and verified repayment sources before any commitment.

## What's in this repository

| Folder / file | Contents |
| --- | --- |
| `memo/` | Two-page credit memo (PDF) |
| `model/` | Excel credit model: historical spread, June 2026 update, cash-flow forecast to 2029, debt schedule, the proposed loan, and five scenarios |
| `code/` | Python pipeline, Google Colab notebook, offline tests, and the benchmark used to score the AI |
| `results/` | Run logs, evaluation results, accounting checks, and my review and approval of every extracted value |
| `sources/source_manifest.csv` | Links to the SEC filings used |

## Credit model

Pick a case from the dropdown on the Assumptions sheet (cell D7): **Base**, **Revenue −20%**, **Rates +200bp**, **Combined stress** or **Severe funding**. The whole forecast recalculates from that one cell, and reported actuals never change.

The model tracks gross debt / EBITDA proxy, EBITDA / cash interest, debt service coverage using maintenance capex and using total capex, and liquid assets against a $500 million minimum reserve. Future capex, the maintenance share of capex (30%), customer advance timing and the loan terms are my assumptions and are labeled in the workbook.

## AI financial spreading

1. Python pulls the text of five statement pages from the FY2024 and FY2025 10-Ks: income statement, two balance sheets, cash flow statement, and cash interest paid.
2. Claude reads one page per call (six calls in total) and returns each requested value as JSON, with the page number, the line label and the exact row it took the number from.
3. Python checks every value. The quoted row has to appear on the page, the number has to sit in the right year column, the units have to be thousands, and 36 accounting checks have to pass (for example, assets = liabilities + equity, and the cash roll-forward).
4. The values are scored against the hand-entered spread in the Excel model (the Raw Spread sheet). That benchmark is never sent to Claude.
5. Every value was checked against the 10-K pages and approved by Eisen before it could be imported.

58 fields × 3 fiscal years (2023–2025) = 174 values.

| | Claude Sonnet 5.5 | Claude Haiku 4.5 |
| --- | ---: | ---: |
| Values matching the benchmark | 174 of 174 | 171 of 174 |
| Values passing all source checks | 174 | 168 |
| Accounting checks passed | 36 of 36 | 33 of 36 |
| Estimated API cost | $0.30 | $0.13 |
| Run time | 2.1 minutes | 2.1 minutes |

Haiku left three values blank where the 10-K prints a dash (meaning zero). On three parent-equity rows it changed a curly apostrophe to a straight one, so its quotes did not match the page exactly; the amounts on those rows were correct.

I used the Sonnet run. All 174 values were approved by Eisen on October 2, 2026, after a 41-minute source review against the 10-K pages. I did not time a fully manual spread, so I am not claiming a time saving.

## Run it yourself

1. Open `code/Amkor_AI_Financial_Spreading.ipynb` in Google Colab.
2. Run the cells from the top. The notebook downloads the 10-K PDFs (or lets you upload them), checks the pages and runs 12 offline tests. None of these steps call the API.
3. For a live run, add your Anthropic API key as a Colab Secret named `ANTHROPIC_API_KEY` and set `RUN_LIVE_API = True`. One Sonnet run costs about $0.30.

`code/README.md` has more detail, including how to run it with local Python. The 10-K PDFs are not stored here; the links are in `sources/source_manifest.csv`.

## Scope

- This is an independent study using public data. It is not work done for a bank, and no real loan was approved or declined.
- Forecast inputs are my assumptions. EBITDA here is an operating proxy, not a covenant definition, and the model does not estimate a probability of default.
- The AI test covers one company and three fiscal years. Testing more companies would be needed before relying on it more widely.
- The June 2026 interim figures and debt-note details were entered by hand.

## Sources

- [Amkor FY2025 10-K](https://www.sec.gov/Archives/edgar/data/1047127/000104712726000014/amkr-20251231.htm)
- [Amkor FY2024 10-K](https://www.sec.gov/Archives/edgar/data/1047127/000104712725000030/amkr-20241231.htm)
- [Amkor Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1047127/000104712726000046/amkr-20260630.htm)
- [Amkor Q2 2026 earnings release](https://ir.amkor.com/news-releases/news-release-details/amkor-technology-reports-financial-results-second-quarter-2026)
- [Arizona phase-2 announcement, September 8, 2026](https://ir.amkor.com/news-releases/news-release-details/amkor-technology-announces-phase-2-arizona-advanced-packaging)
