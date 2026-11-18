"""Tests des installateurs en un clic, dans un bac à sable.

    python3 install/tests/test_installers.py        (depuis la racine du dépôt)

Chaque test crée un HOME temporaire, un faux dossier de jeu (« World of Warcraft/_forever_ »)
et un faux `claude` qui note ses arguments : rien ne touche au vrai jeu, au vrai dossier
du joueur ni au vrai Claude Code. Aucun accès réseau.

- install.sh : macOS et Linux (bash).
- install.ps1 : testé quand PowerShell est présent (pwsh, ou powershell sous Windows).
- archives de release : contenu, bit exécutable, lanceur .command.
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INSTALL_SH = ROOT / "install" / "install.sh"
INSTALL_PS1 = ROOT / "install" / "install.ps1"
sys.path.insert(0, str(ROOT / "tools" / "release"))
import build_release  # noqa: E402

PLUGIN_ID = "forever-companion@wow-forever-companion"

FAKE_CLAUDE_SH = r"""#!/bin/sh
echo "$*" >> "$CLAUDE_LOG"
case "$*" in
  "--version") echo "9.9.9 (Claude Code)" ;;
  "plugin marketplace list") echo "Configured marketplaces:"; [ -f "$CLAUDE_STATE/market" ] && echo "  ❯ wow-forever-companion" ;;
  "plugin marketplace add"*) touch "$CLAUDE_STATE/market" ;;
  "plugin marketplace remove"*) [ -f "$CLAUDE_STATE/market" ] || exit 1; rm "$CLAUDE_STATE/market" ;;
  "plugin list") echo "Installed plugins:"; [ -f "$CLAUDE_STATE/plugin" ] && echo "  ❯ forever-companion@wow-forever-companion" ;;
  "plugin install"*) touch "$CLAUDE_STATE/plugin" ;;
  "plugin uninstall"*) [ -f "$CLAUDE_STATE/plugin" ] || exit 1; rm "$CLAUDE_STATE/plugin" ;;
esac
exit 0
"""

FAKE_CLAUDE_CMD = r"""@echo off
echo %*>> "%CLAUDE_LOG%"
if "%1"=="--version" ( echo 9.9.9 ^(Claude Code^) & exit /b 0 )
if "%1 %2 %3"=="plugin marketplace list" ( if exist "%CLAUDE_STATE%\market" echo   ^> wow-forever-companion
  exit /b 0 )
if "%1 %2 %3"=="plugin marketplace add" ( type nul > "%CLAUDE_STATE%\market" & exit /b 0 )
if "%1 %2 %3"=="plugin marketplace remove" ( if not exist "%CLAUDE_STATE%\market" exit /b 1
  del "%CLAUDE_STATE%\market" & exit /b 0 )
if "%1 %2"=="plugin list" ( if exist "%CLAUDE_STATE%\plugin" echo   ^> forever-companion@wow-forever-companion
  exit /b 0 )
if "%1 %2"=="plugin install" ( type nul > "%CLAUDE_STATE%\plugin" & exit /b 0 )
if "%1 %2"=="plugin uninstall" ( if not exist "%CLAUDE_STATE%\plugin" exit /b 1
  del "%CLAUDE_STATE%\plugin" & exit /b 0 )
exit /b 0
"""


class Sandbox:
    def __init__(self, with_claude: bool = True):
        self.root = Path(tempfile.mkdtemp(prefix="forever-install-"))
        self.home = self.root / "home"
        self.bin = self.root / "bin"
        self.state = self.root / "state"
        self.game = self.root / "Games" / "World of Warcraft"
        self.flavor = self.game / "_forever_"
        self.addons = self.flavor / "Interface" / "AddOns"
        self.log = self.root / "claude.log"
        for d in (self.home, self.bin, self.state, self.addons):
            d.mkdir(parents=True)
        self.data = self.home / "WowForever"
        if with_claude:
            self.add_claude()

    def add_claude(self):
        if os.name == "nt":
            (self.bin / "claude.cmd").write_text(FAKE_CLAUDE_CMD.replace("\n", "\r\n"), encoding="ascii")
        else:
            f = self.bin / "claude"
            f.write_text(FAKE_CLAUDE_SH, encoding="utf-8")
            f.chmod(0o755)

    def env(self, **extra):
        env = dict(os.environ)
        # Seulement des dossiers sans `claude` : le faux en tête, puis les outils du système.
        system = [p for p in env.get("PATH", "").split(os.pathsep)
                  if p and not (Path(p) / "claude").exists() and not (Path(p) / "claude.exe").exists()
                  and not (Path(p) / "claude.cmd").exists()]
        env.update({
            "HOME": str(self.home), "USERPROFILE": str(self.home),
            "LOCALAPPDATA": str(self.home / "AppData" / "Local"), "XDG_DATA_HOME": str(self.home / ".local" / "share"),
            "PATH": os.pathsep.join([str(self.bin)] + system),
            "CLAUDE_LOG": str(self.log), "CLAUDE_STATE": str(self.state),
            "FOREVER_NO_TTY": "1", "FOREVER_NO_SETX": "1", "NO_COLOR": "1",
            "FOREVER_PYTHON": sys.executable,
        })
        for k in ("WOW_FOREVER_PATH", "FOREVER_HOME", "FOREVER_SOURCE_URL", "FOREVER_MARKETPLACE", "LC_ALL"):
            env.pop(k, None)
        env.update({k: str(v) for k, v in extra.items()})
        return env

    def claude_calls(self):
        return self.log.read_text(encoding="utf-8", errors="replace").splitlines() if self.log.exists() else []

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


def run_sh(sb: Sandbox, *args, script: Path = INSTALL_SH, stdin=None, **env):
    return subprocess.run(["bash", str(script), *args], env=sb.env(**env), capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=120, input=stdin)


@unittest.skipIf(os.name == "nt" or not shutil.which("bash"), "bash requis")
class TestInstallSh(unittest.TestCase):
    def setUp(self):
        self.sb = Sandbox()
        self.addCleanup(self.sb.cleanup)

    def install(self, *extra, **env):
        return run_sh(self.sb, "--wow-path", str(self.sb.game), "--no-db", "--lang", "fr", *extra, **env)

    def test_fresh_install(self):
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        toc = self.sb.addons / "ForeverScribe" / "ForeverScribe.toc"
        self.assertTrue(toc.is_file())
        calls = self.sb.claude_calls()
        self.assertIn("plugin marketplace add ArmanetPierre/wow-forever-companion", calls)
        self.assertIn(f"plugin install {PLUGIN_ID}", calls)
        self.assertTrue((self.sb.data / "CLAUDE.md").is_file())
        self.assertTrue((self.sb.data / "perso").is_dir())
        self.assertIn("Installation terminée", r.stdout)
        self.assertIn("[6/6]", r.stdout)
        # Rien d'autre n'est écrit dans le dossier du jeu.
        self.assertEqual(sorted(p.name for p in self.sb.flavor.iterdir()), ["Interface"])
        self.assertEqual(sorted(p.name for p in self.sb.addons.iterdir()), ["ForeverScribe"])

    def test_game_found_from_flavor_folder_and_english(self):
        r = run_sh(self.sb, "--wow-path", str(self.sb.flavor), "--no-db", "--lang", "en")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("All set", r.stdout)
        self.assertTrue((self.sb.addons / "ForeverScribe").is_dir())
        en = (ROOT / "perso.example" / "CLAUDE.example.en.md").read_text(encoding="utf-8")
        self.assertEqual((self.sb.data / "CLAUDE.md").read_text(encoding="utf-8"), en)   # modèle anglais

    def test_update_replaces_addon_and_keeps_player_data(self):
        self.assertEqual(self.install().returncode, 0)
        stale = self.sb.addons / "ForeverScribe" / "ancien-fichier.lua"
        stale.write_text("-- vieux", encoding="utf-8")
        (self.sb.data / "CLAUDE.md").write_text("mes notes à moi", encoding="utf-8")
        (self.sb.data / "perso" / "config.json").write_text("{}", encoding="utf-8")
        self.sb.log.unlink()
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(stale.exists())
        self.assertIn("Addon réinstallé", r.stdout)
        calls = self.sb.claude_calls()
        self.assertIn("plugin marketplace update wow-forever-companion", calls)
        self.assertIn(f"plugin update {PLUGIN_ID}", calls)
        self.assertNotIn(f"plugin install {PLUGIN_ID}", calls)
        self.assertEqual((self.sb.data / "CLAUDE.md").read_text(encoding="utf-8"), "mes notes à moi")
        self.assertTrue((self.sb.data / "perso" / "config.json").is_file())

    def test_uninstall_keeps_player_data(self):
        self.assertEqual(self.install().returncode, 0)
        (self.sb.data / "perso" / "capture.lua").write_text("x", encoding="utf-8")
        r = run_sh(self.sb, "--uninstall", "--wow-path", str(self.sb.game), "--lang", "fr")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.sb.addons / "ForeverScribe").exists())
        calls = self.sb.claude_calls()
        self.assertIn(f"plugin uninstall {PLUGIN_ID}", calls)
        self.assertIn("plugin marketplace remove wow-forever-companion", calls)
        self.assertTrue((self.sb.data / "CLAUDE.md").is_file())
        self.assertTrue((self.sb.data / "perso" / "capture.lua").is_file())
        self.assertFalse((self.sb.home / "Library" / "Application Support" / "WoW Forever Companion").exists())
        self.assertFalse((self.sb.home / ".local" / "share" / "wow-forever-companion").exists())

    def test_dev_symlink_left_alone(self):
        target = self.sb.root / "dev-addon"
        target.mkdir()
        (self.sb.addons / "ForeverScribe").symlink_to(target)
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.sb.addons / "ForeverScribe").is_symlink())
        self.assertIn("Lien de développement", r.stdout)

    def test_missing_claude_installs_nothing_third_party(self):
        sb = Sandbox(with_claude=False)
        self.addCleanup(sb.cleanup)
        r = run_sh(sb, "--wow-path", str(sb.game), "--no-db", "--lang", "fr")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("Claude Code est introuvable", r.stdout)
        self.assertIn("réponse par défaut", r.stdout)    # la question n'a pas été répondue « oui »
        self.assertTrue((sb.addons / "ForeverScribe").is_dir())
        self.assertIn("Installation incomplète", r.stdout)

    def test_python_too_old_stops_before_any_change(self):
        fake = self.sb.bin / "vieux-python"
        fake.write_text("#!/bin/sh\necho '3 8'\n", encoding="utf-8")
        fake.chmod(0o755)
        r = self.install(FOREVER_PYTHON=str(fake))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("3.9", r.stdout)
        self.assertFalse((self.sb.addons / "ForeverScribe").exists())
        self.assertFalse(self.sb.data.exists())
        self.assertEqual(self.sb.claude_calls(), [])

    def test_game_not_found(self):
        r = run_sh(self.sb, "--wow-path", str(self.sb.root / "nulle-part"), "--no-db", "--lang", "fr")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("Jeu introuvable", r.stdout)
        self.assertEqual(list(self.sb.addons.iterdir()), [])

    def test_curl_pipe_bash_downloads_archive(self):
        # Archive du dépôt façon GitHub (dossier racine « <dépôt>-main/ »), servie en file://
        tgz = self.sb.root / "main.tar.gz"
        files = build_release.payload(build_release.repo_files(ROOT))
        with tarfile.open(tgz, "w:gz") as t:
            for f in files:
                t.add(ROOT / f, arcname=f"wow-forever-companion-main/{f}")
        script = INSTALL_SH.read_text(encoding="utf-8")
        r = subprocess.run(["bash", "-s", "--", "--wow-path", str(self.sb.game), "--no-db", "--lang", "fr"],
                           input=script, env=self.sb.env(FOREVER_SOURCE_URL=tgz.as_uri()), capture_output=True,
                           text=True, encoding="utf-8", timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Téléchargement", r.stdout)
        self.assertTrue((self.sb.addons / "ForeverScribe" / "ForeverScribe.toc").is_file())

    def test_help(self):
        r = run_sh(self.sb, "--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("--uninstall", r.stdout)


def powershell():
    for exe in ("pwsh", "powershell"):
        p = shutil.which(exe)
        if p:
            return p
    return None


@unittest.skipIf(powershell() is None, "PowerShell absent (testé par la CI Windows)")
class TestInstallPs1(unittest.TestCase):
    def setUp(self):
        self.sb = Sandbox()
        self.addCleanup(self.sb.cleanup)

    def run_ps(self, *args, **env):
        return subprocess.run([powershell(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(INSTALL_PS1),
                               *args], env=self.sb.env(**env), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=180)

    def test_install_update_uninstall(self):
        r = self.run_ps("-WowPath", str(self.sb.game), "-NoDb", "-Lang", "fr")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.sb.addons / "ForeverScribe" / "ForeverScribe.toc").is_file())
        self.assertTrue((self.sb.data / "CLAUDE.md").is_file())
        calls = " | ".join(self.sb.claude_calls())
        self.assertIn(f"plugin install {PLUGIN_ID}", calls)

        (self.sb.data / "CLAUDE.md").write_text("à moi", encoding="utf-8")
        r = self.run_ps("-WowPath", str(self.sb.game), "-NoDb", "-Lang", "fr")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn(f"plugin update {PLUGIN_ID}", " | ".join(self.sb.claude_calls()))
        self.assertEqual((self.sb.data / "CLAUDE.md").read_text(encoding="utf-8"), "à moi")

        r = self.run_ps("-Uninstall", "-WowPath", str(self.sb.game), "-Lang", "fr")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.sb.addons / "ForeverScribe").exists())
        self.assertTrue((self.sb.data / "CLAUDE.md").is_file())

    def test_missing_claude(self):
        sb = Sandbox(with_claude=False)
        self.addCleanup(sb.cleanup)
        r = subprocess.run([powershell(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(INSTALL_PS1),
                            "-WowPath", str(sb.game), "-NoDb", "-Lang", "en"], env=sb.env(), capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=180)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("Claude Code was not found", r.stdout)
        self.assertTrue((sb.addons / "ForeverScribe").is_dir())


class TestReleaseArchives(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = Path(tempfile.mkdtemp(prefix="forever-release-"))
        cls.zips = {p.name: p for p in build_release.build(cls.out)}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.out, ignore_errors=True)

    def test_names_match_the_download_contract(self):
        self.assertEqual(set(self.zips), {"WoW-Forever-Companion-macOS.zip", "WoW-Forever-Companion-Windows.zip"})

    def test_content_and_no_player_data(self):
        for name, path in self.zips.items():
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
            top = "WoW Forever Companion/"
            launcher = "Installer WoW Forever Companion." + ("command" if "macOS" in name else "cmd")
            self.assertIn(top + launcher, names)
            for needed in ("files/addon/ForeverScribe/ForeverScribe.toc", "files/install/install.sh",
                           "files/install/install.ps1", "files/tools/gamedata/build_db.py",
                           "files/plugins/forever-companion/mcp/wowpaths.py", "files/perso.example/CLAUDE.md"):
                self.assertIn(top + needed, names)
            for n in names:
                self.assertNotIn("/perso/", n)
                self.assertNotIn("/tests/", n)
                self.assertFalse(n.endswith((".sqlite", ".db2")), n)

    def test_unix_permissions(self):
        with zipfile.ZipFile(self.zips["WoW-Forever-Companion-macOS.zip"]) as z:
            mode = lambda n: (z.getinfo("WoW Forever Companion/" + n).external_attr >> 16) & 0o777
            self.assertEqual(mode("Installer WoW Forever Companion.command"), 0o755)
            self.assertEqual(mode("files/install/install.sh"), 0o755)
            self.assertEqual(mode("files/addon/ForeverScribe/ForeverScribe.toc"), 0o644)

    def test_windows_launcher_crlf(self):
        with zipfile.ZipFile(self.zips["WoW-Forever-Companion-Windows.zip"]) as z:
            cmd = z.read("WoW Forever Companion/Installer WoW Forever Companion.cmd")
            ps1 = z.read("WoW Forever Companion/files/install/install.ps1")
        self.assertIn(b"\r\n", cmd)
        self.assertNotIn(b"\r\r", cmd)
        self.assertIn(b'files\\install\\install.ps1', cmd)
        self.assertTrue(ps1.startswith(b"\xef\xbb\xbf"), "BOM UTF-8 requis pour PowerShell 5.1")

    @unittest.skipIf(os.name == "nt" or not shutil.which("unzip"), "unzip requis")
    def test_mac_launcher_runs_from_unzipped_archive(self):
        sb = Sandbox()
        self.addCleanup(sb.cleanup)
        dest = sb.root / "Téléchargements"
        dest.mkdir()
        subprocess.run(["unzip", "-q", str(self.zips["WoW-Forever-Companion-macOS.zip"]), "-d", str(dest)], check=True)
        launcher = dest / "WoW Forever Companion" / "Installer WoW Forever Companion.command"
        self.assertTrue(os.stat(launcher).st_mode & stat.S_IXUSR)
        r = subprocess.run([str(launcher), "--wow-path", str(sb.game), "--no-db", "--lang", "fr"], env=sb.env(),
                           capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((sb.addons / "ForeverScribe" / "ForeverScribe.toc").is_file())
        self.assertIn("Entrée pour fermer", r.stdout)


if __name__ == "__main__":
    unittest.main()
