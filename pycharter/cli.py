"""
Main CLI entry point for pycharter commands.

Provides commands like:
- pycharter db init
- pycharter db upgrade
- etc.
"""

import sys
import argparse


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PyCharter - Data Contract Management and Validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # db subcommand
    db_parser = subparsers.add_parser("db", help="Database management commands")
    db_subparsers = db_parser.add_subparsers(dest="db_command", help="Database command")
    
    # Import db CLI commands
    from pycharter.db.cli import (
        cmd_init,
        cmd_upgrade,
        cmd_downgrade,
        cmd_current,
        cmd_history,
    )
    
    # init
    init_parser = db_subparsers.add_parser("init", help="Initialize database schema from scratch")
    init_parser.add_argument("database_url", help="PostgreSQL connection string")
    init_parser.add_argument("--force", action="store_true", help="Proceed even if database appears initialized")
    
    # upgrade
    upgrade_parser = db_subparsers.add_parser("upgrade", help="Upgrade database to latest revision")
    upgrade_parser.add_argument("database_url", nargs="?", help="PostgreSQL connection string (optional if PYCHARTER_DATABASE_URL is set)")
    upgrade_parser.add_argument("--revision", default="head", help="Target revision (default: head)")
    
    # downgrade
    downgrade_parser = db_subparsers.add_parser("downgrade", help="Downgrade database to a previous revision")
    downgrade_parser.add_argument("database_url", nargs="?", help="PostgreSQL connection string (optional if PYCHARTER_DATABASE_URL is set)")
    downgrade_parser.add_argument("--revision", default="-1", help="Target revision (default: -1)")
    
    # current
    current_parser = db_subparsers.add_parser("current", help="Show current database revision")
    current_parser.add_argument("database_url", nargs="?", help="PostgreSQL connection string (optional if PYCHARTER_DATABASE_URL is set)")
    
    # history
    history_parser = db_subparsers.add_parser("history", help="Show migration history")
    history_parser.add_argument("database_url", nargs="?", help="PostgreSQL connection string (optional if PYCHARTER_DATABASE_URL is set)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == "db":
        if not args.db_command:
            db_parser.print_help()
            return 1
        
        if args.db_command == "init":
            return cmd_init(args.database_url, force=args.force)
        elif args.db_command == "upgrade":
            return cmd_upgrade(args.database_url, args.revision)
        elif args.db_command == "downgrade":
            return cmd_downgrade(args.database_url, args.revision)
        elif args.db_command == "current":
            return cmd_current(args.database_url)
        elif args.db_command == "history":
            return cmd_history(args.database_url)
        else:
            db_parser.print_help()
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

