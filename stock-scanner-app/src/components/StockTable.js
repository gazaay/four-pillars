import React, { useState, useMemo } from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, TableSortLabel, IconButton, Collapse, Box } from '@mui/material';
import MiniChart from './MiniChart';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';

const StockTable = ({ stocks }) => {
  
  const processedStocks = useMemo(() => {
    const groupedBySymbol = stocks.reduce((acc, curr) => {
      (acc[curr.symbol] = acc[curr.symbol] || []).push(curr);
      return acc;
    }, {});

    const sortedAndProcessed = Object.keys(groupedBySymbol).map(symbol => {
      const sortedStocks = groupedBySymbol[symbol].sort((a, b) => new Date(a.time) - new Date(b.time));
      const pc1 = sortedStocks[0]?.Predicted_Close;
      const pc2 = sortedStocks[5]?.Predicted_Close;
      const pc3 = sortedStocks[10]?.Predicted_Close;
      const movement = pc3 ? ((pc3 - pc1) * 100 / pc1).toFixed(2) + '%' : 'N/A'; // Adjusted to show percentage change

      // Pulling additional information from the first object
      const ric_code = sortedStocks[0]?.ric_code;
      const base_time = sortedStocks[0]?.base_time;
      const base_day = sortedStocks[0]?.base_day;
      const base_minus_time = sortedStocks[0]?.base_minus_time;
      const base_month = sortedStocks[0]?.base_month;
      const base_year = sortedStocks[0]?.base_year;
      const base_minus_month = sortedStocks[0]?.base_minus_month;

      const current_time = sortedStocks[0]?.current_time;
      const current_day = sortedStocks[0]?.current_day;
      const current_minus_time = sortedStocks[0]?.current_minus_time;
      const current_month = sortedStocks[0]?.current_month;
      const current_year = sortedStocks[0]?.current_year;
      const current_minus_month = sortedStocks[0]?.current_minus_month;
      const start_time = sortedStocks[0]?.time;
      const end_time = sortedStocks[10]?.time;
      const is_holiday = sortedStocks[0]?.is_holiday === 'true' ? 'Yes' : 'No'; // Assuming is_holiday is a string that can be 'true' or 'false'

      return {
        symbol,
        ric_code,
        base_time,
        base_day,
        base_minus_time,
        base_month,
        base_year,
        base_minus_month,
        current_time,
        current_day,
        current_minus_time,
        current_month,
        current_year,
        current_minus_month,
        is_holiday,
        pc1,
        pc2,
        pc3,
        movement,
        start_time,
        end_time
      };
    });
    return sortedAndProcessed;
    }, [stocks]);

  const [orderDirection, setOrderDirection] = useState('asc');
  const [valueToOrderBy, setValueToOrderBy] = useState('symbol');

  const [open, setOpen] = useState({});

  const handleRowClick = (symbol) => {
    setOpen(prevOpen => ({
      ...prevOpen,
      [symbol]: !prevOpen[symbol]
    }));
  };

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
          <TableCell key="details">
              <TableSortLabel
                active={valueToOrderBy === 'details'}
                direction={valueToOrderBy === 'details' ? orderDirection : 'asc'}
                onClick={() => handleRequestSort('details')}
              >
                Details
              </TableSortLabel>
            </TableCell>
            <TableCell key="symbol">
              <TableSortLabel
                active={valueToOrderBy === 'symbol'}
                direction={valueToOrderBy === 'symbol' ? orderDirection : 'asc'}
                onClick={() => handleRequestSort('symbol')}
              >
                Stock Code
              </TableSortLabel>
            </TableCell>
            <TableCell align="right" key="ric_code">
              <TableSortLabel
                active={valueToOrderBy === 'ric_code'}
                direction={valueToOrderBy === 'ric_code' ? orderDirection : 'asc'}
                onClick={() => handleRequestSort('ric_code')}
              >
                Ric Code
              </TableSortLabel>
            </TableCell>
            <TableCell align="right" key="start_time">
              <TableSortLabel
                active={valueToOrderBy === 'start_time'}
                direction={valueToOrderBy === 'start_time' ? orderDirection : 'asc'}
                onClick={() => handleRequestSort('start_time')}
              >
                Prediction Start Time
              </TableSortLabel>
            </TableCell>
            <TableCell align="right" key="end_time">
              <TableSortLabel
                active={valueToOrderBy === 'end_time'}
                direction={valueToOrderBy === 'end_time' ? orderDirection : 'asc'}
                onClick={() => handleRequestSort('end_time')}
              >
                Prediction End Time
              </TableSortLabel>
            </TableCell>
            <TableCell align="right" key="base_day">
              <TableSortLabel
                active={valueToOrderBy === 'base_day'}
                direction={valueToOrderBy === 'base_day' ? orderDirection : 'asc'}
                onClick={() => handleRequestSort('base_day')}
              >
                八字
              </TableSortLabel>
            </TableCell>
           
            <TableCell align="right" key="is_holiday">
              <TableSortLabel
                active={valueToOrderBy === 'is_holiday'}
                direction={valueToOrderBy === 'is_holiday' ? orderDirection : 'asc'}
                onClick={() => handleRequestSort('is_holiday')}
              >
                is_holiday
              </TableSortLabel>
            </TableCell>
            <TableCell align="right" key="movement">
              <TableSortLabel
                active={valueToOrderBy === 'movement'}
                direction={valueToOrderBy === 'movement' ? orderDirection : 'asc'}
                onClick={() => handleRequestSort('movement')}
              >
                Movement
              </TableSortLabel>
            </TableCell>
            <TableCell align="right" key="pc1">
              <TableSortLabel
                active={valueToOrderBy === 'pc1'}
                direction={valueToOrderBy === 'pc1' ? orderDirection : 'asc'}
                onClick={() => handleRequestSort('pc1')}
              >
                Day + 1
              </TableSortLabel>
            </TableCell>
            <TableCell align="right" key="pc2">
              <TableSortLabel
                active={valueToOrderBy === 'pc2'}
                direction={valueToOrderBy === 'pc2' ? orderDirection : 'asc'}
                onClick={() => handleRequestSort('pc2')}
              >
                Day + 2
              </TableSortLabel>
            </TableCell>
            <TableCell align="right" key="pc3">
              <TableSortLabel
                active={valueToOrderBy === 'pc3'}
                direction={valueToOrderBy === 'pc3' ? orderDirection : 'asc'}
                onClick={() => handleRequestSort('pc3')}
              >
                Day + 3
              </TableSortLabel>
            </TableCell>
            {/* Add more headers based on your requirements */}
            <TableCell align="right">Mini Chart</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {sortData(processedStocks, getComparator(orderDirection, valueToOrderBy))
            .map((row) => (
              <>
                <TableRow key={row.symbol} sx={{ '& > *': { borderBottom: 'unset' } }}>
                  <TableCell>
                    <IconButton size="small" onClick={() => handleRowClick(row.symbol)}>
                      {open[row.symbol] ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                  </TableCell>
                  <TableCell component="th" scope="row">
                    <a href={`http://aastocks.com/en/stocks/analysis/company-fundamental/basic-information?symbol=${row.symbol}`} target="company_info">
                      {row.symbol}
                    </a>
                  </TableCell>
                  <TableCell align="right">{row.ric_code}</TableCell>
                  <TableCell align="right">{row.start_time}</TableCell>
                  <TableCell align="right">{row.end_time}</TableCell>
                  <TableCell align="right" className="horizontalContainer" style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
                    <div className="verticalText">時{row.base_time}</div>
                    <div className="verticalText">日{row.base_day}</div>
                    <div className="verticalText">時{row.base_minus_time}</div>
                    <div className="verticalText">月{row.base_month}</div>
                    <div className="verticalText">年{row.base_year}</div>
                    <div className="verticalText">月{row.base_minus_month}</div>
                  </TableCell>
                  <TableCell align="right" className="horizontalContainer" style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
                    <div className="verticalText">時{row.current_time}</div>
                    <div className="verticalText">日{row.current_day}</div>
                    <div className="verticalText">時{row.current_minus_time}</div>
                    <div className="verticalText">月{row.current_month}</div>
                    <div className="verticalText">年{row.current_year}</div>
                    <div className="verticalText">月{row.current_minus_month}</div>               
                  </TableCell>

                  <TableCell align="right">{row.is_holiday}</TableCell>
                  <TableCell align="right">
                    
                    <a href={`http://aastocks.com/en/stocks/quote/quick-quote.aspx?symbol=0${row.symbol}`} target="movement_window" >
                      {row.movement}
                    </a>
                  </TableCell>
                  <TableCell align="right">{row.pc1}</TableCell>
                  <TableCell align="right">{row.pc2}</TableCell>
                  <TableCell align="right">{row.pc3}</TableCell>
                  
                  {/* Add more cells as needed */}

                  <TableCell align="right"><MiniChart dataPoints={row.MiniChart} symbol={row.symbol}/>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
                    <Collapse in={open[row.symbol]} timeout="auto" unmountOnExit>
                      <Box margin={1}>
                        <Table size="small" aria-label="details">
                          <TableHead>
                            <TableRow>
                              <TableCell>長生(Alpha) </TableCell>
                              <TableCell align="right">Value</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {/* Map over your diff fields here */}
                            <TableRow>
                              <TableCell component="th" scope="row">
                                diff_base_time_current_time
                              </TableCell>
                              <TableCell align="right">{row.diff_base_time_current_time}</TableCell>
                            </TableRow>
                            {/* Include other difference fields similarly */}
                          </TableBody>
                        </Table>
                      </Box>
                    </Collapse>
                  </TableCell>
                </TableRow>
              </>
            ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default StockTable;