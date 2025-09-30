/**
 * @fileoverview Home page component for the Portfolio application.
 * Serves as the main landing page showcasing skills, featured projects, and recent blog posts.
 * 
 * @author Portfolio Application
 * @version 1.0.0
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './Home.css';

/**
 * Home Component - Main landing page of the portfolio application.
 * 
 * This component provides:
 * - Hero section with introduction and call-to-action buttons
 * - Skills showcase with proficiency levels and categories
 * - Featured projects display with technology tags and links
 * - Recent blog posts preview with metadata
 * - Navigation links to detailed pages
 * 
 * @component
 * @returns {JSX.Element} Complete home page with multiple content sections
 * 
 * @example
 * // Used in App.jsx routing
 * <Route path="/" element={<Home />} />
 * 
 * Features:
 * - Fetches data from Django REST API endpoints
 * - Responsive grid layouts for content sections
 * - Dynamic skill proficiency visualization
 * - External links with security attributes
 * - Error handling for API requests
 */
const Home = () => {
  /**
   * State for storing skills data from the API.
   * Limited to first 6 skills for homepage display.
   * 
   * @type {Array<Object>} Array of skill objects with name, category, proficiency
   */
  const [skills, setSkills] = useState([]);
  
  /**
   * State for storing featured projects data from the API.
   * Filtered to show only featured projects, limited to 3.
   * 
   * @type {Array<Object>} Array of project objects with title, description, technologies
   */
  const [featuredProjects, setFeaturedProjects] = useState([]);
  
  /**
   * State for storing recent blog posts data from the API.
   * Limited to 3 most recent posts for homepage preview.
   * 
   * @type {Array<Object>} Array of blog post objects with title, excerpt, metadata
   */
  const [recentPosts, setRecentPosts] = useState([]);

  /**
   * State for storing admin profile data from the API.
   * Contains profile photo URL and admin information.
   * 
   * @type {Object} Admin profile object with photo URL and bio
   */
  const [adminProfile, setAdminProfile] = useState(null);

  /**
   * Effect hook to fetch all required data when component mounts.
   * Makes parallel API calls to portfolio and blog endpoints.
   * Handles errors gracefully with console logging.
   */
  useEffect(() => {
    /**
     * Async function to fetch data from multiple API endpoints.
     * 
     * Fetches:
     * - Skills: First 6 skills for skills section
     * - Projects: Featured projects only, limited to 3
     * - Blog Posts: Most recent 3 posts for preview
     * 
     * @async
     * @function fetchData
     * @throws {Error} Logs API errors to console
     */
    const fetchData = async () => {
      try {
        // Fetch admin profile for profile photo
        const profileResponse = await axios.get('http://127.0.0.1:8000/api/v1/portfolio/admin-profile/');
        setAdminProfile(profileResponse.data);

        // Fetch skills from portfolio API
        const skillsResponse = await axios.get('http://127.0.0.1:8000/api/v1/portfolio/skills/');
        setSkills(skillsResponse.data.results.slice(0, 6)); // Show first 6 skills

        // Fetch featured projects from portfolio API
        const projectsResponse = await axios.get('http://127.0.0.1:8000/api/v1/portfolio/projects/');
        setFeaturedProjects(projectsResponse.data.results.filter(project => project.featured).slice(0, 3));

        // Fetch recent blog posts from blog API
        const postsResponse = await axios.get('http://127.0.0.1:8000/api/v1/blog/posts/');
        setRecentPosts(postsResponse.data.results.slice(0, 3));
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="home">
      {/* Hero Section - Main introduction and call-to-action */}
      <section className="hero">
        <div className="hero-container">
          <div className="hero-content">
            <div className="hero-image">
              {adminProfile?.profile_photo_url ? (
                <img 
                  src={adminProfile.profile_photo_url} 
                  alt="Profile" 
                  className="profile-image" 
                />
              ) : (
                <div className="profile-placeholder">
                  <span>No Photo</span>
                </div>
              )}
            </div>
            <div className="hero-text">
              <h1>Hi, I'm {adminProfile ? `${adminProfile.first_name} ${adminProfile.last_name}` : 'a Full-Stack Developer'}</h1>
              <p>
                {adminProfile?.bio || 
                  "I create amazing web experiences using modern technologies like Django, React, and more. Welcome to my portfolio where you can explore my projects and read my thoughts on development."
                }
              </p>
              <div className="hero-buttons">
                {/* Primary CTA to portfolio */}
                <Link to="/portfolio" className="btn btn-primary">
                  View My Work
                </Link>
                {/* Secondary CTA to contact */}
                <Link to="/contact" className="btn btn-secondary">
                  Get In Touch
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Skills Section - Showcase of technical skills with proficiency levels */}
      <section className="skills-section">
        <div className="container">
          <h2>My Skills</h2>
          <div className="skills-grid">
            {skills.map((skill) => (
              <div key={skill.id} className="skill-card">
                <h3>{skill.name}</h3>
                <p className="skill-category">{skill.category_display}</p>
                {/* Visual proficiency bar (proficiency * 20% for 1-5 scale) */}
                <div className="skill-level">
                  <div 
                    className="skill-bar" 
                    style={{ width: `${skill.proficiency * 20}%` }}
                  ></div>
                </div>
                <span className="skill-proficiency">{skill.proficiency_display}</span>
              </div>
            ))}
          </div>
          <div className="section-footer">
            <Link to="/about" className="btn btn-outline">
              View All Skills
            </Link>
          </div>
        </div>
      </section>

      {/* Featured Projects Section - Highlight of best/featured work */}
      <section className="projects-section">
        <div className="container">
          <h2>Featured Projects</h2>
          <div className="projects-grid">
            {featuredProjects.map((project) => (
              <div key={project.id} className="project-card">
                <div className="project-content">
                  <h3>{project.title}</h3>
                  <p>{project.description}</p>
                  {/* Technology tags for each project */}
                  <div className="project-tech">
                    {project.technologies && project.technologies.map((tech, index) => (
                      <span key={index} className="tech-tag">
                        {tech.trim()}
                      </span>
                    ))}
                  </div>
                  {/* External project links */}
                  <div className="project-links">
                    {project.github_url && (
                      <a href={project.github_url} target="_blank" rel="noopener noreferrer">
                        GitHub
                      </a>
                    )}
                    {project.live_url && (
                      <a href={project.live_url} target="_blank" rel="noopener noreferrer">
                        Live Demo
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="section-footer">
            <Link to="/portfolio" className="btn btn-outline">
              View All Projects
            </Link>
          </div>
        </div>
      </section>

      {/* Recent Blog Posts Section - Preview of latest blog content */}
      <section className="blog-section">
        <div className="container">
          <h2>Recent Blog Posts</h2>
          <div className="blog-grid">
            {recentPosts.map((post) => (
              <article key={post.id} className="blog-card">
                <div className="blog-content">
                  <h3>
                    <Link to={`/blog/${post.slug}`}>{post.title}</Link>
                  </h3>
                  <p>{post.excerpt}</p>
                  {/* Blog post metadata */}
                  <div className="blog-meta">
                    <span className="blog-date">
                      {new Date(post.published_at).toLocaleDateString()}
                    </span>
                    <span className="blog-read-time">{post.read_time} min read</span>
                  </div>
                </div>
              </article>
            ))}
          </div>
          <div className="section-footer">
            <Link to="/blog" className="btn btn-outline">
              Read More Posts
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;