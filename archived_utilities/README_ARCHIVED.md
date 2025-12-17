# Archived Utilities & Testing Files

Folder ini berisi file-file yang **tidak digunakan** dalam runtime aplikasi utama, namun disimpan untuk keperluan:
- Testing & debugging
- Analisis data
- Dokumentasi pengembangan
- Utility scripts
- Migration helpers

## 📁 Kategori File

### 🧪 Testing Files
File-file untuk testing berbagai komponen sistem:
- `test_*.py` - Semua file testing (clustering, DBI, convergence, dll)
- `verify_*.py` - File verifikasi schema dan data

### 📊 Analysis Scripts
Script untuk analisis dan eksplorasi data:
- `analyze_*.py` - Analisis clustering approaches, data patterns, dll
- `check_*.py` - Script untuk checking cluster data, HTML output, dll
- `compare_dbi.py` - Perbandingan Davies-Bouldin Index

### 🛠️ Utility Scripts
Helper scripts untuk berbagai keperluan:
- `calculate_overall_dbi_separated.py` - Kalkulasi DBI untuk separated clustering
- `cluster_by_samples.py`, `cluster_summary.py` - Utility clustering
- `find_user_data.py` - Mencari data user
- `manual_dbi_calculation.py` - Perhitungan DBI manual
- `save_final_result.py` - Helper untuk save hasil
- `simulate_ui_request.py` - Simulasi request dari UI
- `view_final_result.py` - Melihat hasil akhir

### 🔧 Database & Schema
Script untuk database management:
- `alter_schema.py` - Modifikasi schema
- `recreate_tables.py` - Recreate tables

### 📄 Documentation Files
Dokumentasi pengembangan dan changelog:
- `CHANGELOG_SEPARATED_CLUSTERING.md` - Changelog clustering terpisah
- `CONVERGENCE_TEST_REPORT.md` - Report testing convergence
- `DOKUMENTASI_ALUR_SISTEM_CLUSTERING.md` - Dokumentasi lengkap sistem
- `IMPLEMENTASI_CLUSTERING_TERPISAH.md` - Dokumentasi implementasi
- `IMPLEMENTATION_NOTES.md` - Catatan implementasi
- `KMEANS_FINAL_RESULT_DOCS.md` - Dokumentasi hasil K-Means
- `SCHEMA_CLEANUP_SUMMARY.md` - Summary cleanup schema
- `SYSTEM_SUMMARY.md` - Summary sistem keseluruhan

### 📝 Other Files
- `queries_final_result.sql` - SQL queries untuk final result
- `flask_run.log` - Log dari Flask application

## ⚠️ Catatan Penting

**JANGAN DIHAPUS!** File-file ini mungkin berguna untuk:
1. Reference saat debugging
2. Memahami proses pengembangan
3. Testing perubahan di masa depan
4. Dokumentasi keputusan teknis

## 🚀 File Yang Digunakan Program Utama

File yang ada di root folder dan digunakan saat runtime:
- `app.py` - Main Flask application
- `app/` - Core application folder
- `requirements.txt` - Dependencies
- `import_csv.py` - Import data CSV
- `migrate_database.py` - Database migration
- `migrate_kmedoids.py` - K-Medoids migration
- `README.md` - Dokumentasi utama

---
**Archived on:** December 14, 2025
**Reason:** Cleanup project structure - memisahkan file runtime dari testing/utilities
