import React, { useState } from 'react';
import Joke from './Joke';

function App() {
  const [userQuery, setUserQuery] = useState('');

  const updateUserQuery = event => {
    console.log('userQuery', userQuery);
    setUserQuery(event.target.value); 
  }

  const searchQuery = () => {
    window.open(`https://google.com/search?q=${userQuery}`);
  }

  const handleKeyPress = event => {
    if (event.key === 'Enter') {
      searchQuery();
    } 
  }

  return (
    <div>
      <input value={userQuery} onChange={updateUserQuery} onKeyPress={handleKeyPress} />
      <button onClick={searchQuery}>Search</button>
      <div>{userQuery}</div>
      <hr />
      <Joke />
    </div>
  );
}

export default App;
