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
            displayAnalysis(data.analysis);
            document.getElementById('results-container').classList.remove('d-none');

            // Show chart
            displayClusterChart(data.cluster_distribution);
            document.getElementById('chart-container').classList.remove('d-none');

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
                                <span class="badge bg-success" style="padding: 0.4rem 0.6rem; font-size: 0.8rem;">C${dominantCluster}</span>
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
        const response = await fetch('/preprocessing/kmedoids', {
            headers: {
                'Accept': 'application/json'
            }
        });
        const data = await response.json();

        if (data.cost !== null) {
            document.getElementById('cost-value').textContent = 
                parseFloat(data.cost).toFixed(2);
            document.getElementById('dbi-value').textContent = 
                parseFloat(data.davies_bouldin).toFixed(3);
            document.getElementById('metrics-container').classList.remove('d-none');

            if (data.analysis) {
                displayAnalysis(data.analysis);
                document.getElementById('results-container').classList.remove('d-none');
            }

            if (data.cluster_distribution) {
                displayClusterChart(data.cluster_distribution);
                document.getElementById('chart-container').classList.remove('d-none');
            }
        }
    } catch (error) {
        console.error('Error loading results:', error);
    }
});
