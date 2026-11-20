<#
.SYNOPSIS
  Ejecuta pre-commit dentro de Docker (Windows bloquea los binarios de su caché).

.EXAMPLE
  .\scripts\pre-commit.ps1 -Install     # instala el hook de git que usa Docker
  .\scripts\pre-commit.ps1              # pre-commit run --all-files
  .\scripts\pre-commit.ps1 run gitleaks --all-files
#>
param(
    [switch]$Install,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PreCommitArgs
)

# Sin ErrorActionPreference=Stop: en PowerShell 5.1 la salida de progreso de docker
# por stderr se trataría como error. Se comprueba $LASTEXITCODE.
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if ($Install) {
    $hook = Join-Path $root '.git/hooks/pre-commit'
    $content = @'
#!/bin/sh
# Hook generado por scripts/pre-commit.ps1: ejecuta pre-commit en Docker.
exec docker compose --profile tools run --rm -T precommit run --hook-stage pre-commit
'@
    [IO.File]::WriteAllText($hook, $content.Replace("`r`n", "`n"))
    docker compose --profile tools build precommit
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "Hook instalado en .git/hooks/pre-commit"
    exit 0
}

if (-not $PreCommitArgs) { $PreCommitArgs = @('run', '--all-files') }
docker compose --profile tools run --rm -T precommit @PreCommitArgs
exit $LASTEXITCODE
