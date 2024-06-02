import React from 'react';
import { Paper, Typography, Box, Grid } from '@mui/material';

const Current8wCard = ({ data }) => {
    return (
        <Paper elevation={3} sx={{ p: 2, height: '100%' }}>
          <Typography variant="h6">Current 8w</Typography>
          <Box sx={{ mt: 2 }}>
          <Grid container spacing={1}>
              <Grid item xs={2}>
                <Typography variant="h7">
                  時
                </Typography>
              </Grid>
              <Grid item xs={2}>
                <Typography variant="h7">
                日
                </Typography>
              </Grid>
              <Grid item xs={2}>
                <Typography variant="h7">
                負時
                </Typography>
              </Grid>
              <Grid item xs={2}>
                <Typography variant="h7">
                月
                </Typography>
              </Grid>
              <Grid item xs={2}>
                <Typography variant="h7">
                年
                </Typography>
              </Grid>
              <Grid item xs={2}>
                <Typography variant="h7">
                負年
                </Typography>
              </Grid>
              
            </Grid>
            <Grid container spacing={1}>
              <Grid item xs={2}>
                <Typography variant="h5">
                  {data.base_time}
                </Typography>
              </Grid>
              <Grid item xs={2}>
                <Typography variant="h5">
                  {data.base_day}
                </Typography>
              </Grid>
              <Grid item xs={2}>
                <Typography variant="h5">
                  {data.base_minus_time}
                </Typography>
              </Grid>
              <Grid item xs={2}>
                <Typography variant="h5">
                  {data.base_month}
                </Typography>
              </Grid>
              <Grid item xs={2}>
                <Typography variant="h5">
                  {data.base_year}
                </Typography>
              </Grid>
              <Grid item xs={2}>
                <Typography variant="h5">
                  {data.base_minus_month}
                </Typography>
              </Grid>
              {/* <Grid item xs={12}>
                <Typography variant="h6">
                  +{data.percentage_change} month over month
                </Typography>
              </Grid> */}
            </Grid>
          </Box>
        </Paper>
      );
};

export default Current8wCard;
