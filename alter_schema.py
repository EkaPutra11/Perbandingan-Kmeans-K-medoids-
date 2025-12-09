import pymysql

# Connect to database
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='db_penjualan_arwana'
)

cursor = conn.cursor()

# Drop existing FK constraints
try:
    cursor.execute("ALTER TABLE kmeans_cluster_detail DROP FOREIGN KEY kmeans_cluster_detail_ibfk_2")
    print('Dropped FK from kmeans_cluster_detail')
except Exception as e:
    print(f'Could not drop kmeans FK: {e}')

try:
    cursor.execute("ALTER TABLE kmedoids_cluster_detail DROP FOREIGN KEY kmedoids_cluster_detail_ibfk_2")
    print('Dropped FK from kmedoids_cluster_detail')
except Exception as e:
    print(f'Could not drop kmedoids FK: {e}')

# Modify columns to allow NULL
cursor.execute("ALTER TABLE kmeans_cluster_detail MODIFY COLUMN penjualan_id INT NULL")
print('Modified kmeans_cluster_detail.penjualan_id to NULL')

cursor.execute("ALTER TABLE kmedoids_cluster_detail MODIFY COLUMN penjualan_id INT NULL")
print('Modified kmedoids_cluster_detail.penjualan_id to NULL')

# Re-add FK constraints with ON DELETE SET NULL
cursor.execute("ALTER TABLE kmeans_cluster_detail ADD CONSTRAINT kmeans_cluster_detail_ibfk_2 FOREIGN KEY (penjualan_id) REFERENCES penjualan(id) ON DELETE SET NULL")
print('Added FK back to kmeans_cluster_detail with ON DELETE SET NULL')

cursor.execute("ALTER TABLE kmedoids_cluster_detail ADD CONSTRAINT kmedoids_cluster_detail_ibfk_2 FOREIGN KEY (penjualan_id) REFERENCES penjualan(id) ON DELETE SET NULL")
print('Added FK back to kmedoids_cluster_detail with ON DELETE SET NULL')

conn.commit()
conn.close()
print('Database schema updated successfully')
