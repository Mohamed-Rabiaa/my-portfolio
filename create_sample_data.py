#!/usr/bin/env python
"""
Sample Data Creation Script for MyPortfolio Project

This utility script creates comprehensive sample data for the MyPortfolio project,
populating all models with realistic content for development and testing purposes.
The script creates a complete portfolio ecosystem including skills, projects, blog
content, and contact information.

Features:
- Creates admin user with default credentials
- Populates portfolio skills across different categories
- Generates sample projects with technologies and descriptions
- Creates blog categories, tags, and detailed blog posts
- Adds sample comments to blog posts
- Generates contact messages and newsletter subscriptions
- Provides comprehensive summary of created data

Usage:
    python create_sample_data.py

Requirements:
- Django environment must be properly configured
- All models must be migrated before running
- Script should be run from the project root directory

Data Created:
- Admin user (username: admin, password: admin123)
- 8 skills across backend, frontend, database, and tools categories
- 4 sample projects with realistic descriptions and technology stacks
- 5 blog categories covering web development topics
- 13 blog tags for content organization
- 3 detailed blog posts with markdown content
- Sample comments for blog engagement
- Contact messages demonstrating different inquiry types
- Newsletter subscriptions for testing email functionality

Security Note:
This script is intended for development use only. The default admin
credentials should be changed in production environments.

Run this script with: python create_sample_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myportfolio.settings')
django.setup()

from django.contrib.auth.models import User
from portfolio.models import Skill, Project, ProjectImage
from blog.models import Category, Tag, BlogPost, Comment
from contact.models import ContactMessage, Newsletter

def create_sample_data():
    """
    Main function to create comprehensive sample data for the portfolio project.
    
    This function orchestrates the creation of all sample data including users,
    portfolio content, blog posts, and contact information. It uses get_or_create
    methods to avoid duplicating data on multiple runs.
    
    The function creates data in a logical order to handle foreign key relationships:
    1. Admin user for content authorship
    2. Skills for project technologies
    3. Projects with technology associations
    4. Blog categories and tags
    5. Blog posts with category and tag relationships
    6. Comments for blog engagement
    7. Contact messages and newsletter subscriptions
    
    Returns:
        None: Prints progress and summary information to console
        
    Raises:
        Django database errors if models are not properly migrated
        or if there are constraint violations
    """
    
    # Create or get admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
    
    # Create Skills
    skills_data = [
        {'name': 'Python', 'category': 'backend', 'proficiency': 4},
        {'name': 'Django', 'category': 'backend', 'proficiency': 4},
        {'name': 'React', 'category': 'frontend', 'proficiency': 3},
        {'name': 'JavaScript', 'category': 'frontend', 'proficiency': 4},
        {'name': 'PostgreSQL', 'category': 'database', 'proficiency': 3},
        {'name': 'Docker', 'category': 'tools', 'proficiency': 3},
        {'name': 'Git', 'category': 'tools', 'proficiency': 4},
        {'name': 'HTML/CSS', 'category': 'frontend', 'proficiency': 4},
    ]
    
    for skill_data in skills_data:
        skill, created = Skill.objects.get_or_create(
            name=skill_data['name'],
            defaults=skill_data
        )
        if created:
            print(f"Created skill: {skill.name}")
    
    # Create Projects
    projects_data = [
        {
            'title': 'E-commerce Platform',
            'description': 'A full-stack e-commerce platform built with Django and React. Features include user authentication, product catalog, shopping cart, and payment integration.',
            'detailed_description': 'This comprehensive e-commerce platform demonstrates modern web development practices with a Django REST API backend and React frontend. The platform includes user registration and authentication, product management, shopping cart functionality, order processing, and secure payment integration using Stripe.',
            'github_url': 'https://github.com/example/ecommerce-platform',
            'live_url': 'https://ecommerce-demo.example.com',
            'featured': True,
        },
        {
            'title': 'Task Management App',
            'description': 'A collaborative task management application with real-time updates, team collaboration features, and project tracking.',
            'detailed_description': 'Built with Django Channels for WebSocket support, this task management app allows teams to collaborate in real-time. Features include project creation, task assignment, progress tracking, file attachments, and real-time notifications.',
            'github_url': 'https://github.com/example/task-manager',
            'live_url': 'https://taskmanager-demo.example.com',
            'featured': True,
        },
        {
            'title': 'Weather Dashboard',
            'description': 'A responsive weather dashboard that displays current weather conditions and forecasts for multiple cities.',
            'detailed_description': 'This weather dashboard integrates with multiple weather APIs to provide accurate weather information. Built with React and styled with Tailwind CSS, it features location-based weather, 7-day forecasts, weather maps, and customizable dashboard widgets.',
            'github_url': 'https://github.com/example/weather-dashboard',
            'live_url': 'https://weather-demo.example.com',
            'featured': False,
        },
        {
            'title': 'Portfolio Website',
            'description': 'This very portfolio website built with Django REST Framework and React.',
            'detailed_description': 'A modern portfolio website showcasing projects, skills, and blog posts. Built with Django REST Framework for the backend API and React with Tailwind CSS for the frontend. Features include project showcase, blog functionality, contact forms, and admin panel.',
            'github_url': 'https://github.com/example/portfolio',
            'live_url': 'https://portfolio.example.com',
            'featured': True,
        },
    ]
    
    for project_data in projects_data:
        project, created = Project.objects.get_or_create(
            title=project_data['title'],
            defaults=project_data
        )
        if created:
            print(f"Created project: {project.title}")
            
            # Add technologies to projects
            if project.title == 'E-commerce Platform':
                technologies = Skill.objects.filter(name__in=['Python', 'Django', 'React', 'PostgreSQL'])
                project.technologies.set(technologies)
            elif project.title == 'Task Management App':
                technologies = Skill.objects.filter(name__in=['Python', 'Django', 'JavaScript', 'PostgreSQL'])
                project.technologies.set(technologies)
            elif project.title == 'Weather Dashboard':
                technologies = Skill.objects.filter(name__in=['React', 'JavaScript', 'HTML/CSS'])
                project.technologies.set(technologies)
            elif project.title == 'Portfolio Website':
                technologies = Skill.objects.filter(name__in=['Python', 'Django', 'React', 'HTML/CSS'])
                project.technologies.set(technologies)
    
    # Create Blog Categories
    categories_data = [
        {'name': 'Web Development', 'description': 'Articles about web development technologies and practices'},
        {'name': 'Python', 'description': 'Python programming tutorials and tips'},
        {'name': 'React', 'description': 'React.js tutorials and best practices'},
        {'name': 'DevOps', 'description': 'DevOps tools and deployment strategies'},
        {'name': 'Career', 'description': 'Career advice and professional development'},
    ]
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"Created category: {category.name}")
    
    # Create Blog Tags
    tags_data = [
        'django', 'react', 'python', 'javascript', 'tutorial', 'tips', 'best-practices',
        'deployment', 'database', 'api', 'frontend', 'backend', 'full-stack'
    ]
    
    for tag_name in tags_data:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        if created:
            print(f"Created tag: {tag.name}")
    
    # Create Blog Posts
    posts_data = [
        {
            'title': 'Building RESTful APIs with Django REST Framework',
            'excerpt': 'Learn how to build robust and scalable APIs using Django REST Framework with practical examples and best practices.',
            'content': '''
# Building RESTful APIs with Django REST Framework

Django REST Framework (DRF) is a powerful toolkit for building Web APIs in Django. In this tutorial, we'll explore how to create robust and scalable APIs.

## Getting Started

First, install Django REST Framework:

```bash
pip install djangorestframework
```

## Creating Your First API

Let's start by creating a simple API for a blog application:

```python
from rest_framework import serializers, viewsets
from .models import BlogPost

class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = '__all__'

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
```

## Best Practices

1. Use proper HTTP status codes
2. Implement pagination for large datasets
3. Add proper authentication and permissions
4. Use serializers for data validation
5. Document your API with tools like Swagger

This is just the beginning of what you can achieve with DRF!
            ''',
            'category': 'Web Development',
            'author': admin_user,
            'status': 'published',
            'featured': True,
            'published_at': timezone.now() - timedelta(days=7),
            'tags': ['django', 'api', 'tutorial', 'backend']
        },
        {
            'title': 'React Hooks: A Complete Guide',
            'excerpt': 'Master React Hooks with practical examples and learn how to build more efficient functional components.',
            'content': '''
# React Hooks: A Complete Guide

React Hooks revolutionized how we write React components. Let's dive deep into the most commonly used hooks.

## useState Hook

The useState hook allows you to add state to functional components:

```javascript
import React, { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}
```

## useEffect Hook

The useEffect hook lets you perform side effects in functional components:

```javascript
import React, { useState, useEffect } from 'react';

function Example() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    document.title = `You clicked ${count} times`;
  });

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}
```

## Custom Hooks

You can also create your own hooks to reuse stateful logic between components.

Hooks make React code more reusable and easier to test!
            ''',
            'category': 'React',
            'author': admin_user,
            'status': 'published',
            'featured': True,
            'published_at': timezone.now() - timedelta(days=14),
            'tags': ['react', 'javascript', 'tutorial', 'frontend']
        },
        {
            'title': 'Python Best Practices for Clean Code',
            'excerpt': 'Essential Python coding practices for writing clean, maintainable, and professional code.',
            'content': '''
# Python Best Practices for Clean Code

Writing clean, maintainable Python code is essential for any developer. Here are some best practices to follow.

## PEP 8 Style Guide

Always follow PEP 8 for consistent code formatting:

```python
# Good
def calculate_total_price(items, tax_rate):
    subtotal = sum(item.price for item in items)
    tax = subtotal * tax_rate
    return subtotal + tax

# Bad
def calculateTotalPrice(items,tax_rate):
    subtotal=sum(item.price for item in items)
    tax=subtotal*tax_rate
    return subtotal+tax
```

## Use Type Hints

Type hints make your code more readable and help catch errors:

```python
from typing import List, Optional

def process_items(items: List[str], max_length: Optional[int] = None) -> List[str]:
    if max_length is None:
        return items
    return [item for item in items if len(item) <= max_length]
```

## Write Docstrings

Document your functions and classes:

```python
def fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number.
    
    Args:
        n: The position in the Fibonacci sequence
        
    Returns:
        The nth Fibonacci number
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

Following these practices will make your Python code more professional and maintainable!
            ''',
            'category': 'Python',
            'author': admin_user,
            'status': 'published',
            'featured': False,
            'published_at': timezone.now() - timedelta(days=21),
            'tags': ['python', 'best-practices', 'tutorial']
        },
        {
            'title': 'Deploying Django Applications with Docker',
            'excerpt': 'Learn how to containerize and deploy Django applications using Docker for consistent deployments.',
            'content': '''
# Deploying Django Applications with Docker

Docker makes it easy to deploy Django applications consistently across different environments.

## Creating a Dockerfile

Here's a basic Dockerfile for a Django application:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## Docker Compose for Development

Use docker-compose.yml for local development:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    depends_on:
      - db
    environment:
      - DEBUG=1
      - DATABASE_URL=postgresql://user:password@db:5432/mydb

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Production Considerations

For production deployments:

1. Use multi-stage builds to reduce image size
2. Run as non-root user
3. Use environment variables for configuration
4. Implement health checks
5. Use a reverse proxy like Nginx

Docker simplifies deployment and ensures consistency across environments!
            ''',
            'category': 'DevOps',
            'author': admin_user,
            'status': 'published',
            'featured': False,
            'published_at': timezone.now() - timedelta(days=28),
            'tags': ['django', 'docker', 'deployment', 'devops']
        },
    ]
    
    for post_data in posts_data:
        category = Category.objects.get(name=post_data['category'])
        tags = post_data.pop('tags')
        
        post, created = BlogPost.objects.get_or_create(
            title=post_data['title'],
            defaults={**post_data, 'category': category}
        )
        
        if created:
            print(f"Created blog post: {post.title}")
            # Add tags
            for tag_name in tags:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)
    
    # Create comments
    comments_data = [
        {
            'post': 'Building RESTful APIs with Django REST Framework',
            'name': 'John Developer',
            'email': 'john@example.com',
            'content': 'Great tutorial! This helped me understand DRF much better.',
            'approved': True,
        },
        {
            'post': 'React Hooks: A Complete Guide',
            'name': 'Sarah Frontend',
            'email': 'sarah@example.com',
            'content': 'Excellent explanation of hooks. The examples are very clear.',
            'approved': True,
        },
        {
            'post': 'Python Best Practices for Clean Code',
            'name': 'Mike Pythonista',
            'email': 'mike@example.com',
            'content': 'These practices have really improved my code quality. Thanks!',
            'approved': True,
        },
    ]

    for comment_data in comments_data:
        post_title = comment_data.pop('post')
        post = BlogPost.objects.get(title=post_title)
        Comment.objects.get_or_create(
            post=post,
            name=comment_data['name'],
            email=comment_data['email'],
            defaults=comment_data
        )
    
    # Create sample contact messages
    ContactMessage.objects.get_or_create(
        email='client@example.com',
        defaults={
            'name': 'Potential Client',
            'subject': 'Project Inquiry',
            'message': 'Hi, I\'m interested in discussing a web development project. Could we schedule a call?',
            'status': 'new'
        }
    )
    
    ContactMessage.objects.get_or_create(
        email='recruiter@company.com',
        defaults={
            'name': 'Tech Recruiter',
            'subject': 'Job Opportunity',
            'message': 'We have an exciting opportunity that might interest you. Please let me know if you\'re open to discussing it.',
            'status': 'read'
        }
    )
    
    # Create sample newsletter subscriptions
    Newsletter.objects.get_or_create(
        email='subscriber1@example.com',
        defaults={
            'name': 'Tech Enthusiast',
            'is_active': True
        }
    )
    
    Newsletter.objects.get_or_create(
        email='subscriber2@example.com',
        defaults={
            'name': 'Web Developer',
            'is_active': True
        }
    )
    
    print("Sample data created successfully!")
    print("\nSummary:")
    print(f"- Skills: {Skill.objects.count()}")
    print(f"- Projects: {Project.objects.count()}")
    print(f"- Blog Categories: {Category.objects.count()}")
    print(f"- Blog Tags: {Tag.objects.count()}")
    print(f"- Blog Posts: {BlogPost.objects.count()}")
    print(f"- Comments: {Comment.objects.count()}")
    print(f"- Contact Messages: {ContactMessage.objects.count()}")
    print(f"- Newsletter Subscriptions: {Newsletter.objects.count()}")
    print("\nAdmin credentials:")
    print("Username: admin")
    print("Password: admin123")

if __name__ == '__main__':
    create_sample_data()