param([string]$LogisimJar='C:\Program Files\logisim-evolution\app\logisim-evolution-5.0.0-all.jar')
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$sim=Join-Path $root 'not-gate-tests'
Push-Location $sim
try{
    & ghdl -a --std=08 (Join-Path $root 'not_gate.vhd') (Join-Path $root 'tb_not_gate.vhd')
    if($LASTEXITCODE -ne 0){throw 'GHDL analysis failed'}
    & ghdl --synth --std=08 not_gate | Out-File 'not_gate_synth.vhd' -Encoding utf8
    if($LASTEXITCODE -ne 0){throw 'GHDL synthesis failed'}
    & ghdl -r --std=08 tb_not_gate --vcd=not_gate.vcd 2>&1 | Tee-Object 'ghdl.log'
    if($LASTEXITCODE -ne 0){throw 'VHDL simulation failed'}
    New-Item -ItemType Directory -Force -Path 'java_build' | Out-Null
    & javac -cp $LogisimJar -d java_build (Join-Path $root 'sequential-logic-lab/scripts/LogisimVerify.java')
    if($LASTEXITCODE -ne 0){throw 'Java compilation failed; JDK 21+ required'}
    & java -cp "$LogisimJar;java_build" LogisimVerify (Join-Path $root 'not_gate.circ') 'vectors.csv' 'not_gate' 2>&1 | Tee-Object 'logisim.log'
    if($LASTEXITCODE -ne 0){throw 'Logisim simulation failed'}
}finally{Pop-Location}
