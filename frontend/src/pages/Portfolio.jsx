import { useState, useEffect } from 'react';
import axios from 'axios';
import './Portfolio.css';

const Portfolio = () => {
  const [projects, setProjects] = useState([]);
  const [filteredProjects, setFilteredProjects] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/portfolio/projects/');
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

  const categories = ['all', ...new Set(projects.map(project => project.category).filter(Boolean))];

  const filterProjects = (category) => {
    setSelectedCategory(category);
    if (category === 'all') {
      setFilteredProjects(projects);
    } else {
      setFilteredProjects(projects.filter(project => project.category === category));
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long'
    });
  };

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
      {/* Portfolio Hero Section */}
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

      {/* Portfolio Filter Section */}
      <section className="portfolio-filter">
        <div className="container">
          <div className="filter-buttons">
            {categories.map((category) => (
              <button
                key={category}
                className={`filter-btn ${selectedCategory === category ? 'active' : ''}`}
                onClick={() => filterProjects(category)}
              >
                {category === 'all' ? 'All Projects' : (category && category.charAt(0).toUpperCase() + category.slice(1))}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Portfolio Grid Section */}
      <section className="portfolio-grid">
        <div className="container">
          {filteredProjects.length === 0 ? (
            <div className="no-projects">
              <p>No projects found for the selected category.</p>
            </div>
          ) : (
            <div className="projects-grid">
              {filteredProjects.map((project) => (
                <div key={project.id} className="project-card">
                  <div className="project-image">
                    {project.image ? (
                      <img src={project.image} alt={project.title} />
                    ) : (
                      <div className="project-placeholder">
                        <span>No Image</span>
                      </div>
                    )}
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
                  <div className="project-content">
                    <div className="project-meta">
                      <span className="project-category">{project.category?.name || project.category || 'Uncategorized'}</span>
                      <span className="project-date">{formatDate(project.created_at)}</span>
                    </div>
                    <h3 className="project-title">{project.title}</h3>
                    <p className="project-description">{project.description}</p>
                    <div className="project-technologies">
                      {project.technologies && project.technologies.map((tech, index) => (
                        <span key={index} className="tech-tag">
                          {tech.trim()}
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

      {/* Call to Action Section */}
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