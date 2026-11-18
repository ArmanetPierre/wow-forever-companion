<#
  Installe les addons du compagnon WoW Forever (Windows).

  Usage (PowerShell, depuis le dossier du repo) :
    powershell -ExecutionPolicy Bypass -File addon\install.ps1
    powershell -ExecutionPolicy Bypass -File addon\install.ps1 -Addons ForeverProbe
    powershell -ExecutionPolicy Bypass -File addon\install.ps1 -Copy
    powershell -ExecutionPolicy Bypass -File addon\install.ps1 -WowPath "D:\Jeux\World of Warcraft\_forever_"

  Par défaut, crée une jonction (comme un lien, sans droits administrateur) : l'addon
  reste à jour quand le repo change. -Copy copie le dossier à la place.
#>
param(
  [string]$WowPath = $env:WOW_FOREVER_PATH,
  [string[]]$Addons = @("ForeverScribe"),
  [switch]$Copy
)
$ErrorActionPreference = "Stop"
$AddonDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not $WowPath) {
  # Registre écrit par le Battle.net (même recherche que plugins/forever-companion/mcp/wowpaths.py)
  $keys = @(
    "HKLM:\SOFTWARE\WOW6432Node\Blizzard Entertainment\World of Warcraft",
    "HKLM:\SOFTWARE\Blizzard Entertainment\World of Warcraft",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\World of Warcraft",
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\World of Warcraft"
  )
  foreach ($k in $keys) {
    $props = Get-ItemProperty -Path $k -ErrorAction SilentlyContinue
    foreach ($p in @($props.InstallPath, $props.InstallLocation)) {
      if ($p) {
        $cand = Join-Path ($p.Trim('"')) "_forever_"
        if (Test-Path $cand) { $WowPath = $cand; break }
      }
    }
    if ($WowPath) { break }
  }
}
if (-not $WowPath) {
  # Dossier d'installation par défaut du Battle.net
  $bnet = Join-Path $env:APPDATA "Battle.net\Battle.net.config"
  if (Test-Path $bnet) {
    try {
      $base = (Get-Content $bnet -Raw -Encoding UTF8 | ConvertFrom-Json).Client.Install.DefaultInstallPath
      if ($base) {
        $cand = Join-Path $base "World of Warcraft\_forever_"
        if (Test-Path $cand) { $WowPath = $cand }
      }
    } catch { }
  }
}
if (-not $WowPath) {
  $candidates = @()
  foreach ($d in "C","D","E","F","G","H") {
    foreach ($pf in "Program Files (x86)","Program Files","Games","Jeux","Blizzard","") {
      $base = if ($pf) { "${d}:\$pf" } else { "${d}:" }
      $candidates += "$base\World of Warcraft\_forever_"
    }
  }
  foreach ($c in $candidates) { if (Test-Path $c) { $WowPath = $c; break } }
}
if (-not $WowPath -or -not (Test-Path $WowPath)) {
  Write-Error "Dossier du jeu introuvable. Indique-le avec -WowPath ""C:\...\World of Warcraft\_forever_"""
}

$TargetDir = Join-Path $WowPath "Interface\AddOns"
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
Write-Host "Dossier du jeu : $WowPath"

foreach ($name in $Addons) {
  $src = Join-Path $AddonDir $name
  $dest = Join-Path $TargetDir $name
  if (-not (Test-Path (Join-Path $src "$name.toc"))) {
    Write-Error "$name : introuvable dans $AddonDir (pas de $name.toc)"
  }
  if (Test-Path $dest) {
    $item = Get-Item $dest -Force
    if ($item.LinkType) {
      # jonction ou lien : on supprime le lien, pas son contenu
      $item.Delete()
    } elseif ($Copy) {
      Remove-Item -Recurse -Force $dest
    } else {
      Write-Error "$name : un dossier existe déjà dans AddOns. Supprime-le ou relance avec -Copy."
    }
  }
  if ($Copy) {
    Copy-Item -Recurse $src $dest
    Write-Host "  $name : copié (relance après chaque mise à jour du repo)"
  } else {
    try {
      New-Item -ItemType Junction -Path $dest -Target $src | Out-Null
      Write-Host "  $name : jonction créée -> $src"
    } catch {
      Copy-Item -Recurse $src $dest
      Write-Host "  $name : jonction impossible, dossier copié à la place"
    }
  }
}
Write-Host "Terminé. En jeu : écran de sélection des personnages > AddOns > vérifie que l'addon est coché."
