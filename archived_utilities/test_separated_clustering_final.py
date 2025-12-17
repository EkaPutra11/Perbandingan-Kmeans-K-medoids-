# -*- coding: utf-8 -*-
"""
Test script untuk clustering terpisah (Standard vs Non-Standard)
Menguji fungsi process_kmeans_separated() dan process_kmedoids_separated()
"""

from app import create_app
from app.processing_kmeans import process_kmeans_separated, print_separated_kmeans_results
from app.processing_kmedoids import process_kmedoids_separated, print_separated_kmedoids_results

def main():
    # Initialize Flask app context
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("TESTING SEPARATED CLUSTERING")
        print("="*60)
        
        # Test K-Means Separated
        print("\n[1] Testing K-Means Separated Clustering...")
        print("-" * 60)
        kmeans_results = process_kmeans_separated(k=3)
        
        if kmeans_results:
            print("\n[OK] K-Means Separated processing completed successfully!")
            print_separated_kmeans_results(kmeans_results)
            
            # Display summary
            if 'standard' in kmeans_results:
                std_data = kmeans_results['standard']['data']
                print(f"\nStandard Summary:")
                print(f"  Total records: {len(std_data)}")
                print(f"  DBI: {kmeans_results['standard']['dbi']:.4f}")
                print(f"  Iterations: {kmeans_results['standard']['n_iter']}")
                
                # Cluster distribution
                for tier in ['Terlaris', 'Sedang', 'Kurang Laris']:
                    count = len(std_data[std_data['tier'] == tier])
                    print(f"  {tier}: {count} records")
            
            if 'non_standard' in kmeans_results:
                nonstd_data = kmeans_results['non_standard']['data']
                print(f"\nNon-Standard Summary:")
                print(f"  Total records: {len(nonstd_data)}")
                print(f"  DBI: {kmeans_results['non_standard']['dbi']:.4f}")
                print(f"  Iterations: {kmeans_results['non_standard']['n_iter']}")
                
                # Cluster distribution
                for tier in ['Terlaris', 'Sedang', 'Kurang Laris']:
                    count = len(nonstd_data[nonstd_data['tier'] == tier])
                    print(f"  {tier}: {count} records")
        else:
            print("\n[FAILED] K-Means Separated processing failed!")
        
        print("\n" + "="*60)
        
        # Test K-Medoids Separated
        print("\n[2] Testing K-Medoids Separated Clustering...")
        print("-" * 60)
        kmedoids_results = process_kmedoids_separated(k=3)
        
        if kmedoids_results:
            print("\n[OK] K-Medoids Separated processing completed successfully!")
            print_separated_kmedoids_results(kmedoids_results)
            
            # Display summary
            if 'standard' in kmedoids_results:
                std_data = kmedoids_results['standard']['data']
                print(f"\nStandard Summary:")
                print(f"  Total records: {len(std_data)}")
                print(f"  DBI: {kmedoids_results['standard']['dbi']:.4f}")
                print(f"  Iterations: {kmedoids_results['standard']['n_iter']}")
                
                # Cluster distribution
                for tier in ['Terlaris', 'Sedang', 'Kurang Laris']:
                    count = len(std_data[std_data['tier'] == tier])
                    print(f"  {tier}: {count} records")
            
            if 'non_standard' in kmedoids_results:
                nonstd_data = kmedoids_results['non_standard']['data']
                print(f"\nNon-Standard Summary:")
                print(f"  Total records: {len(nonstd_data)}")
                print(f"  DBI: {kmedoids_results['non_standard']['dbi']:.4f}")
                print(f"  Iterations: {kmedoids_results['non_standard']['n_iter']}")
                
                # Cluster distribution
                for tier in ['Terlaris', 'Sedang', 'Kurang Laris']:
                    count = len(nonstd_data[nonstd_data['tier'] == tier])
                    print(f"  {tier}: {count} records")
        else:
            print("\n[FAILED] K-Medoids Separated processing failed!")
        
        print("\n" + "="*60)
        print("TESTING COMPLETED")
        print("="*60 + "\n")


if __name__ == '__main__':
    main()
