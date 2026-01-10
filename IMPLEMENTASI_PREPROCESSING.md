# Tahap Preprocessing Data

Tahap preprocessing merupakan tahapan penting untuk mempersiapkan data penjualan sebelum diproses menggunakan algoritma clustering. Pada penelitian ini, preprocessing dilakukan melalui empat tahap utama untuk mempersiapkan data agar terstruktur, yaitu seleksi atribut, transformasi data, data cleaning, dan ekstraksi fitur. Berikut ini penjelasan detail dari tahapan preprocessing:

## a) Seleksi Atribut

Pada tahapan seleksi atribut, akan diterapkan pemilihan kolom yang relevan dari data penjualan yang mentah. Dari sekian banyaknya kolom yang didapatkan dari database akan dipilih beberapa kolom saja yang relevan dengan metode clustering, yaitu kolom **kategori**, **size**, dan **jumlah_terjual**. 

Kolom **kategori** berisi jenis produk ikan arwana (Standard atau Non-Standard), kolom **size** berisi ukuran ikan dalam satuan centimeter (contoh: "17 cm", "23 cm"), dan kolom **jumlah_terjual** berisi jumlah unit produk yang terjual dalam setiap transaksi. Ketiga kolom ini dipilih karena memiliki relevansi tinggi terhadap pola kelarisan produk yang akan dianalisis.

Kolom-kolom lain seperti harga_satuan, total_harga, nama_penjual, dan kota_tujuan tetap disimpan dalam sistem untuk keperluan analisis tambahan, namun tidak digunakan secara langsung dalam perhitungan clustering.

## b) Transformasi Data

Pada tahapan transformasi data, akan diterapkan pengelompokan data penjualan yang semula berbentuk transaksi per satuan menjadi data ringkas per kombinasi kategori dan rentang ukuran ikan. Tahapan ini bertujuan untuk menyederhanakan data penjualan yang sangat banyak menjadi pola yang lebih terstruktur dan mudah dianalisis.

Proses transformasi dimulai dengan mengkonversi kolom **size** yang berisi ukuran individual (contoh: "17 cm", "18 cm", "16 cm") menjadi kolom **size_range** yang berisi rentang ukuran per 5 cm (contoh: "15-19 cm"). Pengelompokan ini dilakukan dengan cara membagi nilai ukuran dengan 5 dan mengambil hasil pembagian bulat, kemudian mengalikannya kembali dengan 5 untuk mendapat batas bawah rentang. Batas atas rentang didapat dengan menambahkan 4 pada batas bawah.

Sebagai contoh, ukuran "17 cm" akan dikonversi menjadi rentang "15-19 cm" dengan perhitungan: (17 ÷ 5) = 3 (hasil bulat), 3 × 5 = 15 (batas bawah), 15 + 4 = 19 (batas atas).

Setelah kolom **size_range** terbentuk, data kemudian diagregasi berdasarkan kombinasi kolom **kategori** dan **size_range**. Untuk setiap kombinasi unik, dilakukan perhitungan agregasi sebagai berikut:
- Kolom **jumlah_terjual** dijumlahkan untuk mendapat total unit yang terjual
- Kolom **total_harga** dijumlahkan untuk mendapat total pendapatan
- Jumlah baris data dihitung untuk mendapat **jumlah_transaksi**

**Contoh penerapan transformasi data:**

*Data Sebelum Agregasi (per transaksi):*

| ID | Kategori  | Size  | Jumlah_Terjual |
|----|-----------|-------|----------------|
| 1  | Standard  | 17 cm | 5              |
| 2  | Standard  | 18 cm | 3              |
| 3  | Standard  | 16 cm | 7              |

*Data Setelah Agregasi:*

| Kategori  | Size_Range | Jumlah_Terjual | Jumlah_Transaksi |
|-----------|------------|----------------|------------------|
| Standard  | 15-19 cm   | 15             | 3                |

Berdasarkan contoh di atas, tiga transaksi terpisah dengan ukuran yang berbeda (16 cm, 17 cm, 18 cm) namun masih dalam rentang yang sama (15-19 cm) digabungkan menjadi satu baris data. Nilai **jumlah_terjual** dijumlahkan (5 + 3 + 7 = 15), dan **jumlah_transaksi** dihitung dari banyaknya baris yang digabung (3 transaksi).

Hasil dari tahap transformasi ini adalah data penjualan yang lebih ringkas dan terstruktur, sehingga pola penjualan untuk setiap kombinasi kategori dan rentang ukuran menjadi lebih jelas dan mudah dianalisis pada tahap clustering berikutnya.

## c) Data Cleaning

Pada tahapan data cleaning, akan diterapkan beberapa proses pembersihan data untuk menghapus atau memperbaiki data yang tidak valid, tidak lengkap, atau tidak konsisten. Tahapan ini bertujuan untuk memastikan kualitas data sebelum masuk ke tahap clustering. Berikut ini penjelasan detail dari tahapan-tahapan data cleaning yang dilakukan:

### 1. Hapus Data dengan Ukuran Tidak Valid

Pada setiap data penjualan yang memiliki nilai ukuran (size) tidak valid atau tidak dapat dikonversi menjadi angka akan dihapus. Misalnya, jika terdapat data dengan format ukuran yang salah atau kosong, data tersebut akan ditandai sebagai "Unknown" dan kemudian dihapus dari dataset.

**Contoh penerapan:**

| Kategori     | Size     | Jumlah_Terjual |
|--------------|----------|----------------|
| Standard     | 17 cm    | 5              |
| Standard     | -        | 3              |
| Non-Standard | abc cm   | 2              |
| Standard     | 20 cm    | 8              |

Setelah proses penghapusan data tidak valid, data dengan ukuran "-" dan "abc cm" akan dihilangkan, sehingga hanya tersisa data dengan format ukuran yang benar.

### 2. Validasi Kolom Saat Import CSV

Pada tahapan import data dari file CSV, sistem akan melakukan validasi terhadap kolom-kolom yang harus ada dalam file. Kolom yang wajib ada meliputi: **Kategori**, **Size**, **Jumlah_Terjual**, **Harga_Satuan**, **Total_Harga**, **Nama_Penjual**, dan **Kota_Tujuan**. 

Jika terdapat kolom yang hilang atau nama kolom tidak sesuai, sistem akan menampilkan pesan error dan menolak proses import. Hal ini memastikan bahwa data yang masuk ke database memiliki struktur yang konsisten dan lengkap.

### 3. Penghapusan Data Duplikat

Sebelum melakukan import data baru dari file CSV, sistem akan menghapus seluruh data lama yang sudah ada di database terlebih dahulu. Proses ini bertujuan untuk menghindari terjadinya duplikasi data dan memastikan bahwa data yang digunakan untuk clustering adalah data terbaru yang sudah melalui proses validasi.

### 4. Konversi dan Validasi Tipe Data

Pada tahapan ini, sistem akan melakukan konversi tipe data untuk memastikan setiap kolom memiliki format yang benar:
- Kolom **jumlah_terjual** dikonversi menjadi tipe integer (bilangan bulat)
- Kolom **harga_satuan** dan **total_harga** dikonversi menjadi tipe float (bilangan desimal)
- Jika terdapat nilai kosong (null), akan diganti dengan nilai 0

Jika terjadi kesalahan saat konversi (misalnya teks yang tidak bisa diubah menjadi angka), baris data tersebut akan di-skip dan sistem akan melanjutkan proses untuk data yang valid lainnya. Hal ini memastikan bahwa satu data yang bermasalah tidak mengganggu seluruh proses import.

### 5. Penanganan Format Harga

Kolom harga seringkali memiliki format dengan pemisah ribuan berupa titik (contoh: "15.000.000"). Pada tahapan ini, semua karakter titik akan dihapus terlebih dahulu sebelum dikonversi menjadi tipe numeric. Contohnya, nilai "15.000.000" akan diubah menjadi "15000000" kemudian dikonversi menjadi angka 15000000.

Hasil dari tahap data cleaning ini adalah dataset penjualan yang bersih, valid, dan siap untuk diproses pada tahap ekstraksi fitur. Data yang tidak valid atau bermasalah sudah dihilangkan, dan semua data yang tersisa dijamin memiliki format dan tipe data yang benar.

## d) Ekstraksi Fitur

Pada tahapan ekstraksi fitur, akan diterapkan pemilihan dan penyusunan ulang kolom-kolom data yang sudah dibersihkan menjadi variabel numerik yang siap diproses oleh algoritma clustering. Tahapan ini merupakan jembatan antara data yang sudah diagregasi dengan proses clustering yang akan dilakukan.

Dari data hasil agregasi yang memiliki beberapa kolom (kategori, size_range, jumlah_terjual, jumlah_transaksi, total_harga), dipilih dan difokuskan hanya pada informasi yang paling relevan untuk mengukur tingkat kelarisan produk. Fitur-fitur yang diekstraksi meliputi:

1. **Kategori** - Jenis produk (Standard atau Non-Standard) yang menunjukkan klasifikasi produk
2. **Size_Range** - Rentang ukuran dalam format per 5 cm (contoh: "15-19 cm", "20-24 cm") yang menunjukkan kelompok ukuran produk
3. **Jumlah_Terjual** - Total unit yang terjual untuk setiap kombinasi kategori dan size_range, menunjukkan volume penjualan
4. **Jumlah_Transaksi** - Frekuensi transaksi yang terjadi untuk setiap kombinasi kategori dan size_range, menunjukkan seberapa sering produk dibeli

**Contoh hasil ekstraksi fitur dapat dilihat pada tabel berikut:**

| No | Kategori      | Size_Range | Jumlah_Terjual | Jumlah_Transaksi |
|----|---------------|------------|----------------|------------------|
| 1  | Standard      | 15-19 cm   | 15             | 3                |
| 2  | Standard      | 20-24 cm   | 11             | 2                |
| 3  | Standard      | 25-29 cm   | 10             | 2                |
| 4  | Non-Standard  | 10-14 cm   | 8              | 1                |
| 5  | Non-Standard  | 15-19 cm   | 12             | 2                |

Berdasarkan tabel di atas, dapat dilihat bahwa data transaksi mentah yang sangat banyak telah diringkas menjadi representasi yang lebih sederhana. Setiap baris menunjukkan kombinasi unik dari kategori dan rentang ukuran, disertai dengan total jumlah yang terjual dan frekuensi transaksinya.

### Fitur Numerik untuk Clustering

Untuk proses perhitungan clustering, dua fitur numerik yang akan digunakan adalah:
1. **Jumlah_Terjual** - Menunjukkan volume penjualan total, semakin tinggi nilainya maka semakin laku produk tersebut dari segi kuantitas
2. **Jumlah_Transaksi** - Menunjukkan frekuensi pembelian, semakin tinggi nilainya maka semakin sering produk tersebut dibeli oleh konsumen

Kedua fitur ini dipilih karena dapat merepresentasikan tingkat kelarisan produk dari dua sudut pandang yang berbeda namun saling melengkapi: volume penjualan dan frekuensi pembelian.

### Normalisasi Fitur

Setelah fitur numerik diekstraksi, dilakukan proses normalisasi menggunakan metode Z-score normalization untuk memastikan bahwa kedua fitur memiliki skala yang seimbang. Normalisasi ini penting karena kedua fitur memiliki rentang nilai yang mungkin sangat berbeda, dan tanpa normalisasi, fitur dengan nilai yang lebih besar akan mendominasi perhitungan jarak dalam clustering.

Proses normalisasi dilakukan dengan rumus:

$$X_{normalized} = \frac{X - \mu}{\sigma + \epsilon}$$

Di mana:
- $X$ = nilai asli fitur
- $\mu$ = nilai rata-rata fitur
- $\sigma$ = standar deviasi fitur
- $\epsilon$ = nilai sangat kecil (0.00000001) untuk menghindari pembagian dengan nol

**Contoh penerapan normalisasi:**

Misalkan terdapat data fitur:
- Jumlah_Terjual: [15, 11, 10, 8, 12]
- Rata-rata: 11.2
- Standar deviasi: 2.49

Nilai 15 akan dinormalisasi menjadi: (15 - 11.2) / 2.49 = 1.53

Dengan cara yang sama, semua nilai pada kedua fitur akan dinormalisasi sehingga memiliki rata-rata mendekati 0 dan standar deviasi mendekati 1. Hasil normalisasi memastikan bahwa kedua fitur memiliki kontribusi yang seimbang dalam perhitungan jarak Euclidean pada algoritma K-Means dan K-Medoids.

Setelah melakukan ekstraksi fitur dan normalisasi, data penjualan yang sangat besar telah berhasil disederhanakan menjadi matriks fitur yang ringkas, terstruktur, dan siap diproses. Jika algoritma clustering langsung diberikan data mentah per transaksi, pola kelarisan akan sulit ditemukan karena informasi tersebar dan bercampur dengan detail yang tidak relevan. Ekstraksi fitur berfungsi sebagai langkah penghubung yang mengubah data transaksi mentah menjadi representasi yang fokus pada aspek kelarisan produk berdasarkan volume dan frekuensi penjualan.

---

## Rangkuman Alur Preprocessing

Secara keseluruhan, alur preprocessing data dalam sistem ini dapat dirangkum sebagai berikut:

1. **Input** - Data transaksi penjualan dari file CSV diimport ke database
2. **Seleksi Atribut** - Memilih kolom kategori, size, dan jumlah_terjual dari database
3. **Transformasi** - Mengubah ukuran individual menjadi rentang per 5 cm (size_range)
4. **Data Cleaning** - Menghapus data dengan ukuran tidak valid dan memvalidasi tipe data
5. **Agregasi** - Menggabungkan data per kombinasi (kategori, size_range) dengan penjumlahan dan penghitungan
6. **Ekstraksi Fitur** - Memilih fitur numerik (jumlah_terjual, jumlah_transaksi)
7. **Normalisasi** - Menerapkan Z-score normalization pada fitur numerik
8. **Output** - Matriks fitur ternormalisasi siap untuk algoritma clustering

Dengan tahapan preprocessing yang sistematis dan terstruktur ini, data penjualan ikan arwana yang kompleks dapat disederhanakan menjadi representasi yang optimal untuk diproses menggunakan algoritma K-Means dan K-Medoids, sehingga menghasilkan pengelompokan produk berdasarkan tingkat kelarisan yang akurat dan mudah diinterpretasi.
