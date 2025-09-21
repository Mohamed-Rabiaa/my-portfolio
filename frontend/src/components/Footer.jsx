/**
 * @fileoverview Footer component for the Portfolio application.
 * Provides site-wide footer with links, social media connections, and copyright information.
 * 
 * @author Portfolio Application
 * @version 1.0.0
 */

import './Footer.css';

/**
 * Footer Component - Site-wide footer component for the application.
 * 
 * This component provides:
 * - Site description and branding
 * - Quick navigation links to all main pages
 * - Social media links (GitHub, LinkedIn, Twitter)
 * - Dynamic copyright notice with current year
 * - Consistent footer across all pages
 * 
 * @component
 * @returns {JSX.Element} Footer with navigation links, social links, and copyright
 * 
 * @example
 * // Used in App.jsx as the main footer
 * <Footer />
 * 
 * Features:
 * - Automatically updates copyright year
 * - External links open in new tabs with security attributes
 * - Responsive layout with multiple sections
 */
const Footer = () => {
  /**
   * Get the current year for dynamic copyright notice.
   * This ensures the copyright year is always current without manual updates.
   * 
   * @type {number} Current year (e.g., 2024)
   */
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-content">
          {/* Brand/Description section */}
          <div className="footer-section">
            <h3>Portfolio</h3>
            <p>Full-stack developer passionate about creating amazing web experiences.</p>
          </div>
          
          {/* Quick navigation links section */}
          <div className="footer-section">
            <h4>Quick Links</h4>
            <ul>
              <li><a href="/">Home</a></li>
              <li><a href="/about">About</a></li>
              <li><a href="/portfolio">Portfolio</a></li>
              <li><a href="/blog">Blog</a></li>
              <li><a href="/contact">Contact</a></li>
            </ul>
          </div>
          
          {/* Social media links section */}
          <div className="footer-section">
            <h4>Connect</h4>
            <div className="social-links">
              {/* GitHub profile link */}
              <a href="https://github.com" target="_blank" rel="noopener noreferrer">
                GitHub
              </a>
              
              {/* LinkedIn profile link */}
              <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer">
                LinkedIn
              </a>
              
              {/* Twitter profile link */}
              <a href="https://twitter.com" target="_blank" rel="noopener noreferrer">
                Twitter
              </a>
            </div>
          </div>
        </div>
        
        {/* Copyright section with dynamic year */}
        <div className="footer-bottom">
          <p>&copy; {currentYear} Portfolio. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;