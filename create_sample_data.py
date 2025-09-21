#!/usr/bin/env python
"""
Sample Data Creation Script

This module provides functionality to create sample data for the portfolio application.
It generates realistic test data for blog posts, projects, contact messages, and newsletter
subscriptions to facilitate development, testing, and demonstration purposes.

The script uses Django's ORM to create database entries with realistic content,
including proper relationships between models and varied data types.

Functions:
    create_sample_blog_posts: Creates sample blog posts with varied content
    create_sample_projects: Creates sample portfolio projects
    create_sample_contact_messages: Creates sample contact form submissions
    create_sample_newsletter_subscriptions: Creates sample newsletter subscribers
    main: Main function that orchestrates the sample data creation process

Usage:
    python create_sample_data.py

Requirements:
    - Django environment must be properly configured
    - All required models must be available and migrated
    - Faker library for generating realistic fake data

Author: Your Name
Version: 1.0.0
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
from faker import Faker

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')
django.setup()

# Import models after Django setup
from blog.models import BlogPost, Category, Tag
from portfolio.models import Project, Technology
from contact.models import ContactMessage, Newsletter

# Initialize Faker for generating realistic fake data
fake = Faker()


def create_sample_blog_posts(count=10):
    """
    Create sample blog posts with realistic content and metadata.
    
    Generates blog posts with varied titles, content, categories, tags,
    and publication dates. Each post includes proper SEO metadata and
    realistic engagement metrics.
    
    Args:
        count (int): Number of blog posts to create. Defaults to 10.
        
    Returns:
        list: List of created BlogPost instances
        
    Raises:
        Exception: If there's an error creating blog posts or related objects
        
    Example:
        >>> posts = create_sample_blog_posts(5)
        >>> print(f"Created {len(posts)} blog posts")
    """
    print(f"Creating {count} sample blog posts...")
    
    # Sample categories for blog posts
    categories_data = [
        {'name': 'Web Development', 'slug': 'web-development'},
        {'name': 'Mobile Development', 'slug': 'mobile-development'},
        {'name': 'Data Science', 'slug': 'data-science'},
        {'name': 'Machine Learning', 'slug': 'machine-learning'},
        {'name': 'DevOps', 'slug': 'devops'},
        {'name': 'UI/UX Design', 'slug': 'ui-ux-design'},
    ]
    
    # Sample tags for blog posts
    tags_data = [
        'Python', 'JavaScript', 'React', 'Django', 'Node.js', 'Vue.js',
        'Angular', 'TypeScript', 'Docker', 'Kubernetes', 'AWS', 'Azure',
        'Machine Learning', 'AI', 'Data Analysis', 'PostgreSQL', 'MongoDB'
    ]
    
    # Create categories if they don't exist
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'slug': cat_data['slug']}
        )
        categories.append(category)
    
    # Create tags if they don't exist
    tags = []
    for tag_name in tags_data:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        tags.append(tag)
    
    posts = []
    for i in range(count):
        # Generate realistic blog post data
        title = fake.sentence(nb_words=6).rstrip('.')
        content = fake.text(max_nb_chars=2000)
        excerpt = fake.text(max_nb_chars=200)
        
        # Create blog post
        post = BlogPost.objects.create(
            title=title,
            slug=fake.slug(),
            content=content,
            excerpt=excerpt,
            author=fake.name(),
            category=fake.random_element(categories),
            featured_image=f"blog/sample-{i+1}.jpg",
            is_published=fake.boolean(chance_of_getting_true=80),
            published_at=fake.date_time_between(
                start_date='-1y', 
                end_date='now', 
                tzinfo=timezone.get_current_timezone()
            ),
            views_count=fake.random_int(min=10, max=1000),
            reading_time=fake.random_int(min=2, max=15),
            meta_description=fake.text(max_nb_chars=160),
            meta_keywords=', '.join(fake.words(nb=5))
        )
        
        # Add random tags to the post
        post_tags = fake.random_elements(tags, length=fake.random_int(min=2, max=5), unique=True)
        post.tags.set(post_tags)
        
        posts.append(post)
        print(f"  Created blog post: {post.title}")
    
    return posts


def create_sample_projects(count=8):
    """
    Create sample portfolio projects with realistic details and technologies.
    
    Generates portfolio projects with varied titles, descriptions, technologies,
    and project metadata including GitHub links, live demos, and project status.
    
    Args:
        count (int): Number of projects to create. Defaults to 8.
        
    Returns:
        list: List of created Project instances
        
    Raises:
        Exception: If there's an error creating projects or related objects
        
    Example:
        >>> projects = create_sample_projects(6)
        >>> print(f"Created {len(projects)} portfolio projects")
    """
    print(f"Creating {count} sample projects...")
    
    # Sample technologies for projects
    technologies_data = [
        {'name': 'Python', 'category': 'Backend'},
        {'name': 'JavaScript', 'category': 'Frontend'},
        {'name': 'React', 'category': 'Frontend'},
        {'name': 'Django', 'category': 'Backend'},
        {'name': 'Node.js', 'category': 'Backend'},
        {'name': 'PostgreSQL', 'category': 'Database'},
        {'name': 'MongoDB', 'category': 'Database'},
        {'name': 'Docker', 'category': 'DevOps'},
        {'name': 'AWS', 'category': 'Cloud'},
        {'name': 'Vue.js', 'category': 'Frontend'},
    ]
    
    # Create technologies if they don't exist
    technologies = []
    for tech_data in technologies_data:
        technology, created = Technology.objects.get_or_create(
            name=tech_data['name'],
            defaults={'category': tech_data['category']}
        )
        technologies.append(technology)
    
    # Sample project types and descriptions
    project_types = [
        'E-commerce Platform', 'Social Media App', 'Task Management Tool',
        'Blog Platform', 'Portfolio Website', 'API Service', 'Mobile App',
        'Data Dashboard', 'Chat Application', 'Learning Management System'
    ]
    
    projects = []
    for i in range(count):
        # Generate realistic project data
        project_type = fake.random_element(project_types)
        title = f"{fake.company()} {project_type}"
        description = fake.text(max_nb_chars=500)
        
        # Create project
        project = Project.objects.create(
            title=title,
            slug=fake.slug(),
            description=description,
            short_description=fake.text(max_nb_chars=150),
            image=f"projects/sample-project-{i+1}.jpg",
            github_url=f"https://github.com/{fake.user_name()}/{fake.slug()}",
            live_url=f"https://{fake.slug()}.{fake.random_element(['com', 'net', 'org'])}",
            status=fake.random_element(['completed', 'in_progress', 'planning']),
            featured=fake.boolean(chance_of_getting_true=30),
            start_date=fake.date_between(start_date='-2y', end_date='-6m'),
            end_date=fake.date_between(start_date='-6m', end_date='today') if fake.boolean() else None,
            client=fake.company() if fake.boolean(chance_of_getting_true=40) else None,
            order=i + 1
        )
        
        # Add random technologies to the project
        project_technologies = fake.random_elements(
            technologies, 
            length=fake.random_int(min=3, max=6), 
            unique=True
        )
        project.technologies.set(project_technologies)
        
        projects.append(project)
        print(f"  Created project: {project.title}")
    
    return projects


def create_sample_contact_messages(count=15):
    """
    Create sample contact form messages with realistic inquiries.
    
    Generates contact messages with varied subjects, content, and sender
    information to simulate real user inquiries and feedback.
    
    Args:
        count (int): Number of contact messages to create. Defaults to 15.
        
    Returns:
        list: List of created ContactMessage instances
        
    Raises:
        Exception: If there's an error creating contact messages
        
    Example:
        >>> messages = create_sample_contact_messages(10)
        >>> print(f"Created {len(messages)} contact messages")
    """
    print(f"Creating {count} sample contact messages...")
    
    # Sample subjects for contact messages
    subjects = [
        'project_inquiry', 'collaboration', 'job_opportunity', 
        'consultation', 'feedback', 'support', 'other'
    ]
    
    # Sample message templates for different subjects
    message_templates = {
        'project_inquiry': "I'm interested in discussing a potential project with you. Could we schedule a call?",
        'collaboration': "I'd love to collaborate on an upcoming project. Are you available for partnerships?",
        'job_opportunity': "We have an exciting job opportunity that might interest you. Would you like to learn more?",
        'consultation': "I need some technical consultation for my project. What are your rates?",
        'feedback': "I really enjoyed your recent blog post about {}. Great insights!",
        'support': "I'm having some issues with implementing the solution from your tutorial. Could you help?",
        'other': "I have a question about your work and would appreciate your thoughts."
    }
    
    messages = []
    for i in range(count):
        # Generate realistic contact data
        subject = fake.random_element(subjects)
        name = fake.name()
        email = fake.email()
        phone = fake.phone_number() if fake.boolean(chance_of_getting_true=60) else None
        company = fake.company() if fake.boolean(chance_of_getting_true=40) else None
        
        # Generate message based on subject
        base_message = message_templates.get(subject, fake.text(max_nb_chars=300))
        if '{}' in base_message:
            base_message = base_message.format(fake.word())
        
        message_content = f"{base_message}\n\n{fake.text(max_nb_chars=200)}"
        
        # Create contact message
        message = ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            company=company,
            subject=subject,
            message=message_content,
            status=fake.random_element(['unread', 'read', 'replied', 'archived']),
            ip_address=fake.ipv4(),
            user_agent=fake.user_agent(),
            created_at=fake.date_time_between(
                start_date='-3m', 
                end_date='now', 
                tzinfo=timezone.get_current_timezone()
            )
        )
        
        messages.append(message)
        print(f"  Created contact message from: {message.name}")
    
    return messages


def create_sample_newsletter_subscriptions(count=25):
    """
    Create sample newsletter subscriptions with realistic subscriber data.
    
    Generates newsletter subscriptions with varied email addresses and names
    to simulate a realistic subscriber base for testing email campaigns.
    
    Args:
        count (int): Number of newsletter subscriptions to create. Defaults to 25.
        
    Returns:
        list: List of created Newsletter instances
        
    Raises:
        Exception: If there's an error creating newsletter subscriptions
        
    Example:
        >>> subscriptions = create_sample_newsletter_subscriptions(20)
        >>> print(f"Created {len(subscriptions)} newsletter subscriptions")
    """
    print(f"Creating {count} sample newsletter subscriptions...")
    
    subscriptions = []
    for i in range(count):
        # Generate realistic subscriber data
        name = fake.name() if fake.boolean(chance_of_getting_true=70) else None
        email = fake.email()
        
        # Ensure unique email addresses
        while Newsletter.objects.filter(email=email).exists():
            email = fake.email()
        
        # Create newsletter subscription
        subscription = Newsletter.objects.create(
            email=email,
            name=name,
            is_active=fake.boolean(chance_of_getting_true=85),
            ip_address=fake.ipv4(),
            subscribed_at=fake.date_time_between(
                start_date='-6m', 
                end_date='now', 
                tzinfo=timezone.get_current_timezone()
            )
        )
        
        subscriptions.append(subscription)
        print(f"  Created newsletter subscription: {subscription.email}")
    
    return subscriptions


def main():
    """
    Main function that orchestrates the sample data creation process.
    
    Executes all sample data creation functions in the proper order,
    handles any errors that occur during the process, and provides
    a summary of the created data.
    
    The function creates:
    - Blog posts with categories and tags
    - Portfolio projects with technologies
    - Contact messages with varied inquiries
    - Newsletter subscriptions
    
    Returns:
        dict: Summary of created objects with counts for each type
        
    Raises:
        Exception: If there's a critical error during data creation
        
    Example:
        >>> summary = main()
        >>> print(f"Created {summary['total']} total objects")
    """
    print("=" * 50)
    print("CREATING SAMPLE DATA FOR PORTFOLIO APPLICATION")
    print("=" * 50)
    
    summary = {
        'blog_posts': 0,
        'projects': 0,
        'contact_messages': 0,
        'newsletter_subscriptions': 0,
        'total': 0
    }
    
    try:
        # Create sample blog posts
        blog_posts = create_sample_blog_posts(10)
        summary['blog_posts'] = len(blog_posts)
        print(f"✓ Created {len(blog_posts)} blog posts")
        
        # Create sample projects
        projects = create_sample_projects(8)
        summary['projects'] = len(projects)
        print(f"✓ Created {len(projects)} projects")
        
        # Create sample contact messages
        contact_messages = create_sample_contact_messages(15)
        summary['contact_messages'] = len(contact_messages)
        print(f"✓ Created {len(contact_messages)} contact messages")
        
        # Create sample newsletter subscriptions
        newsletter_subs = create_sample_newsletter_subscriptions(25)
        summary['newsletter_subscriptions'] = len(newsletter_subs)
        print(f"✓ Created {len(newsletter_subs)} newsletter subscriptions")
        
        # Calculate total
        summary['total'] = sum([
            summary['blog_posts'],
            summary['projects'], 
            summary['contact_messages'],
            summary['newsletter_subscriptions']
        ])
        
        print("\n" + "=" * 50)
        print("SAMPLE DATA CREATION COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Total objects created: {summary['total']}")
        print(f"  - Blog posts: {summary['blog_posts']}")
        print(f"  - Projects: {summary['projects']}")
        print(f"  - Contact messages: {summary['contact_messages']}")
        print(f"  - Newsletter subscriptions: {summary['newsletter_subscriptions']}")
        print("=" * 50)
        
        return summary
        
    except Exception as e:
        print(f"\n❌ Error creating sample data: {str(e)}")
        print("Please check your Django configuration and database connection.")
        raise


if __name__ == '__main__':
    """
    Entry point for the script when run directly.
    
    Executes the main function and handles any top-level exceptions
    that might occur during the sample data creation process.
    """
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Sample data creation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)