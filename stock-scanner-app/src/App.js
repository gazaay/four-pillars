import React, { useState, useEffect } from 'react';
import axios from 'axios';
import logo from './logo.svg';
import './App.css';
import StockTable from './components/StockTable';
import mockData from './data/mockData.json';  // Import the mock data


function App() {

  // const [stocks, setStocks] = useState([]);

  // useEffect(() => {
  //   const fetchData = async () => {
  //     const result = await axios('/api/stocks');
  //     setStocks(result.data);
  //   };

  //   fetchData();
  // }, []);

  return (
    <div className="App">
      <header className="App-header">
        <div>
          <h1>Stock Scanner</h1>
          <StockTable stocks={mockData} />
        </div>
      </header>
    </div>
  );
}

export default App;
