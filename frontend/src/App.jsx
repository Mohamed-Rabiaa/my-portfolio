/**
 * @fileoverview Main App component that sets up routing and layout for the Portfolio application.
 * This component serves as the root component that defines the application structure,
 * navigation routes, and common layout elements.
 * 
 * @author Portfolio Application
 * @version 1.0.0
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import About from './pages/About';
import Portfolio from './pages/Portfolio';
import Blog from './pages/Blog';
import BlogPost from './pages/BlogPost';
import Contact from './pages/Contact';
import './App.css';

/**
 * App Component - Root component of the Portfolio application.
 * 
 * This component establishes the main application structure and routing system.
 * It provides:
 * - Client-side routing using React Router
 * - Consistent layout with navigation and footer
 * - Route definitions for all application pages
 * - Main content area wrapper
 * 
 * @component
 * @returns {JSX.Element} The complete application layout with routing
 * 
 * @example
 * // App is typically rendered in main.jsx
 * <App />
 * 
 * @see {@link https://reactrouter.com/} React Router documentation
 */
function App() {
  return (
    <Router>
      <div className="App">
        {/* Navigation component - appears on all pages */}
        <Navbar />
        
        {/* Main content area with route-based page rendering */}
        <main>
          <Routes>
            {/* Home page route */}
            <Route path="/" element={<Home />} />
            
            {/* About page route */}
            <Route path="/about" element={<About />} />
            
            {/* Portfolio/Projects page route */}
            <Route path="/portfolio" element={<Portfolio />} />
            
            {/* Blog listing page route */}
            <Route path="/blog" element={<Blog />} />
            
            {/* Individual blog post route with dynamic slug parameter */}
            <Route path="/blog/:slug" element={<BlogPost />} />
            
            {/* Contact page route */}
            <Route path="/contact" element={<Contact />} />
          </Routes>
        </main>
        
        {/* Footer component - appears on all pages */}
        <Footer />
      </div>
    </Router>
  );
}

export default App;
