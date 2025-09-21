/**
 * @fileoverview Test suite for the Footer component.
 * Tests footer content, navigation links, social media links, and dynamic copyright.
 * 
 * @author Portfolio Application
 * @version 1.0.0
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import Footer from '../Footer'

describe('Footer Component', () => {
  describe('Rendering', () => {
    it('renders the footer element', () => {
      render(<Footer />)
      
      const footer = screen.getByRole('contentinfo')
      expect(footer).toBeInTheDocument()
      expect(footer).toHaveClass('footer')
    })

    it('renders the brand section with title and description', () => {
      render(<Footer />)
      
      expect(screen.getByText('Portfolio')).toBeInTheDocument()
      expect(screen.getByText('Full-stack developer passionate about creating amazing web experiences.')).toBeInTheDocument()
    })

    it('renders the Quick Links section', () => {
      render(<Footer />)
      
      expect(screen.getByText('Quick Links')).toBeInTheDocument()
    })

    it('renders the Connect section', () => {
      render(<Footer />)
      
      expect(screen.getByText('Connect')).toBeInTheDocument()
    })
  })

  describe('Navigation Links', () => {
    it('renders all quick navigation links', () => {
      render(<Footer />)
      
      const expectedLinks = [
        { text: 'Home', href: '/' },
        { text: 'About', href: '/about' },
        { text: 'Portfolio', href: '/portfolio' },
        { text: 'Blog', href: '/blog' },
        { text: 'Contact', href: '/contact' }
      ]
      
      expectedLinks.forEach(({ text, href }) => {
        const link = screen.getByRole('link', { name: text })
        expect(link).toBeInTheDocument()
        expect(link).toHaveAttribute('href', href)
      })
    })

    it('navigation links are properly structured in a list', () => {
      render(<Footer />)
      
      const quickLinksSection = screen.getByText('Quick Links').closest('.footer-section')
      const list = quickLinksSection.querySelector('ul')
      expect(list).toBeInTheDocument()
      
      const listItems = quickLinksSection.querySelectorAll('li')
      expect(listItems).toHaveLength(5)
    })
  })

  describe('Social Media Links', () => {
    it('renders all social media links', () => {
      render(<Footer />)
      
      const socialLinks = [
        { text: 'GitHub', href: 'https://github.com' },
        { text: 'LinkedIn', href: 'https://linkedin.com' },
        { text: 'Twitter', href: 'https://twitter.com' }
      ]
      
      socialLinks.forEach(({ text, href }) => {
        const link = screen.getByRole('link', { name: text })
        expect(link).toBeInTheDocument()
        expect(link).toHaveAttribute('href', href)
      })
    })

    it('social media links open in new tab with security attributes', () => {
      render(<Footer />)
      
      const socialLinks = ['GitHub', 'LinkedIn', 'Twitter']
      
      socialLinks.forEach(linkText => {
        const link = screen.getByRole('link', { name: linkText })
        expect(link).toHaveAttribute('target', '_blank')
        expect(link).toHaveAttribute('rel', 'noopener noreferrer')
      })
    })

    it('social links are contained in social-links div', () => {
      render(<Footer />)
      
      const connectSection = screen.getByText('Connect').closest('.footer-section')
      const socialLinksDiv = connectSection.querySelector('.social-links')
      expect(socialLinksDiv).toBeInTheDocument()
      
      const socialLinks = socialLinksDiv.querySelectorAll('a')
      expect(socialLinks).toHaveLength(3)
    })
  })

  describe('Copyright Section', () => {
    let mockDate

    beforeEach(() => {
      // Mock the current year to 2024 for consistent testing
      mockDate = vi.spyOn(global, 'Date').mockImplementation(() => ({
        getFullYear: () => 2024
      }))
    })

    afterEach(() => {
      mockDate.mockRestore()
    })

    it('displays copyright notice with current year', () => {
      render(<Footer />)
      
      expect(screen.getByText('© 2024 Portfolio. All rights reserved.')).toBeInTheDocument()
    })

    it('copyright is in footer-bottom section', () => {
      render(<Footer />)
      
      const footerBottom = screen.getByText('© 2024 Portfolio. All rights reserved.').closest('.footer-bottom')
      expect(footerBottom).toBeInTheDocument()
    })
  })

  describe('Dynamic Year Functionality', () => {
    it('updates copyright year based on current date', () => {
      // Mock different years
      const testYears = [2023, 2024, 2025]
      
      testYears.forEach(year => {
        const mockDate = vi.spyOn(global, 'Date').mockImplementation(() => ({
          getFullYear: () => year
        }))
        
        const { unmount } = render(<Footer />)
        
        expect(screen.getByText(`© ${year} Portfolio. All rights reserved.`)).toBeInTheDocument()
        
        unmount()
        mockDate.mockRestore()
      })
    })
  })

  describe('CSS Structure', () => {
    it('has correct CSS class structure', () => {
      render(<Footer />)
      
      const footer = screen.getByRole('contentinfo')
      expect(footer).toHaveClass('footer')
      
      const container = footer.querySelector('.footer-container')
      expect(container).toBeInTheDocument()
      
      const content = footer.querySelector('.footer-content')
      expect(content).toBeInTheDocument()
      
      const sections = footer.querySelectorAll('.footer-section')
      expect(sections).toHaveLength(3) // Brand, Quick Links, Connect
      
      const bottom = footer.querySelector('.footer-bottom')
      expect(bottom).toBeInTheDocument()
    })
  })

  describe('Content Structure', () => {
    it('has three main content sections', () => {
      render(<Footer />)
      
      const sections = screen.getAllByText(/Portfolio|Quick Links|Connect/)
      expect(sections).toHaveLength(3)
    })

    it('brand section has h3 heading', () => {
      render(<Footer />)
      
      const brandHeading = screen.getByRole('heading', { level: 3, name: 'Portfolio' })
      expect(brandHeading).toBeInTheDocument()
    })

    it('other sections have h4 headings', () => {
      render(<Footer />)
      
      const quickLinksHeading = screen.getByRole('heading', { level: 4, name: 'Quick Links' })
      const connectHeading = screen.getByRole('heading', { level: 4, name: 'Connect' })
      
      expect(quickLinksHeading).toBeInTheDocument()
      expect(connectHeading).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('uses semantic footer element', () => {
      render(<Footer />)
      
      const footer = screen.getByRole('contentinfo')
      expect(footer.tagName.toLowerCase()).toBe('footer')
    })

    it('has proper heading hierarchy', () => {
      render(<Footer />)
      
      const h3 = screen.getByRole('heading', { level: 3 })
      const h4s = screen.getAllByRole('heading', { level: 4 })
      
      expect(h3).toBeInTheDocument()
      expect(h4s).toHaveLength(2)
    })

    it('all links are accessible', () => {
      render(<Footer />)
      
      const links = screen.getAllByRole('link')
      links.forEach(link => {
        expect(link).toBeVisible()
        expect(link).toHaveAttribute('href')
      })
    })
  })
})