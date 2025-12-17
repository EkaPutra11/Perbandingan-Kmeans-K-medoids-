-- SQL Query to view kmeans_final_result table

-- 1. Check table structure
DESCRIBE kmeans_final_result;

-- 2. View all records
SELECT * FROM kmeans_final_result ORDER BY cluster_id, kategori, size_range;

-- 3. Count records per cluster
SELECT 
    cluster_id,
    COUNT(*) as total_records,
    SUM(jumlah_terjual) as total_terjual
FROM kmeans_final_result
GROUP BY cluster_id
ORDER BY cluster_id;

-- 4. View with K-Means result info
SELECT 
    fr.id,
    fr.cluster_id,
    fr.kategori,
    fr.size_range,
    fr.jumlah_terjual,
    fr.created_at,
    kr.k_value,
    kr.davies_bouldin_index,
    kr.inertia,
    kr.n_iter
FROM kmeans_final_result fr
JOIN kmeans_result kr ON fr.kmeans_result_id = kr.id
ORDER BY fr.cluster_id, fr.kategori, fr.size_range;

-- 5. Summary by kategori
SELECT 
    kategori,
    COUNT(*) as total_size_ranges,
    SUM(jumlah_terjual) as total_terjual,
    AVG(jumlah_terjual) as avg_terjual
FROM kmeans_final_result
GROUP BY kategori
ORDER BY total_terjual DESC;

-- 6. Summary by cluster
SELECT 
    cluster_id,
    COUNT(DISTINCT kategori) as unique_kategori,
    COUNT(DISTINCT size_range) as unique_size_ranges,
    COUNT(*) as total_records,
    SUM(jumlah_terjual) as total_terjual,
    AVG(jumlah_terjual) as avg_terjual,
    MIN(jumlah_terjual) as min_terjual,
    MAX(jumlah_terjual) as max_terjual
FROM kmeans_final_result
GROUP BY cluster_id
ORDER BY cluster_id;

-- 7. Top 10 highest jumlah_terjual
SELECT 
    cluster_id,
    kategori,
    size_range,
    jumlah_terjual
FROM kmeans_final_result
ORDER BY jumlah_terjual DESC
LIMIT 10;

-- 8. Count total records
SELECT COUNT(*) as total_records FROM kmeans_final_result;
