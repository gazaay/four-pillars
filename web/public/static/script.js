function updateChart() {
    var plotData = {
        // Replace with your Matplotlib plot data
        x: [1, 2, 3, 4, 5],
        y: [10, 11, 8, 12, 14],
        type: 'scatter',
        mode: 'lines+markers',
        marker: { color: 'blue' },
    };

    Plotly.newPlot('chart-container', [plotData], {
        title: 'Your Plot',
        xaxis: { title: 'X-axis' },
        yaxis: { title: 'Y-axis' },
    });
}

updateChart();
