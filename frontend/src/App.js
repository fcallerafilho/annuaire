import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useLogger } from './utils/logger';
import { ToastContainer } from 'react-toastify';
import Login from './components/Login/Login';
import Signup from './components/Signup/Signup';
import Directory from './components/Directory/Directory';
import Header from './components/common/Header';
import './App.css';

// Composant pour logger les changements de route
const RouteLogger = () => {
  const location = useLocation();
  const { logNavigation } = useLogger();

  useEffect(() => {
    logNavigation(location.pathname);
  }, [location]);

  return null;
};

// Composant Layout avec logging
const Layout = ({ children }) => {
  const { logAction } = useLogger();

  useEffect(() => {
    logAction('APP_MOUNT', { component: 'Layout' });
    return () => logAction('APP_UNMOUNT', { component: 'Layout' });
  }, []);

  return (
    <div className="App">
      <Header />
      <div className="content">
        <div className="main-content">
          {children}
        </div>
      </div>
    </div>
  );
};

// PrivateRoute avec logging
const PrivateRoute = ({ children }) => {
  const { logAuth } = useLogger();
  const token = localStorage.getItem('token');
  
  useEffect(() => {
    logAuth(token ? 'AUTHORIZED' : 'UNAUTHORIZED');
  }, [token]);

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <Layout>{children}</Layout>;
};

function App() {
  return (

    <BrowserRouter>
      <ToastContainer position="top-right" autoClose={3000} />
      <RouteLogger /> 
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        
        <Route 
          path="/directory" 
          element={
            <PrivateRoute>
              <Directory />
            </PrivateRoute>
          } 
        />
        
        <Route 
          path="*" 
          element={<Navigate to="/directory" replace />} 
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;