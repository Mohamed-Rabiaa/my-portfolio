import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import './BlogPost.css';

const BlogPost = () => {
  const { slug } = useParams();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPost = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/blog/posts/${slug}/`);
        setPost(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching blog post:', error);
        setError('Post not found');
        setLoading(false);
      }
    };

    fetchPost();
  }, [slug]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="blog-post">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading blog post...</p>
        </div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="blog-post">
        <div className="error">
          <h1>Post Not Found</h1>
          <p>The blog post you're looking for doesn't exist.</p>
          <Link to="/blog" className="back-to-blog">
            ← Back to Blog
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="blog-post">
      {/* Back to Blog Link */}
      <div className="container">
        <Link to="/blog" className="back-link">
          ← Back to Blog
        </Link>
      </div>

      {/* Post Header */}
      <header className="post-header">
        <div className="container">
          <div className="post-meta">
            <span className="post-category">{post.category}</span>
            <span className="post-date">{formatDate(post.created_at)}</span>
          </div>
          <h1 className="post-title">{post.title}</h1>
          {post.excerpt && (
            <p className="post-excerpt">{post.excerpt}</p>
          )}
        </div>
      </header>

      {/* Featured Image */}
      {post.featured_image && (
        <div className="featured-image">
          <div className="container">
            <img src={post.featured_image} alt={post.title} />
          </div>
        </div>
      )}

      {/* Post Content */}
      <main className="post-content">
        <div className="container">
          <article className="post-article">
            <div 
              className="post-body"
              dangerouslySetInnerHTML={{ __html: post.content }}
            />
            
            {/* Post Tags */}
            {post.tags && (
              <div className="post-tags">
                <h3>Tags:</h3>
                <div className="tags-list">
                  {post.tags.split(',').map((tag, index) => (
                    <span key={index} className="tag">
                      {tag.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </article>

          {/* Post Navigation */}
          <nav className="post-navigation">
            <div className="nav-links">
              <Link to="/blog" className="nav-link">
                <span className="nav-label">← All Posts</span>
                <span className="nav-title">Back to Blog</span>
              </Link>
            </div>
          </nav>
        </div>
      </main>

      {/* Related Posts Section */}
      <section className="related-posts">
        <div className="container">
          <h2>More Articles</h2>
          <p>Check out other blog posts you might find interesting.</p>
          <Link to="/blog" className="view-all-posts">
            View All Posts →
          </Link>
        </div>
      </section>

      {/* Newsletter Subscription */}
      <section className="newsletter-section">
        <div className="container">
          <div className="newsletter-content">
            <h2>Stay Updated</h2>
            <p>
              Subscribe to my newsletter to get the latest blog posts and updates 
              delivered directly to your inbox.
            </p>
            <form className="newsletter-form">
              <input
                type="email"
                placeholder="Enter your email address"
                className="newsletter-input"
                required
              />
              <button type="submit" className="newsletter-btn">
                Subscribe
              </button>
            </form>
          </div>
        </div>
      </section>
    </div>
  );
};

export default BlogPost;