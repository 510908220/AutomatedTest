from pathlib import Path

DB_NAME = "automation"
TB_TASK = "task"
TB_PENDING_CASE = "pending_case"
TB_RUNNING_CASE = "running_case"
TB_MACHINE = "machine"
CUR_DIR = Path(__file__).parent
CASES_DIR = CUR_DIR.joinpath("..").joinpath("files").joinpath("cases")
