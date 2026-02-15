import React, { useEffect, useState } from 'react';

function App() {
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Redirect to Django backend
    const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
    window.location.href = backendUrl;
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-red-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600">Загрузка приложения...</p>
      </div>
    </div>
  );
}

export default App;
