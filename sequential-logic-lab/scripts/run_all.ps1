$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$src = Join-Path $root 'vhdl/src'
$tb = Join-Path $root 'vhdl/tb'
$sim = Join-Path $root 'simulation'
$vcd = Join-Path $sim 'vcd'
$logs = Join-Path $sim 'logs'
$synth = Join-Path $sim 'synth'

New-Item -ItemType Directory -Force -Path $vcd, $logs, $synth | Out-Null
Push-Location $sim

try {
    $designs = @(
        @{ Unit = 'rs_latch'; Stop = '70ns' },
        @{ Unit = 'd_latch'; Stop = '70ns' },
        @{ Unit = 'd_ff'; Stop = '60ns' },
        @{ Unit = 'jk_ff'; Stop = '80ns' },
        @{ Unit = 'd_ff_async'; Stop = '60ns' }
    )

    foreach ($item in $designs) {
        $unit = $item.Unit
        $testbench = "tb_$unit"
        $log = Join-Path $logs "$testbench.log"
        "DESIGN: $unit" | Out-File $log -Encoding utf8

        & ghdl -a --std=08 (Join-Path $src "$unit.vhd") 2>&1 | Tee-Object -FilePath $log -Append
        if ($LASTEXITCODE -ne 0) { throw "Analyze failed: $unit" }

        & ghdl --synth --std=08 --latches $unit | Out-File (Join-Path $synth "$unit.vhd") -Encoding utf8
        if ($LASTEXITCODE -ne 0) { throw "Synthesis failed: $unit" }
        "SYNTHESIS PASS: $unit" | Tee-Object -FilePath $log -Append

        & ghdl -a --std=08 (Join-Path $tb "$testbench.vhd") 2>&1 | Tee-Object -FilePath $log -Append
        if ($LASTEXITCODE -ne 0) { throw "Analyze failed: $testbench" }

        & ghdl -e --std=08 $testbench 2>&1 | Tee-Object -FilePath $log -Append
        if ($LASTEXITCODE -ne 0) { throw "Elaboration failed: $testbench" }

        & ghdl -r --std=08 $testbench "--stop-time=$($item.Stop)" "--vcd=$(Join-Path $vcd "$testbench.vcd")" 2>&1 | Tee-Object -FilePath $log -Append
        if ($LASTEXITCODE -ne 0) { throw "Simulation failed: $testbench" }
    }
} finally {
    Pop-Location
}

Write-Host 'All five self-checking simulations passed.'
