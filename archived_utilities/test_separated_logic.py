# -*- coding: utf-8 -*-
"""
Test script untuk memverifikasi clustering terpisah (Standard vs Non-Standard)
dengan logika baru yang sudah diimplementasikan
"""

from app import create_app
from app.processing_kmeans import process_kmeans_manual
from app.processing_kmedoids import process_kmedoids_manual

def main():
    # Initialize Flask app context
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("TESTING SEPARATED CLUSTERING LOGIC (INTERNAL PROCESSING)")
        print("="*70)
        
        # Test K-Means dengan logika terpisah
        print("\n[1] Testing K-Means with Separated Processing...")
        print("-" * 70)
        kmeans_result = process_kmeans_manual(k=3)
        
        if kmeans_result:
            print("\n[SUCCESS] K-Means processing completed!")
            print(f"\nResults Summary:")
            print(f"  Total samples: {kmeans_result['n_samples']}")
            print(f"  Iterations: {kmeans_result['n_iter']}")
            print(f"  Inertia: {kmeans_result['inertia']:.4f}")
            print(f"  DBI (Combined): {kmeans_result['davies_bouldin']:.4f}")
            
            if 'davies_bouldin_standard' in kmeans_result:
                print(f"  DBI (Standard): {kmeans_result['davies_bouldin_standard']:.4f}")
            if 'davies_bouldin_non_standard' in kmeans_result:
                print(f"  DBI (Non-Standard): {kmeans_result['davies_bouldin_non_standard']:.4f}")
            
            # Tampilkan distribusi cluster
            labels = kmeans_result['labels']
            unique_labels = set(labels)
            print(f"\n  Cluster distribution:")
            for label in sorted(unique_labels):
                count = sum(1 for l in labels if l == label)
                print(f"    Cluster {label}: {count} records")
        else:
            print("\n[FAILED] K-Means processing failed!")
        
        print("\n" + "="*70)
        
        # Test K-Medoids dengan logika terpisah
        print("\n[2] Testing K-Medoids with Separated Processing...")
        print("-" * 70)
        kmedoids_result = process_kmedoids_manual(k=3)
        
        if kmedoids_result:
            print("\n[SUCCESS] K-Medoids processing completed!")
            print(f"\nResults Summary:")
            print(f"  Total samples: {kmedoids_result['n_samples']}")
            print(f"  Iterations: {kmedoids_result['n_iter']}")
            print(f"  Cost: {kmedoids_result['cost']:.4f}")
            print(f"  DBI (Combined): {kmedoids_result['davies_bouldin']:.4f}")
            
            if 'davies_bouldin_standard' in kmedoids_result:
                print(f"  DBI (Standard): {kmedoids_result['davies_bouldin_standard']:.4f}")
            if 'davies_bouldin_non_standard' in kmedoids_result:
                print(f"  DBI (Non-Standard): {kmedoids_result['davies_bouldin_non_standard']:.4f}")
            
            # Tampilkan distribusi cluster
            labels = kmedoids_result['labels']
            unique_labels = set(labels)
            print(f"\n  Cluster distribution:")
            for label in sorted(unique_labels):
                count = sum(1 for l in labels if l == label)
                print(f"    Cluster {label}: {count} records")
        else:
            print("\n[FAILED] K-Medoids processing failed!")
        
        print("\n" + "="*70)
        print("TESTING COMPLETED")
        print("="*70 + "\n")
        
        # Comparison
        if kmeans_result and kmedoids_result:
            print("\n" + "="*70)
            print("COMPARISON SUMMARY")
            print("="*70)
            print(f"\nK-Means vs K-Medoids:")
            print(f"  DBI (Combined):")
            print(f"    K-Means:   {kmeans_result['davies_bouldin']:.4f}")
            print(f"    K-Medoids: {kmedoids_result['davies_bouldin']:.4f}")
            print(f"    Winner: {'K-Means' if kmeans_result['davies_bouldin'] < kmedoids_result['davies_bouldin'] else 'K-Medoids'}")
            
            print(f"\n  DBI (Standard):")
            print(f"    K-Means:   {kmeans_result.get('davies_bouldin_standard', 0):.4f}")
            print(f"    K-Medoids: {kmedoids_result.get('davies_bouldin_standard', 0):.4f}")
            
            print(f"\n  DBI (Non-Standard):")
            print(f"    K-Means:   {kmeans_result.get('davies_bouldin_non_standard', 0):.4f}")
            print(f"    K-Medoids: {kmedoids_result.get('davies_bouldin_non_standard', 0):.4f}")
            
            print("\n" + "="*70)


if __name__ == '__main__':
    main()
