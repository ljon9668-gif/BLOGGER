#!/usr/bin/env python3
"""
Setup Verification Script
Checks if all dependencies and configurations are correct
"""

import sys
import os

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11 or higher required")
        return False

    print("✅ Python version OK")
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    required = [
        'supabase',
        'dotenv',
        'feedparser',
        'requests',
        'trafilatura',
        'bs4',
        'google.genai',
        'googleapiclient',
        'pandas',
        'streamlit'
    ]

    missing = []

    for package in required:
        try:
            if package == 'bs4':
                __import__('bs4')
            elif package == 'google.genai':
                __import__('google.genai')
            elif package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing.append(package)

    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("\nInstall with: pip install -r requirements.txt")
        return False

    print("\n✅ All dependencies installed")
    return True

def check_env_file():
    """Check if .env file exists and has required keys"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False

    print("✅ .env file exists")

    from dotenv import load_dotenv
    load_dotenv()

    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY',
        'GEMINI_API_KEY',
        'BLOGGER_API_KEY'
    ]

    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            print(f"❌ {var} (not set)")
            missing.append(var)
        else:
            masked = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var} = {masked}")

    if missing:
        print(f"\n❌ Missing environment variables: {', '.join(missing)}")
        return False

    print("\n✅ All environment variables set")
    return True

def check_database_connection():
    """Check Supabase database connection"""
    try:
        from dotenv import load_dotenv
        from supabase import create_client

        load_dotenv()

        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_ANON_KEY')

        if not url or not key:
            print("❌ Supabase credentials not found in .env")
            return False

        client = create_client(url, key)

        # Try to query the sources table
        response = client.table('sources').select('*').limit(1).execute()

        print("✅ Supabase connection successful")
        print(f"   Database tables: sources, posts")
        return True

    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
        return False

def check_files():
    """Check if all required files exist"""
    required_files = [
        'app.py',
        'blog_migration_cli.py',
        'blog_migration_colab.ipynb',
        'database.py',
        'content_extractor.py',
        'ai_rewriter.py',
        'blogger_publisher.py',
        'scheduler.py',
        'utils.py',
        'requirements.txt',
        'README.md'
    ]

    missing = []

    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (missing)")
            missing.append(file)

    if missing:
        print(f"\n❌ Missing files: {', '.join(missing)}")
        return False

    print("\n✅ All required files present")
    return True

def main():
    """Run all checks"""
    print("="*60)
    print("🔍 Blog Migration Tool - Setup Verification")
    print("="*60)
    print()

    checks = [
        ("Python Version", check_python_version),
        ("Required Files", check_files),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_env_file),
        ("Database Connection", check_database_connection)
    ]

    results = []

    for name, check_func in checks:
        print(f"\n{'='*60}")
        print(f"Checking: {name}")
        print('-'*60)

        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error during check: {str(e)}")
            results.append((name, False))

    print(f"\n{'='*60}")
    print("📊 Summary")
    print('='*60)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    all_passed = all(result for _, result in results)

    print('='*60)

    if all_passed:
        print("\n🎉 All checks passed! You're ready to use the tool.")
        print("\nNext steps:")
        print("  1. Run web interface: streamlit run app.py")
        print("  2. Run CLI: python blog_migration_cli.py")
        print("  3. Use Colab: Upload blog_migration_colab.ipynb")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install packages: pip install -r requirements.txt")
        print("  - Check .env file has all API keys")
        print("  - Verify Supabase project is active")

    print()
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
