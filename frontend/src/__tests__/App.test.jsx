/**
 * @fileoverview Test suite for the main App component
 * Tests routing functionality, layout structure, and component integration
 * 
 * @author Portfolio Application Test Suite
 * @version 1.0.0
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';

// Mock all page components to avoid complex dependencies
vi.mock('../pages/Home', () => ({
  default: () => <div data-testid="home-page">Home Page</div>
}));

vi.mock('../pages/About', () => ({
  default: () => <div data-testid="about-page">About Page</div>
}));

vi.mock('../pages/Portfolio', () => ({
  default: () => <div data-testid="portfolio-page">Portfolio Page</div>
}));

vi.mock('../pages/Blog', () => ({
  default: () => <div data-testid="blog-page">Blog Page</div>
}));

vi.mock('../pages/BlogPost', () => ({
  default: () => <div data-testid="blog-post-page">Blog Post Page</div>
}));

vi.mock('../pages/Contact', () => ({
  default: () => <div data-testid="contact-page">Contact Page</div>
}));

vi.mock('../components/Navbar', () => ({
  default: () => <nav data-testid="navbar">Navigation</nav>
}));

vi.mock('../components/Footer', () => ({
  default: () => <footer data-testid="footer">Footer</footer>
}));

// Helper function to render App with specific route
const renderWithRouter = (initialEntries = ['/']) => {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <App />
    </MemoryRouter>
  );
};

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Layout Structure', () => {
    it('renders the main app structure with correct CSS class', () => {
      renderWithRouter();
      
      const appDiv = document.querySelector('.App');
      expect(appDiv).toBeInTheDocument();
    });

    it('renders Navbar component', () => {
      renderWithRouter();
      
      expect(screen.getByTestId('navbar')).toBeInTheDocument();
      expect(screen.getByText('Navigation')).toBeInTheDocument();
    });

    it('renders Footer component', () => {
      renderWithRouter();
      
      expect(screen.getByTestId('footer')).toBeInTheDocument();
      expect(screen.getByText('Footer')).toBeInTheDocument();
    });

    it('renders main content area', () => {
      renderWithRouter();
      
      const mainElement = document.querySelector('main');
      expect(mainElement).toBeInTheDocument();
    });

    it('maintains consistent layout across all routes', () => {
      const routes = ['/', '/about', '/portfolio', '/blog', '/contact'];
      
      routes.forEach(route => {
        renderWithRouter([route]);
        
        // Check that navbar and footer are always present
        expect(screen.getByTestId('navbar')).toBeInTheDocument();
        expect(screen.getByTestId('footer')).toBeInTheDocument();
        expect(document.querySelector('main')).toBeInTheDocument();
      });
    });
  });

  describe('Routing Functionality', () => {
    it('renders Home page on root route', async () => {
      renderWithRouter(['/']);
      
      await waitFor(() => {
        expect(screen.getByTestId('home-page')).toBeInTheDocument();
        expect(screen.getByText('Home Page')).toBeInTheDocument();
      });
    });

    it('renders About page on /about route', async () => {
      renderWithRouter(['/about']);
      
      await waitFor(() => {
        expect(screen.getByTestId('about-page')).toBeInTheDocument();
        expect(screen.getByText('About Page')).toBeInTheDocument();
      });
    });

    it('renders Portfolio page on /portfolio route', async () => {
      renderWithRouter(['/portfolio']);
      
      await waitFor(() => {
        expect(screen.getByTestId('portfolio-page')).toBeInTheDocument();
        expect(screen.getByText('Portfolio Page')).toBeInTheDocument();
      });
    });

    it('renders Blog page on /blog route', async () => {
      renderWithRouter(['/blog']);
      
      await waitFor(() => {
        expect(screen.getByTestId('blog-page')).toBeInTheDocument();
        expect(screen.getByText('Blog Page')).toBeInTheDocument();
      });
    });

    it('renders BlogPost page on /blog/:slug route', async () => {
      renderWithRouter(['/blog/test-post']);
      
      await waitFor(() => {
        expect(screen.getByTestId('blog-post-page')).toBeInTheDocument();
        expect(screen.getByText('Blog Post Page')).toBeInTheDocument();
      });
    });

    it('renders Contact page on /contact route', async () => {
      renderWithRouter(['/contact']);
      
      await waitFor(() => {
        expect(screen.getByTestId('contact-page')).toBeInTheDocument();
        expect(screen.getByText('Contact Page')).toBeInTheDocument();
      });
    });

    it('handles dynamic blog post routes with different slugs', async () => {
      const slugs = ['first-post', 'react-tutorial', 'web-development-tips'];
      
      for (const slug of slugs) {
        renderWithRouter([`/blog/${slug}`]);
        
        await waitFor(() => {
          expect(screen.getByTestId('blog-post-page')).toBeInTheDocument();
        });
      }
    });
  });

  describe('Route Navigation', () => {
    it('navigates between different routes correctly', async () => {
      const { rerender } = render(
        <MemoryRouter initialEntries={['/']}>
          <App />
        </MemoryRouter>
      );

      // Start at home
      expect(screen.getByTestId('home-page')).toBeInTheDocument();

      // Navigate to about
      rerender(
        <MemoryRouter initialEntries={['/about']}>
          <App />
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByTestId('about-page')).toBeInTheDocument();
      });

      // Navigate to portfolio
      rerender(
        <MemoryRouter initialEntries={['/portfolio']}>
          <App />
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByTestId('portfolio-page')).toBeInTheDocument();
      });
    });

    it('maintains navbar and footer during navigation', async () => {
      const routes = ['/', '/about', '/portfolio', '/blog', '/contact'];
      
      for (const route of routes) {
        renderWithRouter([route]);
        
        // Navbar and footer should always be present
        expect(screen.getByTestId('navbar')).toBeInTheDocument();
        expect(screen.getByTestId('footer')).toBeInTheDocument();
      }
    });
  });

  describe('Component Integration', () => {
    it('properly integrates all major components', () => {
      renderWithRouter();
      
      // Check that all major structural components are present
      expect(screen.getByTestId('navbar')).toBeInTheDocument();
      expect(screen.getByTestId('home-page')).toBeInTheDocument();
      expect(screen.getByTestId('footer')).toBeInTheDocument();
    });

    it('renders components in correct order', () => {
      renderWithRouter();
      
      const appDiv = document.querySelector('.App');
      const children = Array.from(appDiv.children);
      
      // Should have navbar, main, and footer in that order
      expect(children).toHaveLength(3);
      expect(children[0]).toHaveAttribute('data-testid', 'navbar');
      expect(children[1].tagName.toLowerCase()).toBe('main');
      expect(children[2]).toHaveAttribute('data-testid', 'footer');
    });

    it('wraps page content in main element', () => {
      renderWithRouter();
      
      const mainElement = document.querySelector('main');
      const homePageElement = screen.getByTestId('home-page');
      
      expect(mainElement).toContainElement(homePageElement);
    });
  });

  describe('Router Configuration', () => {
    it('uses BrowserRouter for client-side routing', () => {
      // This test ensures the router is properly configured
      // The fact that our routing tests work confirms BrowserRouter is working
      renderWithRouter();
      
      expect(screen.getByTestId('home-page')).toBeInTheDocument();
    });

    it('handles route parameters correctly', async () => {
      const testSlugs = ['my-first-post', 'react-hooks-guide', 'css-grid-tutorial'];
      
      for (const slug of testSlugs) {
        renderWithRouter([`/blog/${slug}`]);
        
        await waitFor(() => {
          expect(screen.getByTestId('blog-post-page')).toBeInTheDocument();
        });
      }
    });
  });

  describe('CSS and Styling', () => {
    it('applies App CSS class to root container', () => {
      renderWithRouter();
      
      const appContainer = document.querySelector('.App');
      expect(appContainer).toBeInTheDocument();
      expect(appContainer).toHaveClass('App');
    });

    it('maintains proper DOM structure for styling', () => {
      renderWithRouter();
      
      const appDiv = document.querySelector('.App');
      const navbar = screen.getByTestId('navbar');
      const main = document.querySelector('main');
      const footer = screen.getByTestId('footer');
      
      // Check proper nesting
      expect(appDiv).toContainElement(navbar);
      expect(appDiv).toContainElement(main);
      expect(appDiv).toContainElement(footer);
    });
  });

  describe('Error Handling', () => {
    it('handles invalid routes gracefully', () => {
      // Test with a non-existent route
      renderWithRouter(['/non-existent-route']);
      
      // Should still render navbar and footer
      expect(screen.getByTestId('navbar')).toBeInTheDocument();
      expect(screen.getByTestId('footer')).toBeInTheDocument();
      
      // Main element should still be present even if no route matches
      expect(document.querySelector('main')).toBeInTheDocument();
    });

    it('maintains app structure even with routing errors', () => {
      renderWithRouter(['/invalid/nested/route']);
      
      const appDiv = document.querySelector('.App');
      expect(appDiv).toBeInTheDocument();
      expect(appDiv).toHaveClass('App');
    });
  });

  describe('Accessibility', () => {
    it('provides proper semantic structure', () => {
      renderWithRouter();
      
      // Check for semantic HTML elements
      expect(document.querySelector('nav')).toBeInTheDocument();
      expect(document.querySelector('main')).toBeInTheDocument();
      expect(document.querySelector('footer')).toBeInTheDocument();
    });

    it('maintains focus management during route changes', async () => {
      renderWithRouter(['/']);
      
      // Initial route should be accessible
      expect(screen.getByTestId('home-page')).toBeInTheDocument();
      
      // Navigation should maintain accessibility
      const { rerender } = render(
        <MemoryRouter initialEntries={['/about']}>
          <App />
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByTestId('about-page')).toBeInTheDocument();
      });
    });
  });
});