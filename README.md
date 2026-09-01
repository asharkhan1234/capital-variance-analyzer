# Capital Cost Variance Analyzer

A small Python tool that takes planned vs. actual cost data for a capital
project, broken down by work package and cost category, and produces a
variance report, a category roll-up, a simple sensitivity check, and a
chart.

## Why I built this

I've worked on cost, variance, and sensitivity analysis for capital
projects in a project management role, work package by work package,
category by category, done by hand in Excel. This project is a small,
generalized version of that same workflow: given any set of planned vs.
actual costs, it flags where a project is over or under budget, rolls
that up by cost category (labour, materials, contracts), and shows which
category has the biggest swing potential on total cost.

All data in this repo is synthetic and generated for demonstration
purposes only, no real project or company data is used.

It's built to run against any CSV in the same shape, not just the sample
data included here.

## What it does

1. **Line-item variance** — dollar and percent variance for every work
   package / category combination, sorted by absolute impact.
2. **Category roll-up** — totals and variance aggregated by Labour,
   Materials, and Contracts.
3. **Sensitivity check** — a simple one-factor-at-a-time view of how much
   a ±5% swing in each category would move total project cost, the same
   logic behind a tornado chart in capital planning.
4. **Chart** — a horizontal bar chart of variance by work package, saved
   as `variance_chart.png`.

## Running it

```bash
pip install -r requirements.txt
python analyzer.py sample_data.csv
```

This prints the full report to the console and writes two files:
`variance_report.csv` (full line-item detail) and `variance_chart.png`
(the variance chart).

## Input format

A CSV with four columns:

| column        | description                          |
|----------------|--------------------------------------|
| work_package   | name of the project work package     |
| category       | Labour / Materials / Contracts (or your own categories) |
| planned_cost   | budgeted cost for that line item     |
| actual_cost    | actual cost incurred                 |

Swap in your own CSV in the same shape and run the script against it.

## Sample output

On the included sample data (an 18-line-item capital project), the tool
reports a total variance of **+$114,500 (+3.0%)** against a $3.79M
planned budget, and flags Structural Steel materials as the single
largest cost overrun at +$45,000 (+7.4%).
