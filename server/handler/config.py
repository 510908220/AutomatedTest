from pathlib import Path
DB_NAME = "automation"
TB_TASK ="tasks"
CUR_DIR = Path(__file__).parent
CASES_DIR = CUR_DIR.joinpath("..").joinpath("files").joinpath("cases")
