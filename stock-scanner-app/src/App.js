import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Details from './components/Details';
import Layout from './components/Layout';
import './App.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/:date" element={<Dashboard />} />
          <Route path="/details" element={<Details />} />
          <Route path="/s-and-p" element={<div>S&P Page</div>} /> {/* Placeholder for S&P page */}
          <Route path="/dj" element={<div>DJ Page</div>} /> {/* Placeholder for DJ page */}
          <Route path="/support" element={<div>Support Page</div>} /> {/* Placeholder for Support page */}
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;


// const [stocks, setStocks] = useState([]);

// useEffect(() => {
//   const fetchData = async () => {
//     const result = await axios('/api/stocks');
//     setStocks(result.data);
//   };

//   fetchData();
// }, []);
// return (
//   <div className="App">
//     <header className="App-header">
//       <div>
//         <h1>Stock Scanner</h1>
//         <StockTable stocks={mockData} />
//       </div>
//     </header>
//   </div>
// );