"""
CLI commands for database management (pycharter db init, pycharter db upgrade)

Following Airflow's pattern: airflow db init, airflow db upgrade
"""

import os
import sys
import argparse
from typing import Optional

try:
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import create_engine, inspect
    from sqlalchemy.exc import OperationalError
    ALEMBIC_AVAILABLE = True
except ImportError:
    ALEMBIC_AVAILABLE = False

from pycharter.db.models.base import Base
from pycharter.config import get_database_url, set_database_url


def get_alembic_config(database_url: Optional[str] = None) -> Config:
    """
    Get Alembic configuration.
    
    Args:
        database_url: Optional database URL (if None, uses PYCHARTER_DATABASE_URL env var)
        
    Returns:
        Alembic Config object
    """
    # Get the path to alembic.ini (should be in project root)
    # __file__ is pycharter/db/cli.py, so we need to go up 3 levels
    current_file = os.path.abspath(__file__)
    # pycharter/db/cli.py -> pycharter/db -> pycharter -> project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
    alembic_ini_path = os.path.join(project_root, "alembic.ini")
    
    # Alternative: try to find it relative to current working directory
    if not os.path.exists(alembic_ini_path):
        # Try current working directory
        cwd_alembic = os.path.join(os.getcwd(), "alembic.ini")
        if os.path.exists(cwd_alembic):
            alembic_ini_path = cwd_alembic
        else:
            raise FileNotFoundError(
                f"Alembic configuration not found. Tried:\n"
                f"  - {alembic_ini_path}\n"
                f"  - {cwd_alembic}\n"
                "Make sure you're running from the project root or alembic.ini exists."
            )
    
    config = Config(alembic_ini_path)
    
    # Set database URL from argument, config, or environment variable
    if database_url:
        set_database_url(database_url)
    else:
        # Try to get from configuration
        db_url = get_database_url()
        if db_url:
            set_database_url(db_url)
        elif not os.getenv("PYCHARTER_DATABASE_URL"):
            # Last resort: try to get from alembic.ini directly
            database_url = config.get_main_option("sqlalchemy.url")
            if database_url and database_url != "driver://user:pass@localhost/dbname":
                set_database_url(database_url)
    
    return config


def cmd_init(database_url: Optional[str] = None, force: bool = False) -> int:
    """
    Initialize the database schema from scratch.
    
    Equivalent to: airflow db init
    
    Args:
        database_url: Optional PostgreSQL connection string (uses config if not provided)
        force: If True, proceed even if database appears initialized
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if not ALEMBIC_AVAILABLE:
        print("❌ Error: alembic and sqlalchemy are required. Install with: pip install alembic sqlalchemy")
        return 1
    
    try:
        # Get database URL from argument or configuration
        db_url = database_url or get_database_url()
        if not db_url:
            print("❌ Error: Database URL required.")
            print("   Provide as argument: pycharter db init <database_url>")
            print("   Or set environment variable: PYCHARTER__DATABASE__SQL_ALCHEMY_CONN or PYCHARTER_DATABASE_URL")
            print("   Or configure in pycharter.cfg or alembic.ini")
            return 1
        
        # Set environment variable for Alembic
        set_database_url(db_url)
        
        # Get Alembic config
        config = get_alembic_config(db_url)
        
        # Check if database is already initialized
        engine = create_engine(db_url)
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if "schemas" in existing_tables and not force:
            print("⚠ Warning: Database appears to already be initialized.")
            print("Use --force to proceed anyway, or run 'pycharter db upgrade' to apply migrations.")
            return 1
        
        # Create all tables using SQLAlchemy (for initial setup)
        print("Creating database tables...")
        Base.metadata.create_all(engine)
        
        # Stamp the database with the current Alembic revision
        # First, check if we have any migrations
        versions_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "migrations",
            "versions"
        )
        
        if os.path.exists(versions_dir) and os.listdir(versions_dir):
            # We have migrations, stamp with head
            print("Stamping database with Alembic version...")
            command.stamp(config, "head")
        else:
            # No migrations yet, create initial migration
            print("Creating initial migration...")
            command.revision(config, autogenerate=True, message="Initial schema")
            command.stamp(config, "head")
        
        print("✓ Database initialized successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_upgrade(database_url: Optional[str] = None, revision: str = "head") -> int:
    """
    Upgrade database to the latest revision.
    
    Equivalent to: airflow db upgrade
    
    Args:
        database_url: Optional PostgreSQL connection string (uses PYCHARTER_DATABASE_URL if not provided)
        revision: Target revision (default: "head")
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if not ALEMBIC_AVAILABLE:
        print("❌ Error: alembic and sqlalchemy are required. Install with: pip install alembic sqlalchemy")
        return 1
    
    try:
        # Get database URL from argument or configuration
        db_url = database_url or get_database_url()
        if not db_url:
            print("❌ Error: Database URL required.")
            print("   Provide as argument: pycharter db upgrade <database_url>")
            print("   Or set environment variable: PYCHARTER__DATABASE__SQL_ALCHEMY_CONN or PYCHARTER_DATABASE_URL")
            print("   Or configure in pycharter.cfg or alembic.ini")
            return 1
        
        if database_url:
            set_database_url(database_url)
        
        # Get Alembic config
        config = get_alembic_config(db_url)
        
        # Run upgrade
        print(f"Upgrading database to revision: {revision}...")
        command.upgrade(config, revision)
        
        print("✓ Database upgraded successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Error upgrading database: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_downgrade(database_url: Optional[str] = None, revision: str = "-1") -> int:
    """
    Downgrade database to a previous revision.
    
    Equivalent to: airflow db downgrade
    
    Args:
        database_url: Optional PostgreSQL connection string (uses PYCHARTER_DATABASE_URL if not provided)
        revision: Target revision (default: "-1" for one step back)
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if not ALEMBIC_AVAILABLE:
        print("❌ Error: alembic and sqlalchemy are required. Install with: pip install alembic sqlalchemy")
        return 1
    
    try:
        # Get database URL from argument or configuration
        db_url = database_url or get_database_url()
        if not db_url:
            print("❌ Error: Database URL required.")
            print("   Provide as argument: pycharter db downgrade <database_url>")
            print("   Or set environment variable: PYCHARTER__DATABASE__SQL_ALCHEMY_CONN or PYCHARTER_DATABASE_URL")
            print("   Or configure in pycharter.cfg or alembic.ini")
            return 1
        
        if database_url:
            set_database_url(database_url)
        
        config = get_alembic_config(db_url)
        
        print(f"Downgrading database to revision: {revision}...")
        command.downgrade(config, revision)
        
        print("✓ Database downgraded successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Error downgrading database: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_current(database_url: Optional[str] = None) -> int:
    """
    Show current database revision.
    
    Args:
        database_url: Optional PostgreSQL connection string
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if not ALEMBIC_AVAILABLE:
        print("❌ Error: alembic and sqlalchemy are required. Install with: pip install alembic sqlalchemy")
        return 1
    
    try:
        # Get database URL from argument or configuration
        db_url = database_url or get_database_url()
        if not db_url:
            print("❌ Error: Database URL required.")
            print("   Provide as argument: pycharter db current <database_url>")
            print("   Or set environment variable: PYCHARTER__DATABASE__SQL_ALCHEMY_CONN or PYCHARTER_DATABASE_URL")
            print("   Or configure in pycharter.cfg or alembic.ini")
            return 1
        
        if database_url:
            set_database_url(database_url)
        
        config = get_alembic_config(db_url)
        
        # Get current revision
        from alembic.script import ScriptDirectory
        from alembic.runtime.migration import MigrationContext
        from sqlalchemy import create_engine
        
        engine = create_engine(db_url)
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
        
        if current_rev:
            print(f"Current database revision: {current_rev}")
        else:
            print("Database is not initialized. Run 'pycharter db init' first.")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error getting current revision: {e}")
        return 1


def cmd_history(database_url: Optional[str] = None) -> int:
    """
    Show migration history.
    
    Args:
        database_url: Optional PostgreSQL connection string
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if not ALEMBIC_AVAILABLE:
        print("❌ Error: alembic and sqlalchemy are required. Install with: pip install alembic sqlalchemy")
        return 1
    
    try:
        if database_url:
            set_database_url(database_url)
        
        config = get_alembic_config()
        
        command.history(config)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error showing history: {e}")
        return 1


def main():
    """Main CLI entry point for pycharter db commands."""
    parser = argparse.ArgumentParser(
        description="PyCharter database management commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize database from scratch
  pycharter db init postgresql://user:pass@localhost/pycharter
  
  # Upgrade to latest version
  pycharter db upgrade postgresql://user:pass@localhost/pycharter
  
  # Upgrade using environment variable
  export PYCHARTER_DATABASE_URL=postgresql://user:pass@localhost/pycharter
  pycharter db upgrade
  
  # Show current revision
  pycharter db current postgresql://user:pass@localhost/pycharter
  
  # Show migration history
  pycharter db history
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # init command
    init_parser = subparsers.add_parser("init", help="Initialize database schema from scratch")
    init_parser.add_argument("database_url", nargs="?", help="PostgreSQL connection string (optional if configured)")
    init_parser.add_argument("--force", action="store_true", help="Proceed even if database appears initialized")
    
    # upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database to latest revision")
    upgrade_parser.add_argument("database_url", nargs="?", help="PostgreSQL connection string (optional if PYCHARTER_DATABASE_URL is set)")
    upgrade_parser.add_argument("--revision", default="head", help="Target revision (default: head)")
    
    # downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database to a previous revision")
    downgrade_parser.add_argument("database_url", nargs="?", help="PostgreSQL connection string (optional if PYCHARTER_DATABASE_URL is set)")
    downgrade_parser.add_argument("--revision", default="-1", help="Target revision (default: -1)")
    
    # current command
    current_parser = subparsers.add_parser("current", help="Show current database revision")
    current_parser.add_argument("database_url", nargs="?", help="PostgreSQL connection string (optional if PYCHARTER_DATABASE_URL is set)")
    
    # history command
    history_parser = subparsers.add_parser("history", help="Show migration history")
    history_parser.add_argument("database_url", nargs="?", help="PostgreSQL connection string (optional if PYCHARTER_DATABASE_URL is set)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == "init":
        return cmd_init(args.database_url, force=args.force)
    elif args.command == "upgrade":
        return cmd_upgrade(args.database_url, args.revision)
    elif args.command == "downgrade":
        return cmd_downgrade(args.database_url, args.revision)
    elif args.command == "current":
        return cmd_current(args.database_url)
    elif args.command == "history":
        return cmd_history(args.database_url)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

