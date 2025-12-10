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


// ========================================
// CLUSTERING RESULTS FILTER (Dashboard)
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard clustering filter initialized');
    
    const tierFilter = document.getElementById('tierFilter');
    const clusteringTable = document.getElementById('clusteringTable');
    const emptyState = document.getElementById('emptyState');
    
    if (!tierFilter || !clusteringTable) {
        console.log('No clustering results on page');
        return; // No clustering results on page
    }

    console.log('Found tierFilter and clusteringTable');

    // Calculate and update summary counts
    updateSummaryCounts();

    // Get apply filter button
    const applyFilterBtn = document.getElementById('applyFilterBtn');
    
    // Filter table when button is clicked
    if (applyFilterBtn) {
        applyFilterBtn.addEventListener('click', function() {
            const selectedTier = tierFilter.value;
            console.log('Applying filter:', selectedTier);
            filterClusteringTable(selectedTier);
            
            // Visual feedback
            this.innerHTML = '<i class="bi bi-check-circle-fill"></i> Diterapkan!';
            this.style.backgroundColor = '#28a745';
            this.style.borderColor = '#28a745';
            
            setTimeout(() => {
                this.innerHTML = '<i class="bi bi-check-circle"></i> Terapkan Filter';
                this.style.backgroundColor = '';
                this.style.borderColor = '';
            }, 1500);
        });
    }
    
    // Also allow Enter key in dropdown to trigger filter
    tierFilter.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && applyFilterBtn) {
            applyFilterBtn.click();
        }
    });

    function filterClusteringTable(tier) {
        console.log('=== Filter Started ===');
        console.log('Selected tier:', tier);
        const rows = document.querySelectorAll('.cluster-row');
        console.log('Total rows found:', rows.length);
        let visibleCount = 0;

        rows.forEach((row, index) => {
            const rowTier = row.getAttribute('data-tier');
            console.log(`Row ${index}: tier="${rowTier}"`);
            
            // Exact match check
            const shouldShow = (tier === 'all') || (rowTier === tier);
            console.log(`  Should show: ${shouldShow} (tier="${tier}", rowTier="${rowTier}")`);
            
            if (shouldShow) {
                row.style.display = 'table-row';
                row.style.opacity = '1';
                visibleCount++;
                
                // Update row number
                const rowNumber = row.querySelector('td:first-child');
                if (rowNumber) {
                    rowNumber.textContent = visibleCount;
                }
            } else {
                row.style.display = 'none';
            }
        });

        console.log('=== Filter Completed ===');
        console.log('Visible rows:', visibleCount);

        // Show/hide empty state
        if (visibleCount === 0) {
            clusteringTable.style.display = 'none';
            if (emptyState) emptyState.style.display = 'block';
        } else {
            clusteringTable.style.display = 'table';
            if (emptyState) emptyState.style.display = 'none';
        }
    }

    function updateSummaryCounts() {
        const rows = document.querySelectorAll('.cluster-row');
        const counts = {
            'Terlaris': 0,
            'Sedang': 0,
            'Kurang Laris': 0
        };

        rows.forEach(row => {
            const tier = row.getAttribute('data-tier');
            if (counts.hasOwnProperty(tier)) {
                counts[tier]++;
            }
        });

        console.log('Tier counts:', counts);

        // Update count displays
        const countTerlaris = document.getElementById('count-terlaris');
        const countSedang = document.getElementById('count-sedang');
        const countKurang = document.getElementById('count-kurang');

        if (countTerlaris) countTerlaris.textContent = counts['Terlaris'];
        if (countSedang) countSedang.textContent = counts['Sedang'];
        if (countKurang) countKurang.textContent = counts['Kurang Laris'];
    }

    // Add hover effects to table rows
    const rows = document.querySelectorAll('.cluster-row');
    rows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
            this.style.transform = 'scale(1.005)';
            this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        });

        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
            this.style.transform = 'scale(1)';
            this.style.boxShadow = '';
        });
    });

    // Simple fade-in animation for tier cards
    const tierCards = document.querySelectorAll('.tier-card');
    tierCards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transition = 'opacity 0.5s ease';
        }, index * 100);
    });

    console.log('Dashboard clustering filter ready');
});
