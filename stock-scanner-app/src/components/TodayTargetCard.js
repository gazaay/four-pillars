import React from 'react';
import { Paper, Typography, Box, Grid } from '@mui/material';

const TodayTargetCard = ({ data }) => {
  return (
    <Paper elevation={3} sx={{ p: 2, textAlign: 'center', height: '100%' }}>
      <Typography variant="h6">Today's Target</Typography>
      <Box sx={{ mt: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Typography variant="h4">H {data.high}</Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="h4">O {data.open}</Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="h4">C {data.close}</Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="h4">L {data.low}</Typography>
          </Grid>
        </Grid>
        <Typography variant="body2" sx={{ mt: 2 }}>{data.date}</Typography>
      </Box>
    </Paper>
  );
};

export default TodayTargetCard;
