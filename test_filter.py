#!/usr/bin/env python3
"""Quick test of profanity filter"""

import sys
sys.path.insert(0, '/Users/Dollar/Documents/ultrathink-enhanced')

from create_real_system import filter_profanity

# Test the filter
test_cases = [
    "Am I Getting Fucked Friday, June 20th",
    "This pricing is shit",
    "What the hell is happening with licensing?",
    "Normal professional content",
    "damn expensive software costs"
]

print("🧪 Testing Profanity Filter:")
print("=" * 50)

for test in test_cases:
    filtered = filter_profanity(test)
    print(f"Original: {test}")
    print(f"Filtered: {filtered}")
    print("-" * 30)