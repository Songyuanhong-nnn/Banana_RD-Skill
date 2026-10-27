<#
.SYNOPSIS
    Install the AI-SQ Universal Root-Inquiry skill bundle.

.DESCRIPTION
    Two install routes:
      copy   - copy ai-sq-universal into the user skill root (~/.dsh/skills).
               No config change needed; DSH discovers user skills by default.
      plugin - keep the skill where it is and emit a Cordis patch that registers
               this bundle directory as an extra skill root. Nothing is copied,
               and the user's ~/.dsh/cordis.patch.yml is never modified for you.
      verify - run the package self-check (frontmatter, layout, packs, evals).

.PARAMETER Mode
    copy | plugin | verify. Default: copy.

.PARAMETER SkillsDir
    Target user skill root for copy mode. Default: $HOME\.dsh\skills

.PARAMETER DshHome
    DSH config root, used only to print instructions. Default: $HOME\.dsh

.EXAMPLE
    .\install.ps1
    .\install.ps1 -Mode plugin
    .\install.ps1 -Mode verify
#>
[CmdletBinding()]
param(
    [ValidateSet('copy', 'plugin', 'verify')]
    [string]$Mode = 'copy',
    [string]$SkillsDir = (Join-Path $HOME '.dsh\skills'),
    [string]$DshHome = (Join-Path $HOME '.dsh')
)

$ErrorActionPreference = 'Stop'
$BundleRoot = Split-Path -Parent $PSScriptRoot
$SkillSrc = Join-Path $BundleRoot 'ai-sq-universal'
$SkillName = 'ai-sq-universal'

function Write-Step([string]$Text) { Write-Host "==> $Text" -ForegroundColor Cyan }
function Write-Ok([string]$Text) { Write-Host "    $Text" -ForegroundColor Green }
function Write-Warn([string]$Text) { Write-Host "    $Text" -ForegroundColor Yellow }

Write-Host ''
Write-Host 'AI-SQ Universal Root-Inquiry / 通用求根问底调研  v2.4.0' -ForegroundColor White
Write-Host "bundle root : $BundleRoot"
Write-Host "skill source: $SkillSrc"
Write-Host "mode        : $Mode"
Write-Host ''

if (-not (Test-Path (Join-Path $SkillSrc 'SKILL.md'))) {
    throw "SKILL.md not found under $SkillSrc - run this script from the plugin\ folder of a complete bundle."
}

function Invoke-Copy {
    Write-Step "Copying skill to $SkillsDir"
    if (-not (Test-Path $SkillsDir)) {
        New-Item -ItemType Directory -Force -Path $SkillsDir | Out-Null
        Write-Ok "created $SkillsDir"
    }

    $target = Join-Path $SkillsDir $SkillName
    if (Test-Path $target) {
        $backup = "$target.bak-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Move-Item -LiteralPath $target -Destination $backup
        Write-Warn "existing install moved to $backup (delete it once you are satisfied)"
    }

    Copy-Item -LiteralPath $SkillSrc -Destination $target -Recurse -Force
    if (-not (Test-Path (Join-Path $target 'SKILL.md'))) {
        throw "copy finished but $target\SKILL.md is missing"
    }
    Write-Ok "installed: $target"
    Write-Host ''
    Write-Host 'Next: restart DSH (or start a new session) and check that' -ForegroundColor White
    Write-Host '      ai-sq-universal-root-inquiry appears in the skill catalog.' -ForegroundColor White
    Write-Host '      Verify with:  .\install.ps1 -Mode verify' -ForegroundColor White
}

function Invoke-Plugin {
    Write-Step 'Emitting a Cordis patch (nothing is copied)'
    $template = Join-Path $PSScriptRoot 'cordis.patch.yml'
    if (-not (Test-Path $template)) { throw "missing $template" }

    $escaped = $BundleRoot -replace '\\', '\\\\'
    $body = Get-Content -LiteralPath $template -Raw -Encoding UTF8
    $body = $body.Replace('__SKILL_ROOT__', $escaped)

    $out = Join-Path $PSScriptRoot 'cordis.patch.generated.yml'
    Set-Content -LiteralPath $out -Value $body -Encoding UTF8
    Write-Ok "wrote $out"
    Write-Host ''
    Write-Host 'Now merge the "insert:" block from that file into:' -ForegroundColor White
    Write-Host "      $(Join-Path $DshHome 'cordis.patch.yml')" -ForegroundColor White
    Write-Host 'then restart DSH. The skill stays at its current path.' -ForegroundColor White
    Write-Host ''
    Write-Warn 'This script does not edit your config automatically - merging YAML by machine is how installers break setups.'
}

function Invoke-Verify {
    Write-Step 'Self-check'
    $validator = Join-Path $SkillSrc 'scripts\validate.py'
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) { $python = Get-Command python3 -ErrorAction SilentlyContinue }

    if ($python -and (Test-Path $validator)) {
        & $python.Source $validator
        if ($LASTEXITCODE -ne 0) { throw "validate.py reported failures (exit $LASTEXITCODE)" }
        Write-Ok 'package validation passed'
    }
    else {
        Write-Warn 'python or scripts\validate.py not available - checking layout only'
        foreach ($rel in @('SKILL.md', 'prompts\planner.md', 'schemas\report.json', 'templates\report.md', 'evals\cases.yaml')) {
            $p = Join-Path $SkillSrc $rel
            if (Test-Path $p) { Write-Ok "ok  $rel" } else { throw "missing $rel" }
        }
    }

    $installed = Join-Path $SkillsDir $SkillName
    if (Test-Path (Join-Path $installed 'SKILL.md')) {
        Write-Ok "copy-install present at $installed"
    }
    else {
        Write-Warn "not installed under $SkillsDir (copy mode not run yet)"
    }
}

switch ($Mode) {
    'copy' { Invoke-Copy }
    'plugin' { Invoke-Plugin }
    'verify' { Invoke-Verify }
}

Write-Host ''
