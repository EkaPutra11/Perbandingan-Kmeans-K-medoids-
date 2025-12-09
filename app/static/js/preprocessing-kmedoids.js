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
    statusText.textContent = 'Running KMedoids Clustering...';
    statusMessage.textContent = `Processing ${k} clusters, please wait...`;

    try {
        const response = await fetch('/preprocessing/kmedoids', {
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
            statusMessage.textContent = `Hasil disimpan dengan Cost: ${parseFloat(data.cost).toFixed(2)}`;
            
            // Show metrics
            document.getElementById('cost-value').textContent = 
                parseFloat(data.cost).toFixed(2);
            document.getElementById('dbi-value').textContent = 
                parseFloat(data.davies_bouldin).toFixed(3);
            document.getElementById('metrics-container').classList.remove('d-none');

            // Show results
            displayFinalResults(data.analysis);
            document.getElementById('final-results-container').classList.remove('d-none');

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
        btnText.textContent = '▶️ Jalankan Clustering';
        this.disabled = false;
    }
});

// Display final results table and summary
function displayFinalResults(analysis) {
    const tbody = document.getElementById('final-results-tbody');
    const summaryStatsDiv = document.getElementById('summary-stats');
    
    tbody.innerHTML = '';
    summaryStatsDiv.innerHTML = '';

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

    // Determine tier based on cluster totals
    const tierByTotal = {};
    const clusterTotals = [];
    
    for (let i = 0; i <= 2; i++) {
        clusterTotals.push({
            cluster: i,
            total: clusterData[i].total
        });
    }
    
    clusterTotals.sort((a, b) => b.total - a.total);
    
    tierByTotal[clusterTotals[0].cluster] = { name: 'Terlaris ⭐', icon: '⭐' };
    tierByTotal[clusterTotals[1].cluster] = { name: 'Sedang 📊', icon: '📊' };
    tierByTotal[clusterTotals[2].cluster] = { name: 'Kurang Laris 📉', icon: '📉' };
    
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
    summaryStatsDiv.innerHTML = summaryHtml;
}

// Load and display iterations
async function loadAndDisplayIterations() {
    try {
        const response = await fetch('/preprocessing/kmedoids/iterations');
        const data = await response.json();

        if (data.status === 'success') {
            const iterations = data.iterations || [];
            
            if (iterations.length > 0) {
                renderIterations(iterations);
                document.getElementById('iterations-container').classList.remove('d-none');
            }
        }
    } catch (error) {
        console.error('Error loading iterations:', error);
    }
}

// Render iterations
function renderIterations(iterations) {
    const listContainer = document.getElementById('iterations-list');
    listContainer.innerHTML = '';

    if (!iterations || iterations.length === 0) {
        listContainer.innerHTML = '<p class="text-muted text-center py-4">Tidak ada data iterasi</p>';
        return;
    }

    iterations.forEach((iteration, idx) => {
        const isLast = idx === iterations.length - 1;
        const card = document.createElement('div');
        card.className = 'iteration-card';
        
        let html = `
            <div class="iteration-header">
                🔄 Iterasi ${iteration.iteration}${isLast ? ' (Konvergen)' : ''}
            </div>
            <div class="iteration-content">
        `;

        // Tampilkan Medoid (Pusat Cluster)
        if (iteration.medoid_points && iteration.medoid_points.length > 0) {
            html += `
                <div class="centroid-section" style="margin-bottom: 2rem;">
                    <div class="centroid-title" style="font-size: 1rem; font-weight: 600; margin-bottom: 1rem; color: #333;">📍 Medoid (Pusat Cluster)</div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem;">
            `;

            iteration.medoid_points.forEach((medoidPoint, clusterId) => {
                const tierColors = { '0': '#198754', '1': '#ffc107', '2': '#dc3545' };
                const tierBgColors = { '0': '#d1e7dd', '1': '#fff3cd', '2': '#f8d7da' };
                const tierColor = tierColors[String(clusterId)] || '#198754';
                const tierBgColor = tierBgColors[String(clusterId)] || '#e7f5f0';
                
                html += `
                    <div style="border: 2px solid ${tierColor}; border-radius: 8px; padding: 1.25rem; background-color: ${tierBgColor}; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <div style="font-size: 1.25rem; font-weight: 700; color: ${tierColor}; margin-bottom: 1.5rem; padding-bottom: 0.75rem; border-bottom: 2px solid ${tierColor}; text-align: center;">
                            C${clusterId}
                        </div>
                        <div style="margin-bottom: 1.5rem;">
                            <div style="font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-bottom: 0.4rem;">Jumlah Terjual</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: ${tierColor}; font-family: 'Courier New', monospace;">${parseFloat(medoidPoint[0]).toFixed(2)}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-bottom: 0.4rem;">Total Harga</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: ${tierColor}; font-family: 'Courier New', monospace;">${parseFloat(medoidPoint[1]).toFixed(2)}</div>
                        </div>
                    </div>
                `;
            });

            html += `</div></div>`;
        }

        // Tampilkan Distance Table
        if (iteration.cluster_assignments && iteration.cluster_assignments.length > 0) {
            html += `
                <div class="distance-section" style="margin-top: 1.5rem;">
                    <div class="distance-title" style="font-size: 1rem; font-weight: 600; margin-bottom: 1rem; color: #333;">📏 Jarak Euclidean ke Setiap Medoid</div>
                    <div class="table-responsive">
                        <table class="table table-hover table-sm" style="border: 1px solid #dee2e6; border-radius: 6px; overflow: hidden; margin-bottom: 0;">
                            <thead style="background-color: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                                <tr>
                                    <th style="padding: 0.75rem; font-weight: 600; color: #333;">Kategori</th>
                                    <th style="padding: 0.75rem; font-weight: 600; color: #333;">Size</th>
                                    <th style="padding: 0.75rem; font-weight: 600; color: #333; text-align: right;">Jumlah Terjual</th>
                                    <th style="padding: 0.75rem; font-weight: 600; color: #333; text-align: center;">C0 Distance</th>
                                    <th style="padding: 0.75rem; font-weight: 600; color: #333; text-align: center;">C1 Distance</th>
                                    <th style="padding: 0.75rem; font-weight: 600; color: #333; text-align: center;">C2 Distance</th>
                                    <th style="padding: 0.75rem; font-weight: 600; color: #333; text-align: center;">Assigned</th>
                                </tr>
                            </thead>
                            <tbody>
            `;

            iteration.cluster_assignments.slice(0, 15).forEach((assignment, rowIdx) => {
                const clusterClass = `c${assignment.assigned_cluster.toLowerCase().replace('c', '')}`;
                const bgColor = rowIdx % 2 === 0 ? 'white' : '#f9f9f9';
                html += `
                    <tr style="background-color: ${bgColor}; border-bottom: 1px solid #dee2e6;">
                        <td style="padding: 0.75rem;">${assignment.kategori}</td>
                        <td style="padding: 0.75rem;">${assignment.size_range}</td>
                        <td style="padding: 0.75rem; text-align: right; font-weight: 500;">${assignment.jumlah_terjual}</td>
                        <td style="padding: 0.75rem; text-align: center; font-family: monospace; color: #666;">${assignment.distances['C0'] ? parseFloat(assignment.distances['C0']).toFixed(3) : '0.000'}</td>
                        <td style="padding: 0.75rem; text-align: center; font-family: monospace; color: #666;">${assignment.distances['C1'] ? parseFloat(assignment.distances['C1']).toFixed(3) : '0.000'}</td>
                        <td style="padding: 0.75rem; text-align: center; font-family: monospace; color: #666;">${assignment.distances['C2'] ? parseFloat(assignment.distances['C2']).toFixed(3) : '0.000'}</td>
                        <td style="padding: 0.75rem; text-align: center;"><span class="badge bg-success" style="padding: 0.4rem 0.6rem; font-size: 0.8rem;">${assignment.assigned_cluster}</span></td>
                    </tr>
                `;
            });

            html += `
                            </tbody>
                        </table>
                    </div>
                    <p style="font-size: 0.8rem; color: #6c757d; margin-top: 0.75rem; margin-bottom: 0;">* Menampilkan 15 data pertama</p>
                </div>
            `;

            if (isLast) {
                html += `
                    <div class="convergence-badge">
                        ✓ <strong>Medoid Konvergen</strong> - Algoritma selesai pada iterasi ini
                    </div>
                `;
            }
        }

        html += `</div>`;
        card.innerHTML = html;
        listContainer.appendChild(card);
    });
}

// Load existing results on page load
window.addEventListener('DOMContentLoaded', async function() {
    try {
        const response = await fetch('/preprocessing/kmedoids');
        const data = await response.json();

        if (data.cost !== null) {
            document.getElementById('cost-value').textContent = 
                parseFloat(data.cost).toFixed(2);
            document.getElementById('dbi-value').textContent = 
                parseFloat(data.davies_bouldin).toFixed(3);
            document.getElementById('metrics-container').classList.remove('d-none');

            if (data.analysis) {
                displayFinalResults(data.analysis);
                document.getElementById('final-results-container').classList.remove('d-none');
            }
        }
    } catch (error) {
        console.error('Error loading results:', error);
    }

    // Load iterations
    await loadAndDisplayIterations();
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
                document.getElementById('cost-value').textContent = '-';
                document.getElementById('dbi-value').textContent = '-';
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
});

