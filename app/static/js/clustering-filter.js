// Clustering filter functionality for dashboard
(function() {
    'use strict';
    
    console.log('🔧 Clustering filter script loaded');
    
    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log('📱 DOM ready, initializing clustering filter...');
        
        // Get elements
        const tierFilter = document.getElementById('tierFilter');
        const applyFilterBtn = document.getElementById('applyFilterBtn');
        const clusteringTable = document.getElementById('clusteringTable');
        const emptyState = document.getElementById('emptyState');
        
        // Check if elements exist
        if (!tierFilter || !clusteringTable) {
            console.log('ℹ️ Clustering elements not found (probably not on dashboard page)');
            return;
        }
        
        console.log('✅ All elements found, setting up event listeners');
        
        // Initial counts update
        updateSummaryCounts();
        
        // Apply filter button click handler
        if (applyFilterBtn) {
            applyFilterBtn.addEventListener('click', function() {
                const selectedTier = tierFilter.value;
                console.log('🎯 Apply button clicked, filter:', selectedTier);
                applyFilter(selectedTier);
                showFeedback();
            });
            console.log('✓ Button event listener attached');
        }
        
        // Enter key support
        tierFilter.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && applyFilterBtn) {
                e.preventDefault();
                applyFilterBtn.click();
            }
        });
        
        console.log('✅ Clustering filter ready!');
        
        // Filter function
        function applyFilter(tier) {
            console.log('\n━━━━━ APPLYING FILTER ━━━━━');
            console.log('Filter value:', `"${tier}"`);
            
            const rows = document.querySelectorAll('#clusteringTableBody .cluster-row');
            console.log('Total rows:', rows.length);
            
            if (rows.length === 0) {
                console.error('❌ No rows found!');
                return;
            }
            
            let visibleCount = 0;
            
            // Log first 3 rows for debugging
            rows.forEach((row, index) => {
                const rowTier = row.getAttribute('data-tier');
                
                if (index < 3) {
                    console.log(`Sample row ${index + 1}:`, {
                        tier: rowTier,
                        matches: (tier === 'all' || rowTier === tier)
                    });
                }
                
                const shouldShow = (tier === 'all') || (rowTier === tier);
                
                if (shouldShow) {
                    row.style.display = 'table-row';
                    visibleCount++;
                    
                    // Update row number
                    const firstCell = row.querySelector('td:first-child');
                    if (firstCell) {
                        firstCell.textContent = visibleCount;
                    }
                } else {
                    row.style.display = 'none';
                }
            });
            
            console.log('Visible rows:', visibleCount);
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━\n');
            
            // Show/hide empty state
            if (visibleCount === 0) {
                clusteringTable.style.display = 'none';
                if (emptyState) emptyState.style.display = 'block';
            } else {
                clusteringTable.style.display = 'table';
                if (emptyState) emptyState.style.display = 'none';
            }
        }
        
        // Update summary counts
        function updateSummaryCounts() {
            const rows = document.querySelectorAll('#clusteringTableBody .cluster-row');
            const counts = {
                'Terlaris': 0,
                'Sedang': 0,
                'Kurang Laris': 0
            };
            
            rows.forEach(row => {
                const tier = row.getAttribute('data-tier');
                if (tier in counts) {
                    counts[tier]++;
                }
            });
            
            console.log('📊 Summary counts:', counts);
            
            // Update displays
            const elements = {
                'Terlaris': document.getElementById('count-terlaris'),
                'Sedang': document.getElementById('count-sedang'),
                'Kurang Laris': document.getElementById('count-kurang')
            };
            
            Object.keys(elements).forEach(tier => {
                if (elements[tier]) {
                    elements[tier].textContent = counts[tier];
                }
            });
        }
        
        // Visual feedback
        function showFeedback() {
            if (!applyFilterBtn) return;
            
            const originalHTML = applyFilterBtn.innerHTML;
            const originalClass = applyFilterBtn.className;
            
            applyFilterBtn.innerHTML = '<i class="bi bi-check-circle-fill"></i> Diterapkan!';
            applyFilterBtn.className = 'btn btn-success';
            
            setTimeout(() => {
                applyFilterBtn.innerHTML = originalHTML;
                applyFilterBtn.className = originalClass;
            }, 1500);
        }
    });
})();
