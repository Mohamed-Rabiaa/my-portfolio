import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import Contact from '../Contact';

// Mock axios
vi.mock('axios');
const mockedAxios = vi.mocked(axios);

describe('Contact Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Rendering', () => {
    it('renders the contact page with all sections', () => {
      render(<Contact />);
      
      // Check hero section
      expect(screen.getByText('Get In Touch')).toBeInTheDocument();
      expect(screen.getByText(/Have a project in mind/)).toBeInTheDocument();
      
      // Check contact info section
      expect(screen.getByText("Let's Connect")).toBeInTheDocument();
      expect(screen.getByText('your.email@example.com')).toBeInTheDocument();
      expect(screen.getByText('+1 (555) 123-4567')).toBeInTheDocument();
      expect(screen.getByText('San Francisco, CA')).toBeInTheDocument();
      
      // Check form section
      expect(screen.getByText('Send Me a Message')).toBeInTheDocument();
    });

    it('renders all form fields with proper labels', () => {
      render(<Contact />);
      
      expect(screen.getByLabelText('Name *')).toBeInTheDocument();
      expect(screen.getByLabelText('Email *')).toBeInTheDocument();
      expect(screen.getByLabelText('Subject *')).toBeInTheDocument();
      expect(screen.getByLabelText('Message *')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Send Message' })).toBeInTheDocument();
    });

    it('renders social media links', () => {
      render(<Contact />);
      
      expect(screen.getByLabelText('LinkedIn')).toBeInTheDocument();
      expect(screen.getByLabelText('GitHub')).toBeInTheDocument();
      expect(screen.getByLabelText('Twitter')).toBeInTheDocument();
    });

    it('renders contact method icons and information', () => {
      render(<Contact />);
      
      expect(screen.getByText('Email')).toBeInTheDocument();
      expect(screen.getByText('Phone')).toBeInTheDocument();
      expect(screen.getByText('Location')).toBeInTheDocument();
    });
  });

  describe('Form Functionality', () => {
    it('updates form data when user types in fields', async () => {
      const user = userEvent.setup();
      render(<Contact />);
      
      const nameInput = screen.getByLabelText('Name *');
      const emailInput = screen.getByLabelText('Email *');
      const subjectInput = screen.getByLabelText('Subject *');
      const messageInput = screen.getByLabelText('Message *');
      
      await user.type(nameInput, 'John Doe');
      await user.type(emailInput, 'john@example.com');
      await user.type(subjectInput, 'Test Subject');
      await user.type(messageInput, 'Test message content');
      
      expect(nameInput).toHaveValue('John Doe');
      expect(emailInput).toHaveValue('john@example.com');
      expect(subjectInput).toHaveValue('Test Subject');
      expect(messageInput).toHaveValue('Test message content');
    });

    it('shows validation errors for required fields', async () => {
      const user = userEvent.setup();
      render(<Contact />);
      
      const submitButton = screen.getByRole('button', { name: 'Send Message' });
      await user.click(submitButton);
      
      // HTML5 validation should prevent submission
      const nameInput = screen.getByLabelText('Name *');
      expect(nameInput).toBeRequired();
      expect(nameInput).toBeInvalid();
    });

    it('validates email format', async () => {
      const user = userEvent.setup();
      render(<Contact />);
      
      const emailInput = screen.getByLabelText('Email *');
      await user.type(emailInput, 'invalid-email');
      
      const submitButton = screen.getByRole('button', { name: 'Send Message' });
      await user.click(submitButton);
      
      expect(emailInput).toBeInvalid();
    });
  });

  describe('Form Submission', () => {
    const mockFormData = {
      name: 'John Doe',
      email: 'john@example.com',
      subject: 'Test Subject',
      message: 'Test message content'
    };

    it('submits form successfully and shows success message', async () => {
    // Mock successful API response with delay
    mockedAxios.post.mockImplementation(() => 
      new Promise(resolve => 
        setTimeout(() => resolve({ data: { message: 'Message sent successfully' } }), 100)
      )
    );

    render(<Contact />);
    
    // Fill out form
    await user.type(screen.getByLabelText('Name *'), mockFormData.name);
    await user.type(screen.getByLabelText('Email *'), mockFormData.email);
    await user.type(screen.getByLabelText('Subject *'), mockFormData.subject);
    await user.type(screen.getByLabelText('Message *'), mockFormData.message);
    
    // Submit form
    const submitButton = screen.getByRole('button', { name: 'Send Message' });
    await user.click(submitButton);
    
    // Check loading state
    expect(screen.getByText('Sending...')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
    
    // Wait for success message
    await waitFor(() => {
      expect(screen.getByText(/Thank you for your message/)).toBeInTheDocument();
    });
    
    // Check API call
    expect(mockedAxios.post).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/contact/messages/',
      mockFormData
    );

    // Check form is reset
    expect(screen.getByLabelText('Name *')).toHaveValue('');
    expect(screen.getByLabelText('Email *')).toHaveValue('');
    expect(screen.getByLabelText('Subject *')).toHaveValue('');
    expect(screen.getByLabelText('Message *')).toHaveValue('');
  });

    it('handles form submission error and shows error message', async () => {
      const user = userEvent.setup();
      mockedAxios.post.mockRejectedValueOnce(new Error('Network error'));
      
      render(<Contact />);
      
      // Fill out form
      await user.type(screen.getByLabelText('Name *'), mockFormData.name);
      await user.type(screen.getByLabelText('Email *'), mockFormData.email);
      await user.type(screen.getByLabelText('Subject *'), mockFormData.subject);
      await user.type(screen.getByLabelText('Message *'), mockFormData.message);
      
      // Submit form
      const submitButton = screen.getByRole('button', { name: 'Send Message' });
      await user.click(submitButton);
      
      // Wait for error message
      await waitFor(() => {
        expect(screen.getByText(/Sorry, there was an error/)).toBeInTheDocument();
      });
      
      // Check button is re-enabled
      expect(submitButton).not.toBeDisabled();
      expect(screen.getByText('Send Message')).toBeInTheDocument();
    });

    it('prevents multiple submissions while request is in progress', async () => {
      const user = userEvent.setup();
      mockedAxios.post.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));
      
      render(<Contact />);
      
      // Fill out form
      await user.type(screen.getByLabelText('Name *'), mockFormData.name);
      await user.type(screen.getByLabelText('Email *'), mockFormData.email);
      await user.type(screen.getByLabelText('Subject *'), mockFormData.subject);
      await user.type(screen.getByLabelText('Message *'), mockFormData.message);
      
      // Submit form
      const submitButton = screen.getByRole('button', { name: 'Send Message' });
      await user.click(submitButton);
      
      // Button should be disabled
      expect(submitButton).toBeDisabled();
      expect(screen.getByText('Sending...')).toBeInTheDocument();
      
      // Try to click again
      await user.click(submitButton);
      
      // Should only be called once
      expect(mockedAxios.post).toHaveBeenCalledTimes(1);
    });
  });

  describe('Accessibility', () => {
    it('has proper form labels and ARIA attributes', () => {
      render(<Contact />);
      
      // Check form labels
      expect(screen.getByLabelText('Name *')).toBeInTheDocument();
      expect(screen.getByLabelText('Email *')).toBeInTheDocument();
      expect(screen.getByLabelText('Subject *')).toBeInTheDocument();
      expect(screen.getByLabelText('Message *')).toBeInTheDocument();
      
      // Check social links have aria-labels
      expect(screen.getByLabelText('LinkedIn')).toBeInTheDocument();
      expect(screen.getByLabelText('GitHub')).toBeInTheDocument();
      expect(screen.getByLabelText('Twitter')).toBeInTheDocument();
    });

    it('has proper heading hierarchy', () => {
      render(<Contact />);
      
      const h1 = screen.getByRole('heading', { level: 1 });
      const h2Elements = screen.getAllByRole('heading', { level: 2 });
      const h3Elements = screen.getAllByRole('heading', { level: 3 });
      
      expect(h1).toHaveTextContent('Get In Touch');
      expect(h2Elements).toHaveLength(2); // "Let's Connect" and "Send Me a Message"
      expect(h3Elements.length).toBeGreaterThan(0); // Contact method headings
    });

    it('has proper form structure and semantics', () => {
      render(<Contact />);
      
      const form = document.querySelector('form');
      expect(form).toBeInTheDocument();
      
      const submitButton = screen.getByRole('button', { type: 'submit' });
      expect(submitButton).toBeInTheDocument();
    });
  });

  describe('CSS Classes and Structure', () => {
    it('applies correct CSS classes to main sections', () => {
      const { container } = render(<Contact />);
      
      expect(container.querySelector('.contact')).toBeInTheDocument();
      expect(container.querySelector('.contact-hero')).toBeInTheDocument();
      expect(container.querySelector('.contact-content')).toBeInTheDocument();
      expect(container.querySelector('.contact-grid')).toBeInTheDocument();
      expect(container.querySelector('.contact-info')).toBeInTheDocument();
      expect(container.querySelector('.contact-form-container')).toBeInTheDocument();
    });

    it('applies correct CSS classes to form elements', () => {
      const { container } = render(<Contact />);
      
      expect(container.querySelector('.contact-form')).toBeInTheDocument();
      expect(container.querySelectorAll('.form-group')).toHaveLength(4);
      expect(container.querySelector('.submit-btn')).toBeInTheDocument();
    });

    it('applies correct CSS classes to contact methods', () => {
      const { container } = render(<Contact />);
      
      expect(container.querySelector('.contact-methods')).toBeInTheDocument();
      expect(container.querySelectorAll('.contact-method')).toHaveLength(3);
      expect(container.querySelectorAll('.method-icon')).toHaveLength(3);
      expect(container.querySelectorAll('.method-content')).toHaveLength(3);
    });

    it('applies correct CSS classes to social links', () => {
      const { container } = render(<Contact />);
      
      expect(container.querySelector('.social-links')).toBeInTheDocument();
      expect(container.querySelector('.social-icons')).toBeInTheDocument();
      expect(container.querySelectorAll('.social-link')).toHaveLength(3);
    });
  });

  describe('Alert Messages', () => {
    it('shows and hides success alert correctly', async () => {
      const user = userEvent.setup();
      mockedAxios.post.mockResolvedValueOnce({ data: { success: true } });
      
      render(<Contact />);
      
      // Initially no alert
      expect(screen.queryByText(/Thank you for your message/)).not.toBeInTheDocument();
      
      // Fill and submit form
      await user.type(screen.getByLabelText('Name *'), 'John Doe');
      await user.type(screen.getByLabelText('Email *'), 'john@example.com');
      await user.type(screen.getByLabelText('Subject *'), 'Test');
      await user.type(screen.getByLabelText('Message *'), 'Test message');
      
      await user.click(screen.getByRole('button', { name: 'Send Message' }));
      
      // Success alert should appear
      await waitFor(() => {
        expect(screen.getByText(/Thank you for your message/)).toBeInTheDocument();
      });
      
      // Check alert has correct CSS class
      const alert = screen.getByText(/Thank you for your message/).closest('.alert');
      expect(alert).toHaveClass('alert-success');
    });

    it('shows error alert with correct styling', async () => {
      const user = userEvent.setup();
      mockedAxios.post.mockRejectedValueOnce(new Error('Network error'));
      
      render(<Contact />);
      
      // Fill and submit form
      await user.type(screen.getByLabelText('Name *'), 'John Doe');
      await user.type(screen.getByLabelText('Email *'), 'john@example.com');
      await user.type(screen.getByLabelText('Subject *'), 'Test');
      await user.type(screen.getByLabelText('Message *'), 'Test message');
      
      await user.click(screen.getByRole('button', { name: 'Send Message' }));
      
      // Error alert should appear
      await waitFor(() => {
        expect(screen.getByText(/Sorry, there was an error/)).toBeInTheDocument();
      });
      
      // Check alert has correct CSS class
      const alert = screen.getByText(/Sorry, there was an error/).closest('.alert');
      expect(alert).toHaveClass('alert-error');
    });
  });
});