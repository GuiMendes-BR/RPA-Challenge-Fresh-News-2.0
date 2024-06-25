import yaml
from pathlib import Path
config = yaml.safe_load(Path('robot.yaml').read_text())