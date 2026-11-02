#!/usr/bin/env python3
"""
Script de packaging Windows 64 bits (PRD Section 10.1 & 10.2).
Compile PDF Unlocker MVP 1.0 en exécutable autonome (.exe) avec PyInstaller
et génère automatiquement le fichier d'empreinte SHA-256 pour vérification d'intégrité.
"""

import hashlib
import subprocess
import sys
from pathlib import Path


def compute_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_pyinstaller():
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("[*] Installation de PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller>=6.0.0"], check=True)


def build_executable():
    ensure_pyinstaller()
    root = Path(__file__).resolve().parent
    entry = root / "pdf_unlocker.py"
    icon = root / "assets" / "app_icon.ico"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--onefile",
        "--name",
        "PDF_Unlocker_MVP_1.0",
        "--add-data",
        f"{root / 'assets'};assets",
        "--collect-all",
        "customtkinter",
        "--collect-all",
        "pikepdf",
    ]
    if icon.exists():
        cmd.extend(["--icon", str(icon)])
    cmd.append(str(entry))

    print("[*] Compilation PyInstaller en cours...")
    subprocess.run(cmd, check=True, cwd=str(root))

    exe_path = root / "dist" / "PDF_Unlocker_MVP_1.0.exe"
    if exe_path.exists():
        sha256 = compute_sha256(exe_path)
        checksum_file = root / "dist" / "PDF_Unlocker_MVP_1.0.exe.sha256"
        checksum_file.write_text(f"{sha256}  {exe_path.name}\n", encoding="utf-8")
        print(f"[OK] Executable genere : {exe_path}")
        print(f"[OK] SHA-256 : {sha256}")
        print(f"[OK] Fichier checksum : {checksum_file}")


if __name__ == "__main__":
    build_executable()

