import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { TranslationProvider } from './context/TranslationContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Translate from './pages/Translate';
import Settings from './pages/Settings';
import './App.css';

function App() {
  return (
    <TranslationProvider>
      <Router>
        <div className="flex flex-col min-h-screen bg-slate-50 text-slate-800 transition-colors duration-300">
          {/* Main Navbar */}
          <Navbar />
          
          {/* Main Application Container */}
          <main className="flex-grow flex flex-col">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/translate" element={<Translate />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
          
          {/* Main Footer */}
          <Footer />
        </div>
      </Router>
    </TranslationProvider>
  );
}

export default App;

