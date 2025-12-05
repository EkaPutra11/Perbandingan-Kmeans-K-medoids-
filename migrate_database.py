"""
Database migration script to add analysis_data column to result tables
Run this once to update the database schema
"""
import pymysql

def add_analysis_data_columns():
    try:
        # Connect to database
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='db_penjualan_arwana'
        )
        cursor = conn.cursor()

        print("Adding analysis_data column to kmeans_result...")
        try:
            cursor.execute("""
                ALTER TABLE kmeans_result 
                ADD COLUMN analysis_data JSON DEFAULT NULL 
                AFTER cluster_distribution
            """)
            print("✓ kmeans_result updated")
        except pymysql.err.OperationalError as e:
            if "Duplicate column name" in str(e):
                print("✓ kmeans_result already has analysis_data column")
            else:
                raise

        print("Adding analysis_data column to kmedoids_result...")
        try:
            cursor.execute("""
                ALTER TABLE kmedoids_result 
                ADD COLUMN analysis_data JSON DEFAULT NULL 
                AFTER cluster_distribution
            """)
            print("✓ kmedoids_result updated")
        except pymysql.err.OperationalError as e:
            if "Duplicate column name" in str(e):
                print("✓ kmedoids_result already has analysis_data column")
            else:
                raise

        conn.commit()
        conn.close()
        
        print("\n✅ Database migration completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Error during migration: {str(e)}")
        return False


if __name__ == '__main__':
    add_analysis_data_columns()
