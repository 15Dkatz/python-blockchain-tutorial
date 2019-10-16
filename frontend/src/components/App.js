import React, { useState, useEffect } from 'react';
import logo from '../assets/logo.png';

function App() {
  const [walletInfo, setWalletInfo] = useState({});

  useEffect(() => {
    fetch('http://localhost:5000/wallet/info')
      .then(response => response.json())
      .then(json => setWalletInfo(json));
  });

  return (
    <div className="App">
      <img className="logo" src={logo} alt="application-logo" />
      <h3>Welcome to pychain</h3>
    </div>
  );
}

export default App;
