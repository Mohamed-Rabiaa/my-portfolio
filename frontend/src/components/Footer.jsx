/**
 * @fileoverview Footer component for the Portfolio application.
 * Provides site-wide footer with links, social media connections, and copyright information.
 * 
 * @author Portfolio Application
 * @version 1.0.0
 */

import { useState, useEffect } from 'react';
import axios from 'axios';
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

  /**
   * State for storing admin profile data including social media URLs.
   * 
   * @type {Object|null} Admin profile data with social media links
   */
  const [adminProfile, setAdminProfile] = useState(null);

  /**
   * Fetch admin profile data on component mount.
   * Gets social media URLs from the backend API.
   */
  useEffect(() => {
    const fetchAdminProfile = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/v1/portfolio/admin-profile/');
        setAdminProfile(response.data);
      } catch (error) {
        console.error('Error fetching admin profile:', error);
      }
    };

    fetchAdminProfile();
  }, []);

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
              {/* Show loading state or social links */}
              {adminProfile === null ? (
                <p style={{ color: '#ccc', fontSize: '0.9rem' }}>Loading social links...</p>
              ) : (
                <>
                  {/* GitHub profile link */}
                  {adminProfile.github_url && (
                    <a href={adminProfile.github_url} target="_blank" rel="noopener noreferrer">
                      GitHub
                    </a>
                  )}
                  
                  {/* LinkedIn profile link */}
                  {adminProfile.linkedin_url && (
                    <a href={adminProfile.linkedin_url} target="_blank" rel="noopener noreferrer">
                      LinkedIn
                    </a>
                  )}
                  
                  {/* X (formerly Twitter) profile link */}
                  {adminProfile.twitter_url && (
                    <a href={adminProfile.twitter_url} target="_blank" rel="noopener noreferrer">
                      X
                    </a>
                  )}
                  
                  {/* Show message if no social links are available */}
                  {!adminProfile.github_url && !adminProfile.linkedin_url && !adminProfile.twitter_url && (
                    <p style={{ color: '#ccc', fontSize: '0.9rem' }}>No social links available</p>
                  )}
                </>
              )}
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