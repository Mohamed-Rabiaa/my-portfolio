from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from common.mixins import TimestampMixin, SlugMixin, BaseModel, StatusMixin
from common.utils import StatusChoices


class Category(BaseModel, TimestampMixin, SlugMixin):
    """
    A model representing blog post categories.
    
    This class defines categories that can be assigned to blog posts for organization
    and filtering purposes. Each category has a unique name and slug (URL-friendly version
    of the name), an optional description, and tracks when it was created.

    Attributes:
        name (CharField): The category name (max 100 chars, must be unique)
        slug (SlugField): URL-friendly version of the name (auto-generated if not provided)
        description (TextField): Optional detailed description of the category
        created_at (DateTimeField): Timestamp of when the category was created (inherited)
        updated_at (DateTimeField): Timestamp of when the category was last updated (inherited)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Tag(BaseModel, TimestampMixin, SlugMixin):
    """
    A model representing blog post tags for content labeling and filtering.
    
    Tags provide a flexible way to label blog posts with keywords or topics,
    allowing for better content organization and discovery. Unlike categories,
    posts can have multiple tags.

    Attributes:
        name (CharField): The tag name (max 50 chars, must be unique)
        slug (SlugField): URL-friendly version of the name (auto-generated if not provided)
        created_at (DateTimeField): Timestamp of when the tag was created (inherited)
        updated_at (DateTimeField): Timestamp of when the tag was last updated (inherited)
    """
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class BlogPost(BaseModel, TimestampMixin, SlugMixin, StatusMixin):
    """
    A model representing individual blog posts.
    
    This is the main content model for the blog application. Each blog post contains
    all the necessary information for display, categorization, and management.
    
    The model includes content fields (title, excerpt, content), metadata (author,
    category, tags), display options (featured image, featured flag), status management
    (draft/published/archived), engagement tracking (views), and automatic timestamps.
    
    Attributes:
        title (CharField): The blog post title (max 200 chars)
        slug (SlugField): URL-friendly version of title (auto-generated if not provided)
        excerpt (TextField): Brief description/summary (max 300 chars)
        content (TextField): Full blog post content
        author (ForeignKey): Reference to User who created the post
        category (ForeignKey): Optional category assignment
        tags (ManyToManyField): Multiple tag assignments for flexible labeling
        featured_image (ImageField): Optional header/featured image
        status (CharField): Publication status (draft/published/archived) - inherited
        featured (BooleanField): Whether post should be highlighted
        read_time (PositiveIntegerField): Estimated reading time in minutes
        views (PositiveIntegerField): View count for analytics
        created_at (DateTimeField): Creation timestamp (inherited)
        updated_at (DateTimeField): Last modification timestamp (inherited)
        published_at (DateTimeField): Publication timestamp
    """

    title = models.CharField(max_length=200)
    excerpt = models.TextField(max_length=300, help_text="Brief description of the post")
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    featured = models.BooleanField(default=False)
    read_time = models.PositiveIntegerField(default=5, help_text="Estimated read time in minutes")
    views = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        """
        Override save method to handle publishing timestamps.
        
        Sets the published_at timestamp when status changes to 'published'.
        Slug generation is handled by the SlugMixin.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        # Set published_at when status changes to published
        if self.status == StatusChoices.PUBLISHED and not self.published_at:
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
        return self.status == StatusChoices.PUBLISHED


class Comment(BaseModel, TimestampMixin):
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
        created_at (DateTimeField): When the comment was submitted (inherited)
        updated_at (DateTimeField): When the comment was last modified (inherited)
    """
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.name} on {self.post.title}"
