param(
    [string]$LogisimJar = 'C:\Program Files\logisim-evolution\app\logisim-evolution-5.0.0-all.jar'
)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$build=Join-Path $root 'simulation/java_build'
New-Item -ItemType Directory -Force -Path $build | Out-Null
& javac -cp $LogisimJar -d $build (Join-Path $PSScriptRoot 'LogisimVerify.java')
if($LASTEXITCODE -ne 0){throw 'Java compilation failed (JDK 21 or later is required)'}
$tests=@(
    @('01_rs_latch_nor','rs_latch','01'),
    @('02_d_latch_nand','d_latch','02'),
    @('03_d_flip_flop_master_slave','d_ff','03'),
    @('04_jk_flip_flop_nand','jk_ff','04'),
    @('05_d_ff_async_set_clear','d_ff_async','05')
)
foreach($t in $tests){
    $log=Join-Path $root "simulation/logs/logisim_$($t[1]).log"
    & java -cp "$LogisimJar;$build" LogisimVerify (Join-Path $root "logisim/$($t[0]).circ") (Join-Path $root "simulation/logisim_vectors/$($t[1]).csv") (Join-Path $root "report/assets/$($t[2])_logisim") 2>&1 | Out-File $log -Encoding utf8
    if($LASTEXITCODE -ne 0){throw "Logisim check failed: $($t[1]); see $log"}
    Get-Content $log | Select-Object -Last 1
}
Push-Location (Join-Path $root 'simulation')
try{
    & ghdl -a --std=08 (Join-Path $root 'vhdl/tb/tb_gate_vectors.vhd')
    if($LASTEXITCODE -ne 0){throw 'Compile tb_gate_vectors failed; run run_all.ps1 first'}
    foreach($t in $tests){
        & ghdl -r --std=08 tb_gate_vectors "-gdesign_name=$($t[1])" "-gvector_file=$(Join-Path $root "simulation/logisim_vectors/$($t[1]).csv")" 2>&1 | Tee-Object -FilePath (Join-Path $root "simulation/logs/equivalence_$($t[1]).log")
        if($LASTEXITCODE -ne 0){throw "VHDL vector equivalence failed: $($t[1])"}
    }
}finally{Pop-Location}
