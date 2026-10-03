# Run from the echovault folder: .\check.ps1
# Needs on PATH: rojo, lune, luau-lsp (install with Rokit, see CLAUDE.md)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "== unit/sim tests (lune)"
lune run tests/smoke
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "== type-check (luau-lsp)"
if (-not (Test-Path globalTypes.d.luau)) {
    Invoke-WebRequest "https://raw.githubusercontent.com/JohnnyMorganz/luau-lsp/main/scripts/globalTypes.d.luau" -OutFile globalTypes.d.luau
}
rojo sourcemap default.project.json --output sourcemap.json
luau-lsp analyze --definitions=globalTypes.d.luau --sourcemap=sourcemap.json src
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "== build numbered .rbxl"
New-Item -ItemType Directory -Force builds | Out-Null
$n = (Get-ChildItem builds -Filter "EchoVault_*.rbxl" -ErrorAction SilentlyContinue).Count + 1
$out = "builds/EchoVault_{0:D3}.rbxl" -f $n
rojo build default.project.json --output $out
Write-Host "Built $out - open it in Studio"
