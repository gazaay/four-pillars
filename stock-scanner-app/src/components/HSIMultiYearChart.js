import React from 'react';
import { Paper, Typography } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,ResponsiveContainer } from 'recharts';

const HSIMultiYearChart = ({ data }) => {
  return (
    <Paper elevation={3} sx={{ p: 2, textAlign: 'center', height: '100%' }}>
      <Typography variant="h6">HSI Multi Year</Typography>
      <ResponsiveContainer width="100%" height={300}>
      <LineChart width={700} height={500} data={data} margin={{ top: 5, right: 30, left: 50, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis domain={['dataMin - 1000', 'dataMax + 1000']} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="value" stroke="#8884d8" activeDot={{ r: 8 }} />
      </LineChart>
      </ResponsiveContainer>
    </Paper>
  );
};

export default HSIMultiYearChart;
