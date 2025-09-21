/**
 * @fileoverview Navigation bar component for the Portfolio application.
 * Provides site-wide navigation with active link highlighting and responsive design.
 * 
 * @author Portfolio Application
 * @version 1.0.0
 */

import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

/**
 * Navbar Component - Main navigation component for the application.
 * 
 * This component provides:
 * - Site-wide navigation menu
 * - Active link highlighting based on current route
 * - Responsive navigation layout
 * - Brand/logo link to home page
 * - Consistent navigation across all pages
 * 
 * @component
 * @returns {JSX.Element} Navigation bar with links and active state management
 * 
 * @example
 * // Used in App.jsx as the main navigation
 * <Navbar />
 * 
 * @see {@link https://reactrouter.com/web/api/Link} React Router Link documentation
 * @see {@link https://reactrouter.com/web/api/Hooks/uselocation} useLocation hook documentation
 */
const Navbar = () => {
  // Get current location to determine active navigation item
  const location = useLocation();

  /**
   * Determines if a navigation link should be marked as active.
   * 
   * @param {string} path - The path to check against current location
   * @returns {boolean} True if the path matches the current location
   * 
   * @example
   * // Check if home page is active
   * const homeActive = isActive('/');
   * 
   * // Check if about page is active
   * const aboutActive = isActive('/about');
   */
  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        {/* Brand/Logo - Links to home page */}
        <Link to="/" className="nav-logo">
          Mohamed Rabiaa
        </Link>
        
        {/* Main navigation menu */}
        <ul className="nav-menu">
          {/* Home navigation item */}
          <li className="nav-item">
            <Link 
              to="/" 
              className={`nav-link ${isActive('/') ? 'active' : ''}`}
            >
              Home
            </Link>
          </li>
          
          {/* About navigation item */}
          <li className="nav-item">
            <Link 
              to="/about" 
              className={`nav-link ${isActive('/about') ? 'active' : ''}`}
            >
              About
            </Link>
          </li>
          
          {/* Portfolio navigation item */}
          <li className="nav-item">
            <Link 
              to="/portfolio" 
              className={`nav-link ${isActive('/portfolio') ? 'active' : ''}`}
            >
              Portfolio
            </Link>
          </li>
          
          {/* Blog navigation item */}
          <li className="nav-item">
            <Link 
              to="/blog" 
              className={`nav-link ${isActive('/blog') ? 'active' : ''}`}
            >
              Blog
            </Link>
          </li>
          
          {/* Contact navigation item */}
          <li className="nav-item">
            <Link 
              to="/contact" 
              className={`nav-link ${isActive('/contact') ? 'active' : ''}`}
            >
              Contact
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;