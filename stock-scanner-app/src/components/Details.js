import React, { useEffect } from 'react';

const Details = () => {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/tv.js';
    script.async = true;
    script.onload = () => {
      new window.TradingView.widget({
        "width": "100%",
        "height": 610,
        "symbol": "HKEX:HSI",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "light",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_5d8f0"
      });
    };
    document.getElementById('tradingview_container').appendChild(script);
  }, []);

  return (
    <div id="tradingview_container">
      <div id="tradingview_5d8f0"></div>
    </div>
  );
};

export default Details;
