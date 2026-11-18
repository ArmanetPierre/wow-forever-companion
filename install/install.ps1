<#
  WoW Forever Companion : installateur Windows (installation et mise à jour).

  Double-clic : « Installer WoW Forever Companion.cmd » (archive Windows)
  En une ligne (PowerShell) :
    irm https://raw.githubusercontent.com/ArmanetPierre/wow-forever-companion/main/install/install.ps1 | iex
  Depuis le dépôt :
    powershell -ExecutionPolicy Bypass -File install\install.ps1 [options]

  Options :
    -WowPath DOSSIER   dossier du jeu (« World of Warcraft » ou son « _forever_ »)
    -DataDir DOSSIER   dossier du joueur (défaut : %USERPROFILE%\WowForever)
    -Lang fr|en        langue des messages (défaut : celle du système)
    -Yes               répond oui aux questions sur NOS étapes (base du jeu) ;
                       n'installe jamais un logiciel tiers sans un « oui » tapé
    -NoDb              ne propose pas de construire la base du jeu
    -Uninstall         retire l'addon et le plugin ; ne touche jamais à tes données

  Variables utiles : FOREVER_PYTHON, WOW_FOREVER_PATH, FOREVER_HOME (dossier du joueur),
  FOREVER_SOURCE_URL (archive .zip du dépôt, URL ou chemin), FOREVER_MARKETPLACE,
  FOREVER_NO_TTY=1 (aucune question), FOREVER_NO_SETX=1 (ne pas enregistrer FOREVER_PYTHON).

  Tout est dans une fonction appelée à la fin : avec « irm | iex », rien ne s'exécute
  avant que le script soit arrivé en entier, et la fenêtre PowerShell n'est jamais fermée.
#>
param(
  [string]$WowPath = $env:WOW_FOREVER_PATH,
  [string]$DataDir = "",
  [string]$Lang = "",
  [switch]$Yes,
  [switch]$NoDb,
  [switch]$Uninstall
)

function Install-ForeverCompanion {
  param([string]$WowPath, [string]$DataDir, [string]$Lang, [switch]$Yes, [switch]$NoDb, [switch]$Uninstall,
        [string]$ScriptRoot)

  $ErrorActionPreference = "Continue"
  function J { $p = $args[0]; foreach ($x in $args[1..($args.Count - 1)]) { $p = [IO.Path]::Combine($p, $x) }; return $p }
  try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }
  $OnWindows = ($env:OS -eq "Windows_NT")

  $Repo = "ArmanetPierre/wow-forever-companion"
  $MarketName = "wow-forever-companion"
  $PluginId = "forever-companion@wow-forever-companion"
  $MarketSource = if ($env:FOREVER_MARKETPLACE) { $env:FOREVER_MARKETPLACE } else { $Repo }
  $SourceUrl = if ($env:FOREVER_SOURCE_URL) { $env:FOREVER_SOURCE_URL } else { "https://github.com/$Repo/archive/refs/heads/main.zip" }
  $UserHome = if ($OnWindows) { $env:USERPROFILE } else { $env:HOME }
  if (-not $DataDir) { $DataDir = if ($env:FOREVER_HOME) { $env:FOREVER_HOME } else { Join-Path $UserHome "WowForever" } }
  $App = if ($OnWindows) { Join-Path $env:LOCALAPPDATA "WoW Forever Companion" } else {
    $xdg = if ($env:XDG_DATA_HOME) { $env:XDG_DATA_HOME } else { Join-Path $UserHome ".local/share" }
    Join-Path $xdg "wow-forever-companion" }

  # ---------- langue et affichage ----------
  if (-not $Lang) {
    $culture = try { (Get-UICulture).Name } catch { "" }
    if (-not $culture) { $culture = "$env:LANG" }
    $Lang = if ($culture -like "fr*") { "fr" } else { "en" }
  }
  $script:L = $Lang
  function T([string]$fr, [string]$en) { if ($script:L -eq "fr") { $fr } else { $en } }
  $script:Step = 0
  $script:Total = 6
  function Step([string]$m) { $script:Step++; Write-Host ""; Write-Host ("[{0}/{1}] {2}" -f $script:Step, $script:Total, $m) -ForegroundColor Cyan }
  function Ok([string]$m) { Write-Host "  √ " -ForegroundColor Green -NoNewline; Write-Host $m }
  function Info([string]$m) { Write-Host "  · " -ForegroundColor DarkGray -NoNewline; Write-Host $m }
  function Warn([string]$m) { Write-Host "  ! " -ForegroundColor Yellow -NoNewline; Write-Host $m }
  function Fail([string]$m) { Write-Host "  x " -ForegroundColor Red -NoNewline; Write-Host $m }

  $Interactive = (-not $env:FOREVER_NO_TTY) -and [Environment]::UserInteractive -and -not [Console]::IsInputRedirected
  function AskYes([string]$q, [bool]$def, [bool]$allowYes = $false) {
    if ($allowYes -and $Yes) { return $true }
    $hint = if ($def) { T "[O/n]" "[Y/n]" } else { T "[o/N]" "[y/N]" }
    if (-not $Interactive) { Info ("$q $hint -> " + (T "pas de terminal, réponse par défaut" "no terminal, default answer")); return $def }
    $a = Read-Host "  ? $q $hint"
    if (-not $a) { return $def }
    return ($a -match '^(o|oui|y|yes)$')
  }
  function AskText([string]$q) { if (-not $Interactive) { return "" }; return (Read-Host "  ? $q") }
  function PauseFor { if ($Interactive) { $null = Read-Host (T "  Appuie sur Entrée quand c'est fait" "  Press Enter when done") } }

  Write-Host ""
  $title = if ($Uninstall) { T "désinstallation" "uninstall" } else { T "installation et mise à jour" "install and update" }
  Write-Host "WoW Forever Companion - $title" -ForegroundColor Yellow
  Write-Host (T "Ce programme n'installe rien sans te le dire. Tes données de joueur ne sont jamais modifiées." "This installer tells you everything it does. Your player data is never modified.") -ForegroundColor DarkGray

  # ---------- sources ----------
  $Src = $null
  if ($ScriptRoot -and (Test-Path (J $ScriptRoot ".." "addon" "ForeverScribe" "ForeverScribe.toc"))) {
    $Src = (Resolve-Path (Join-Path $ScriptRoot "..")).Path
  }
  $Tmp = $null
  if (-not $Src -and -not $Uninstall) {
    $Tmp = Join-Path ([IO.Path]::GetTempPath()) ("forever-" + [Guid]::NewGuid().ToString("N"))
    $null = New-Item -ItemType Directory -Path $Tmp
    Info (T "Téléchargement du compagnon…" "Downloading the companion…")
    $zip = Join-Path $Tmp "src.zip"
    try {
      if (Test-Path $SourceUrl) { Copy-Item $SourceUrl $zip }
      else {
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $SourceUrl -OutFile $zip -UseBasicParsing
      }
      Expand-Archive -Path $zip -DestinationPath $Tmp -Force
    } catch {
      Fail ((T "Téléchargement impossible : " "Download failed: ") + $SourceUrl)
      return 1
    }
    $toc = Get-ChildItem -Path $Tmp -Recurse -Filter "ForeverScribe.toc" -ErrorAction SilentlyContinue |
      Where-Object { $_.Directory.Parent.Name -eq "addon" } | Select-Object -First 1
    if (-not $toc) { Fail (T "Archive inattendue (addon absent)." "Unexpected archive (addon missing)."); return 1 }
    $Src = $toc.Directory.Parent.Parent.FullName
  }
  if ($Src -and $OnWindows) { Get-ChildItem -Path $Src -Recurse -File -ErrorAction SilentlyContinue | Unblock-File -ErrorAction SilentlyContinue }

  # ---------- outils ----------
  function Find-Claude {
    $c = Get-Command claude -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($c) { return $c.Source }
    foreach ($p in @((J $UserHome ".local" "bin" "claude.exe"), (Join-Path $UserHome ".local/bin/claude"))) {
      if (Test-Path $p) { return $p }
    }
    return $null
  }
  function Test-Py([string[]]$cmd) {
    $exe = $cmd[0]; $pre = @(); if ($cmd.Count -gt 1) { $pre = $cmd[1..($cmd.Count - 1)] }
    if (-not (Get-Command $exe -ErrorAction SilentlyContinue) -and -not (Test-Path $exe)) { return $null }
    try {
      $out = & $exe @pre -c "import sys; print('%d %d %s' % (sys.version_info[0], sys.version_info[1], sys.executable))" 2>$null
      if ($LASTEXITCODE -ne 0 -or -not $out) { return $null }
      $parts = "$out".Trim() -split " ", 3
      $maj = [int]$parts[0]; $min = [int]$parts[1]
      if ($maj -gt 3 -or ($maj -eq 3 -and $min -ge 9)) { return $parts[2] }
    } catch { }
    return $null
  }
  function Find-Python {
    if ($env:FOREVER_PYTHON) { return (Test-Py @($env:FOREVER_PYTHON)) }
    foreach ($cand in @(@("py", "-3"), @("python"), @("python3"))) {
      $exe = Test-Py $cand
      if ($exe) { return $exe }
    }
    return $null
  }
  function Normalize-Wow([string]$p) {
    if (-not $p) { return $null }
    $p = $p.Trim().Trim('"').Trim("'").TrimEnd('\', '/')
    if (-not $p) { return $null }
    if ((Split-Path $p -Leaf) -eq "_forever_" -and (Test-Path $p -PathType Container)) { return (Resolve-Path $p).Path }
    foreach ($sub in @("_forever_", "World of Warcraft\_forever_", "World of Warcraft/_forever_")) {
      $c = Join-Path $p $sub
      if (Test-Path $c -PathType Container) { return (Resolve-Path $c).Path }
    }
    return $null
  }

  $Py = $null; $Claude = $null
  $R = @{ addon = ""; plugin = ""; data = ""; db = "" }

  if ($Uninstall) {
    $script:Total = 3
    Step (T "Retrait de l'addon" "Removing the addon")
  } else {
    Step (T "Vérification des prérequis" "Checking prerequisites")
    while (-not ($Py = Find-Python)) {
      if ($env:FOREVER_PYTHON) { Fail ((T "FOREVER_PYTHON=$($env:FOREVER_PYTHON) ne répond pas ou date d'avant 3.9." "FOREVER_PYTHON=$($env:FOREVER_PYTHON) does not run or is older than 3.9.")) }
      else { Fail (T "Python 3.9 ou plus récent est introuvable. Le compagnon en a besoin (aucune bibliothèque en plus)." "Python 3.9 or newer was not found. The companion needs it (no extra packages).") }
      Info (T "Le plus simple : python.org, en cochant « Add python.exe to PATH »." 'Easiest: python.org, ticking "Add python.exe to PATH".')
      if (AskYes (T "Ouvrir la page de téléchargement de Python ?" "Open the Python download page?") $false) {
        Start-Process "https://www.python.org/downloads/"
        PauseFor
      } else {
        Fail (T "Installation arrêtée : rien n'a été modifié." "Install stopped: nothing was changed.")
        return 1
      }
    }
    Ok ("Python : $Py")
    # Le plugin lance « ${FOREVER_PYTHON:-python3} » : sous Windows, python3 manque souvent.
    if ($OnWindows -and -not $env:FOREVER_PYTHON -and -not (Test-Py @("python3")) -and -not $env:FOREVER_NO_SETX) {
      [Environment]::SetEnvironmentVariable("FOREVER_PYTHON", $Py, "User")
      $env:FOREVER_PYTHON = $Py
      Ok (T "FOREVER_PYTHON enregistré pour le plugin (variable utilisateur)." "FOREVER_PYTHON saved for the plugin (user variable).")
    }

    $Claude = Find-Claude
    if ($Claude) {
      $v = (& $Claude --version 2>$null | Select-Object -First 1)
      Ok "Claude Code : $v"
    } else {
      Warn (T "Claude Code est introuvable. C'est l'assistant dans lequel le compagnon répond (abonnement Claude requis)." "Claude Code was not found. It is the assistant the companion answers in (Claude subscription required).")
      Info (T "Installateur officiel d'Anthropic : irm https://claude.ai/install.ps1 | iex" "Anthropic's official installer: irm https://claude.ai/install.ps1 | iex")
      if (AskYes (T "Lancer l'installateur officiel de Claude Code maintenant ?" "Run the official Claude Code installer now?") $false) {
        try { Invoke-RestMethod https://claude.ai/install.ps1 | Invoke-Expression | Out-Host } catch { Fail $_.Exception.Message }
        $env:Path = [Environment]::GetEnvironmentVariable("Path", "User") + ";" + [Environment]::GetEnvironmentVariable("Path", "Machine")
        $Claude = Find-Claude
      } else {
        Info (T "Page officielle : https://claude.com/product/claude-code" "Official page: https://claude.com/product/claude-code")
      }
      if ($Claude) { Ok "Claude Code : $Claude" }
      else { Warn (T "Je continue sans : relance cet installateur une fois Claude Code installé." "Continuing without it: run this installer again once Claude Code is installed.") }
    }
  }

  # ---------- le jeu ----------
  $Wow = $null
  if (-not $Uninstall) { Step (T "Recherche de WoW Forever" "Finding WoW Forever") }
  if ($WowPath) {
    $Wow = Normalize-Wow $WowPath
    if (-not $Wow) { Warn ((T "Pas de dossier _forever_ dans : " "No _forever_ folder in: ") + $WowPath) }
  } else {
    $pyc = if ($Py) { $Py } else { Find-Python }
    $base = if ($Src) { $Src } else { $App }
    $wp = (J $base "plugins" "forever-companion" "mcp")
    if ($pyc -and (Test-Path (Join-Path $wp "wowpaths.py"))) {
      Push-Location $wp
      try { $det = & $pyc -c "import wowpaths; p = wowpaths.detect_wow_paths(); print(p[0] if p else '')" 2>$null } catch { $det = "" }
      Pop-Location
      $Wow = Normalize-Wow "$det"
    }
    if (-not $Wow -and $OnWindows) {
      foreach ($d in "C", "D", "E", "F", "G") {
        foreach ($pf in "Program Files (x86)", "Program Files", "Games", "Jeux", "Blizzard", "") {
          $b = if ($pf) { "${d}:\$pf" } else { "${d}:" }
          $Wow = Normalize-Wow "$b\World of Warcraft"
          if ($Wow) { break }
        }
        if ($Wow) { break }
      }
    }
  }
  if (-not $Wow -and -not $WowPath) {
    $typed = AskText (T "Dossier du jeu introuvable. Colle ici le chemin de « World of Warcraft » (ou Entrée pour passer)" 'Game folder not found. Paste the path of "World of Warcraft" (or Enter to skip)')
    if ($typed) { $Wow = Normalize-Wow $typed }
  }
  if ($Wow) { Ok ((T "Jeu" "Game") + " : $Wow") }
  else { Warn (T "Jeu introuvable : l'addon ne sera pas installé. Relance avec -WowPath ""C:\...\World of Warcraft""." 'Game not found: the addon will not be installed. Run again with -WowPath "C:\...\World of Warcraft".') }

  $AddonsDir = $null; $Dest = $null
  if ($Wow) { $AddonsDir = (J $Wow "Interface" "AddOns"); $Dest = Join-Path $AddonsDir "ForeverScribe" }
  function TocVersion([string]$f) {
    if (-not (Test-Path $f)) { return "" }
    $line = Get-Content $f -Encoding UTF8 | Where-Object { $_ -match '^## Version:' } | Select-Object -First 1
    if ($line) { return ($line -replace '^## Version:\s*', '').Trim() } else { return "" }
  }

  # ---------- désinstallation ----------
  if ($Uninstall) {
    if (-not $Dest) { Warn (T "Jeu introuvable : addon non retiré." "Game not found: addon not removed.") }
    elseif (Test-Path $Dest) {
      $item = Get-Item $Dest -Force
      if ($item.LinkType) { $item.Delete(); Ok (T "Lien de développement ForeverScribe retiré (sa cible est intacte)." "ForeverScribe development link removed (its target is untouched).") }
      else { Remove-Item -Recurse -Force $Dest; Ok (T "Addon ForeverScribe retiré." "ForeverScribe addon removed.") }
    } else { Info (T "Addon déjà absent." "Addon already absent.") }
    Info (T "Les captures du jeu (WTF\...\SavedVariables) et ton dossier de joueur restent en place." "Game captures (WTF\...\SavedVariables) and your player folder stay in place.")

    Step (T "Retrait du plugin Claude Code" "Removing the Claude Code plugin")
    $Claude = Find-Claude
    if ($Claude) {
      $null = & $Claude plugin uninstall $PluginId 2>&1
      if ($LASTEXITCODE -eq 0) { Ok (T "Plugin retiré." "Plugin removed.") } else { Info (T "Plugin déjà absent." "Plugin already absent.") }
      $null = & $Claude plugin marketplace remove $MarketName 2>&1
      if ($LASTEXITCODE -eq 0) { Ok (T "Marketplace retirée." "Marketplace removed.") }
    } else { Info (T "Claude Code absent : rien à retirer." "Claude Code absent: nothing to remove.") }

    Step (T "Nettoyage" "Cleanup")
    if (Test-Path $App) { Remove-Item -Recurse -Force $App; Ok ((T "Outils de l'installateur retirés" "Installer tools removed") + " ($App)") }
    Ok ((T "Ton dossier de joueur est intact" "Your player folder is untouched") + " : $DataDir")
    Write-Host ""; Write-Host (T "Désinstallation terminée." "Uninstall complete.") -ForegroundColor Green; Write-Host ""
    return 0
  }

  # ---------- l'addon ----------
  Step (T "Installation de l'addon ForeverScribe" "Installing the ForeverScribe addon")
  if (-not $Dest) {
    $R.addon = "skip"; Warn (T "Étape passée (jeu introuvable)." "Step skipped (game not found).")
  } elseif ((Test-Path $Dest) -and (Get-Item $Dest -Force).LinkType) {
    $R.addon = "dev"; Info (T "Lien de développement détecté : je n'y touche pas." "Development link detected: left as is.")
  } else {
    $newv = TocVersion (J $Src "addon" "ForeverScribe" "ForeverScribe.toc")
    $oldv = TocVersion (Join-Path $Dest "ForeverScribe.toc")
    $staging = "$Dest.tmp-install"
    try {
      $null = New-Item -ItemType Directory -Force -Path $AddonsDir -ErrorAction Stop
      if (Test-Path $staging) { Remove-Item -Recurse -Force $staging -ErrorAction Stop }
      Copy-Item -Recurse (J $Src "addon" "ForeverScribe") $staging -ErrorAction Stop
      if (Test-Path $Dest) { Remove-Item -Recurse -Force $Dest -ErrorAction Stop }
      Move-Item $staging $Dest -ErrorAction Stop
      $R.addon = "ok"
      if ($oldv -and $oldv -ne $newv) { Ok ((T "Addon mis à jour" "Addon updated") + " : $oldv -> $newv") }
      elseif ($oldv) { Ok ((T "Addon réinstallé" "Addon reinstalled") + " ($newv)") }
      else { Ok ((T "Addon installé" "Addon installed") + " ($newv)") }
      Info $Dest
    } catch {
      if (Test-Path $staging) { Remove-Item -Recurse -Force $staging -ErrorAction SilentlyContinue }
      $R.addon = "fail"; Fail ((T "Copie impossible dans " "Could not copy into ") + "$AddonsDir : " + $_.Exception.Message)
    }
  }

  # ---------- le plugin ----------
  Step (T "Installation du plugin dans Claude Code" "Installing the plugin in Claude Code")
  if (-not $Claude) {
    $R.plugin = "skip"; Warn (T "Étape passée (Claude Code absent)." "Step skipped (Claude Code missing).")
  } else {
    $markets = (& $Claude plugin marketplace list 2>$null) -join "`n"
    if ($markets -match "(?m)(^|\s)$([regex]::Escape($MarketName))\s*$") {
      $null = & $Claude plugin marketplace update $MarketName 2>&1
      if ($LASTEXITCODE -eq 0) { Ok (T "Marketplace mise à jour." "Marketplace updated.") }
      else { Warn (T "Mise à jour de la marketplace impossible (réseau ?)." "Could not update the marketplace (network?).") }
    } else {
      $out = & $Claude plugin marketplace add $MarketSource 2>&1
      if ($LASTEXITCODE -eq 0) { Ok ((T "Marketplace ajoutée" "Marketplace added") + " ($MarketSource)") }
      else { Fail ((T "Ajout de la marketplace impossible : " "Could not add the marketplace: ") + ($out | Select-Object -Last 1)) }
    }
    $plugins = (& $Claude plugin list 2>$null) -join "`n"
    if ($plugins -match [regex]::Escape($PluginId)) {
      $out = & $Claude plugin update $PluginId 2>&1
      if ($LASTEXITCODE -eq 0) { $R.plugin = "ok"; Ok (T "Plugin mis à jour (redémarre Claude Code pour en profiter)." "Plugin updated (restart Claude Code to use it).") }
      else { $R.plugin = "fail"; Fail ((T "Mise à jour du plugin impossible : " "Could not update the plugin: ") + ($out | Select-Object -Last 1)) }
    } else {
      $out = & $Claude plugin install $PluginId 2>&1
      if ($LASTEXITCODE -eq 0) {
        $R.plugin = "ok"; Ok ((T "Plugin installé" "Plugin installed") + " ($PluginId)")
        Info (T "Si Claude Code était ouvert, redémarre-le." "If Claude Code was open, restart it.")
      } else { $R.plugin = "fail"; Fail ((T "Installation du plugin impossible : " "Could not install the plugin: ") + ($out | Select-Object -Last 1)) }
    }
  }

  # ---------- dossier du joueur et outils ----------
  Step (T "Ton dossier de joueur" "Your player folder")
  try {
    $null = New-Item -ItemType Directory -Force -Path (Join-Path $DataDir "perso") -ErrorAction Stop
    $claudeMd = Join-Path $DataDir "CLAUDE.md"
    if (Test-Path $claudeMd) { Ok ((T "Dossier existant gardé tel quel" "Existing folder kept as is") + " : $DataDir") }
    else {
      $tpl = (J $Src "perso.example" "CLAUDE.md")
      $en = (J $Src "perso.example" "CLAUDE.example.en.md")
      if ($script:L -eq "en" -and (Test-Path $en)) { $tpl = $en }
      Copy-Item $tpl $claudeMd -ErrorAction Stop
      Ok ((T "Dossier créé" "Folder created") + " : $DataDir")
    }
    $R.data = "ok"
  } catch { $R.data = "fail"; Fail ((T "Impossible de créer " "Could not create ") + $DataDir) }
  if ($Src -ne $App) {
    try {
      $staging = "$App.tmp-install"
      if (Test-Path $staging) { Remove-Item -Recurse -Force $staging }
      $null = New-Item -ItemType Directory -Force -Path $staging
      foreach ($part in "plugins", "tools", "install") { Copy-Item -Recurse (Join-Path $Src $part) (Join-Path $staging $part) -ErrorAction Stop }
      if (Test-Path (Join-Path $Src "LICENSE")) { Copy-Item (Join-Path $Src "LICENSE") $staging }
      if (Test-Path $App) { Remove-Item -Recurse -Force $App -ErrorAction Stop }
      Move-Item $staging $App -ErrorAction Stop
      Info ((T "Outils gardés dans" "Tools kept in") + " : $App")
    } catch { Warn ((T "Copie des outils impossible dans " "Could not copy the tools into ") + $App) }
  }

  # ---------- base locale ----------
  Step (T "Base locale du jeu" "Local game database")
  $Build = (J $App "tools" "gamedata" "build_db.py")
  if (-not (Test-Path $Build)) { $Build = (J $Src "tools" "gamedata" "build_db.py") }
  $Root = if ($Wow) { Split-Path $Wow -Parent } else { $null }
  if (-not $Root) { $R.db = "skip"; Warn (T "Étape passée (jeu introuvable)." "Step skipped (game not found).") }
  elseif ($NoDb) { $R.db = "skip"; Info (T "Étape passée (-NoDb)." "Step skipped (-NoDb).") }
  else {
    Info (T "Elle donne au compagnon les objets, quêtes, PNJ, /way et cartes de TON client. Lecture seule du jeu ; télécharge une fois CascLib et QuestieDB ; quelques minutes." "It gives the companion the items, quests, NPCs, /way and maps of YOUR client. Reads the game only; downloads CascLib and QuestieDB once; a few minutes.")
    if (AskYes (T "Construire (ou mettre à jour) la base maintenant ?" "Build (or update) the database now?") $true $true) {
      & $Py $Build --wow $Root --data-dir $DataDir | Out-Host
      if ($LASTEXITCODE -eq 0) { $R.db = "ok"; Ok (T "Base prête." "Database ready.") }
      else { $R.db = "fail"; Warn (T "La construction a échoué ; le compagnon marche quand même, en moins précis." "The build failed; the companion still works, with less detail.") }
    } else { $R.db = "later"; Info ((T "Plus tard" "Later") + " : & ""$Py"" ""$Build"" --wow ""$Root""") }
  }

  # ---------- récapitulatif ----------
  function Mark([string]$s, [string]$label) {
    switch ($s) {
      { $_ -in "ok", "dev" } { Write-Host "  √ " -ForegroundColor Green -NoNewline }
      "fail" { Write-Host "  x " -ForegroundColor Red -NoNewline }
      default { Write-Host "  - " -ForegroundColor Yellow -NoNewline }
    }
    Write-Host $label
  }
  Write-Host ""; Write-Host (T "Récapitulatif" "Summary") -ForegroundColor White
  Mark $R.addon (T "Addon ForeverScribe" "ForeverScribe addon")
  Mark $R.plugin (T "Plugin Claude Code" "Claude Code plugin")
  Mark $R.data ((T "Dossier du joueur" "Player folder") + " ($DataDir)")
  Mark $R.db (T "Base locale du jeu" "Local game database")
  Write-Host ""; Write-Host (T "Et maintenant :" "Next:") -ForegroundColor White
  Write-Host ("  1. " + (T "Redémarre complètement le jeu (pas seulement /reload)." "Fully restart the game (not just /reload)."))
  Write-Host ("  2. " + (T "En jeu, appuie sur Ctrl+Maj+S (ou tape /sync)." "In game, press Ctrl+Shift+S (or type /sync)."))
  Write-Host ("  3. " + (T "Ouvre Claude Code dans ton dossier : cd ""$DataDir""; claude" "Open Claude Code in your folder: cd ""$DataDir""; claude"))
  Write-Host ("     " + (T "et demande : « Je fais quoi maintenant ? »" 'and ask: "What should I do now?"'))
  Write-Host ""

  if ($Tmp) { Remove-Item -Recurse -Force $Tmp -ErrorAction SilentlyContinue }
  if ($R.addon -eq "fail" -or $R.plugin -eq "fail" -or $R.data -eq "fail") { return 1 }
  if ($R.addon -eq "skip" -or $R.plugin -eq "skip") {
    Write-Host (T "Installation incomplète : voir les étapes marquées « - »." 'Install incomplete: see the steps marked "-".') -ForegroundColor Yellow; Write-Host ""
    return 2
  }
  Write-Host (T "Installation terminée. Bon jeu !" "All set. Have fun!") -ForegroundColor Green; Write-Host ""
  return 0
}

$ForeverCode = Install-ForeverCompanion -WowPath $WowPath -DataDir $DataDir -Lang $Lang -Yes:$Yes -NoDb:$NoDb `
  -Uninstall:$Uninstall -ScriptRoot $PSScriptRoot
if ($PSCommandPath) { exit ([int]($ForeverCode | Select-Object -Last 1)) }
