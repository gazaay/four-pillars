import React, { useState } from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, TableSortLabel } from '@mui/material';
import MiniChart from './MiniChart';


const StockTable = ({ stocks }) => {
  const [orderDirection, setOrderDirection] = useState('asc');
  const [valueToOrderBy, setValueToOrderBy] = useState('stockCode');

  const handleRequestSort = (property) => {
    const isAscending = (valueToOrderBy === property && orderDirection === 'asc');
    setValueToOrderBy(property);
    setOrderDirection(isAscending ? 'desc' : 'asc');
  };

  const sortData = (array, comparator) => {
    const stabilizedThis = array.map((el, index) => [el, index]);
    stabilizedThis.sort((a, b) => {
      const order = comparator(a[0], b[0]);
      if (order !== 0) return order;
      return a[1] - b[1];
    });
    return stabilizedThis.map((el) => el[0]);
  };

  const getComparator = (order, orderBy) => {
    return order === 'desc'
      ? (a, b) => descendingComparator(a, b, orderBy)
      : (a, b) => -descendingComparator(a, b, orderBy);
  };

  const descendingComparator = (a, b, orderBy) => {
    if (b[orderBy] < a[orderBy]) {
      return -1;
    }
    if (b[orderBy] > a[orderBy]) {
      return 1;
    }
    return 0;
  };

  return (
    <TableContainer component={Paper}>
      <Table aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell key="stockCode">
              <TableSortLabel
                active={valueToOrderBy === 'stockCode'}
                direction={valueToOrderBy === 'stockCode' ? orderDirection : 'asc'}
                onClick={() => handleRequestSort('stockCode')}
              >
                Stock Code
              </TableSortLabel>
            </TableCell>
            <TableCell align="right" key="companyName">
              <TableSortLabel
                active={valueToOrderBy === 'companyName'}
                direction={valueToOrderBy === 'companyName' ? orderDirection : 'asc'}
                onClick={() => handleRequestSort('companyName')}
              >
                Company Name
              </TableSortLabel>
            </TableCell>
            <TableCell align="right" key="currentPrice">
              <TableSortLabel
                active={valueToOrderBy === 'currentPrice'}
                direction={valueToOrderBy === 'currentPrice' ? orderDirection : 'asc'}
                onClick={() => handleRequestSort('currentPrice')}
              >
                currentPrice
              </TableSortLabel>
            </TableCell>
            {/* Add more headers based on your requirements */}
            <TableCell align="right">Mini Chart</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {sortData(stocks, getComparator(orderDirection, valueToOrderBy))
            .map((row) => (
              <TableRow key={row.stockCode}>
                <TableCell component="th" scope="row">{row.stockCode}</TableCell>
                <TableCell align="right">{row.companyName}</TableCell>
                <TableCell align="right">{row.currentPrice}</TableCell>
               {/* Add more cells as needed */}

                <TableCell align="right"><MiniChart dataPoints={row.MiniChart} />
                </TableCell>
              </TableRow>
            ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default StockTable;