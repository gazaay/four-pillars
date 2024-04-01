import React from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js';

// Register the components necessary for Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
);

const MiniChart = ({ dataPoints }) => {
  // Ensure dataPoints is defined before proceeding to map over it
  if (!dataPoints) {
    // Optionally, you can return null or some placeholder component here
    return <div>Loading...</div>;
  }

  const labels = dataPoints.map((_, index) => `Point ${index + 1}`);

  const data = {
    labels,
    datasets: [
      {
        label: 'Stock Value',
        data: dataPoints,
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        display: false,
      },
      y: {
        display: true,
      },
    },
  };

  return <Line data={data} options={options} />;
};

export default MiniChart;
