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
  $candidates = @(
    "C:\Program Files (x86)\World of Warcraft\_forever_",
    "C:\Program Files\World of Warcraft\_forever_",
    "D:\World of Warcraft\_forever_",
    "D:\Program Files (x86)\World of Warcraft\_forever_"
  )
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
