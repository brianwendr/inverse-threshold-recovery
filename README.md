# Supplementary Material for RAIRO-Operations Research Submission

Article title: Recovering Switching-Cost Differences from Threshold Policies on a Finite Chain

Author: Yen-Chun Wen
Affiliation: Department of Finance & Cooperative Management, National Taipei University
Email: brianwen@mail.ntpu.edu.tw

## Contents

- `replicate_tables.py`: deterministic Python script that regenerates the finite verification values reported in Section 6 of the manuscript.
- `results/table1_base_instance.csv`: base-instance thresholds, feasible intervals, and near-origin representative.
- `results/table2_boundary_verification.csv`: boundary and sensitivity checks.
- `results/table3_systematic_verification.csv`: systematic parametric and independent finite-instance checks.

## Reproduction

Run:

```bash
python3 replicate_tables.py
```

The script uses only the Python standard library. No external datasets and no third-party packages are required.

## Public copy

A public copy of this replication package is available at:
https://github.com/brianwendr/inverse-threshold-recovery
