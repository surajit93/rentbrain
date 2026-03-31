import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from engines.enhanced_system_engine import EnhancedSystemEngine

if __name__ == '__main__':
    EnhancedSystemEngine().run()
