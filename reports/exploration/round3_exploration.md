# Exploration round 3: exploration window

**EXPLORATORY (contaminated: the window was looked at before the plan).** These numbers count for nothing; every test is decided once
on future CGI data (docs/exploration_round3_plan.md, D49). They are shown
because the frozen coefficients for C2 come from this window.

Jump threshold 0.0025 (log). One-sided p in the pre-registered direction;
c is the slope on the channel net of the past 6-hour move (Frisch-Waugh-Lovell,
Newey-West lag 12). CI is the block-bootstrap 95% CI of corr(x, y) after FWL.

| ID | GPU | channel | n | events | channel windows | c | t | p (one-sided) | circular-shift p | corr CI | past-only slope |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R3-01 | H100 | np | 539 | 189 | 59 | -0.002 | -0.01 | 0.496 | 0.985 | [-0.19, 0.16] | -0.350 |
| R3-02 | H100 | jump | 539 | 214 | 61 | -0.157 | -0.92 | 0.180 | 0.257 | [-0.27, 0.11] | -0.350 |
| R3-03 | B200 | jump | 551 | 291 | 54 | 0.151 | 1.22 | 0.888 | 0.531 | [-0.02, 0.12] | -0.347 |
| R3-04 | H100 | edge | 539 | 401 | 38 | 0.020 | 0.31 | 0.379 | 0.723 | [-0.11, 0.15] | -0.350 |

Descriptive jump thresholds (not tested):

- R3-02@0.001: n 539, c -0.081, t -0.22, events 414
- R3-03@0.001: n 551, c 0.051, t 0.44, events 474
- R3-02@0.005: n 539, c -0.061, t -0.36, events 130
- R3-03@0.005: n 551, c 0.076, t 0.75, events 202
