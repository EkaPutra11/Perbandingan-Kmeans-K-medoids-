let currentPage = 1;
const itemsPerPage = 10;
let filteredData = [];

// Initialize table
function initTable() {
    const table = document.getElementById('dataTable');
    if (table) {
        filterTable();
    }
}

// Filter and search table
function filterTable() {
    const searchText = document.getElementById('searchInput').value.toLowerCase();
    const categoryFilter = document.getElementById('categoryFilter').value;
    const rows = document.getElementById('tableBody').querySelectorAll('tr');
    
    filteredData = [];
    
    rows.forEach(row => {
        const kategori = row.getAttribute('data-kategori');
        const text = row.textContent.toLowerCase();
        
        const matchCategory = !categoryFilter || 
            (categoryFilter === 'Standard' && kategori === 'Standard') ||
            (categoryFilter === 'Non-Standard' && kategori !== 'Standard');
        
        const matchSearch = !searchText || text.includes(searchText);
        
        if (matchCategory && matchSearch) {
            filteredData.push(row);
        }
    });
    
    currentPage = 1;
    updateTableDisplay();
}

// Update table display
function updateTableDisplay() {
    const rows = document.getElementById('tableBody').querySelectorAll('tr');
    rows.forEach(row => row.style.display = 'none');
    
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    
    for (let i = start; i < end && i < filteredData.length; i++) {
        filteredData[i].style.display = '';
    }
    
    // Update pagination
    const pageInfo = document.getElementById('pageInfo');
    pageInfo.textContent = `${start + 1}-${Math.min(end, filteredData.length)}`;
    
    document.getElementById('prevBtn').disabled = currentPage === 1;
    document.getElementById('nextBtn').disabled = end >= filteredData.length;
}

// Pagination
function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        updateTableDisplay();
    }
}

function nextPage() {
    const maxPage = Math.ceil(filteredData.length / itemsPerPage);
    if (currentPage < maxPage) {
        currentPage++;
        updateTableDisplay();
    }
}

// Search event
document.getElementById('searchInput').addEventListener('keyup', filterTable);

// Export to CSV
function exportTable() {
    let csv = 'ID,Kategori,Ukuran,Jumlah Terjual,Total Harga\n';
    
    const rows = document.getElementById('tableBody').querySelectorAll('tr');
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const rowData = Array.from(cells).slice(0, 5).map(cell => '"' + cell.textContent.trim() + '"').join(',');
        csv += rowData + '\n';
    });
    
    const link = document.createElement('a');
    link.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
    link.download = 'data_penjualan_' + new Date().toISOString().slice(0, 10) + '.csv';
    link.click();
}

// Initialize on load
window.addEventListener('load', initTable);
