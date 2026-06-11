# Supplementary Material S1: Replication Package

This package supports the manuscript:

**Finite Relay Hysteresis in Dynamic Acquire-Divest Decisions with Transaction Costs**

## Requirements

- Python 3.9 or later
- No third-party Python packages are required

## How to reproduce

From the root of this package, run:

```bash
python src/replicate_hysteresis.py
```

The script reads `config/capabilities.csv` and writes all generated files to `output/`.

## Files

- `config/capabilities.csv`: capability descriptions, costs, transaction costs, slopes, and prerequisites.
- `config/paths.csv`: budget paths used for trace illustrations.
- `src/replicate_hysteresis.py`: code that computes thresholds, decompositions, band-order checks, and budget-loop traces.
- `output/manuscript_table2_capability_parameters.csv`: reproduced main-text Table 2.
- `output/manuscript_table3_threshold_verification.csv`: reproduced main-text Table 3.
- `output/supplementary_tableS1_frictionless_friction_decomposition.csv`: Supplementary Table S1, the full frictionless-friction decomposition moved out of the main text.
- `output/manuscript_table4_band_ordering_verification.csv`: reproduced main-text Table 4.
- `output/manuscript_table5_dynamic_budget_loop_c1.csv`: reproduced main-text Table 5.
- `output/manuscript_table6_return_point_trace_certificate.csv`: reproduced main-text Table 6.
- `output/supplement_partial_prerequisite_loop_trace.csv`: trace supporting Section 5.6.

## Notes

All values are illustrative and are stated in the manuscript or in Supplementary Table S1. The package is intended to make the threshold and relay traces auditable; it is not a separate empirical validation study.
