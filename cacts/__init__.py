""" Main entry point for cacts"""

from cacts.cacts import main as cacts_main
from cacts.get_mach_env import print_mach_env

__version__ = "0.2.0"

def main() -> None:
    cacts_main()

def get_mach_env() -> None:
    print_mach_env()
