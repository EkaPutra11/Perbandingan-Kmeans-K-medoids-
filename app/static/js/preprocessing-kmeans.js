let clusterChart = null;

document.getElementById('run-btn').addEventListener('click', async function() {
    const k = document.getElementById('k-value').value;
    const spinner = document.getElementById('spinner');
    const btnText = document.getElementById('btn-text');
    const alertContainer = document.getElementById('alert-container');
    const statusContainer = document.getElementById('status-container');
    const statusText = document.getElementById('status-text');
    const statusMessage = document.getElementById('status-message');
    const statusSpinner = document.getElementById('status-spinner');

    // Show loading state
    spinner.classList.remove('d-none');
    btnText.textContent = 'Processing...';
    this.disabled = true;
    alertContainer.innerHTML = '';
    statusContainer.classList.remove('d-none');
    statusText.textContent = 'Running KMeans Clustering...';
    statusMessage.textContent = `Processing ${k} clusters, please wait...`;

    try {
        const response = await fetch('/preprocessing/kmeans', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'k=' + k
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            // Show success message
            statusSpinner.innerHTML = '<i class="text-success" style="font-size: 1.5rem;">✓</i>';
            statusText.textContent = 'Clustering Berhasil!';
            statusMessage.textContent = `Hasil disimpan dengan Inertia: ${parseFloat(data.inertia).toFixed(2)}`;
            
            // Show metrics
            document.getElementById('inertia-value').textContent = 
                parseFloat(data.inertia).toFixed(2);
            document.getElementById('dbi-value').textContent = 
                parseFloat(data.davies_bouldin).toFixed(3);
            document.getElementById('metrics-container').classList.remove('d-none');

            // Load and display iterations
            await loadAndDisplayIterations();

            // Change status container color to success
            setTimeout(() => {
                const statusDiv = statusContainer.querySelector('.alert');
                statusDiv.classList.remove('alert-info');
                statusDiv.classList.add('alert-success');
            }, 500);


            // Success alert
            alertContainer.innerHTML = `
                <div class="alert alert-success alert-dismissible fade show" role="alert">
                    <strong>Success!</strong> Clustering completed with K=${k} clusters.
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
        } else {
            statusSpinner.innerHTML = '<i class="text-danger" style="font-size: 1.5rem;">✗</i>';
            statusText.textContent = 'Clustering Gagal!';
            statusMessage.textContent = data.error || 'Unknown error occurred';
            const statusDiv = statusContainer.querySelector('.alert');
            statusDiv.classList.remove('alert-info');
            statusDiv.classList.add('alert-danger');
            
            alertContainer.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <strong>Error:</strong> ${data.error || 'Unknown error occurred'}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
        }
    } catch (error) {
        statusSpinner.innerHTML = '<i class="text-danger" style="font-size: 1.5rem;">✗</i>';
        statusText.textContent = 'Clustering Gagal!';
        statusMessage.textContent = error.message;
        const statusDiv = statusContainer.querySelector('.alert');
        statusDiv.classList.remove('alert-info');
        statusDiv.classList.add('alert-danger');
        
        alertContainer.innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <strong>Error:</strong> ${error.message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    } finally {
        // Hide loading state
        spinner.classList.add('d-none');
        btnText.textContent = 'Run Clustering';
        this.disabled = false;
    }
});

// Function to display final results
function displayFinalResults(analysis) {
    const tbody = document.getElementById('final-results-tbody');
    const summaryStats = document.getElementById('summary-stats');
    
    if (!analysis || (!analysis.standard && !analysis.non_standard)) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-3">Tidak ada data</td></tr>';
        return;
    }

    let html = '';
    const clusterData = { '0': {}, '1': {}, '2': {} };
    
    // Initialize cluster data
    for (let i = 0; i <= 2; i++) {
        clusterData[i] = {
            count: 0,
            total: 0,
            sizeRanges: 0
        };
    }

    // Process Standard
    if (analysis.standard) {
        Object.entries(analysis.standard).forEach(([range, data]) => {
            const dominantCluster = data.dominant_cluster !== undefined ? data.dominant_cluster : '-';
            html += `
                <tr>
                    <td>Standard</td>
                    <td>${range}</td>
                    <td style="text-align: right;">${data.total_terjual.toFixed(0)}</td>
                    <td style="text-align: center;">
                        <span class="cluster-badge c${dominantCluster}">C${dominantCluster}</span>
                    </td>
                </tr>
            `;
            if (dominantCluster !== '-') {
                clusterData[dominantCluster].count += data.items ? data.items.length : 1;
                clusterData[dominantCluster].total += data.total_terjual;
                clusterData[dominantCluster].sizeRanges++;
            }
        });
    }

    // Process Non-Standard
    if (analysis.non_standard) {
        Object.entries(analysis.non_standard).forEach(([range, data]) => {
            const dominantCluster = data.dominant_cluster !== undefined ? data.dominant_cluster : '-';
            // Extract kategori from first item if available
            let kategori = 'Non-Standard';
            if (data.items && data.items.length > 0) {
                kategori = data.items[0].kategori;
            }
            
            html += `
                <tr>
                    <td>${kategori}</td>
                    <td>${range}</td>
                    <td style="text-align: right;">${data.total_terjual.toFixed(0)}</td>
                    <td style="text-align: center;">
                        <span class="cluster-badge c${dominantCluster}">C${dominantCluster}</span>
                    </td>
                </tr>
            `;
            if (dominantCluster !== '-') {
                clusterData[dominantCluster].count += data.items ? data.items.length : 1;
                clusterData[dominantCluster].total += data.total_terjual;
                clusterData[dominantCluster].sizeRanges++;
            }
        });
    }

    tbody.innerHTML = html;

    // Determine tier based on actual cluster totals
    const tierByTotal = {};
    const clusterTotals = [];
    
    // Collect cluster totals
    for (let i = 0; i <= 2; i++) {
        clusterTotals.push({
            cluster: i,
            total: clusterData[i].total
        });
    }
    
    // Sort by total (descending)
    clusterTotals.sort((a, b) => b.total - a.total);
    
    // Assign tiers based on ranking
    tierByTotal[clusterTotals[0].cluster] = { name: 'Terlaris ⭐', icon: '⭐', emoji: '⭐' };
    tierByTotal[clusterTotals[1].cluster] = { name: 'Sedang 📊', icon: '📊', emoji: '📊' };
    tierByTotal[clusterTotals[2].cluster] = { name: 'Kurang Laris 📉', icon: '📉', emoji: '📉' };
    
    const tierColors = { 
        'Terlaris ⭐': '#198754',
        'Sedang 📊': '#ffc107',
        'Kurang Laris 📉': '#dc3545'
    };

    // Display Summary Stats as Table
    let summaryHtml = `
        <div class="table-responsive" style="margin-top: 1rem;">
            <table class="table table-hover" style="border: 1px solid #dee2e6; border-radius: 6px;">
                <thead style="background-color: #f8f9fa;">
                    <tr>
                        <th style="padding: 0.75rem; font-weight: 600; color: #333;">CLUSTER</th>
                        <th style="padding: 0.75rem; font-weight: 600; color: #333; text-align: right;">JUMLAH</th>
                        <th style="padding: 0.75rem; font-weight: 600; color: #333;">DESKRIPSI</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    for (let i = 0; i <= 2; i++) {
        const tierInfo = tierByTotal[i];
        const tierName = tierInfo.name;
        const bgColor = tierColors[tierName];
        const data = clusterData[i];
        
        // Extract description (without emoji)
        const desc = tierName.split(' ')[0]; // 'Terlaris', 'Sedang', or 'Kurang Laris'
        
        summaryHtml += `
            <tr style="border-bottom: 1px solid #dee2e6;">
                <td style="padding: 0.75rem; font-weight: 600; color: ${bgColor};">C${i}</td>
                <td style="padding: 0.75rem; text-align: right; font-weight: 500;">${data.total.toFixed(0)}</td>
                <td style="padding: 0.75rem;">${tierName}</td>
            </tr>
        `;
    }
    
    summaryHtml += `
                </tbody>
            </table>
        </div>
    `;
    summaryStats.innerHTML = summaryHtml;
}

function displayAnalysis(analysis) {
    const standardContent = document.getElementById('standard-content');
    const nonStandardContent = document.getElementById('non-standard-content');

    function renderCategoryAnalysis(categoryData, categoryName) {
        if (!categoryData || Object.keys(categoryData).length === 0) {
            return '<p class="text-muted text-center py-4">Tidak ada data</p>';
        }

        let html = '';
        
        // Group by tier
        const tiers = {
            'terlaris': { name: 'Terlaris', icon: '⭐', color: '#198754' },
            'sedang': { name: 'Sedang', icon: '📊', color: '#ffc107' },
            'kurang_laris': { name: 'Kurang Laris', icon: '📉', color: '#dc3545' }
        };

        // Group data by tier
        const tierData = {
            'terlaris': [],
            'sedang': [],
            'kurang_laris': []
        };

        Object.entries(categoryData).forEach(([range, data]) => {
            const tier = data.tier || 'kurang_laris';
            if (tierData[tier] !== undefined) {
                tierData[tier].push({ range, ...data });
            }
        });

        // Render category header
        html += `<div class="category-wrapper">`;

        // Render each tier
        Object.entries(tiers).forEach(([tierKey, tierInfo]) => {
            if (tierData[tierKey].length === 0) return;

            html += `
                <div class="tier-block mb-4">
                    <h6 class="tier-header mb-3" style="color: ${tierInfo.color}; font-weight: 600; padding-bottom: 0.5rem; border-bottom: 2px solid ${tierInfo.color};">
                        ${tierInfo.icon} ${tierInfo.name}
                    </h6>
                    
                    <div class="table-responsive">
                        <table class="table table-sm table-hover" style="border: 1px solid #dee2e6; border-radius: 6px; overflow: hidden;">
                            <thead style="background-color: #f8f9fa;">
                                <tr>
                                    <th style="padding: 0.75rem; font-weight: 600; color: #333;">Kategori</th>
                                    <th style="padding: 0.75rem; font-weight: 600; color: #333;">Size</th>
                                    <th style="padding: 0.75rem; font-weight: 600; color: #333; text-align: right;">Jumlah Terjual</th>
                                    <th style="padding: 0.75rem; font-weight: 600; color: #333; text-align: center;">Cluster</th>
                                </tr>
                            </thead>
                            <tbody>
            `;

            tierData[tierKey].forEach((item, idx) => {
                if (item.items && Array.isArray(item.items)) {
                    let sizeRangeTotal = 0;
                    let dominantCluster = item.dominant_cluster !== undefined ? item.dominant_cluster : null;
                    
                    item.items.forEach(subItem => {
                        sizeRangeTotal += parseFloat(subItem.jumlah_terjual || 0);
                    });

                    const bgColor = idx % 2 === 0 ? 'white' : '#f9f9f9';
                    const kategoriText = item.items.length > 0 ? item.items[0].kategori : '-';

                    html += `
                        <tr style="background-color: ${bgColor};">
                            <td style="padding: 0.75rem;">${kategoriText}</td>
                            <td style="padding: 0.75rem;">${item.range}</td>
                            <td style="padding: 0.75rem; text-align: right; font-weight: 500;">${sizeRangeTotal.toFixed(0)}</td>
                            <td style="padding: 0.75rem; text-align: center;">
                                <span class="badge bg-primary" style="padding: 0.4rem 0.6rem; font-size: 0.8rem;">C${dominantCluster}</span>
                            </td>
                        </tr>
                    `;
                }
            });

            html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        });

        html += `</div>`;
        return html;
    }

    // Standard
    let standardHtml = `
        <div class="standard-section mb-5">
            <h5 style="font-weight: 700; margin-bottom: 1.5rem; padding-bottom: 0.5rem; border-bottom: 3px solid #0d6efd; color: #0d6efd;">
                ✓ Standard
            </h5>
            ${renderCategoryAnalysis(analysis.standard, 'Standard')}
        </div>
    `;
    standardContent.innerHTML = standardHtml;

    // Non-Standard
    let nonStandardHtml = `
        <div class="non-standard-section">
            <h5 style="font-weight: 700; margin-bottom: 1.5rem; padding-bottom: 0.5rem; border-bottom: 3px solid #dc3545; color: #dc3545;">
                ✗ Non-Standard
            </h5>
            ${renderCategoryAnalysis(analysis.non_standard, 'Non-Standard')}
        </div>
    `;
    nonStandardContent.innerHTML = nonStandardHtml;
}

function displayClusterChart(distribution) {
    const ctx = document.getElementById('cluster-chart').getContext('2d');
    
    if (clusterChart) {
        clusterChart.destroy();
    }

    clusterChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(distribution).map(k => 'Cluster ' + k),
            datasets: [{
                label: 'Number of Items',
                data: Object.values(distribution),
                backgroundColor: [
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(255, 99, 132, 0.7)',
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

// Load existing results on page load
window.addEventListener('DOMContentLoaded', async function() {
    try {
        const response = await fetch('/preprocessing/kmeans', {
            headers: {
                'Accept': 'application/json'
            }
        });
        const data = await response.json();

        if (data.inertia !== null) {
            document.getElementById('inertia-value').textContent = 
                parseFloat(data.inertia).toFixed(2);
            document.getElementById('dbi-value').textContent = 
                parseFloat(data.davies_bouldin).toFixed(3);
            document.getElementById('metrics-container').classList.remove('d-none');
        }
    } catch (error) {
        console.error('Error loading results:', error);
    }
});

// Reset button handler
document.getElementById('reset-btn').addEventListener('click', async function() {
    if (confirm('Apakah Anda yakin ingin mereset semua hasil clustering?')) {
        try {
            const response = await fetch('/delete/results', {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                // Hide metrics and results
                document.getElementById('metrics-container').classList.add('d-none');
                document.getElementById('final-results-container').classList.add('d-none');
                document.getElementById('iterations-container').classList.add('d-none');
                
                // Clear alert
                document.getElementById('alert-container').innerHTML = `
                    <div class="alert alert-info alert-dismissible fade show" role="alert">
                        <strong>Reset Berhasil!</strong> Semua hasil clustering telah dihapus.
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `;
                
                // Clear metric values
                document.getElementById('inertia-value').textContent = '-';
                document.getElementById('dbi-value').textContent = '-';
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
});

// Function to load and display iterations
async function loadAndDisplayIterations() {
    try {
        const response = await fetch('/preprocessing/kmeans/iterations');
        const data = await response.json();

        if (data.status === 'success') {
            displayIterations(data.iterations);
            document.getElementById('iterations-container').classList.remove('d-none');
            
            // Display final results if analysis is available
            if (data.analysis) {
                displayFinalResults(data.analysis);
                document.getElementById('final-results-container').classList.remove('d-none');
            }
        }
    } catch (error) {
        console.error('Error loading iterations:', error);
    }
}

// Function to display iterations
function displayIterations(iterations) {
    const iterationsList = document.getElementById('iterations-list');
    let html = '';

    iterations.forEach((iter, idx) => {
        const isLast = idx === iterations.length - 1;
        html += `
            <div class="iteration-card">
                <div class="iteration-header">
                    🔄 Iterasi ${iter.iteration}${isLast ? ' (Konvergen)' : ''}
                </div>
                <div class="iteration-content">
        `;

        // Tampilkan Centroid
        if (iter.centroids && iter.centroids.length > 0) {
            html += `
                <div class="centroid-section">
                    <div class="centroid-title">📍 Centroid (Pusat Cluster)</div>
                    <div class="centroid-row">
            `;

            const tierNames = { '0': 'Terlaris ⭐', '1': 'Sedang 📊', '2': 'Kurang Laris 📉' };
            const tierClasses = { '0': 'c0', '1': 'c1', '2': 'c2' };

            iter.centroids.forEach((centroid) => {
                const tierName = tierNames[centroid.cluster_id] || `Cluster ${centroid.cluster_id}`;
                const tierClass = tierClasses[centroid.cluster_id] || 'c0';
                html += `
                    <div class="centroid-box">
                        <div class="centroid-label ${tierClass}">
                            C${centroid.cluster_id}
                        </div>
                        <div class="centroid-value">${centroid.jumlah_terjual.toFixed(2)}</div>
                        <div class="centroid-label-small">Jumlah Terjual</div>
                        <div style="margin-top: 0.5rem;"></div>
                        <div class="centroid-value">${centroid.total_harga.toFixed(2)}</div>
                        <div class="centroid-label-small">Total Harga</div>
                    </div>
                `;
            });

            html += `</div></div>`;
        }

        // Tampilkan Distance Table
        if (iter.cluster_assignments && iter.cluster_assignments.length > 0) {
            html += `
                <div class="distance-section">
                    <div class="distance-title">📏 Jarak Euclidean ke Setiap Centroid</div>
                    <div class="table-responsive">
                        <table class="distance-table">
                            <thead>
                                <tr>
                                    <th>Kategori</th>
                                    <th>Size</th>
                                    <th>Jumlah Terjual</th>
                                    <th>C0 Distance</th>
                                    <th>C1 Distance</th>
                                    <th>C2 Distance</th>
                                    <th>Assigned</th>
                                </tr>
                            </thead>
                            <tbody>
            `;

            iter.cluster_assignments.slice(0, 15).forEach((assignment) => {
                const clusterClass = `c${assignment.assigned_cluster.toLowerCase().replace('c', '')}`;
                html += `
                    <tr>
                        <td>${assignment.kategori}</td>
                        <td>${assignment.size_range}</td>
                        <td>${assignment.jumlah_terjual.toFixed(0)}</td>
                        <td class="distance-value">${assignment.distances['C0'].toFixed(3)}</td>
                        <td class="distance-value">${assignment.distances['C1'].toFixed(3)}</td>
                        <td class="distance-value">${assignment.distances['C2'].toFixed(3)}</td>
                        <td><span class="cluster-badge ${clusterClass}">${assignment.assigned_cluster}</span></td>
                    </tr>
                `;
            });

            html += `
                            </tbody>
                        </table>
                        <p style="font-size: 0.8rem; color: #6c757d; margin-top: 0.5rem;">* Menampilkan 15 data pertama</p>
                    </div>
                </div>
            `;

            if (isLast) {
                html += `
                    <div class="convergence-badge">
                        ✓ <strong>Centroid Konvergen</strong> - Algoritma selesai pada iterasi ini
                    </div>
                `;
            }
        }

        html += `</div></div>`;
    });

    iterationsList.innerHTML = html;
}
// Restore state on page load (after all functions are defined)
// REMOVED - localStorage approach removed for simplicity
