// import React, { useState, useEffect } from 'react';
// import { AppBar, Toolbar, Typography, Tabs, Tab, Box, Grid, Paper, IconButton, Avatar, TextField } from '@mui/material';
// import { MoreVert as MoreVertIcon, Share as ShareIcon } from '@mui/icons-material';
// import TodayTargetCard from './TodayTargetCard';
// import Base8wCard from './Base8wCard';
// import Current8wCard from './Current8wCard';
// import HSIWeeklyChart from './HSIWeeklyChart';
// import WatchList from './WatchList';
// import Next10Days from './Next10Days';
// import HSIMultiYearChart from './HSIMultiYearChart';
// import { useParams } from 'react-router-dom';
// import axios from 'axios';

// const Dashboard = () => {
//   const { date } = useParams();
//   const [data, setData] = useState(null);

//   useEffect(() => {
//     const fetchData = async () => {
//       try {
//         const result = await axios.get(`/data/GF4_data/${date}.json`);
//         setData(result.data);
//       } catch (error) {
//         console.error('Error fetching data:', error);
//       }
//     };
//     fetchData();
//   }, [date]);

//   const handleTabChange = (event, newValue) => {
//     setTabValue(newValue);
//     if (newValue === 1) { // Assuming 'Detail' is the second tab (index 1)
//       navigate('/details');
//     }
//   };


//   if (!data) {
//     return <div>Loading...</div>;
//   }

//   return (
//     <Box sx={{ flexGrow: 1, px: 4, py: 2 }}> 
//       <AppBar position="static">
//         <Toolbar>
//           <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
//             GF 4.0
//           </Typography>
//           {/* <Tabs value={0} aria-label="navigation tabs">
//             <Tab label="HSI" />
//             <Tab label="S&P" />
//             <Tab label="DJ" />
//           </Tabs> */}
//           <IconButton color="inherit">
//             <MoreVertIcon />
//           </IconButton>
//           <IconButton color="inherit">
//             <ShareIcon />
//           </IconButton>
//           <Avatar alt="User" src="/static/images/avatar/1.jpg" />
//         </Toolbar>
//       </AppBar>
//       <Box sx={{ mt: 2, mb: 2 }}>
//         <Grid container spacing={2} alignItems="stretch" sx={{ mb: 2 }}>
//           <Grid item xs={9} sx={{ display: 'flex', flexDirection: 'column' }}>
//             <Tabs value={tabValue} onChange={handleTabChange} aria-label="sub tabs">
//              <Tab label="Summary" />
//               <Tab label="Detail" />
//               <Tab label="Support" />
//             </Tabs>
//           </Grid>
//           <Grid item xs={3}>
//             <TextField fullWidth label="Search" variant="outlined" />
//           </Grid>
//         </Grid>
//         <Grid container spacing={2} alignItems="stretch" sx={{ mb: 2 }}>
//         <Grid item xs={4} sx={{ display: 'flex', flexDirection: 'column' }}>
//            <TodayTargetCard data={data.todayTarget} />
//           </Grid>
//           <Grid item xs={4} sx={{ display: 'flex', flexDirection: 'column' }}>
//            <Base8wCard data={data.base8w} />
//           </Grid>
//           <Grid item xs={4} sx={{ display: 'flex', flexDirection: 'column' }}>
//           <Current8wCard data={data.current8w} />
//           </Grid>
//         </Grid>
//         <Grid container spacing={2} alignItems="stretch" sx={{ mb: 2 }}>
//           <Grid item xs={8} sx={{ display: 'flex', flexDirection: 'column' }}>
//             <HSIWeeklyChart data={data.hsiWeekly} />
//           </Grid>
//           <Grid item xs={4} sx={{ display: 'flex', flexDirection: 'column' }}>
//             <WatchList data={data.watchList} />
//           </Grid>
//         </Grid>
//         <Grid container spacing={2} sx={{ mt: 2 }}>
//           <Grid item xs={4}>
//             <Next10Days data={data.next10Days} />
//           </Grid>
//           <Grid item xs={8}>
//             <HSIMultiYearChart data={data.hsiMultiYear} />
//           </Grid>
//         </Grid>
//       </Box>
//     </Box>
//   );
// };

// export default Dashboard;
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { Box, Grid } from '@mui/material';
import TodayTargetCard from './TodayTargetCard';
import Base8wCard from './Base8wCard';
import Current8wCard from './Current8wCard';
import HSIWeeklyChart from './HSIWeeklyChart';
import WatchList from './WatchList';
import Next10Days from './Next10Days';
import HSIMultiYearChart from './HSIMultiYearChart';

const Dashboard = () => {
  const { date } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await axios.get(`/data/GF4_data/${date}.json`);
        setData(result.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    fetchData();
  }, [date]);

  if (!data) {
    return <div>Loading...</div>;
  }

  return (
    <Box>
      <Grid container spacing={2} alignItems="stretch" sx={{ mb: 2 }}>
        <Grid item xs={4} sx={{ display: 'flex', flexDirection: 'column' }}>
          <TodayTargetCard data={data.todayTarget} />
        </Grid>
        <Grid item xs={4} sx={{ display: 'flex', flexDirection: 'column' }}>
          <Base8wCard data={data.base8w} />
        </Grid>
        <Grid item xs={4} sx={{ display: 'flex', flexDirection: 'column' }}>
          <Current8wCard data={data.current8w} />
        </Grid>
      </Grid>
      <Grid container spacing={2} alignItems="stretch" sx={{ mb: 2 }}>
      <Grid item xs={8} sx={{ display: 'flex', flexDirection: 'column' }}>
          <HSIWeeklyChart data={data.hsiWeekly} />
        </Grid>
        <Grid item xs={4} sx={{ display: 'flex', flexDirection: 'column' }}>
          <WatchList data={data.watchList} />
        </Grid>
      </Grid>
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={4}>
          <Next10Days data={data.next10Days} />
        </Grid>
        <Grid item xs={8}>
          <HSIMultiYearChart data={data.hsiMultiYear} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
