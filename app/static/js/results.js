function exportResults() {
    let text = 'HASIL CLUSTERING ARWANA SALES\n';
    text += '============================\n\n';
    
    // KMeans
    text += 'KMEANS\n';
    text += `Inertia: {{ formatted_results.kmeans.inertia }}\n`;
    text += `DBI: {{ formatted_results.kmeans.dbi }}\n\n`;
    
    // KMedoids
    text += 'KMEDOIDS\n';
    text += `Cost: {{ formatted_results.kmedoids.cost }}\n`;
    text += `DBI: {{ formatted_results.kmedoids.dbi }}\n\n`;
    
    const link = document.createElement('a');
    link.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(text);
    link.download = 'clustering_results_' + new Date().toISOString().slice(0, 10) + '.txt';
    link.click();
}

function printResults() {
    window.print();
}
