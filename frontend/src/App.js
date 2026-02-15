import React from 'react';

function App() {
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  
  return (
    <iframe 
      src={backendUrl}
      title="Оценка ущерба"
      style={{
        width: '100%',
        height: '100vh',
        border: 'none',
        margin: 0,
        padding: 0,
        overflow: 'hidden',
      }}
      allow="camera; microphone"
    />
  );
}

export default App;
