# TerraSpectra - Week 4: Timeline & Refine

## Overview
Adds a historical progression timeline slider to the Week 3 dashboard,
allowing users to replay how a disease outbreak spread over time
(Day 0 to Day 21) using recorded spectral risk data.

## How It Works
- TIMELINE_DAYS array defines checkpoint days (0, 3, 6, 9, 12, 15, 18, 21)
- generateRealisticSatelliteRaster(dayOffset) recalculates risk scores for all 144 grid cells based on outbreak growth at that day
- Moving the slider updates dayIndex state, which triggers a re-render of the risk layer with updated colors and intensities

## Important Note
This slider represents HISTORICAL playback of recorded spectral data, not future prediction. It answers "how did the outbreak spread over the past 21 days", distinct from the core model's early-detection capability (predicting outbreaks ~3 weeks before visible symptoms).

## Status
Week 4 Frontend Complete. Timeline slider integrated with existing Week 3 dashboard (satellite map, analytics panel, risk legend).                              EOF
