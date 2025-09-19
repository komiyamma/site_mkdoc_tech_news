import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import macros.home as mod
print('ok', Path(mod.__file__).resolve())
