import sys
import subprocess
import os
from pathlib import Path

def get_venv_python():
    # Busca la carpeta venv relativa a la raíz del proyecto
    project_root = Path(__file__).parent.parent  # Sube un nivel desde management/
    venv_dir = project_root / "venv"
    if os.name == "nt":  # Windows
        return venv_dir / "Scripts" / "python.exe"
    else:  # Linux/macOS
        return venv_dir / "bin" / "python"

def run_alembic(args):
    venv_python = str(get_venv_python())
    if not Path(venv_python).exists():
        print(f"ERROR: No se encontró el ejecutable de Python en el entorno virtual: {venv_python}")
        sys.exit(1)
    subprocess.run([venv_python, "-m", "alembic"] + args, check=True)

def main():
    if len(sys.argv) < 2:
        print("Uso: python management/migrate.py \"mensaje de la migración\"")
        sys.exit(1)
    message = sys.argv[1]
    run_alembic(["revision", "--autogenerate", "-m", message])
    run_alembic(["upgrade", "head"])

if __name__ == "__main__":
    main()
