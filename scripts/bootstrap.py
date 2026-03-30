import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from engines.strategy_engine import StrategyEngine

if __name__=='__main__':
    StrategyEngine().run()
