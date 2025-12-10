"""
Recreate cluster detail tables with updated schema (removed unnecessary columns)
"""
import pymysql

# Connect to database
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='db_penjualan_arwana'
)

cursor = conn.cursor()

# Drop existing foreign key constraints
try:
    cursor.execute("ALTER TABLE kmeans_cluster_detail DROP FOREIGN KEY kmeans_cluster_detail_ibfk_1")
    print('Dropped FK from kmeans_cluster_detail (KMeansResult)')
except Exception as e:
    print(f'Could not drop kmeans FK 1: {e}')

try:
    cursor.execute("ALTER TABLE kmedoids_cluster_detail DROP FOREIGN KEY kmedoids_cluster_detail_ibfk_1")
    print('Dropped FK from kmedoids_cluster_detail (KMedoidsResult)')
except Exception as e:
    print(f'Could not drop kmedoids FK 1: {e}')

# Drop the tables
try:
    cursor.execute("DROP TABLE IF EXISTS kmeans_cluster_detail")
    print('Dropped kmeans_cluster_detail table')
except Exception as e:
    print(f'Error dropping kmeans_cluster_detail: {e}')

try:
    cursor.execute("DROP TABLE IF EXISTS kmedoids_cluster_detail")
    print('Dropped kmedoids_cluster_detail table')
except Exception as e:
    print(f'Error dropping kmedoids_cluster_detail: {e}')

# Recreate kmeans_cluster_detail with updated schema
create_kmeans = """
CREATE TABLE kmeans_cluster_detail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kmeans_result_id INT NOT NULL,
    cluster_id INT NOT NULL,
    kategori VARCHAR(255),
    size VARCHAR(50),
    jumlah_terjual INT DEFAULT 0,
    total_harga DECIMAL(15, 2) DEFAULT 0,
    distance_to_centroid FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kmeans_result_id) REFERENCES kmeans_result(id) ON DELETE CASCADE
)
"""

# Recreate kmedoids_cluster_detail with updated schema
create_kmedoids = """
CREATE TABLE kmedoids_cluster_detail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kmedoids_result_id INT NOT NULL,
    cluster_id INT NOT NULL,
    kategori VARCHAR(255),
    size VARCHAR(50),
    jumlah_terjual INT DEFAULT 0,
    total_harga DECIMAL(15, 2) DEFAULT 0,
    distance_to_medoid FLOAT DEFAULT 0,
    is_medoid BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kmedoids_result_id) REFERENCES kmedoids_result(id) ON DELETE CASCADE
)
"""

try:
    cursor.execute(create_kmeans)
    print('Created new kmeans_cluster_detail table')
except Exception as e:
    print(f'Error creating kmeans_cluster_detail: {e}')

try:
    cursor.execute(create_kmedoids)
    print('Created new kmedoids_cluster_detail table')
except Exception as e:
    print(f'Error creating kmedoids_cluster_detail: {e}')

conn.commit()
conn.close()
print('\nDatabase schema updated successfully!')
print('Old cluster detail data has been cleared (new tables created)')
print('You can now run clustering again to populate the new tables')
