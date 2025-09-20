import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './Home.css';

const Home = () => {
  const [skills, setSkills] = useState([]);
  const [featuredProjects, setFeaturedProjects] = useState([]);
  const [recentPosts, setRecentPosts] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch skills
        const skillsResponse = await axios.get('http://127.0.0.1:8000/api/portfolio/skills/');
        setSkills(skillsResponse.data.results.slice(0, 6)); // Show first 6 skills

        // Fetch featured projects
        const projectsResponse = await axios.get('http://127.0.0.1:8000/api/portfolio/projects/');
        setFeaturedProjects(projectsResponse.data.results.filter(project => project.featured).slice(0, 3));

        // Fetch recent blog posts
        const postsResponse = await axios.get('http://127.0.0.1:8000/api/blog/posts/');
        setRecentPosts(postsResponse.data.results.slice(0, 3));
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-container">
          <div className="hero-content">
            <h1>Hi, I'm a Full-Stack Developer</h1>
            <p>
              I create amazing web experiences using modern technologies like Django, React, and more.
              Welcome to my portfolio where you can explore my projects and read my thoughts on development.
            </p>
            <div className="hero-buttons">
              <Link to="/portfolio" className="btn btn-primary">
                View My Work
              </Link>
              <Link to="/contact" className="btn btn-secondary">
                Get In Touch
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Skills Section */}
      <section className="skills-section">
        <div className="container">
          <h2>My Skills</h2>
          <div className="skills-grid">
            {skills.map((skill) => (
              <div key={skill.id} className="skill-card">
                <h3>{skill.name}</h3>
                <p className="skill-category">{skill.category_display}</p>
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

      {/* Featured Projects Section */}
      <section className="projects-section">
        <div className="container">
          <h2>Featured Projects</h2>
          <div className="projects-grid">
            {featuredProjects.map((project) => (
              <div key={project.id} className="project-card">
                <div className="project-content">
                  <h3>{project.title}</h3>
                  <p>{project.description}</p>
                  <div className="project-tech">
                    {project.technologies && project.technologies.map((tech, index) => (
                      <span key={index} className="tech-tag">
                        {tech.trim()}
                      </span>
                    ))}
                  </div>
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

      {/* Recent Blog Posts Section */}
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