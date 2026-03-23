import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

for script in ['collect_steam.py', 'collect_reddit.py']:
    print(f'==> running {script}')
    subprocess.run([sys.executable, str(BASE / script)], check=True)

print('collection complete')
