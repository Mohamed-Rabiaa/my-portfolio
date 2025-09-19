import { useState, useEffect } from 'react';
import axios from 'axios';
import './About.css';

const About = () => {
  const [skills, setSkills] = useState([]);

  useEffect(() => {
    const fetchSkills = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/portfolio/skills/');
        setSkills(response.data.results);
      } catch (error) {
        console.error('Error fetching skills:', error);
      }
    };

    fetchSkills();
  }, []);

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
      {/* About Hero Section */}
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

      {/* About Content Section */}
      <section className="about-content">
        <div className="container">
          <div className="about-grid">
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

      {/* Skills Section */}
      <section className="skills-section">
        <div className="container">
          <h2>Technical Skills</h2>
          <div className="skills-categories">
            {Object.entries(groupedSkills).map(([category, categorySkills]) => (
              <div key={category} className="skill-category">
                <h3>{category}</h3>
                <div className="skills-list">
                  {categorySkills.map((skill) => (
                    <div key={skill.id} className="skill-item">
                      <div className="skill-header">
                        <span className="skill-name">{skill.name}</span>
                        <span className="skill-level">{skill.proficiency_display}</span>
                      </div>
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

      {/* Experience Section */}
      <section className="experience-section">
        <div className="container">
          <h2>Experience & Education</h2>
          <div className="timeline">
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