# VHDL Course Assignments

**HUANGZE - Student ID 2024095705**

This is the shared repository for the course assignments. Each assignment includes source code, a Logisim circuit, reproducible tests, and a PDF report.

| Assignment | Report | Design and tests |
| --- | --- | --- |
| NOT gate | [Verified NOT gate report](NOT_Gate_Report.pdf) | [VHDL](not_gate.vhd), [Logisim](not_gate.circ), [testbench](tb_not_gate.vhd), [evidence](not-gate-tests/) |
| Latches and flip-flops | [Sequential logic report](sequential-logic-lab/Sequential_Logic_Lab_Report.pdf) | [Assignment folder](sequential-logic-lab/), [VHDL](sequential-logic-lab/vhdl/), [Logisim](sequential-logic-lab/logisim/), [evidence](sequential-logic-lab/simulation/) |

## Verified results

- NOT gate: GHDL analysis, synthesis, and four self-checking simulation vectors pass. The actual Logisim engine independently passes the four vectors (`0 -> 1`, `1 -> 0`, repeated).
- Sequential logic: all five designs pass GHDL synthesis and directed simulations. The actual Logisim engine and GHDL independently check the **same 1,194 ordered vectors**: RS 9, D latch 151, D flip-flop 402, JK 214, asynchronous D flip-flop 418.
- Reports contain native Logisim circuit-state renders and waveforms derived from GHDL VCD files. Raw logs and expected-vector files are included.

## Run the tests

Install GHDL 6.0.0, JDK 21 or newer (both `java` and `javac` on PATH), and Logisim-evolution 5.0.0. PowerShell commands from the repository root:

```powershell
./run_not_gate.ps1
./sequential-logic-lab/scripts/run_all.ps1
./sequential-logic-lab/scripts/run_gate_checks.ps1
```

If Logisim is installed elsewhere, pass `-LogisimJar 'path/to/logisim-evolution-all.jar'` to `run_not_gate.ps1` and `run_gate_checks.ps1`.

The NOT gate main circuit is now a directly runnable native gate circuit. Its matching VHDL is compiled and simulated in GHDL; no external VHDL simulator is needed to run the Logisim circuit.

## LMS submission

Submit this public repository link: **https://github.com/TKAET/not-gate-vhdl**. Use the table above to find each assignment.
