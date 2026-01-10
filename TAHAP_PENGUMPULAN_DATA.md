# Tahap Pengumpulan Data

## 3.1 Tahap Pengumpulan Data

Pada tahap pengumpulan data, penelitian ini dimulai dengan menetapkan beberapa parameter yang dibutuhkan untuk mengumpulkan data penjualan ikan arwana dari CV Putra Rizky Aroindo. Beberapa parameter yang digunakan meliputi periode waktu transaksi, kategori produk, ukuran ikan, dan informasi penjualan yang relevan. Durasi waktu yang ditentukan untuk pengumpulan data dimulai dari tahun 2023 hingga 2025, yang mencakup data transaksi penjualan selama periode tersebut. Proses pengumpulan data dilakukan melalui sistem pencatatan transaksi perusahaan hingga menghasilkan data penjualan yang komprehensif. Setelah proses pengambilan data selesai, data akan disimpan dalam format file CSV.

Selanjutnya, data penjualan yang telah berhasil dikumpulkan akan disimpan ke dalam database melalui fitur import data yang tersedia pada sistem. Data dari file CSV tersebut menghasilkan beberapa kolom, yaitu:

- **tanggal_terjual**: Tanggal terjadinya transaksi penjualan
- **kategori**: Jenis kategori ikan arwana (Standard/Non-Standard)
- **size**: Ukuran ikan dalam satuan centimeter (cm)
- **jumlah_terjual**: Jumlah unit ikan yang terjual dalam satu transaksi
- **harga_satuan**: Harga per unit ikan dalam rupiah
- **total_harga**: Total nilai transaksi (jumlah_terjual × harga_satuan)
- **nama_penjual**: Nama sales/penjual yang menangani transaksi
- **kota_tujuan**: Kota tujuan pengiriman produk

Data yang terkumpul kemudian melalui proses validasi untuk memastikan tidak ada data yang kosong atau tidak valid pada kolom-kolom yang bersifat mandatory. Sistem akan melakukan pengecekan terhadap format data, khususnya untuk kolom numerik seperti jumlah_terjual, harga_satuan, dan total_harga agar sesuai dengan tipe data yang diharapkan. Setelah data berhasil disimpan ke dalam database dengan struktur tabel 'penjualan', tahapan selanjutnya data tersebut akan diolah pada tahapan preprocessing dan clustering menggunakan algoritma K-Means dan K-Medoids untuk mengidentifikasi pola penjualan dan mengelompokkan produk berdasarkan tingkat kelarisan.

## 3.2 Struktur Data

Total data yang berhasil dikumpulkan dan digunakan dalam penelitian ini berasal dari transaksi penjualan aktual perusahaan. Data tersebut mencakup berbagai variasi ukuran ikan arwana mulai dari ukuran kecil hingga besar, dengan rentang harga yang beragam sesuai dengan kategori dan ukuran produk. Proses import data ke dalam sistem dilakukan melalui antarmuka web yang memvalidasi format CSV dan memastikan setiap kolom sesuai dengan struktur database yang telah ditentukan.

Fitur import data pada sistem dirancang untuk:
1. Membaca file CSV dengan encoding yang sesuai
2. Memvalidasi setiap baris data sebelum disimpan ke database
3. Melakukan konversi tipe data secara otomatis (string ke numeric untuk kolom harga)
4. Menghapus data lama sebelum melakukan import baru untuk menghindari duplikasi
5. Memberikan feedback kepada pengguna mengenai status import (berhasil/gagal)

Dengan struktur data yang terorganisir dan tervalidasi dengan baik, tahapan selanjutnya yaitu preprocessing dan clustering dapat dilakukan dengan lebih optimal untuk menghasilkan insight mengenai pola penjualan ikan arwana berdasarkan kategori dan ukuran produk.
