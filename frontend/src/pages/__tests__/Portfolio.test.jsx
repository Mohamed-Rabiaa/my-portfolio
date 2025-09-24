import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import Portfolio from '../Portfolio';

// Mock axios
vi.mock('axios');
const mockedAxios = vi.mocked(axios);

// Mock data
const mockProjects = [
  {
    id: 1,
    title: 'E-commerce Website',
    description: 'A full-stack e-commerce platform with React and Django',
    category: 'web-development',
    technologies: ['React', 'Django', 'PostgreSQL'],
    image: 'https://example.com/ecommerce.jpg',
    live_url: 'https://ecommerce-demo.com',
    github_url: 'https://github.com/user/ecommerce',
    created_at: '2024-01-15T10:30:00Z'
  },
  {
    id: 2,
    title: 'Mobile Banking App',
    description: 'A secure mobile banking application with biometric authentication',
    category: 'mobile-development',
    technologies: ['React Native', 'Node.js', 'MongoDB'],
    image: 'https://example.com/banking.jpg',
    live_url: null,
    github_url: 'https://github.com/user/banking-app',
    created_at: '2024-02-20T14:45:00Z'
  },
  {
    id: 3,
    title: 'Data Analytics Dashboard',
    description: 'Interactive dashboard for business intelligence and analytics',
    category: 'data-science',
    technologies: ['Python', 'Plotly', 'Pandas'],
    image: null,
    live_url: 'https://analytics-demo.com',
    github_url: null,
    created_at: '2024-03-10T09:15:00Z'
  }
];

describe('Portfolio Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Loading State', () => {
    it('shows loading spinner while fetching projects', async () => {
      mockedAxios.get.mockImplementation(() => new Promise(() => {})); // Never resolves
      
      render(<Portfolio />);
      
      expect(screen.getByText('Loading projects...')).toBeInTheDocument();
      expect(document.querySelector('.spinner')).toBeInTheDocument(); // spinner
    });

    it('hides loading state after data is fetched', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: { results: mockProjects }
      });
      
      render(<Portfolio />);
      
      await waitFor(() => {
        expect(screen.queryByText('Loading projects...')).not.toBeInTheDocument();
      });
    });
  });

  describe('API Integration', () => {
    it('fetches projects from the correct API endpoint', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: { results: mockProjects }
      });
      
      render(<Portfolio />);
      
      expect(mockedAxios.get).toHaveBeenCalledWith('http://127.0.0.1:8000/api/v1/portfolio/projects/');
    });

    it('handles API errors gracefully', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      mockedAxios.get.mockRejectedValueOnce(new Error('Network error'));
      
      render(<Portfolio />);
      
      await waitFor(() => {
        expect(screen.queryByText('Loading projects...')).not.toBeInTheDocument();
      });
      
      expect(consoleSpy).toHaveBeenCalledWith('Error fetching projects:', expect.any(Error));
      consoleSpy.mockRestore();
    });
  });

  describe('Rendering', () => {
    beforeEach(async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: { results: mockProjects }
      });
    });

    it('renders the portfolio page with all sections', async () => {
      render(<Portfolio />);
      
      await waitFor(() => {
        expect(screen.getByText('My Portfolio')).toBeInTheDocument();
      });
      
      // Check hero section
      expect(screen.getByText(/Explore my collection of projects/)).toBeInTheDocument();
      
      // Check CTA section
      expect(screen.getByText('Interested in Working Together?')).toBeInTheDocument();
      expect(screen.getByRole('link', { name: 'Get In Touch' })).toBeInTheDocument();
    });

    it('renders all projects initially', async () => {
      render(<Portfolio />);
      
      await waitFor(() => {
        expect(screen.getByText('E-commerce Website')).toBeInTheDocument();
        expect(screen.getByText('Mobile Banking App')).toBeInTheDocument();
        expect(screen.getByText('Data Analytics Dashboard')).toBeInTheDocument();
      });
    });

    it('renders project details correctly', async () => {
      render(<Portfolio />);
      
      await waitFor(() => {
        // Check project titles
        expect(screen.getByText('E-commerce Website')).toBeInTheDocument();
        
        // Check project descriptions
        expect(screen.getByText(/A full-stack e-commerce platform/)).toBeInTheDocument();
        
        // Check technology tags
        expect(screen.getByText('React')).toBeInTheDocument();
        expect(screen.getByText('Django')).toBeInTheDocument();
        expect(screen.getByText('PostgreSQL')).toBeInTheDocument();
        
        // Check formatted dates
        expect(screen.getByText('January 2024')).toBeInTheDocument();
        expect(screen.getByText('February 2024')).toBeInTheDocument();
        expect(screen.getByText('March 2024')).toBeInTheDocument();
      });
    });

    it('renders project links correctly', async () => {
      render(<Portfolio />);
      
      await waitFor(() => {
        // Check live demo links
        const liveDemoLinks = screen.getAllByText('Live Demo');
        expect(liveDemoLinks).toHaveLength(2); // Only projects with live_url
        
        // Check GitHub links
        const githubLinks = screen.getAllByText('GitHub');
        expect(githubLinks).toHaveLength(2); // Only projects with github_url
      });
    });

    it('handles projects without images', async () => {
      render(<Portfolio />);
      
      await waitFor(() => {
        expect(screen.getByText('No Image')).toBeInTheDocument();
      });
    });
  });

  describe('Category Filtering', () => {
    beforeEach(async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: { results: mockProjects }
      });
    });

    it('renders filter buttons for all categories', async () => {
      render(<Portfolio />);
      
      await waitFor(() => {
        expect(screen.getByText('All Projects')).toBeInTheDocument();
        expect(screen.getByText('Web-development')).toBeInTheDocument();
        expect(screen.getByText('Mobile-development')).toBeInTheDocument();
        expect(screen.getByText('Data-science')).toBeInTheDocument();
      });
    });

    it('filters projects by category', async () => {
      const user = userEvent.setup();
      render(<Portfolio />);
      
      await waitFor(() => {
        expect(screen.getByText('E-commerce Website')).toBeInTheDocument();
      });
      
      // Filter by web-development
      const webDevButton = screen.getByText('Web-development');
      await user.click(webDevButton);
      
      // Should only show web development project
      expect(screen.getByText('E-commerce Website')).toBeInTheDocument();
      expect(screen.queryByText('Mobile Banking App')).not.toBeInTheDocument();
      expect(screen.queryByText('Data Analytics Dashboard')).not.toBeInTheDocument();
    });

    it('shows all projects when "All Projects" is selected', async () => {
      const user = userEvent.setup();
      render(<Portfolio />);
      
      await waitFor(() => {
        expect(screen.getByText('E-commerce Website')).toBeInTheDocument();
      });
      
      // Filter by specific category first
      await user.click(screen.getByText('Web-development'));
      
      // Then click "All Projects"
      await user.click(screen.getByText('All Projects'));
      
      // Should show all projects again
      expect(screen.getByText('E-commerce Website')).toBeInTheDocument();
      expect(screen.getByText('Mobile Banking App')).toBeInTheDocument();
      expect(screen.getByText('Data Analytics Dashboard')).toBeInTheDocument();
    });

    it('highlights active filter button', async () => {
      const user = userEvent.setup();
      render(<Portfolio />);
      
      await waitFor(() => {
        expect(screen.getByText('All Projects')).toBeInTheDocument();
      });
      
      // Initially "All Projects" should be active
      expect(screen.getByText('All Projects')).toHaveClass('active');
      
      // Click on web-development filter
      const webDevButton = screen.getByText('Web-development');
      await user.click(webDevButton);
      
      // Web-development should now be active
      expect(webDevButton).toHaveClass('active');
      expect(screen.getByText('All Projects')).not.toHaveClass('active');
    });

    it('shows empty state when no projects match filter', async () => {
      const user = userEvent.setup();
      // Mock with projects that don't have a specific category
      mockedAxios.get.mockResolvedValueOnce({
        data: { results: [mockProjects[0]] } // Only web-development project
      });
      
      render(<Portfolio />);
      
      await waitFor(() => {
        expect(screen.getByText('E-commerce Website')).toBeInTheDocument();
      });
      
      // Filter by a category that doesn't exist
      const mobileButton = screen.queryByText('Mobile-development');
      if (mobileButton) {
        await user.click(mobileButton);
        expect(screen.getByText('No projects found for the selected category.')).toBeInTheDocument();
      }
    });
  });

  describe('Date Formatting', () => {
    beforeEach(async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: { results: mockProjects }
      });
    });

    it('formats dates correctly', async () => {
      render(<Portfolio />);
      
      await waitFor(() => {
        expect(screen.getByText('January 2024')).toBeInTheDocument();
        expect(screen.getByText('February 2024')).toBeInTheDocument();
        expect(screen.getByText('March 2024')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    beforeEach(async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: { results: mockProjects }
      });
    });

    it('has proper heading hierarchy', async () => {
      render(<Portfolio />);
      
      await waitFor(() => {
        const h1 = screen.getByRole('heading', { level: 1 });
        const h2Elements = screen.getAllByRole('heading', { level: 2 });
        const h3Elements = screen.getAllByRole('heading', { level: 3 });
        
        expect(h1).toHaveTextContent('My Portfolio');
        expect(h2Elements).toHaveLength(1); // CTA section
        expect(h3Elements.length).toBeGreaterThan(0); // Project titles
      });
    });

    it('has proper alt text for images', async () => {
      render(<Portfolio />);
      
      await waitFor(() => {
        const images = screen.getAllByRole('img');
        images.forEach(img => {
          expect(img).toHaveAttribute('alt');
        });
      });
    });

    it('has proper link attributes for external links', async () => {
      render(<Portfolio />);
      
      await waitFor(() => {
        const externalLinks = screen.getAllByRole('link').filter(link => 
          link.getAttribute('href')?.startsWith('http')
        );
        
        externalLinks.forEach(link => {
          expect(link).toHaveAttribute('target', '_blank');
          expect(link).toHaveAttribute('rel', 'noopener noreferrer');
        });
      });
    });
  });

  describe('CSS Classes and Structure', () => {
    beforeEach(async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: { results: mockProjects }
      });
    });

    it('applies correct CSS classes to main sections', async () => {
      const { container } = render(<Portfolio />);
      
      await waitFor(() => {
        expect(container.querySelector('.portfolio')).toBeInTheDocument();
        expect(container.querySelector('.portfolio-hero')).toBeInTheDocument();
        expect(container.querySelector('.portfolio-filter')).toBeInTheDocument();
        expect(container.querySelector('.portfolio-grid')).toBeInTheDocument();
        expect(container.querySelector('.portfolio-cta')).toBeInTheDocument();
      });
    });

    it('applies correct CSS classes to project cards', async () => {
      const { container } = render(<Portfolio />);
      
      await waitFor(() => {
        expect(container.querySelectorAll('.project-card')).toHaveLength(3);
        expect(container.querySelectorAll('.project-image')).toHaveLength(3);
        expect(container.querySelectorAll('.project-content')).toHaveLength(3);
        expect(container.querySelectorAll('.project-overlay')).toHaveLength(3);
      });
    });

    it('applies correct CSS classes to filter buttons', async () => {
      const { container } = render(<Portfolio />);
      
      await waitFor(() => {
        expect(container.querySelector('.filter-buttons')).toBeInTheDocument();
        expect(container.querySelectorAll('.filter-btn')).toHaveLength(4); // all + 3 categories
      });
    });

    it('applies correct CSS classes to technology tags', async () => {
      const { container } = render(<Portfolio />);
      
      await waitFor(() => {
        expect(container.querySelectorAll('.tech-tag').length).toBeGreaterThan(0);
        expect(container.querySelectorAll('.project-technologies')).toHaveLength(3);
      });
    });
  });

  describe('Loading Spinner', () => {
    it('renders loading spinner with correct structure', () => {
      mockedAxios.get.mockImplementation(() => new Promise(() => {}));
      
      const { container } = render(<Portfolio />);
      
      expect(container.querySelector('.loading')).toBeInTheDocument();
      expect(container.querySelector('.spinner')).toBeInTheDocument();
    });
  });
});