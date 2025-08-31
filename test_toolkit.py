#!/usr/bin/env python3
"""
Test script for SP-404 MK2 Toolkit
Validates that all tools are working correctly
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from sp404_toolkit import PadConfig, PatternFile, SP404MK2Error
        print("✅ sp404_toolkit imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import sp404_toolkit: {e}")
        return False
    
    try:
        from pattern_editor import AdvancedPatternParser
        print("✅ pattern_editor imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pattern_editor: {e}")
        return False
    
    return True

def test_padconf_operations():
    """Test PADCONF file operations"""
    print("\n🧪 Testing PADCONF operations...")
    
    # Find a PADCONF file to test with
    padconf_files = list(Path('padconf').glob('PADCONF*.BIN'))
    if not padconf_files:
        print("❌ No PADCONF files found for testing")
        return False
    
    test_file = str(padconf_files[0])
    print(f"📁 Using test file: {test_file}")
    
    try:
        from sp404_toolkit import PadConfig
        
        # Test reading pad info
        padconf = PadConfig(test_file)
        info = padconf.get_pad_info(1)
        print(f"✅ Read pad 1 info: BPM={info['bpm']:.2f}, Volume={info['volume']}")
        
        # Test listing all pads (just first 3)
        all_pads = padconf.list_all_pads()[:3]
        print(f"✅ Listed {len(all_pads)} pads successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ PADCONF test failed: {e}")
        return False

def test_pattern_operations():
    """Test pattern file operations"""
    print("\n🧪 Testing pattern operations...")
    
    # Find a pattern file to test with
    pattern_files = list(Path('pattern').glob('PTN*.BIN'))
    if not pattern_files:
        print("❌ No pattern files found for testing")
        return False
    
    test_file = str(pattern_files[0])
    print(f"📁 Using test file: {test_file}")
    
    try:
        from pattern_editor import AdvancedPatternParser
        from sp404_toolkit import PatternFile
        
        # Test pattern analysis
        parser = AdvancedPatternParser(test_file)
        summary = parser.get_pattern_summary()
        print(f"✅ Analyzed pattern: {summary['num_events']} events, {summary['file_size']} bytes")
        
        # Test basic pattern file operations
        pattern = PatternFile(test_file)
        basic_info = pattern.get_pattern_info()
        print(f"✅ Basic pattern info: {basic_info['file_size']} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Pattern test failed: {e}")
        return False

def test_cli_tools():
    """Test that CLI tools are executable"""
    print("\n🧪 Testing CLI tool executability...")
    
    tools = [
        'sp404_toolkit.py',
        'pattern_editor.py',
        'web_interface.py'
    ]
    
    all_good = True
    for tool in tools:
        if os.path.exists(tool) and os.access(tool, os.X_OK):
            print(f"✅ {tool} is executable")
        else:
            print(f"❌ {tool} is not executable or doesn't exist")
            all_good = False
    
    return all_good

def test_web_dependencies():
    """Test web interface dependencies"""
    print("\n🧪 Testing web interface dependencies...")
    
    try:
        import flask
        print(f"✅ Flask {flask.__version__} available")
        return True
    except ImportError:
        print("❌ Flask not available - run: pip3 install flask")
        return False

def run_all_tests():
    """Run all tests"""
    print("🎛️ SP-404 MK2 Toolkit Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_cli_tools,
        test_padconf_operations,
        test_pattern_operations,
        test_web_dependencies
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The toolkit is ready to use.")
        print("\n🚀 Next steps:")
        print("  1. Try: ./sp404_toolkit.py --help")
        print("  2. Or start web interface: ./web_interface.py")
        print("  3. Or explore with: jupyter notebook SP404_MK2_Explorer.ipynb")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("💡 Try running: ./setup.sh")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)