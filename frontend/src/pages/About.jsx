/**
 * @fileoverview About page component for the Portfolio application.
 * Displays personal information, skills categorization, experience timeline, and professional statistics.
 * 
 * @author Portfolio Application
 * @version 1.0.0
 */

import { useState, useEffect } from 'react';
import axios from 'axios';
import './About.css';

/**
 * About Component - Personal and professional information page.
 * 
 * This component provides:
 * - Hero section with personal introduction
 * - Professional journey narrative and statistics
 * - Comprehensive skills display grouped by categories
 * - Experience and education timeline
 * - Visual skill proficiency indicators
 * 
 * @component
 * @returns {JSX.Element} Complete about page with personal and professional information
 * 
 * @example
 * // Used in App.jsx routing
 * <Route path="/about" element={<About />} />
 * 
 * Features:
 * - Fetches all skills from Django REST API
 * - Groups skills by category for better organization
 * - Dynamic skill proficiency visualization
 * - Professional timeline with dates and descriptions
 * - Statistics cards with achievements
 */
const About = () => {
  /**
   * State for storing all skills data from the API.
   * Contains complete skills list with categories and proficiency levels.
   * 
   * @type {Array<Object>} Array of skill objects with name, category, proficiency
   */
  const [skills, setSkills] = useState([]);

  /**
   * Effect hook to fetch skills data when component mounts.
   * Retrieves all skills from the portfolio API endpoint.
   */
  useEffect(() => {
    /**
     * Async function to fetch all skills data from the API with pagination handling.
     * 
     * @async
     * @function fetchSkills
     * @throws {Error} Logs API errors to console
     */
    const fetchSkills = async () => {
      try {
        let allSkills = [];
        let nextUrl = 'http://127.0.0.1:8000/api/v1/portfolio/skills/?page_size=100';
        
        // Fetch all pages of skills
        while (nextUrl) {
          const response = await axios.get(nextUrl);
          allSkills = [...allSkills, ...response.data.results];
          nextUrl = response.data.next;
        }
        
        setSkills(allSkills);
      } catch (error) {
        console.error('Error fetching skills:', error);
      }
    };

    fetchSkills();
  }, []);

  /**
   * Groups skills by category for organized display.
   * Creates an object where keys are category names and values are arrays of skills.
   * 
   * @type {Object<string, Array<Object>>} Object with category names as keys and skill arrays as values
   * 
   * @example
   * // Result structure:
   * {
   *   "Frontend": [skill1, skill2],
   *   "Backend": [skill3, skill4],
   *   "Database": [skill5]
   * }
   */
  const groupedSkills = skills.reduce((acc, skill) => {
    const category = skill.category_display;
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(skill);
    return acc;
  }, {});

  return (
    <div className="about">
      {/* About Hero Section - Personal introduction and overview */}
      <section className="about-hero">
        <div className="container">
          <div className="about-hero-content">
            <h1>About Me</h1>
            <p className="about-intro">
              I'm a passionate full-stack developer with expertise in modern web technologies. 
              I love creating efficient, scalable, and user-friendly applications that solve real-world problems.
            </p>
          </div>
        </div>
      </section>

      {/* About Content Section - Professional journey and statistics */}
      <section className="about-content">
        <div className="container">
          <div className="about-grid">
            {/* Personal narrative and professional philosophy */}
            <div className="about-text">
              <h2>My Journey</h2>
              <p>
                With several years of experience in web development, I've worked on various projects 
                ranging from small business websites to large-scale enterprise applications. My journey 
                started with curiosity about how websites work, and it has evolved into a passion for 
                creating amazing digital experiences.
              </p>
              <p>
                I specialize in full-stack development using technologies like Django, React, Python, 
                and JavaScript. I'm always eager to learn new technologies and stay up-to-date with 
                the latest industry trends and best practices.
              </p>
              <p>
                When I'm not coding, you can find me reading tech blogs, contributing to open-source 
                projects, or exploring new frameworks and tools that can improve my development workflow.
              </p>
            </div>
            {/* Professional achievement statistics */}
            <div className="about-stats">
              <div className="stat-card">
                <h3>3+</h3>
                <p>Years of Experience</p>
              </div>
              <div className="stat-card">
                <h3>50+</h3>
                <p>Projects Completed</p>
              </div>
              <div className="stat-card">
                <h3>10+</h3>
                <p>Technologies Mastered</p>
              </div>
              <div className="stat-card">
                <h3>100%</h3>
                <p>Client Satisfaction</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Skills Section - Comprehensive technical skills display */}
      <section className="skills-section">
        <div className="container">
          <h2>Technical Skills</h2>
          <div className="skills-categories">
            {/* Render skills grouped by category */}
            {Object.entries(groupedSkills).map(([category, categorySkills]) => (
              <div key={category} className="skill-category">
                <h3>{category}</h3>
                <div className="skills-list">
                  {/* Individual skill items with proficiency bars */}
                  {categorySkills.map((skill) => (
                    <div key={skill.id} className="skill-item">
                      <div className="skill-header">
                        <span className="skill-name">{skill.name}</span>
                        <span className="skill-level">{skill.proficiency_display}</span>
                      </div>
                      {/* Visual proficiency indicator (proficiency * 20% for 1-5 scale) */}
                      <div className="skill-progress">
                        <div 
                          className="skill-progress-bar" 
                          style={{ width: `${skill.proficiency * 20}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Experience Section - Professional and educational timeline */}
      <section className="experience-section">
        <div className="container">
          <h2>Experience & Education</h2>
          <div className="timeline">
            {/* Current position */}
            <div className="timeline-item">
              <div className="timeline-date">2021 - Present</div>
              <div className="timeline-content">
                <h3>Senior Full-Stack Developer</h3>
                <h4>Tech Company</h4>
                <p>
                  Leading development of web applications using Django and React. 
                  Mentoring junior developers and implementing best practices for code quality and performance.
                </p>
              </div>
            </div>
            {/* Previous full-stack role */}
            <div className="timeline-item">
              <div className="timeline-date">2019 - 2021</div>
              <div className="timeline-content">
                <h3>Full-Stack Developer</h3>
                <h4>Digital Agency</h4>
                <p>
                  Developed and maintained multiple client websites and web applications. 
                  Worked with various technologies including Python, JavaScript, and SQL databases.
                </p>
              </div>
            </div>
            {/* Junior developer role */}
            <div className="timeline-item">
              <div className="timeline-date">2017 - 2019</div>
              <div className="timeline-content">
                <h3>Junior Web Developer</h3>
                <h4>Startup Company</h4>
                <p>
                  Started my professional journey building responsive websites and learning 
                  modern web development practices. Gained experience in both frontend and backend development.
                </p>
              </div>
            </div>
            {/* Educational background */}
            <div className="timeline-item">
              <div className="timeline-date">2015 - 2019</div>
              <div className="timeline-content">
                <h3>Bachelor's in Computer Science</h3>
                <h4>University</h4>
                <p>
                  Studied computer science fundamentals, algorithms, data structures, 
                  and software engineering principles. Graduated with honors.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;