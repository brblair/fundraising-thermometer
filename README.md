# Capital Commitment Tracker

**Campaign:** Quansight Initiate Fund III, L.P.  
**Goal:** $10,000,000 USD
<br>
![Capital Commitments Thermometers](./thermometer.svg?v=20250811154832-16885081679-1)

## What this shows
- **10 mini thermometers** side by side, each representing **$1,000,000** of the $10M goal.
- **Solid red fill** grows upward as capital commitments increase.
- **Bulb:** white at $0; turns **red** once the segment > $0.
- **Tube:** white background, light gray outline.
- **Ticks:** Major every **$100k**, minor every **$50k**.
- Tracks **capital commitments** (not cash collections).

## License
© 2025 Bradden Blair, Ph.D. Licensed under the Apache License, Version 2.0.  
See `LICENSE` and `NOTICE` for details. Please preserve copyright and license notices.  
Brand assets in `/assets` are not covered by the code license (see `/assets/LICENSE`).


## How to update numbers
Edit `data/funds.json` and set the 10 values in `"segments"` (dollars). Example:
```json
{
  "goal": 10000000,
  "currency": "USD",
  "label": "Quansight Initiate Fund III, L.P.",
  "segments": [1000000, 1000000, 750000, 0, 0, 0, 0, 0, 0, 0]
}
