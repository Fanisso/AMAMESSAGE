import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from migrations.create_forwarding_tables import run_migration

if __name__ == "__main__":
    run_migration()
