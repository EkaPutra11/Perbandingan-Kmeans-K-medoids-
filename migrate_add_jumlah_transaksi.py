"""
Migration script to add jumlah_transaksi column to clustering tables
Run this script to update the database schema after adding the second clustering feature
"""

from app import create_app
from app.models import db
from sqlalchemy import text
import sys

app = create_app()

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    with db.engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = '{table_name}' 
            AND COLUMN_NAME = '{column_name}'
        """))
        return result.scalar() > 0

def add_column_if_not_exists(table_name, column_name, column_def):
    """Add a column to a table if it doesn't exist"""
    if check_column_exists(table_name, column_name):
        print(f"✓ Column '{column_name}' already exists in '{table_name}'")
        return False
    
    try:
        with db.engine.connect() as conn:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}"))
            conn.commit()
        print(f"✓ Successfully added column '{column_name}' to '{table_name}'")
        return True
    except Exception as e:
        print(f"✗ Error adding column '{column_name}' to '{table_name}': {str(e)}")
        return False

def main():
    """Run the migration"""
    print("=" * 60)
    print("Database Migration: Add jumlah_transaksi column")
    print("=" * 60)
    print()
    
    with app.app_context():
        # Check database connection
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT DATABASE()"))
                db_name = result.scalar()
                print(f"Connected to database: {db_name}")
                print()
        except Exception as e:
            print(f"✗ Failed to connect to database: {str(e)}")
            sys.exit(1)
        
        # Add jumlah_transaksi to kmeans_final_result
        print("1. Updating table: kmeans_final_result")
        print("-" * 60)
        add_column_if_not_exists(
            'kmeans_final_result',
            'jumlah_transaksi',
            'INT DEFAULT 0'
        )
        print()
        
        # Add jumlah_transaksi to kmedoids_cluster_detail
        print("2. Updating table: kmedoids_cluster_detail")
        print("-" * 60)
        add_column_if_not_exists(
            'kmedoids_cluster_detail',
            'jumlah_transaksi',
            'INT DEFAULT 0'
        )
        print()
        
        # Verify changes
        print("=" * 60)
        print("Verification:")
        print("-" * 60)
        
        kmeans_has_col = check_column_exists('kmeans_final_result', 'jumlah_transaksi')
        kmedoids_has_col = check_column_exists('kmedoids_cluster_detail', 'jumlah_transaksi')
        
        print(f"✓ kmeans_final_result.jumlah_transaksi: {'EXISTS' if kmeans_has_col else 'MISSING'}")
        print(f"✓ kmedoids_cluster_detail.jumlah_transaksi: {'EXISTS' if kmedoids_has_col else 'MISSING'}")
        print()
        
        if kmeans_has_col and kmedoids_has_col:
            print("=" * 60)
            print("✓ Migration completed successfully!")
            print("=" * 60)
            print()
            print("Next steps:")
            print("1. Clear old clustering results (optional)")
            print("2. Run new clustering with 2 features (jumlah_terjual + jumlah_transaksi)")
            print("3. The system will now use both features for clustering")
            print()
        else:
            print("=" * 60)
            print("✗ Migration incomplete - please check errors above")
            print("=" * 60)
            sys.exit(1)

if __name__ == '__main__':
    main()
