/**
 * @fileoverview Test suite for the Navbar component.
 * Tests navigation functionality, active link highlighting, and routing behavior.
 * 
 * @author Portfolio Application
 * @version 1.0.0
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter, MemoryRouter } from 'react-router-dom'
import Navbar from '../Navbar'

/**
 * Helper function to render Navbar with router context
 * @param {string} initialRoute - Initial route for testing
 * @returns {object} Render result from testing library
 */
const renderNavbarWithRouter = (initialRoute = '/') => {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <Navbar />
    </MemoryRouter>
  )
}

describe('Navbar Component', () => {
  describe('Rendering', () => {
    it('renders the navbar with brand name', () => {
      renderNavbarWithRouter()
      
      expect(screen.getByText('Mohamed Rabiaa')).toBeInTheDocument()
      expect(screen.getByRole('navigation')).toBeInTheDocument()
    })

    it('renders all navigation links', () => {
      renderNavbarWithRouter()
      
      const expectedLinks = ['Home', 'About', 'Portfolio', 'Blog', 'Contact']
      
      expectedLinks.forEach(linkText => {
        expect(screen.getByRole('link', { name: linkText })).toBeInTheDocument()
      })
    })

    it('renders brand logo as a link to home', () => {
      renderNavbarWithRouter()
      
      const brandLink = screen.getByRole('link', { name: 'Mohamed Rabiaa' })
      expect(brandLink).toHaveAttribute('href', '/')
    })
  })

  describe('Navigation Links', () => {
    it('has correct href attributes for all navigation links', () => {
      renderNavbarWithRouter()
      
      const linkMappings = [
        { text: 'Home', href: '/' },
        { text: 'About', href: '/about' },
        { text: 'Portfolio', href: '/portfolio' },
        { text: 'Blog', href: '/blog' },
        { text: 'Contact', href: '/contact' }
      ]
      
      linkMappings.forEach(({ text, href }) => {
        const link = screen.getByRole('link', { name: text })
        expect(link).toHaveAttribute('href', href)
      })
    })

    it('applies nav-link class to all navigation links', () => {
      renderNavbarWithRouter()
      
      const navLinks = screen.getAllByRole('link')
      // Skip the brand link (first one) and check navigation links
      const navigationLinks = navLinks.slice(1)
      
      navigationLinks.forEach(link => {
        expect(link).toHaveClass('nav-link')
      })
    })
  })

  describe('Active Link Highlighting', () => {
    it('highlights Home link when on home page', () => {
      renderNavbarWithRouter('/')
      
      const homeLink = screen.getByRole('link', { name: 'Home' })
      expect(homeLink).toHaveClass('active')
      
      // Other links should not be active
      const otherLinks = ['About', 'Portfolio', 'Blog', 'Contact']
      otherLinks.forEach(linkText => {
        const link = screen.getByRole('link', { name: linkText })
        expect(link).not.toHaveClass('active')
      })
    })

    it('highlights About link when on about page', () => {
      renderNavbarWithRouter('/about')
      
      const aboutLink = screen.getByRole('link', { name: 'About' })
      expect(aboutLink).toHaveClass('active')
      
      // Other links should not be active
      const otherLinks = ['Home', 'Portfolio', 'Blog', 'Contact']
      otherLinks.forEach(linkText => {
        const link = screen.getByRole('link', { name: linkText })
        expect(link).not.toHaveClass('active')
      })
    })

    it('highlights Portfolio link when on portfolio page', () => {
      renderNavbarWithRouter('/portfolio')
      
      const portfolioLink = screen.getByRole('link', { name: 'Portfolio' })
      expect(portfolioLink).toHaveClass('active')
    })

    it('highlights Blog link when on blog page', () => {
      renderNavbarWithRouter('/blog')
      
      const blogLink = screen.getByRole('link', { name: 'Blog' })
      expect(blogLink).toHaveClass('active')
    })

    it('highlights Contact link when on contact page', () => {
      renderNavbarWithRouter('/contact')
      
      const contactLink = screen.getByRole('link', { name: 'Contact' })
      expect(contactLink).toHaveClass('active')
    })

    it('does not highlight any link on unknown route', () => {
      renderNavbarWithRouter('/unknown-route')
      
      const allNavLinks = ['Home', 'About', 'Portfolio', 'Blog', 'Contact']
      allNavLinks.forEach(linkText => {
        const link = screen.getByRole('link', { name: linkText })
        expect(link).not.toHaveClass('active')
      })
    })
  })

  describe('CSS Classes', () => {
    it('applies correct CSS classes to navbar elements', () => {
      renderNavbarWithRouter()
      
      const navbar = screen.getByRole('navigation')
      expect(navbar).toHaveClass('navbar')
      
      const container = navbar.querySelector('.nav-container')
      expect(container).toBeInTheDocument()
      
      const menu = navbar.querySelector('.nav-menu')
      expect(menu).toBeInTheDocument()
      
      const items = navbar.querySelectorAll('.nav-item')
      expect(items).toHaveLength(5) // 5 navigation items
    })

    it('applies nav-logo class to brand link', () => {
      renderNavbarWithRouter()
      
      const brandLink = screen.getByRole('link', { name: 'Mohamed Rabiaa' })
      expect(brandLink).toHaveClass('nav-logo')
    })
  })

  describe('Accessibility', () => {
    it('has proper semantic structure with nav element', () => {
      renderNavbarWithRouter()
      
      const nav = screen.getByRole('navigation')
      expect(nav).toBeInTheDocument()
    })

    it('uses proper list structure for navigation items', () => {
      renderNavbarWithRouter()
      
      const list = screen.getByRole('list')
      expect(list).toBeInTheDocument()
      
      const listItems = screen.getAllByRole('listitem')
      expect(listItems).toHaveLength(5) // 5 navigation items
    })

    it('all links are keyboard accessible', () => {
      renderNavbarWithRouter()
      
      const links = screen.getAllByRole('link')
      links.forEach(link => {
        expect(link).toBeVisible()
        expect(link).not.toHaveAttribute('tabindex', '-1')
      })
    })
  })
})