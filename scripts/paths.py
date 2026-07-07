from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
POWERBI_DIR = DATA_DIR / "powerbi"
DB_DIR = DATA_DIR / "db"
REPORTS_DIR = PROJECT_ROOT / "reports"
SQL_DIR = PROJECT_ROOT / "sql"


def project_path(*parts: str) -> Path:
    return PROJECT_ROOT.joinpath(*parts)


def display_path(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()
