-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 05, 2025 at 09:05 AM
-- Server version: 10.11.11-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_penjualan_arwana`
--

-- --------------------------------------------------------

--
-- Table structure for table `kmeans_cluster_detail`
--

CREATE TABLE `kmeans_cluster_detail` (
  `id` int(11) NOT NULL,
  `kmeans_result_id` int(11) NOT NULL,
  `penjualan_id` int(11) NOT NULL,
  `cluster_id` int(11) NOT NULL,
  `kategori` varchar(100) DEFAULT NULL,
  `size` varchar(50) DEFAULT NULL,
  `jumlah_terjual` int(11) DEFAULT NULL,
  `harga_satuan` decimal(15,0) DEFAULT NULL,
  `total_harga` decimal(18,0) DEFAULT NULL,
  `nama_penjual` varchar(100) DEFAULT NULL,
  `kota_tujuan` varchar(100) DEFAULT NULL,
  `distance_to_centroid` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `kmeans_result`
--

CREATE TABLE `kmeans_result` (
  `id` int(11) NOT NULL,
  `k_value` int(11) NOT NULL,
  `inertia` float NOT NULL,
  `davies_bouldin_index` float NOT NULL,
  `n_iter` int(11) DEFAULT NULL,
  `n_samples` int(11) DEFAULT NULL,
  `max_iterations` int(11) DEFAULT NULL,
  `random_state` int(11) DEFAULT NULL,
  `cluster_distribution` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`cluster_distribution`)),
  `data_kategori_count` int(11) DEFAULT NULL,
  `data_size_count` int(11) DEFAULT NULL,
  `data_penjual_count` int(11) DEFAULT NULL,
  `data_kota_count` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `kmedoids_cluster_detail`
--

CREATE TABLE `kmedoids_cluster_detail` (
  `id` int(11) NOT NULL,
  `kmedoids_result_id` int(11) NOT NULL,
  `penjualan_id` int(11) NOT NULL,
  `cluster_id` int(11) NOT NULL,
  `kategori` varchar(100) DEFAULT NULL,
  `size` varchar(50) DEFAULT NULL,
  `jumlah_terjual` int(11) DEFAULT NULL,
  `harga_satuan` decimal(15,0) DEFAULT NULL,
  `total_harga` decimal(18,0) DEFAULT NULL,
  `nama_penjual` varchar(100) DEFAULT NULL,
  `kota_tujuan` varchar(100) DEFAULT NULL,
  `distance_to_medoid` float DEFAULT NULL,
  `is_medoid` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `kmedoids_result`
--

CREATE TABLE `kmedoids_result` (
  `id` int(11) NOT NULL,
  `k_value` int(11) NOT NULL,
  `cost` float NOT NULL,
  `davies_bouldin_index` float NOT NULL,
  `n_iter` int(11) DEFAULT NULL,
  `n_samples` int(11) DEFAULT NULL,
  `max_iterations` int(11) DEFAULT NULL,
  `random_state` int(11) DEFAULT NULL,
  `cluster_distribution` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`cluster_distribution`)),
  `data_kategori_count` int(11) DEFAULT NULL,
  `data_size_count` int(11) DEFAULT NULL,
  `data_penjual_count` int(11) DEFAULT NULL,
  `data_kota_count` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `penjualan`
--

CREATE TABLE `penjualan` (
  `id` int(11) NOT NULL,
  `tanggal_terjual` date NOT NULL,
  `kategori` varchar(100) DEFAULT NULL,
  `size` varchar(50) DEFAULT NULL,
  `jumlah_terjual` int(11) DEFAULT NULL,
  `harga_satuan` decimal(15,0) DEFAULT NULL,
  `total_harga` decimal(18,0) DEFAULT NULL,
  `nama_penjual` varchar(100) DEFAULT NULL,
  `kota_tujuan` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `kmeans_cluster_detail`
--
ALTER TABLE `kmeans_cluster_detail`
  ADD PRIMARY KEY (`id`),
  ADD KEY `kmeans_result_id` (`kmeans_result_id`),
  ADD KEY `penjualan_id` (`penjualan_id`);

--
-- Indexes for table `kmeans_result`
--
ALTER TABLE `kmeans_result`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `kmedoids_cluster_detail`
--
ALTER TABLE `kmedoids_cluster_detail`
  ADD PRIMARY KEY (`id`),
  ADD KEY `kmedoids_result_id` (`kmedoids_result_id`),
  ADD KEY `penjualan_id` (`penjualan_id`);

--
-- Indexes for table `kmedoids_result`
--
ALTER TABLE `kmedoids_result`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `penjualan`
--
ALTER TABLE `penjualan`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `kmeans_cluster_detail`
--
ALTER TABLE `kmeans_cluster_detail`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10866;

--
-- AUTO_INCREMENT for table `kmeans_result`
--
ALTER TABLE `kmeans_result`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `kmedoids_cluster_detail`
--
ALTER TABLE `kmedoids_cluster_detail`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13223;

--
-- AUTO_INCREMENT for table `kmedoids_result`
--
ALTER TABLE `kmedoids_result`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `penjualan`
--
ALTER TABLE `penjualan`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8149;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `kmeans_cluster_detail`
--
ALTER TABLE `kmeans_cluster_detail`
  ADD CONSTRAINT `kmeans_cluster_detail_ibfk_1` FOREIGN KEY (`kmeans_result_id`) REFERENCES `kmeans_result` (`id`),
  ADD CONSTRAINT `kmeans_cluster_detail_ibfk_2` FOREIGN KEY (`penjualan_id`) REFERENCES `penjualan` (`id`);

--
-- Constraints for table `kmedoids_cluster_detail`
--
ALTER TABLE `kmedoids_cluster_detail`
  ADD CONSTRAINT `kmedoids_cluster_detail_ibfk_1` FOREIGN KEY (`kmedoids_result_id`) REFERENCES `kmedoids_result` (`id`),
  ADD CONSTRAINT `kmedoids_cluster_detail_ibfk_2` FOREIGN KEY (`penjualan_id`) REFERENCES `penjualan` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
