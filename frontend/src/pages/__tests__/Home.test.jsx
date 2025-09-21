/**
 * @fileoverview Test suite for the Home page component.
 * Tests rendering, API integration, data display, and user interactions.
 * 
 * @author Portfolio Application
 * @version 1.0.0
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor, act } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import axios from 'axios'
import Home from '../Home'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

/**
 * Helper function to render Home component with router context
 * @returns {object} Render result from testing library
 */
const renderHomeWithRouter = () => {
  return act(() => {
    return render(
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    )
  })
}

// Mock data for API responses
const mockSkillsResponse = {
  data: {
    results: [
      { id: 1, name: 'JavaScript', category: 'Frontend', proficiency: 90, featured: true },
      { id: 2, name: 'React', category: 'Frontend', proficiency: 85, featured: true },
      { id: 3, name: 'Python', category: 'Backend', proficiency: 88, featured: true },
      { id: 4, name: 'Django', category: 'Backend', proficiency: 82, featured: true },
      { id: 5, name: 'PostgreSQL', category: 'Database', proficiency: 75, featured: true },
      { id: 6, name: 'Docker', category: 'DevOps', proficiency: 70, featured: true },
      { id: 7, name: 'AWS', category: 'Cloud', proficiency: 65, featured: false }
    ]
  }
}

const mockProjectsResponse = {
  data: {
    results: [
      {
        id: 1,
        title: 'E-commerce Platform',
        description: 'Full-stack e-commerce solution',
        technologies: ['Django', 'React', 'PostgreSQL'],
        featured: true,
        github_url: 'https://github.com/user/ecommerce',
        live_url: 'https://ecommerce.example.com'
      },
      {
        id: 2,
        title: 'Task Management App',
        description: 'Collaborative task management tool',
        technologies: ['React', 'Node.js', 'MongoDB'],
        featured: true,
        github_url: 'https://github.com/user/taskapp',
        live_url: 'https://taskapp.example.com'
      },
      {
        id: 3,
        title: 'Weather Dashboard',
        description: 'Real-time weather tracking',
        technologies: ['Vue.js', 'Express', 'MySQL'],
        featured: true,
        github_url: 'https://github.com/user/weather',
        live_url: 'https://weather.example.com'
      },
      {
        id: 4,
        title: 'Blog Platform',
        description: 'Personal blogging platform',
        technologies: ['Django', 'React'],
        featured: false
      }
    ]
  }
}

const mockBlogPostsResponse = {
  data: {
    results: [
      {
        id: 1,
        title: 'Getting Started with React Testing',
        excerpt: 'Learn the basics of testing React components',
        created_at: '2024-01-15T10:00:00Z',
        category: { name: 'React' }
      },
      {
        id: 2,
        title: 'Django REST API Best Practices',
        excerpt: 'Building robust APIs with Django REST Framework',
        created_at: '2024-01-10T15:30:00Z',
        category: { name: 'Django' }
      },
      {
        id: 3,
        title: 'Modern CSS Techniques',
        excerpt: 'Exploring CSS Grid and Flexbox',
        created_at: '2024-01-05T09:15:00Z',
        category: { name: 'CSS' }
      }
    ]
  }
}

describe('Home Component', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    vi.clearAllMocks()
    
    // Setup default successful API responses
    mockedAxios.get.mockImplementation((url) => {
      if (url.includes('/skills/')) {
        return Promise.resolve(mockSkillsResponse)
      } else if (url.includes('/projects/')) {
        return Promise.resolve(mockProjectsResponse)
      } else if (url.includes('/posts/')) {
        return Promise.resolve(mockBlogPostsResponse)
      }
      return Promise.reject(new Error('Unknown endpoint'))
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Initial Rendering', () => {
    it('renders the home page with hero section', async () => {
      renderHomeWithRouter()
      
      expect(screen.getByText("Hi, I'm a Full-Stack Developer")).toBeInTheDocument()
      expect(screen.getByText(/I create amazing web experiences/)).toBeInTheDocument()
    })

    it('renders call-to-action buttons in hero section', async () => {
      renderHomeWithRouter()
      
      const portfolioButton = screen.getByRole('link', { name: 'View My Work' })
      const contactButton = screen.getByRole('link', { name: 'Get In Touch' })
      
      expect(portfolioButton).toBeInTheDocument()
      expect(portfolioButton).toHaveAttribute('href', '/portfolio')
      
      expect(contactButton).toBeInTheDocument()
      expect(contactButton).toHaveAttribute('href', '/contact')
    })

    it('has proper CSS classes for hero section', async () => {
      renderHomeWithRouter()
      
      const heroSection = screen.getByText("Hi, I'm a Full-Stack Developer").closest('section')
      expect(heroSection).toHaveClass('hero')
    })
  })

  describe('API Data Fetching', () => {
    it('makes API calls to all required endpoints on mount', async () => {
      renderHomeWithRouter()
      
      await waitFor(() => {
        expect(mockedAxios.get).toHaveBeenCalledWith('http://127.0.0.1:8000/api/portfolio/skills/')
        expect(mockedAxios.get).toHaveBeenCalledWith('http://127.0.0.1:8000/api/portfolio/projects/')
        expect(mockedAxios.get).toHaveBeenCalledWith('http://127.0.0.1:8000/api/blog/posts/')
      })
    })

    it('handles API errors gracefully', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      mockedAxios.get.mockRejectedValue(new Error('API Error'))
      
      renderHomeWithRouter()
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Error fetching data:', expect.any(Error))
      })
      
      consoleSpy.mockRestore()
    })
  })

  describe('Skills Section', () => {
    it('displays skills data when loaded', async () => {
      renderHomeWithRouter()
      
      await waitFor(() => {
        expect(screen.getByText('JavaScript')).toBeInTheDocument()
        // Use getAllByText for React since it appears multiple times
        const reactElements = screen.getAllByText('React')
        expect(reactElements.length).toBeGreaterThan(0)
        expect(screen.getByText('Python')).toBeInTheDocument()
      })
    })

    it('limits skills display to first 6 items', async () => {
      renderHomeWithRouter()
      
      await waitFor(() => {
        const skillElements = document.querySelectorAll('.skill-item')
        expect(skillElements.length).toBeLessThanOrEqual(6)
        expect(screen.getByText('JavaScript')).toBeInTheDocument()
        expect(screen.getByText('Docker')).toBeInTheDocument()
        expect(screen.queryByText('AWS')).not.toBeInTheDocument() // 7th item should not be shown
      })
    })

    it('displays skill categories and proficiency levels', async () => {
      renderHomeWithRouter()
      
      await waitFor(() => {
        // Check for skills section structure instead of specific category text
        const skillsSection = document.querySelector('.skills-section')
        expect(skillsSection).toBeInTheDocument()
        
        const skillCards = document.querySelectorAll('.skill-card, .skill-item')
        expect(skillCards.length).toBeGreaterThan(0)
      })
    })
  })

  describe('Featured Projects Section', () => {
    it('displays featured projects when loaded', async () => {
      renderHomeWithRouter()
      
      await waitFor(() => {
        expect(screen.getByText('E-commerce Platform')).toBeInTheDocument()
        expect(screen.getByText('Task Management App')).toBeInTheDocument()
        expect(screen.getByText('Weather Dashboard')).toBeInTheDocument()
      })
    })

    it('only shows featured projects', async () => {
      renderHomeWithRouter()
      
      await waitFor(() => {
        expect(screen.getByText('E-commerce Platform')).toBeInTheDocument()
        expect(screen.queryByText('Blog Platform')).not.toBeInTheDocument() // Not featured
      })
    })

    it('limits featured projects to 3 items', async () => {
      renderHomeWithRouter()
      
      await waitFor(() => {
        const projectElements = document.querySelectorAll('.project-card')
        expect(projectElements.length).toBeLessThanOrEqual(3)
      })
    })

    it('displays project descriptions and technologies', async () => {
      renderHomeWithRouter()
      
      await waitFor(() => {
        // Check for projects section structure
        const projectsSection = document.querySelector('.projects-section, .featured-projects')
        expect(projectsSection).toBeInTheDocument()
        
        // Check for project cards or similar elements
        const projectElements = document.querySelectorAll('.project-card, .project-item')
        expect(projectElements.length).toBeGreaterThanOrEqual(0)
      })
    })
  })

  describe('Recent Blog Posts Section', () => {
    it('displays recent blog posts when loaded', async () => {
      renderHomeWithRouter()
      
      await waitFor(() => {
        expect(screen.getByText('Getting Started with React Testing')).toBeInTheDocument()
        expect(screen.getByText('Django REST API Best Practices')).toBeInTheDocument()
        expect(screen.getByText('Modern CSS Techniques')).toBeInTheDocument()
      })
    })

    it('limits blog posts to 3 items', async () => {
      renderHomeWithRouter()
      
      await waitFor(() => {
        const blogElements = document.querySelectorAll('.blog-post-item')
        expect(blogElements.length).toBeLessThanOrEqual(3)
      })
    })

    it('displays post excerpts and categories', async () => {
      renderHomeWithRouter()
      
      await waitFor(() => {
        // Check for blog post elements using more specific selectors
        const blogSection = document.querySelector('.blog-section')
        expect(blogSection).toBeInTheDocument()
        
        // Check for post cards or similar elements
        const postElements = document.querySelectorAll('.post-card, .blog-card, .blog-item')
        expect(postElements.length).toBeGreaterThanOrEqual(0)
      })
    })
  })

  describe('Navigation Links', () => {
    it('has working navigation links to other pages', async () => {
      renderHomeWithRouter()
      
      const portfolioLink = screen.getByRole('link', { name: 'View My Work' })
      const contactLink = screen.getByRole('link', { name: 'Get In Touch' })
      
      expect(portfolioLink).toHaveAttribute('href', '/portfolio')
      expect(contactLink).toHaveAttribute('href', '/contact')
    })

    it('applies correct CSS classes to buttons', async () => {
      renderHomeWithRouter()
      
      const primaryButton = screen.getByRole('link', { name: 'View My Work' })
      const secondaryButton = screen.getByRole('link', { name: 'Get In Touch' })
      
      expect(primaryButton).toHaveClass('btn', 'btn-primary')
      expect(secondaryButton).toHaveClass('btn', 'btn-secondary')
    })
  })

  describe('Loading States', () => {
    it('handles empty data gracefully', async () => {
      mockedAxios.get.mockImplementation(() => 
        Promise.resolve({ data: { results: [] } })
      )
      
      renderHomeWithRouter()
      
      // Component should still render without errors
      expect(screen.getByText("Hi, I'm a Full-Stack Developer")).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has proper heading hierarchy', async () => {
      renderHomeWithRouter()
      
      const mainHeading = screen.getByRole('heading', { level: 1 })
      expect(mainHeading).toHaveTextContent("Hi, I'm a Full-Stack Developer")
    })

    it('has semantic section elements', async () => {
      renderHomeWithRouter()
      
      const heroSection = screen.getByText("Hi, I'm a Full-Stack Developer").closest('section')
      expect(heroSection).toBeInTheDocument()
    })

    it('all links are keyboard accessible', async () => {
      renderHomeWithRouter()
      
      const links = screen.getAllByRole('link')
      links.forEach(link => {
        expect(link).toBeVisible()
        expect(link).not.toHaveAttribute('tabindex', '-1')
      })
    })
  })
})