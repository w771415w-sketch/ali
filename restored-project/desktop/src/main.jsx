import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './styles.css';

document.documentElement.lang = 'ar';
document.documentElement.dir = 'rtl';
document.documentElement.dataset.aliDesign = 'design4';
document.body.dataset.aliDesign = 'design4';

createRoot(document.getElementById('root')).render(<App />);
