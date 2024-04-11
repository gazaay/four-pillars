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

const MiniChart = ({ dataPoints, symbol }) => {
  const imagePath = `/minigraph/${symbol}.jpg`;
  dataPoints = [
    {"day": 1, "price": 162.48},
    {"day": 2, "price": 161.55},
    {"day": 3, "price": 158.51},
    {"day": 4, "price": 163.58},
    {"day": 5, "price": 159.09},
    {"day": 6, "price": 164.76},
    {"day": 7, "price": 158.01},
    {"day": 8, "price": 160.29},
    {"day": 9, "price": 164.99},
    {"day": 10, "price": 165.58}
  ];
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

  // return <Line data={data} options={options} />;
  return <div>
          <img src={imagePath} alt={`${symbol} Mini Chart`} width="250px" />
        </div>;
};

export default MiniChart;
