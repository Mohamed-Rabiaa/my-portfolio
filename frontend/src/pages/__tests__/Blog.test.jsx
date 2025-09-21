import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import axios from 'axios';
import Blog from '../Blog';

// Mock axios
vi.mock('axios');
const mockedAxios = vi.mocked(axios);

// Mock data
const mockPosts = [
  {
    id: 1,
    title: 'Getting Started with React Hooks',
    content: 'React Hooks are a powerful feature that allows you to use state and other React features without writing a class component. In this comprehensive guide, we will explore the most commonly used hooks and how to implement them effectively in your applications.',
    slug: 'getting-started-with-react-hooks',
    featured_image: 'https://example.com/react-hooks.jpg',
    created_at: '2024-01-15T10:30:00Z',
    category: { name: 'React' },
    tags: [
      { name: 'React' },
      { name: 'JavaScript' },
      { name: 'Frontend' }
    ]
  },
  {
    id: 2,
    title: 'Building RESTful APIs with Django',
    content: 'Django REST Framework provides a powerful and flexible toolkit for building Web APIs. This tutorial will walk you through creating a complete RESTful API from scratch, including authentication, serialization, and testing.',
    slug: 'building-restful-apis-with-django',
    featured_image: null,
    created_at: '2024-02-20T14:45:00Z',
    category: { name: 'Django' },
    tags: [
      { name: 'Django' },
      { name: 'Python' },
      { name: 'Backend' },
      { name: 'API' }
    ]
  },
  {
    id: 3,
    title: 'CSS Grid vs Flexbox: When to Use Which',
    content: 'Both CSS Grid and Flexbox are powerful layout systems, but they serve different purposes. Understanding when to use each one will make you a more effective frontend developer.',
    slug: 'css-grid-vs-flexbox',
    featured_image: 'https://example.com/css-layout.jpg',
    created_at: '2024-03-10T09:15:00Z',
    category: { name: 'CSS' },
    tags: [
      { name: 'CSS' },
      { name: 'Layout' }
    ]
  }
];

const mockApiResponse = {
  results: mockPosts,
  count: 25, // Total posts
  next: 'http://127.0.0.1:8000/api/blog/posts/?page=2',
  previous: null
};

// Wrapper component for React Router
const BlogWrapper = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('Blog Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock window.scrollTo
    Object.defineProperty(window, 'scrollTo', {
      value: vi.fn(),
      writable: true
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Loading State', () => {
    it('shows loading spinner while fetching posts', async () => {
      mockedAxios.get.mockImplementation(() => new Promise(() => {})); // Never resolves
      
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      expect(screen.getByText('Loading blog posts...')).toBeInTheDocument();
      expect(screen.getByRole('status', { hidden: true })).toBeInTheDocument(); // spinner
    });

    it('hides loading state after data is fetched', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: mockApiResponse });
      
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        expect(screen.queryByText('Loading blog posts...')).not.toBeInTheDocument();
      });
    });
  });

  describe('API Integration', () => {
    it('fetches posts from the correct API endpoint', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: mockApiResponse });
      
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      expect(mockedAxios.get).toHaveBeenCalledWith('http://127.0.0.1:8000/api/blog/posts/?page=1');
    });

    it('handles API errors gracefully', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      mockedAxios.get.mockRejectedValueOnce(new Error('Network error'));
      
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        expect(screen.queryByText('Loading blog posts...')).not.toBeInTheDocument();
      });
      
      expect(consoleSpy).toHaveBeenCalledWith('Error fetching blog posts:', expect.any(Error));
      consoleSpy.mockRestore();
    });
  });

  describe('Rendering', () => {
    beforeEach(async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: mockApiResponse });
    });

    it('renders the blog page with all sections', async () => {
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('My Blog')).toBeInTheDocument();
      });
      
      // Check hero section
      expect(screen.getByText(/Thoughts, tutorials, and insights/)).toBeInTheDocument();
      
      // Check newsletter section
      expect(screen.getByText('Stay Updated')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter your email address')).toBeInTheDocument();
    });

    it('renders all blog posts', async () => {
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Getting Started with React Hooks')).toBeInTheDocument();
        expect(screen.getByText('Building RESTful APIs with Django')).toBeInTheDocument();
        expect(screen.getByText('CSS Grid vs Flexbox: When to Use Which')).toBeInTheDocument();
      });
    });

    it('renders post details correctly', async () => {
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        // Check post titles are links
        const postLinks = screen.getAllByRole('link').filter(link => 
          link.textContent.includes('Getting Started with React Hooks')
        );
        expect(postLinks.length).toBeGreaterThan(0);
        
        // Check formatted dates
        expect(screen.getByText('January 15, 2024')).toBeInTheDocument();
        expect(screen.getByText('February 20, 2024')).toBeInTheDocument();
        expect(screen.getByText('March 10, 2024')).toBeInTheDocument();
        
        // Check categories
        expect(screen.getByText('React')).toBeInTheDocument();
        expect(screen.getByText('Django')).toBeInTheDocument();
        expect(screen.getByText('CSS')).toBeInTheDocument();
        
        // Check truncated content
        expect(screen.getByText(/React Hooks are a powerful feature/)).toBeInTheDocument();
      });
    });

    it('renders post tags correctly', async () => {
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        // Check that tags are rendered (limited to 3 per post)
        expect(screen.getByText('JavaScript')).toBeInTheDocument();
        expect(screen.getByText('Frontend')).toBeInTheDocument();
        expect(screen.getByText('Python')).toBeInTheDocument();
        expect(screen.getByText('Backend')).toBeInTheDocument();
      });
    });

    it('handles posts without images', async () => {
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('No Image')).toBeInTheDocument();
      });
    });

    it('renders "Read More" links correctly', async () => {
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        const readMoreLinks = screen.getAllByText('Read More →');
        expect(readMoreLinks).toHaveLength(3);
        
        // Check that links have correct href
        readMoreLinks.forEach(link => {
          expect(link.closest('a')).toHaveAttribute('href');
        });
      });
    });
  });

  describe('Content Truncation', () => {
    beforeEach(async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: mockApiResponse });
    });

    it('truncates long content correctly', async () => {
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        // Check that long content is truncated with ellipsis
        const truncatedContent = screen.getByText(/React Hooks are a powerful feature/);
        expect(truncatedContent.textContent).toMatch(/\.\.\.$/);
      });
    });

    it('does not truncate short content', async () => {
      const shortPostResponse = {
        ...mockApiResponse,
        results: [{
          ...mockPosts[0],
          content: 'Short content'
        }]
      };
      
      mockedAxios.get.mockResolvedValueOnce({ data: shortPostResponse });
      
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Short content')).toBeInTheDocument();
      });
    });
  });

  describe('Pagination', () => {
    beforeEach(() => {
      mockedAxios.get.mockResolvedValueOnce({ data: mockApiResponse });
    });

    it('renders pagination controls when there are multiple pages', async () => {
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('← Previous')).toBeInTheDocument();
        expect(screen.getByText('Next →')).toBeInTheDocument();
        expect(screen.getByText('1')).toBeInTheDocument();
        expect(screen.getByText('2')).toBeInTheDocument();
        expect(screen.getByText('3')).toBeInTheDocument();
      });
    });

    it('disables previous button on first page', async () => {
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        const prevButton = screen.getByText('← Previous');
        expect(prevButton).toBeDisabled();
        expect(prevButton).toHaveClass('disabled');
      });
    });

    it('highlights current page number', async () => {
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        const currentPageButton = screen.getByText('1');
        expect(currentPageButton).toHaveClass('active');
      });
    });

    it('handles page navigation correctly', async () => {
      const user = userEvent.setup();
      
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Next →')).toBeInTheDocument();
      });
      
      // Mock second page response
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          ...mockApiResponse,
          results: [mockPosts[0]], // Different posts for page 2
          previous: 'http://127.0.0.1:8000/api/blog/posts/?page=1'
        }
      });
      
      // Click next page
      const nextButton = screen.getByText('Next →');
      await user.click(nextButton);
      
      // Should call API with page 2
      expect(mockedAxios.get).toHaveBeenCalledWith('http://127.0.0.1:8000/api/blog/posts/?page=2');
      
      // Should scroll to top
      expect(window.scrollTo).toHaveBeenCalledWith({ top: 0, behavior: 'smooth' });
    });

    it('handles direct page number clicks', async () => {
      const user = userEvent.setup();
      
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('3')).toBeInTheDocument();
      });
      
      // Mock page 3 response
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          ...mockApiResponse,
          results: [mockPosts[2]]
        }
      });
      
      // Click page 3
      const page3Button = screen.getByText('3');
      await user.click(page3Button);
      
      expect(mockedAxios.get).toHaveBeenCalledWith('http://127.0.0.1:8000/api/blog/posts/?page=3');
    });

    it('does not render pagination for single page', async () => {
      const singlePageResponse = {
        ...mockApiResponse,
        count: 3 // Only 3 posts, so 1 page
      };
      
      mockedAxios.get.mockResolvedValueOnce({ data: singlePageResponse });
      
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Getting Started with React Hooks')).toBeInTheDocument();
      });
      
      expect(screen.queryByText('← Previous')).not.toBeInTheDocument();
      expect(screen.queryByText('Next →')).not.toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('shows empty state when no posts are available', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: { results: [], count: 0 }
      });
      
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('No blog posts found')).toBeInTheDocument();
        expect(screen.getByText('Check back later for new content!')).toBeInTheDocument();
      });
    });
  });

  describe('Newsletter Section', () => {
    beforeEach(async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: mockApiResponse });
    });

    it('renders newsletter subscription form', async () => {
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Stay Updated')).toBeInTheDocument();
        expect(screen.getByPlaceholderText('Enter your email address')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Subscribe' })).toBeInTheDocument();
      });
    });

    it('has proper form structure', async () => {
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        const emailInput = screen.getByPlaceholderText('Enter your email address');
        expect(emailInput).toHaveAttribute('type', 'email');
        expect(emailInput).toBeRequired();
        
        const submitButton = screen.getByRole('button', { name: 'Subscribe' });
        expect(submitButton).toHaveAttribute('type', 'submit');
      });
    });
  });

  describe('Accessibility', () => {
    beforeEach(async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: mockApiResponse });
    });

    it('has proper heading hierarchy', async () => {
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        const h1 = screen.getByRole('heading', { level: 1 });
        const h2Elements = screen.getAllByRole('heading', { level: 2 });
        
        expect(h1).toHaveTextContent('My Blog');
        expect(h2Elements.length).toBeGreaterThan(0); // Post titles and newsletter
      });
    });

    it('uses semantic HTML elements', async () => {
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        const articles = screen.getAllByRole('article');
        expect(articles).toHaveLength(3);
        
        const form = document.querySelector('.newsletter-form');
        expect(form).toBeInTheDocument();
      });
    });

    it('has proper alt text for images', async () => {
      render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        const images = screen.getAllByRole('img');
        images.forEach(img => {
          expect(img).toHaveAttribute('alt');
        });
      });
    });
  });

  describe('CSS Classes and Structure', () => {
    beforeEach(async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: mockApiResponse });
    });

    it('applies correct CSS classes to main sections', async () => {
      const { container } = render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        expect(container.querySelector('.blog')).toBeInTheDocument();
        expect(container.querySelector('.blog-hero')).toBeInTheDocument();
        expect(container.querySelector('.blog-posts')).toBeInTheDocument();
        expect(container.querySelector('.newsletter-section')).toBeInTheDocument();
      });
    });

    it('applies correct CSS classes to post cards', async () => {
      const { container } = render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        expect(container.querySelectorAll('.post-card')).toHaveLength(3);
        expect(container.querySelectorAll('.post-image')).toHaveLength(3);
        expect(container.querySelectorAll('.post-content')).toHaveLength(3);
        expect(container.querySelectorAll('.post-meta')).toHaveLength(3);
      });
    });

    it('applies correct CSS classes to pagination', async () => {
      const { container } = render(
        <BlogWrapper>
          <Blog />
        </BlogWrapper>
      );
      
      await waitFor(() => {
        expect(container.querySelector('.pagination')).toBeInTheDocument();
        expect(container.querySelector('.pagination-numbers')).toBeInTheDocument();
        expect(container.querySelectorAll('.pagination-btn')).toHaveLength(2);
      });
    });
  });
});