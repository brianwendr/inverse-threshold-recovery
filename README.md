# Minimal replication package

This package reproduces the deterministic finite calculations reported in Section 6 of the manuscript:

**Inverse Threshold Problem for Finite-Chain Scheduling with Switching Costs: Feasibility, Half-Open Box Structure, and Sparse Recovery**

## Contents

- `replicate_tables.py` — self-contained Python script.
- `results/table1_base_instance.csv` — base instance used for Table 1.
- `results/table2_boundary_verification.csv` — boundary checks for Propositions 2 and 3.
- `results/table3_systematic_verification.csv` — systematic finite-instance verification.

## How to run

Use Python 3.9 or later:

```bash
python replicate_tables.py
```

The command regenerates the three CSV files in `results/`.

## Data and randomness

No external dataset is used. The calculations are deterministic and involve no random seed, stochastic simulation, or fitted model.
