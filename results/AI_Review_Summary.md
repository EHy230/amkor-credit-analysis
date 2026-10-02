# AI spreading results and review

Runs and review completed October 2, 2026. The pilot covers 58 fields across FY2023–FY2025, or 174 field/year values. Each model was run once, with six API calls per run.

## Results

| Measure | Claude Sonnet 5.5 | Claude Haiku 4.5 |
| --- | ---: | ---: |
| Values matching the benchmark | 174 / 174 (100%) | 171 / 174 (98.3%) |
| Values passing number and source checks | 174 / 174 | 168 / 174 |
| Accounting checks | 36 pass | 33 pass, 3 could not run |
| Missing values | 0 | 3 |
| Estimated API cost | $0.2960 | $0.1311 |
| Run time | 127.35 seconds | 124.50 seconds |
| Values approved by Eisen | 174 | not reviewed |

Costs are estimates from token counts and the published prices entered for each run, not a billing invoice. Both runs together cost about $0.43. Neither run was cut off, and the model names returned by the API are saved in each `run_log.json`.

## Review and approval

The Sonnet run was selected for review. Eisen checked all 174 values against the 10-K pages (line, year column, sign and units) and approved every one on October 2, 2026, with no amounts changed. The source review took 41 minutes. The approval step in the pipeline confirmed that no staged amount changed during review.

- `sonnet-5-5_live_.../human_review_returned.csv`: Eisen's decision and note for each value.
- `sonnet-5-5_live_.../human_approved_import.csv`: the 174 approved values.
- `review_2026-10-02/approval_and_timing.json`: approval count, review time and file hashes.

The `evaluation_summary.json` files were written before the review, so they still show zero approved records. The approval is recorded separately in the files above.

API time plus review time was 43.12 minutes, not counting setup or the Haiku run. I did not time a fully manual spread, so there is no time-saving figure.

## Haiku exceptions

- **Three missing values.** Haiku left three values blank where the 10-K prints a dash, which means zero: revolving credit repayments in 2024 and 2025, and short-term debt repayments in 2025. Without them, three accounting checks could not run.
- **Three quote mismatches.** On the parent equity rows for 2023, 2024 and 2025, Haiku wrote a straight apostrophe where the PDF has a curly one. The amounts were correct, but the exact-quote check flagged them.

The six corrections are saved separately in `review_2026-10-02/haiku_amendments.json`. With them, Haiku passes 174/174 values and all 36 accounting checks. That is the corrected result. The original Haiku score above is unchanged.

## Reproducibility checks

- Both evaluations were re-run offline from the page text saved in the API requests, and every amount and accounting check matched.
- A stricter local quote check flagged three FX-line quotes in each run. Local pypdf joins the last word of that label to the first number, while the Colab text has a space between them. With spaces removed, the characters and numbers are identical, so no amount is affected. Details are in `review_2026-10-02/independent_review.json`.
- `code/benchmark_verified.json` records the hash of the workbook version used as the benchmark. The current workbook has the same inputs and formulas. Only text notes changed (the review status note in `Credit Summary!C63` and the header line), so its hash is different. See `review_2026-10-02/final_model_checks.json`.

## Credit model check

All five scenarios were recalculated offline. The base case has a $3,015.5m cumulative gap to the $500m minimum liquid-asset reserve by 2029, and the combined revenue and rate stress raises it to $4,237.1m. These results depend on my capex and cash-timing assumptions and are not a default forecast. Scenario outputs are in `review_2026-10-02/model_review.json`.
