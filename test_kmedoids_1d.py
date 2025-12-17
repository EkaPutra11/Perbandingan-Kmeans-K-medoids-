#!/usr/bin/env python
"""Test K-Medoids dengan 1 feature untuk debug error"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.processing_kmedoids import process_kmedoids_manual
import traceback

print("=" * 80)
print("Testing K-Medoids dengan 1 Feature (jumlah_terjual only)")
print("=" * 80)

try:
    print("\n[1] Running process_kmedoids_manual()...")
    result = process_kmedoids_manual(k=3)
    
    if result:
        print("✓ K-Medoids SUCCESS!")
        print(f"  - Medoids shape: {result['kmedoids'].medoids.shape if hasattr(result['kmedoids'], 'medoids') else 'N/A'}")
        print(f"  - Labels count: {len(result['labels'])}")
        print(f"  - Cost: {result['cost']:.2f}")
        print(f"  - Davies-Bouldin: {result['davies_bouldin']:.3f}")
        print(f"  - Iterations: {result['n_iter']}")
    else:
        print("✗ K-Medoids returned None!")
        
except Exception as e:
    print(f"\n✗ ERROR OCCURRED:")
    print(f"  Type: {type(e).__name__}")
    print(f"  Message: {str(e)}")
    print(f"\n  Full Traceback:")
    traceback.print_exc()

print("\n" + "=" * 80)
