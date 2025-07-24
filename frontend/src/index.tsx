import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// Create root element
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

// Render the application
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Service worker registration (optional)
// If you want to enable offline functionality and faster loading,
// you can change unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://cra.link/PWA
// serviceWorker.unregister(); 