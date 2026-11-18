# Sequential Logic Lab: Latches and Flip-Flops

This repository contains gate-level Logisim circuits, synthesizable VHDL, self-checking testbenches, simulation waveforms, and a PDF report for five sequential-logic exercises.

## Contents

- `vhdl/src/`: synthesizable VHDL design units
- `vhdl/tb/`: self-checking VHDL testbenches
- `logisim/`: Logisim-evolution gate-level circuits (no latch/flip-flop primitives)
- `simulation/`: generated VCD waveforms and GHDL transcripts
- `report/`: rendered circuit figures and simulation figures
- `Sequential_Logic_Lab_Report.pdf`: final report

## Exercises

1. Active-high NOR RS latch
2. Active-high-enable NAND D latch
3. Positive-edge-triggered D flip-flop and master-slave gate circuit
4. Positive-edge-triggered JK flip-flop
5. Positive-edge-triggered D flip-flop with asynchronous active-high clear and set (clear priority)

## Reproduce the VHDL simulations

Install GHDL, then run from PowerShell:

```powershell
./scripts/run_all.ps1
```

Each testbench is self-checking. A successful run ends with `PASS` and produces a `.vcd` file under `simulation/vcd/`.

## Open the gate-level circuits

Open any `.circ` file in Logisim-evolution 5.0.0 or later. Toggle the input pins with the Poke tool. All storage elements are built from individual gates and explicit feedback wires.

See the PDF report for truth tables, test procedures, schematics, and simulation results.

## Verified tool results

- GHDL 6.0.0: analysis PASS for all five design units and all five testbenches
- GHDL synthesis: PASS for all five design units (`--latches` explicitly permits the intended latch inference)
- GHDL simulation: PASS for all five directed self-checking testbenches
- Actual Logisim-evolution 5.0.0 propagation engine: PASS for 1,194 ordered vectors (9 RS, 151 D latch, 402 D flip-flop, 214 JK, 418 asynchronous D flip-flop)
- The same CSV files are replayed independently in GHDL by `tb_gate_vectors.vhd`; every checked output matches the state-table expectations.
- Native Logisim renders and raw test logs are included. Same-named tunnels connect wires, including feedback nets. Only NAND/NOR gates store state; no pre-built latch or flip-flop component is used.

Run `./scripts/run_gate_checks.ps1` after `run_all.ps1` to reproduce the gate simulation and the shared-vector VHDL checks. Requires JDK 21+ and Logisim-evolution 5.0.0. Pass `-LogisimJar` for a non-default installation.

## GitHub submission

This assignment is stored under `sequential-logic-lab/` in the course repository: https://github.com/TKAET/not-gate-vhdl. The root README links both the NOT gate assignment and this sequential logic assignment. Submit the repository URL to LMS.
