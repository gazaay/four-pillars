import React from 'react';
import { Paper, Typography, List, ListItem, ListItemText, Avatar } from '@mui/material';

const WatchList = ({ data }) => {
  return (
    // <Paper elevation={3} sx={{ p: 2 }}>
        <Paper elevation={3} sx={{ p: 2, textAlign: 'center', height: '100%' }}>
      <Typography variant="h6">Watch List</Typography>
      <List>
        {data.map((item, index) => (
          <ListItem key={index}>
            <Avatar alt={item.symbol} src={`/static/images/avatar/${index + 1}.jpg`} />
            <ListItemText primary={item.symbol} secondary={item.value} />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default WatchList;
