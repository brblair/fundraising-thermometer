# Capital Commitments Thermometers (10 × $1M)

Campaign: **Quansight Initiate Fund III, L.P.**  
Goal: **$10,000,000 USD**

This visualization renders **10 mini thermometers side-by-side** tracking **capital commitments** (not cash collections). Each thermometer represents **$1,000,000** of the total goal.

![Capital Commitments Thermometers](./thermometer.svg)

## How to update
Edit `data/funds.json` and set the per-segment values (in dollars) under `"segments"` (exactly 10 numbers), then open a pull request.  
On merge, a GitHub Action regenerates `thermometer.svg`.

- **Each thermometer** fills with a **red → green** gradient based on its own progress.  
- **Major ticks:** every **$100k**.  
- **Minor ticks:** every **$50k**.  
- The header shows **total committed** vs **$10M** and overall %.
