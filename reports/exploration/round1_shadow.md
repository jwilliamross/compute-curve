# Exploration round 1: candidates in shadow mode

Updated 2026-10-10 00:24 UTC. A candidate is not a finding. It logs forecasts
only, and the existing gate is evaluated only if it passes its forward test.

## H05: CGI H100 past 6-hour change → CGI H100 next 6-hour change

- Frozen rule: forecast = 0.000267 + (-0.3450) × signal (`round1_frozen.json`). Shadow only: no order is sent anywhere.
- Forward window: 2026-10-07 00:00 to 2026-12-31 23:59 UTC, the next 60 US equity sessions after the candidate was added; 2052 hourly decision points.
- Logged so far: 67 forecasts, 61 with a known outcome.
- Point-in-time guards: 0 CGI stamps revised after first observation (first value kept); 0 values published more than 15 minutes late (excluded).
- No interim performance is shown: the test is evaluated once, after the last outcome is known (docs/exploration_plan.md section 9).

