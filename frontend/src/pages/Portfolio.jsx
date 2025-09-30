/**
 * @fileoverview Portfolio page component for the Portfolio application.
 * Displays a filterable grid of projects with categories, images, and project details.
 * 
 * @author Portfolio Application
 * @version 1.0.0
 */

import { useState, useEffect } from 'react';
import axios from 'axios';
import './Portfolio.css';

/**
 * Portfolio Component - Projects showcase page with technology-based filtering capabilities.
 * 
 * This component provides:
 * - Hero section with portfolio introduction
 * - Technology-based project filtering system (instead of categories)
 * - Responsive project grid with hover effects
 * - Project cards with images, descriptions, and technology tags
 * - External links to live demos and GitHub repositories
 * - Loading states and empty state handling
 * - Call-to-action section for contact
 * 
 * @component
 * @returns {JSX.Element} Complete portfolio page with filterable project grid
 * 
 * @example
 * // Used in App.jsx routing
 * <Route path="/portfolio" element={<Portfolio />} />
 * 
 * Features:
 * - Fetches projects from Django REST API
 * - Dynamic technology filtering (e.g., React, Django, Python)
 * - Responsive image handling with fallbacks
 * - SEO-friendly project URLs and metadata
 * - Performance optimized with proper loading states
 * 
 * @version 2.0.0 - Updated to use technology-based filtering instead of categories
 */
const Portfolio = () => {
  /**
   * State for storing all projects fetched from the API.
   * Contains project data including title, description, technologies, and images.
   * 
   * @type {Array<Object>} Array of project objects with title, description, technologies, images
   */
  const [projects, setProjects] = useState([]);
  
  /**
   * State for storing filtered projects based on selected technology.
   * Updates when technology filter is applied.
   * 
   * @type {Array<Object>} Filtered array of project objects
   */
  const [filteredProjects, setFilteredProjects] = useState([]);
  
  /**
   * State for tracking the currently selected technology filter.
   * Defaults to 'all' to show all projects initially.
   * 
   * @type {string} Current technology filter ('all' or specific technology name like 'React (Frontend)')
   */
  const [selectedCategory, setSelectedCategory] = useState('all');
  
  /**
   * State for tracking loading status during API fetch.
   * Used to display loading spinner while fetching projects.
   * 
   * @type {boolean} Loading state indicator
   */
  const [loading, setLoading] = useState(true);

  /**
   * Effect hook to fetch projects data when component mounts.
   * Retrieves all projects from the portfolio API endpoint.
   */
  useEffect(() => {
    /**
     * Async function to fetch projects data from the API.
     * Sets both projects and filteredProjects to show all initially.
     * 
     * @async
     * @function fetchProjects
     * @throws {Error} Logs API errors to console and sets loading to false
     */
    const fetchProjects = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/v1/portfolio/projects/');
        setProjects(response.data.results);
        setFilteredProjects(response.data.results);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching projects:', error);
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  /**
   * Dynamically generated array of unique technologies from all projects.
   * Includes 'all' option plus all unique technology names from projects.
   * Extracts technologies from the technologies array of each project.
   * 
   * @type {Array<string>} Array of technology names for filter buttons
   */
  const technologies = ['all', ...new Set(
    projects.flatMap(project => 
      project.technologies ? project.technologies : []
    )
  )];

  /**
   * Filters projects based on selected technology.
   * Updates both selectedCategory and filteredProjects states.
   * 
   * @param {string} technology - Technology to filter by ('all' for no filter)
   * 
   * @example
   * // Filter to show only projects using React
   * filterProjects('React (Frontend)');
   * 
   * // Show all projects
   * filterProjects('all');
   */
  const filterProjects = (technology) => {
    setSelectedCategory(technology);
    if (technology === 'all') {
      setFilteredProjects(projects);
    } else {
      setFilteredProjects(projects.filter(project => 
        project.technologies && project.technologies.includes(technology)
      ));
    }
  };

  /**
   * Formats date string to readable format.
   * Converts ISO date string to "Month Year" format.
   * 
   * @param {string} dateString - ISO date string from API
   * @returns {string} Formatted date string (e.g., "January 2024")
   * 
   * @example
   * formatDate('2024-01-15T10:30:00Z') // Returns "January 2024"
   */
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long'
    });
  };

  // Loading state display
  if (loading) {
    return (
      <div className="portfolio">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading projects...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="portfolio">
      {/* Portfolio Hero Section - Introduction and overview */}
      <section className="portfolio-hero">
        <div className="container">
          <div className="portfolio-hero-content">
            <h1>My Portfolio</h1>
            <p>
              Explore my collection of projects showcasing various technologies and solutions. 
              Each project represents a unique challenge and learning experience.
            </p>
          </div>
        </div>
      </section>

      {/* Portfolio Filter Section - Technology filtering buttons */}
      <section className="portfolio-filter">
        <div className="container">
          <div className="filter-buttons">
            {technologies.map((technology) => (
              <button
                key={technology}
                className={`filter-btn ${selectedCategory === technology ? 'active' : ''}`}
                onClick={() => filterProjects(technology)}
              >
                {/* Display formatted technology names */}
                {technology === 'all' ? 'All Projects' : technology}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Portfolio Grid Section - Main projects display */}
      <section className="portfolio-grid">
        <div className="container">
          {filteredProjects.length === 0 ? (
            /* Empty state when no projects match filter */
            <div className="no-projects">
              <p>No projects found for the selected technology.</p>
            </div>
          ) : (
            <div className="projects-grid">
              {/* Project cards with hover effects and overlays */}
              {filteredProjects.map((project) => (
                <div key={project.id} className="project-card">
                  {/* Project image with overlay for links */}
                  <div className="project-image">
                    {project.image ? (
                      <img src={project.image} alt={project.title} />
                    ) : (
                      /* Fallback for projects without images */
                      <div className="project-placeholder">
                        <span>No Image</span>
                      </div>
                    )}
                    {/* Hover overlay with external links */}
                    <div className="project-overlay">
                      <div className="project-links">
                        {project.live_url && (
                          <a 
                            href={project.live_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="project-link live-link"
                          >
                            Live Demo
                          </a>
                        )}
                        {project.github_url && (
                          <a 
                            href={project.github_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="project-link github-link"
                          >
                            GitHub
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                  {/* Project information and metadata */}
                  <div className="project-content">
                    <div className="project-meta">
                      <span className="project-category">
                        {project.technologies && project.technologies.length > 0 
                          ? project.technologies[0]
                          : 'No Technology'
                        }
                      </span>
                      <span className="project-date">{formatDate(project.created_at)}</span>
                    </div>
                    <h3 className="project-title">{project.title}</h3>
                    <p className="project-description">{project.description}</p>
                    {/* Technology tags for each project */}
                    <div className="project-technologies">
                      {project.technologies && project.technologies.map((tech, index) => (
                        <span key={`${project.id}-tech-${index}`} className="tech-tag">
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Call to Action Section - Contact encouragement */}
      <section className="portfolio-cta">
        <div className="container">
          <div className="cta-content">
            <h2>Interested in Working Together?</h2>
            <p>
              I'm always open to discussing new opportunities and interesting projects. 
              Let's create something amazing together!
            </p>
            <a href="/contact" className="cta-button">
              Get In Touch
            </a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Portfolio;