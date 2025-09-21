from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class Category(models.Model):
    """
    A model representing blog post categories.
    
    This class defines categories that can be assigned to blog posts for organization
    and filtering purposes. Each category has a unique name and slug (URL-friendly version
    of the name), an optional description, and tracks when it was created.

    Attributes:
        name (CharField): The category name (max 100 chars, must be unique)
        slug (SlugField): URL-friendly version of the name (auto-generated if not provided)
        description (TextField): Optional detailed description of the category
        created_at (DateTimeField): Timestamp of when the category was created
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        """
        Override save method to handle slug generation.
        
        Generates a slug from the name if no slug is provided.
        For updates, only regenerates slug if it's empty to preserve custom slugs.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Tag(models.Model):
    """
    A model representing blog post tags for content labeling and filtering.
    
    Tags provide a flexible way to label blog posts with keywords or topics,
    allowing for better content organization and discovery. Unlike categories,
    posts can have multiple tags.

    Attributes:
        name (CharField): The tag name (max 50 chars, must be unique)
        slug (SlugField): URL-friendly version of the name (auto-generated if not provided)
        created_at (DateTimeField): Timestamp of when the tag was created
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        """
        Override save method to auto-generate slug from name if not provided.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """
    A comprehensive model representing individual blog posts.
    
    This model handles all aspects of blog posts including content, metadata,
    publishing status, categorization, and engagement tracking. It supports
    draft/published workflows, SEO-friendly URLs, and content organization.

    Attributes:
        title (CharField): The post title (max 200 chars)
        slug (SlugField): URL-friendly version of title (auto-generated if not provided)
        excerpt (TextField): Brief description/summary (max 300 chars)
        content (TextField): Full post content (supports rich text/markdown)
        author (ForeignKey): Reference to User who authored the post
        category (ForeignKey): Optional category assignment (can be null)
        tags (ManyToManyField): Multiple tags for flexible content labeling
        featured_image (ImageField): Optional header/featured image
        status (CharField): Publishing status (draft/published/archived)
        featured (BooleanField): Whether post should be highlighted/featured
        read_time (PositiveIntegerField): Estimated reading time in minutes
        views (PositiveIntegerField): View count for analytics
        created_at (DateTimeField): When the post was first created
        updated_at (DateTimeField): When the post was last modified
        published_at (DateTimeField): When the post was published (null for drafts)
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.TextField(max_length=300, help_text="Brief description of the post")
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False)
    read_time = models.PositiveIntegerField(default=5, help_text="Estimated read time in minutes")
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        """
        Override save method to handle slug generation and publishing timestamps.
        
        Generates a slug from the title if not provided, and sets the published_at 
        timestamp when status changes to 'published'. For updates, preserves custom slugs.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        # Only generate slug if it's empty to preserve custom slugs
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        """
        Check if the blog post is currently published.
        
        Returns:
            bool: True if status is 'published', False otherwise
        """
        return self.status == 'published'


class Comment(models.Model):
    """
    A model representing user comments on blog posts.
    
    This model handles user-generated comments with moderation capabilities.
    Comments require approval before being displayed publicly, helping maintain
    content quality and prevent spam.

    Attributes:
        post (ForeignKey): Reference to the BlogPost being commented on
        name (CharField): Commenter's display name (max 100 chars)
        email (EmailField): Commenter's email address (for notifications/contact)
        content (TextField): The actual comment text
        approved (BooleanField): Whether comment has been approved by moderators
        created_at (DateTimeField): When the comment was submitted
    """
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.name} on {self.post.title}"
