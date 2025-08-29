#!/usr/bin/env python3
"""
Development script for SkyPost
"""

import sys
import os
import subprocess
import asyncio

def install_dependencies():
    """Install project dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def setup_environment():
    """Set up environment file."""
    if not os.path.exists('.env'):
        print("📋 Creating .env file from template...")
        try:
            subprocess.run(["cp", ".env.example", ".env"], check=True)
            print("✅ Created .env file. Please update it with your settings.")
        except subprocess.CalledProcessError:
            print("❌ Failed to create .env file")
    else:
        print("✅ .env file already exists")

def run_development_server():
    """Run the development server."""
    print("🚀 Starting development server...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")

def run_database_setup():
    """Set up the database."""
    print("🔧 Setting up database...")
    try:
        subprocess.run([sys.executable, "db_setup.py", "setup"], check=True)
        print("✅ Database setup completed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Database setup failed: {e}")

def create_sample_data():
    """Create sample users."""
    print("👥 Creating sample data...")
    try:
        subprocess.run([sys.executable, "db_setup.py", "sample_users"], check=True)
        print("✅ Sample data created!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create sample data: {e}")

def show_help():
    """Show help information."""
    print("""
🌟 SkyPost Development Script

Available commands:
  install       Install project dependencies
  setup         Set up environment and database
  run           Start the development server
  db-setup      Set up database tables
  sample-data   Create sample users for testing
  help          Show this help message

Examples:
  python dev.py install
  python dev.py setup
  python dev.py run
  python dev.py db-setup
  python dev.py sample-data

For quick start:
  1. python dev.py install
  2. python dev.py setup
  3. Update .env file with your database settings
  4. python dev.py db-setup
  5. python dev.py sample-data
  6. python dev.py run
    """)

def main():
    """Main function."""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "install":
        install_dependencies()
    elif command == "setup":
        setup_environment()
        print("\n📝 Next steps:")
        print("1. Update .env file with your database settings")
        print("2. Run: python dev.py db-setup")
        print("3. Run: python dev.py sample-data")
        print("4. Run: python dev.py run")
    elif command == "run":
        run_development_server()
    elif command == "db-setup":
        run_database_setup()
    elif command == "sample-data":
        create_sample_data()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
