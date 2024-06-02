import React from 'react';
import { AppBar, Toolbar, Typography, Tabs, Tab, Box, Grid, IconButton, Avatar, TextField } from '@mui/material';
import { MoreVert as MoreVertIcon, Share as ShareIcon } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const Layout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [tabValue, setTabValue] = React.useState(location.pathname);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    navigate(newValue);
  };

  return (
    <Box sx={{ flexGrow: 1, px: 4, py: 2 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            GF 4.0
          </Typography>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="navigation tabs">
            <Tab label="HSI" value="/" />
            <Tab label="S&P" value="/s-and-p" />
            <Tab label="DJ" value="/dj" />
          </Tabs>
          <IconButton color="inherit">
            <MoreVertIcon />
          </IconButton>
          <IconButton color="inherit">
            <ShareIcon />
          </IconButton>
          <Avatar alt="User" src="/static/images/avatar/1.jpg" />
        </Toolbar>
      </AppBar>
      <Box sx={{ mt: 2, mb: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={9}>
            <Tabs value={tabValue} onChange={handleTabChange} aria-label="sub tabs">
              <Tab label="Summary" value="/" />
              <Tab label="Detail" value="/details" />
              <Tab label="Support" value="/support" />
            </Tabs>
          </Grid>
          <Grid item xs={3}>
            <TextField fullWidth label="Search" variant="outlined" />
          </Grid>
        </Grid>
      </Box>
      {children}
    </Box>
  );
};

export default Layout;
