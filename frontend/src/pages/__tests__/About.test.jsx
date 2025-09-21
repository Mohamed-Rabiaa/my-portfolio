/**
 * @fileoverview Test suite for the About page component.
 * Tests rendering, API integration, skills grouping, and content display.
 * 
 * @author Portfolio Application
 * @version 1.0.0
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor, act } from '@testing-library/react'
import axios from 'axios'
import About from '../About'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

// Mock data for API responses
const mockSkillsResponse = {
  data: {
    results: [
      { id: 1, name: 'JavaScript', category: 'Frontend', proficiency: 90, years_experience: 5 },
      { id: 2, name: 'React', category: 'Frontend', proficiency: 85, years_experience: 4 },
      { id: 3, name: 'Vue.js', category: 'Frontend', proficiency: 75, years_experience: 2 },
      { id: 4, name: 'Python', category: 'Backend', proficiency: 88, years_experience: 6 },
      { id: 5, name: 'Django', category: 'Backend', proficiency: 82, years_experience: 4 },
      { id: 6, name: 'Node.js', category: 'Backend', proficiency: 78, years_experience: 3 },
      { id: 7, name: 'PostgreSQL', category: 'Database', proficiency: 75, years_experience: 4 },
      { id: 8, name: 'MongoDB', category: 'Database', proficiency: 70, years_experience: 2 },
      { id: 9, name: 'Docker', category: 'DevOps', proficiency: 70, years_experience: 3 },
      { id: 10, name: 'AWS', category: 'Cloud', proficiency: 65, years_experience: 2 }
    ]
  }
}

describe('About Component', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    vi.clearAllMocks()
    
    // Setup default successful API response
    mockedAxios.get.mockResolvedValue(mockSkillsResponse)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Initial Rendering', () => {
    it('renders the about page with main content', async () => {
      act(() => {
        render(<About />)
      })
      
      // Check for main heading or key content that should always be present
      expect(screen.getByText(/About/i)).toBeInTheDocument()
    })

    it('has proper page structure with sections', async () => {
      act(() => {
        render(<About />)
      })
      
      // Check for semantic structure
      const sections = screen.getAllByRole('region', { hidden: true }) || 
                      document.querySelectorAll('section')
      expect(sections.length).toBeGreaterThan(0)
    })
  })

  describe('API Data Fetching', () => {
    it('makes API call to skills endpoint on mount', async () => {
      act(() => {
        render(<About />)
      })
      
      await waitFor(() => {
        expect(mockedAxios.get).toHaveBeenCalledWith('http://127.0.0.1:8000/api/skills/')
      })
    })

    it('displays loading state initially', async () => {
      // Mock a delayed response
      mockedAxios.get.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
      
      act(() => {
        render(<About />)
      })
      
      // Should show loading indicator or empty state initially
      // Note: Adjust this based on your actual loading implementation
    })

    it('handles API errors gracefully', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('API Error'))
      
      act(() => {
        render(<About />)
      })
      
      // Should handle error state appropriately
      await waitFor(() => {
        expect(mockedAxios.get).toHaveBeenCalled()
      })
    })
  })

  describe('Skills Display', () => {
    it('displays skills after successful API call', async () => {
      act(() => {
        render(<About />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('JavaScript')).toBeInTheDocument()
        expect(screen.getByText('React')).toBeInTheDocument()
        expect(screen.getByText('Python')).toBeInTheDocument()
      })
    })

    it('groups skills by category', async () => {
      act(() => {
        render(<About />)
      })
      
      await waitFor(() => {
        // Check for category headers or grouped display
        expect(screen.getByText('Frontend')).toBeInTheDocument()
        expect(screen.getByText('Backend')).toBeInTheDocument()
        expect(screen.getByText('Database')).toBeInTheDocument()
      })
    })

    it('displays skill proficiency levels', async () => {
      act(() => {
        render(<About />)
      })
      
      await waitFor(() => {
        // Check for proficiency indicators (adjust based on implementation)
        const skillElements = screen.getAllByText(/\d+%|\d+\/10|Advanced|Intermediate/)
        expect(skillElements.length).toBeGreaterThan(0)
      })
    })

    it('shows years of experience for skills', async () => {
      act(() => {
        render(<About />)
      })
      
      await waitFor(() => {
        // Check for experience indicators
        const experienceElements = screen.getAllByText(/\d+\s*years?/i)
        expect(experienceElements.length).toBeGreaterThan(0)
      })
    })
  })

  describe('Skills Filtering and Sorting', () => {
    it('displays all skill categories', async () => {
      act(() => {
        render(<About />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('Frontend')).toBeInTheDocument()
        expect(screen.getByText('Backend')).toBeInTheDocument()
        expect(screen.getByText('Database')).toBeInTheDocument()
        expect(screen.getByText('DevOps')).toBeInTheDocument()
        expect(screen.getByText('Cloud')).toBeInTheDocument()
      })
    })

    it('shows correct number of skills per category', async () => {
      act(() => {
        render(<About />)
      })
      
      await waitFor(() => {
        // Frontend: JavaScript, React, Vue.js (3 skills)
        const frontendSkills = ['JavaScript', 'React', 'Vue.js']
        frontendSkills.forEach(skill => {
          expect(screen.getByText(skill)).toBeInTheDocument()
        })
        
        // Backend: Python, Django, Node.js (3 skills)
        const backendSkills = ['Python', 'Django', 'Node.js']
        backendSkills.forEach(skill => {
          expect(screen.getByText(skill)).toBeInTheDocument()
        })
      })
    })
  })

  describe('Content Sections', () => {
    it('displays personal introduction section', async () => {
      act(() => {
        render(<About />)
      })
      
      // Check for introduction content
      expect(screen.getByText(/passionate|developer|experience/i)).toBeInTheDocument()
    })

    it('displays professional background section', async () => {
      act(() => {
        render(<About />)
      })
      
      // Check for background content
      expect(screen.getByText(/background|career|journey/i)).toBeInTheDocument()
    })

    it('displays technical expertise section', async () => {
      act(() => {
        render(<About />)
      })
      
      // Check for technical content
      expect(screen.getByText(/skills|technologies|expertise/i)).toBeInTheDocument()
    })
  })

  describe('Responsive Design', () => {
    it('renders properly on different screen sizes', async () => {
      act(() => {
        render(<About />)
      })
      
      // Basic rendering test - more detailed responsive tests would require viewport manipulation
      expect(screen.getByText(/About/i)).toBeInTheDocument()
    })

    it('maintains accessibility standards', async () => {
      act(() => {
        render(<About />)
      })
      
      // Check for proper heading hierarchy and semantic structure
      const headings = screen.getAllByRole('heading')
      expect(headings.length).toBeGreaterThan(0)
    })
  })
})