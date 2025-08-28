#!/usr/bin/env python3
"""
Simple test script for the enhanced i3-help.py functionality.
Tests search term generation, synonym expansion, and categorization.
"""

import sys
from pathlib import Path
import json

# Add the script directory to path so we can import the helper
sys.path.insert(0, str(Path(__file__).parent))

# Import the class with the correct module name
sys.path.insert(0, str(Path(__file__).parent))
exec(open(Path(__file__).parent / 'i3-help.py').read())

def test_search_terms():
    """Test search term generation with synonyms and intents"""
    print("=== Testing Search Term Generation ===")
    
    helper = I3KeybindingHelper()
    
    # Test binding examples
    test_bindings = [
        {
            'description': 'Screenshot - Full screen',
            'key': 'Print',
            'command': 'exec --no-startup-id ~/.config/i3/scripts/screenshot.sh full',
            'line': 1,
            'search_text': '',
            'category': '',
            'subcategory': ''
        },
        {
            'description': 'Volume up',
            'key': 'XF86AudioRaiseVolume',
            'command': 'exec --no-startup-id pactl set-sink-volume @DEFAULT_SINK@ +5%',
            'line': 2,
            'search_text': '',
            'category': '',
            'subcategory': ''
        },
        {
            'description': 'Launch browser',
            'key': 'Super+Shift+b',
            'command': 'exec brave || firefox',
            'line': 3,
            'search_text': '',
            'category': '',
            'subcategory': ''
        }
    ]
    
    for binding in test_bindings:
        search_terms = helper.generate_search_terms(binding)
        print(f"Binding: {binding['description']}")
        print(f"Search terms: {search_terms}")
        print(f"Key words: {len(search_terms.split())} terms")
        
        # Check if synonyms are included
        if "snapshot" in search_terms and "capture" in search_terms:
            print("✓ Screenshot synonyms found")
        if "sound" in search_terms or "audio" in search_terms:
            print("✓ Volume synonyms found")  
        if "web" in search_terms or "internet" in search_terms:
            print("✓ Browser synonyms found")
        
        print()

def test_typo_correction():
    """Test typo correction functionality"""
    print("=== Testing Typo Correction ===")
    
    helper = I3KeybindingHelper()
    
    test_typos = [
        "sceenshot",
        "volme up", 
        "broswer",
        "workspce"
    ]
    
    for typo in test_typos:
        corrected = helper.correct_typos(typo)
        print(f"'{typo}' → '{corrected}'")

def test_intent_mapping():
    """Test intent mapping functionality"""
    print("=== Testing Intent Mapping ===")
    
    helper = I3KeybindingHelper()
    
    test_cases = [
        ("exec firefox", "Launch browser"),
        ("exec --no-startup-id flameshot gui", "Interactive screenshot"),
        ("pactl set-sink-volume", "Volume control"),
        ("playerctl play-pause", "Media control")
    ]
    
    for command, description in test_cases:
        intents = helper.map_intents(command, description)
        print(f"Command: {command}")
        print(f"Description: {description}")
        print(f"Mapped intents: {intents}")
        print()

def test_dictionaries_loaded():
    """Test that dictionaries are properly loaded"""
    print("=== Testing Dictionary Loading ===")
    
    helper = I3KeybindingHelper()
    
    print(f"Synonyms loaded: {len(helper.synonyms)} entries")
    print(f"Intents loaded: {len(helper.intents)} entries") 
    print(f"Typos loaded: {len(helper.typos)} entries")
    
    # Show some examples
    if helper.synonyms:
        print(f"Sample synonyms: {list(helper.synonyms.keys())[:5]}")
    if helper.intents:
        print(f"Sample intents: {list(helper.intents.keys())[:3]}")

def main():
    print("Enhanced i3-help.py Test Suite")
    print("=" * 50)
    
    try:
        test_dictionaries_loaded()
        print()
        test_search_terms()
        test_typo_correction()
        print()
        test_intent_mapping()
        
        print("=" * 50)
        print("✓ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
