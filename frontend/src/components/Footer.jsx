/**
 * @fileoverview Footer component for the Portfolio application with dynamic social media links.
 * Provides site-wide footer with links, dynamic social media connections from admin profile, and copyright information.
 * 
 * @author Portfolio Application
 * @version 2.0.0 - Added dynamic social media links from admin profile API
 */

import { useState, useEffect } from 'react';
import axios from 'axios';
import './Footer.css';

/**
 * Footer Component - Site-wide footer component with dynamic social media links.
 * 
 * This component provides:
 * - Site description and branding
 * - Quick navigation links to all main pages
 * - Dynamic social media links (GitHub, LinkedIn, X/Twitter) fetched from admin profile
 * - Loading states and fallback handling for social media links
 * - Dynamic copyright notice with current year
 * - Consistent footer across all pages
 * 
 * @component
 * @returns {JSX.Element} Footer with navigation links, dynamic social links, and copyright
 * 
 * @example
 * // Used in App.jsx layout
 * <Footer />
 * 
 * Features:
 * - Fetches admin profile data for social media URLs
 * - Conditional rendering of social links based on availability
 * - Loading states while fetching admin profile
 * - Automatically updates copyright year
 * - External links open in new tabs with security attributes
 * - Responsive layout with multiple sections
 * 
 * @version 2.0.0 - Added dynamic social media links from admin profile
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