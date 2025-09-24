"""
Service layer for portfolio functionality.

This module contains business logic for portfolio operations, separating concerns
from views and providing reusable methods for portfolio-related operations.
"""

import logging
import time
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet, Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from .models import Project, Skill, Experience, Education
from common.exceptions import (
    ProjectNotFound,
    ValidationError as CustomValidationError,
    NotFoundError
)
from common.utils import StatusChoices, generate_unique_slug

# Initialize loggers
logger = logging.getLogger('portfolio')
performance_logger = logging.getLogger('performance')


class ProjectService:
    """
    Service class for project operations.
    
    Handles all business logic related to projects including creation,
    retrieval, updates, and filtering.
    """
    
    @staticmethod
    def get_all_projects(featured_only=False):
        """
        Get all projects with optional featured filtering and optimized queries.
        
        Args:
            featured_only: Only return featured projects
            
        Returns:
            QuerySet of projects
        """
        start_time = time.time()
        logger.info(f"Fetching all projects - featured_only: {featured_only}")
        
        try:
            queryset = Project.objects.select_related(
                'category'
            ).prefetch_related(
                'technologies', 'skills'
            )
            
            if featured_only:
                queryset = queryset.filter(featured=True)
                logger.debug("Applied featured filter")
            
            result_count = queryset.count()
            execution_time = time.time() - start_time
            
            logger.info(f"Successfully fetched {result_count} projects")
            performance_logger.info(f"get_all_projects executed in {execution_time:.3f}s, returned {result_count} projects")
            
            return queryset.order_by('-created_at')
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error fetching projects: {str(e)}", exc_info=True)
            performance_logger.info(f"get_all_projects failed in {execution_time:.3f}s")
            raise
    
    @staticmethod
    def get_project_by_slug(slug):
        """
        Get a project by its slug with optimized queries.
        
        Args:
            slug: Project slug
            
        Returns:
            Project instance
            
        Raises:
            ProjectNotFound: If project doesn't exist
        """
        try:
            return Project.objects.select_related(
                'category'
            ).prefetch_related(
                'technologies', 'skills'
            ).get(slug=slug)
        except Project.DoesNotExist:
            raise ProjectNotFound(f"Project with slug '{slug}' not found")
    
    @staticmethod
    def get_featured_projects(limit=6):
        """
        Get featured projects with optimized queries.
        
        Args:
            limit: Number of projects to return
            
        Returns:
            QuerySet of featured projects
        """
        return Project.objects.select_related(
            'category'
        ).prefetch_related(
            'technologies', 'skills'
        ).filter(featured=True).order_by('-created_at')[:limit]
    
    @staticmethod
    def create_project(
        title: str,
        description: str,
        technologies: List[str],
        github_url: Optional[str] = None,
        live_url: Optional[str] = None,
        image=None,
        featured: bool = False
    ) -> Project:
        """
        Create a new project.
        
        Args:
            title: Project title
            description: Project description
            technologies: List of technology names
            github_url: GitHub repository URL
            live_url: Live project URL
            image: Project image
            featured: Whether project is featured
            
        Returns:
            Created project instance
        """
        # Generate unique slug
        slug = generate_unique_slug(title, Project)
        
        project = Project.objects.create(
            title=title,
            slug=slug,
            description=description,
            github_url=github_url,
            live_url=live_url,
            image=image,
            featured=featured
        )
        
        # Add technologies
        if technologies:
            project.technologies.set(technologies)
        
        return project
    
    @staticmethod
    def update_project(project: Project, **kwargs) -> Project:
        """
        Update an existing project.
        
        Args:
            project: Project instance to update
            **kwargs: Fields to update
            
        Returns:
            Updated project instance
        """
        for field, value in kwargs.items():
            if hasattr(project, field):
                setattr(project, field, value)
        
        project.save()
        return project
    
    @staticmethod
    def get_projects_by_technology(technology):
        """
        Get projects filtered by technology with optimized queries.
        
        Args:
            technology: Technology name to filter by
            
        Returns:
            QuerySet of projects using the specified technology
        """
        return Project.objects.select_related(
            'category'
        ).prefetch_related(
            'technologies', 'skills'
        ).filter(
            technologies__name__icontains=technology
        ).distinct().order_by('-created_at')


class SkillService:
    """Service class for skill operations."""
    
    @staticmethod
    def get_all_skills() -> QuerySet[Skill]:
        """Get all skills ordered by category and proficiency."""
        return Skill.objects.all().order_by('category', '-proficiency')
    
    @staticmethod
    def get_skills_by_category(category: str) -> QuerySet[Skill]:
        """
        Get skills filtered by category.
        
        Args:
            category: Skill category
            
        Returns:
            QuerySet of skills in the category
        """
        return Skill.objects.filter(category=category).order_by('-proficiency')
    
    @staticmethod
    def create_skill(
        name: str,
        category: str,
        proficiency: int,
        icon: Optional[str] = None
    ) -> Skill:
        """
        Create a new skill.
        
        Args:
            name: Skill name
            category: Skill category
            proficiency: Proficiency level (1-100)
            icon: Skill icon
            
        Returns:
            Created skill instance
        """
        if not (1 <= proficiency <= 100):
            raise CustomValidationError("Proficiency must be between 1 and 100")
        
        return Skill.objects.create(
            name=name,
            category=category,
            proficiency=proficiency,
            icon=icon
        )


class ExperienceService:
    """Service class for experience operations."""
    
    @staticmethod
    def get_all_experiences() -> QuerySet[Experience]:
        """Get all experiences ordered by start date (most recent first)."""
        return Experience.objects.all().order_by('-start_date')
    
    @staticmethod
    def get_current_experiences() -> QuerySet[Experience]:
        """Get current experiences (where end_date is None)."""
        return Experience.objects.filter(end_date__isnull=True).order_by('-start_date')
    
    @staticmethod
    def create_experience(
        company: str,
        position: str,
        description: str,
        start_date,
        end_date=None,
        location: Optional[str] = None
    ) -> Experience:
        """
        Create a new experience entry.
        
        Args:
            company: Company name
            position: Job position
            description: Job description
            start_date: Start date
            end_date: End date (None for current)
            location: Job location
            
        Returns:
            Created experience instance
        """
        return Experience.objects.create(
            company=company,
            position=position,
            description=description,
            start_date=start_date,
            end_date=end_date,
            location=location
        )


class EducationService:
    """Service class for education operations."""
    
    @staticmethod
    def get_all_education() -> QuerySet[Education]:
        """Get all education entries ordered by start date (most recent first)."""
        return Education.objects.all().order_by('-start_date')
    
    @staticmethod
    def create_education(
        institution: str,
        degree: str,
        field_of_study: str,
        start_date,
        end_date=None,
        gpa: Optional[float] = None,
        description: Optional[str] = None
    ) -> Education:
        """
        Create a new education entry.
        
        Args:
            institution: Educational institution
            degree: Degree obtained
            field_of_study: Field of study
            start_date: Start date
            end_date: End date (None for current)
            gpa: Grade point average
            description: Additional description
            
        Returns:
            Created education instance
        """
        return Education.objects.create(
            institution=institution,
            degree=degree,
            field_of_study=field_of_study,
            start_date=start_date,
            end_date=end_date,
            gpa=gpa,
            description=description
        )