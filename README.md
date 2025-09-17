# my-portfolio

This is my personal portfolio website, built as a full stack web application to present my journey as a full stack software engineer and showcase the projects I’ve worked on, such as Flasheeta (a flashcards learning app) and PostSphere (a blogging platform). The portfolio reflects my passion for clean design and efficient backend architecture, while also giving me a flexible platform to manage and update content without touching the codebase.

# Tech Stack:
Frontend: React.js with Tailwind CSS for a fast and modern interface.  
Backend: Django REST Framework (Python) for reliable APIs and content management.  
Database: PostgreSQL for structured, relational data storage.  
Authentication: JWT-based login for the admin dashboard.  


# Deployment: 
To be determined  

# Outcome:
This portfolio project is both a showcase of my work and a living demonstration of my full stack development skills, from designing APIs and managing databases to building responsive user interfaces and deploying production-ready applications.  

# AI Integration Strategy:
## Code generation: 
I will use Trae AI to:  
Brainstorming the structure of the project.  
Authentication.  
Build my api routes and UI components.  
Determine the database schema.  
Refactor the code as needed.  


## Testing: 
Unit Tests:
Scope: Individual functions, utilities, and backend logic (e.g., form validation, authentication helpers, content serializers).  
Prompt Example: “Write Pytest unit tests for utils/validators.py (validate email in contact form)”  
What to look for: Correct data validation, expected return values (e.g., JSON format), error handling for invalid inputs.  

Integration Tests:
Scope: API endpoints, database interactions, and multi-function workflows (e.g., creating/updating projects, posting blogs, submitting contact forms).  
Prompt Example: “Test that api/projects.py correctly creates a new project and returns it in the portfolio list”  
What to look for: HTTP status codes, successful database writes, proper authentication flow (for admin dashboard), and accurate end-to-end input/output behavior.  

## Documentation
Docstrings & Inline Comments:    
Approach: Each function, class, and endpoint will include a docstring not just describing what it does but why it exists (e.g., “This function validates email format in the contact form to prevent invalid submissions”).  
AI Contribution: I will use AI to suggest initial docstrings and inline comments, then refine them manually to ensure accuracy and alignment with the project’s coding style.  
Best Practices:  
Include edge cases (e.g., “what happens if the contact form is submitted without a message”).  
Maintain consistent terminology across the codebase (e.g., always use “project” vs. “portfolio item”).  
Keep explanations concise but meaningful.  

README
Project Overview & Purpose: A clear introduction explaining that this portfolio is both a personal showcase and a demonstration of full stack engineering skills.  
AI Contribution: AI will assist in drafting structured sections (overview, usage examples, configuration lists), which I will polish to ensure they are approachable and accurate.  

Contents:  
Installation steps for local development and production environments.  
Getting started guide with sample commands and example API usage (e.g., adding a project via the admin dashboard).  
List of environment variables (e.g., DATABASE_URL, SECRET_KEY, EMAIL_SERVER).  
Dependencies and version constraints (Python, Django/DRF, React, PostgreSQL, etc.).  
Instructions on how to run unit and integration tests.  
Links to documentation, open issues, and a roadmap for future improvements.  
Written in an approachable tone for new contributors or potential collaborators.  
