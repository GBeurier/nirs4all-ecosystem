# W11 - Branch Fallback Probe

Status: no committed code change.

## Scope

W11 investigated whether a `concat_transform` / branch-related parity case could
be lowered from fallback to native dag-ml in this wave.

## Outcome

The agent left only a temporary feasibility probe named
`tests/integration/parity/test_w11_probe.py`. The probe was explicitly marked
`TEMP W11 feasibility probe - deleted before commit` and contained diagnostic
prints rather than a stable assertion contract.

I removed the probe and left the worktree clean. No production or test change was
committed for W11.

## Commit

None.
