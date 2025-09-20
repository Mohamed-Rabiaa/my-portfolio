"""
Portfolio application models for showcasing skills, projects, and work experience.

This module defines the core data models for the portfolio functionality:
- Skills with categorization and proficiency levels
- Projects with detailed descriptions, technologies, and media
- Project image galleries for visual presentation
- Automatic slug generation and ordering capabilities
"""

from django.db import models
from django.utils.text import slugify


class Skill(models.Model):
    """
    Model representing technical skills and competencies.
    
    Stores information about various technical skills with categorization
    and proficiency levels. Used to showcase expertise areas and create
    skill-based filtering for projects and content.
    
    Attributes:
        name (CharField): The skill name (e.g., "Python", "React", "PostgreSQL")
        category (CharField): Skill category with predefined choices:
            - frontend: Frontend development technologies
            - backend: Backend development technologies  
            - database: Database and data storage technologies
            - tools: Development tools and other technologies
        proficiency (IntegerField): Skill level with choices:
            - 1: Beginner
            - 2: Intermediate
            - 3: Advanced
            - 4: Expert
        created_at (DateTimeField): Timestamp when skill was added
    
    Meta:
        ordering: Ordered by category, then by name alphabetically
    """
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=[
        ('frontend', 'Frontend'),
        ('backend', 'Backend'),
        ('database', 'Database'),
        ('tools', 'Tools & Others'),
    ])
    proficiency = models.IntegerField(choices=[
        (1, 'Beginner'),
        (2, 'Intermediate'),
        (3, 'Advanced'),
        (4, 'Expert'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        """
        String representation showing skill name and category.
        
        Returns:
            str: Formatted string like "Python (Backend)" or "React (Frontend)"
        """
        return f"{self.name} ({self.get_category_display()})"


class Project(models.Model):
    """
    Model representing portfolio projects and work samples.
    
    Stores comprehensive information about projects including descriptions,
    technologies used, links, and media. Supports featured projects for
    highlighting important work and automatic slug generation for SEO-friendly URLs.
    
    Attributes:
        title (CharField): Project title/name
        slug (SlugField): URL-friendly identifier, auto-generated from title
        description (TextField): Brief project description for listings
        detailed_description (TextField): Comprehensive project details
        technologies (ManyToManyField): Skills/technologies used in the project
        github_url (URLField): Link to project's GitHub repository
        live_url (URLField): Link to live/deployed project
        image (ImageField): Main project screenshot or image
        featured (BooleanField): Whether project should be highlighted
        created_at (DateTimeField): Project creation timestamp
        updated_at (DateTimeField): Last modification timestamp
    
    Meta:
        ordering: Featured projects first, then by creation date (newest first)
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    detailed_description = models.TextField(blank=True)
    technologies = models.ManyToManyField(Skill, related_name='projects')
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-featured', '-created_at']

    def save(self, *args, **kwargs):
        """
        Override save method to automatically generate slug from title.
        
        Creates a URL-friendly slug from the project title if one doesn't
        already exist. This ensures SEO-friendly URLs and consistent
        project identification.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        """
        String representation of the project.
        
        Returns:
            str: The project title
        """
        return self.title


class ProjectImage(models.Model):
    """
    Model for additional project images and gallery functionality.
    
    Allows projects to have multiple images beyond the main project image,
    creating gallery functionality for showcasing different aspects of
    the project. Supports ordering and captions for better presentation.
    
    Attributes:
        project (ForeignKey): Reference to the associated Project
        image (ImageField): The additional project image
        caption (CharField): Optional caption describing the image
        order (PositiveIntegerField): Display order for image sorting
    
    Meta:
        ordering: Ordered by the 'order' field for consistent display
    
    Related name 'additional_images' allows accessing from Project model
    as project.additional_images.all()
    """
    project = models.ForeignKey(Project, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='projects/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        """
        String representation showing project and image order.
        
        Returns:
            str: Formatted string like "My Project - Image 1"
        """
        return f"{self.project.title} - Image {self.order}"
