"""import sys

Test script to verify all required packages are installed correctly.try:

Run this before starting the main application.    import pdfplumber

    import fitz

Usage: python test_imports.py    import pandas

"""    import dateutil

    print('IMPORTS OK')

import sysexcept Exception as e:

    print('IMPORT ERROR:', e)

def test_imports():    sys.exit(2)

    """Test if all required packages can be imported."""
    
    print("="*60)
    print("Credit Card Parser - Package Import Test")
    print("="*60)
    print("\nTesting package imports...\n")
    
    packages = [
        ("pdfplumber", "pdfplumber"),
        ("PyMuPDF", "fitz"),
        ("streamlit", "streamlit"),
        ("pandas", "pandas"),
        ("python-dateutil", "dateutil"),
    ]
    
    all_success = True
    failed_packages = []
    
    for package_name, import_name in packages:
        try:
            module = __import__(import_name)
            version = getattr(module, "__version__", "unknown")
            print(f"[OK]  {package_name:20s} (version: {version})")
        except ImportError as e:
            print(f"[FAIL] {package_name:20s}")
            all_success = False
            failed_packages.append(package_name)
    
    print("\n" + "="*60)
    
    if all_success:
        print("SUCCESS: All packages installed correctly")
        print("\n" + "="*60)
        print("You can now run the application:")
        print("  streamlit run app.py")
        print("="*60)
    else:
        print("ERROR: Some packages are missing")
        print("\nFailed packages:", ", ".join(failed_packages))
        print("\n" + "="*60)
        print("To install missing packages, run:")
        print("  pip install -r requirements.txt")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    try:
        test_imports()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
