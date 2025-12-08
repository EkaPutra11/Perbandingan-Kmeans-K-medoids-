// File input handling
const fileInput = document.getElementById('fileInput');
const uploadForm = document.getElementById('uploadForm');
const fileName = document.getElementById('fileName');

fileInput.addEventListener('change', function() {
    if (this.files && this.files[0]) {
        fileName.textContent = '✓ File terpilih: ' + this.files[0].name;
    }
});

// Drag and drop
const dropZone = document.querySelector('.file-input-label');
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.background = '#0056b3';
});
dropZone.addEventListener('dragleave', () => {
    dropZone.style.background = '#007bff';
});
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.background = '#007bff';
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        fileName.textContent = '✓ File terpilih: ' + files[0].name;
    }
});

// Form submission
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const uploadBtn = document.getElementById('uploadBtn');
    const originalText = uploadBtn.innerHTML;
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Uploading...';

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        showAlert(data.status, data.message);

        if (data.status === 'success') {
            fileInput.value = '';
            fileName.textContent = '';
            loadStatistics();
        }
    } catch (error) {
        showAlert('error', 'Upload failed: ' + error.message);
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = originalText;
    }
});

function showAlert(type, message) {
    const alertContainer = document.getElementById('alertContainer');
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const icon = type === 'success' ? '✓' : '✗';
    
    alertContainer.innerHTML = `
        <div class="alert alert-${alertClass === 'alert-success' ? 'success' : 'danger'} alert-dismissible fade show" role="alert">
            <strong>${icon}</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
}

async function loadStatistics() {
    try {
        const response = await fetch('/data/stats');
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('totalRecords').textContent = stats.total_records;
            document.getElementById('standardCount').textContent = stats.standard_count;
            document.getElementById('nonStandardCount').textContent = stats.non_standard_count;
            document.getElementById('stats').classList.add('show');
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

async function deleteAllData() {
    if (!confirm('⚠️ Apakah Anda yakin ingin menghapus SEMUA data? Tindakan ini tidak bisa dibatalkan!')) {
        return;
    }

    const deleteBtn = document.getElementById('deleteDataBtn');
    deleteBtn.disabled = true;
    deleteBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Menghapus...';

    try {
        const response = await fetch('/delete/data', { method: 'POST' });
        const data = await response.json();
        showAlert(data.status, data.message);
        
        if (data.status === 'success') {
            document.getElementById('stats').classList.remove('show');
            setTimeout(() => location.reload(), 1500);
        }
    } catch (error) {
        showAlert('error', 'Delete failed: ' + error.message);
    } finally {
        deleteBtn.disabled = false;
        deleteBtn.innerHTML = '<i class="bi bi-trash"></i> Hapus Data';
    }
}

async function deleteAllResults() {
    if (!confirm('⚠️ Apakah Anda yakin ingin menghapus SEMUA hasil clustering?')) {
        return;
    }

    const deleteBtn = document.getElementById('deleteResultsBtn');
    deleteBtn.disabled = true;
    deleteBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Menghapus...';

    try {
        const response = await fetch('/delete/results', { method: 'POST' });
        const data = await response.json();
        showAlert(data.status, data.message);
        
        if (data.status === 'success') {
            setTimeout(() => location.reload(), 1500);
        }
    } catch (error) {
        showAlert('error', 'Delete failed: ' + error.message);
    } finally {
        deleteBtn.disabled = false;
        deleteBtn.innerHTML = '<i class="bi bi-trash"></i> Hapus Hasil';
    }
}

// Load stats on page load
window.addEventListener('load', loadStatistics);
