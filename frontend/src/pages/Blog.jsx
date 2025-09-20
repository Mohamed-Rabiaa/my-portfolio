import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './Blog.css';

const Blog = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/blog/posts/?page=${currentPage}`);
        setPosts(response.data.results);
        setTotalPages(Math.ceil(response.data.count / 10)); // Assuming 10 posts per page
        setLoading(false);
      } catch (error) {
        console.error('Error fetching blog posts:', error);
        setLoading(false);
      }
    };

    fetchPosts();
  }, [currentPage]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const truncateContent = (content, maxLength = 150) => {
    if (!content || content.length <= maxLength) return content || '';
    return content.substr(0, maxLength) + '...';
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div className="blog">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading blog posts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="blog">
      {/* Blog Hero Section */}
      <section className="blog-hero">
        <div className="container">
          <div className="blog-hero-content">
            <h1>My Blog</h1>
            <p>
              Thoughts, tutorials, and insights about web development, technology, 
              and my journey as a developer. Stay updated with the latest trends and tips.
            </p>
          </div>
        </div>
      </section>

      {/* Blog Posts Section */}
      <section className="blog-posts">
        <div className="container">
          {posts.length === 0 ? (
            <div className="no-posts">
              <h2>No blog posts found</h2>
              <p>Check back later for new content!</p>
            </div>
          ) : (
            <>
              <div className="posts-grid">
                {posts.map((post) => (
                  <article key={post.id} className="post-card">
                    <div className="post-image">
                      {post.featured_image ? (
                        <img src={post.featured_image} alt={post.title} />
                      ) : (
                        <div className="post-placeholder">
                          <span>No Image</span>
                        </div>
                      )}
                    </div>
                    <div className="post-content">
                      <div className="post-meta">
                        <span className="post-date">{formatDate(post.created_at)}</span>
                        <span className="post-category">{post.category?.name || post.category}</span>
                      </div>
                      <h2 className="post-title">
                        <Link to={`/blog/${post.slug}`}>{post.title}</Link>
                      </h2>
                      <p className="post-excerpt">
                        {truncateContent(post.content)}
                      </p>
                      <div className="post-footer">
                        <div className="post-tags">
                          {post.tags && post.tags.slice(0, 3).map((tag, index) => (
                             <span key={index} className="tag">
                               {tag.name || tag}
                             </span>
                           ))}
                        </div>
                        <Link to={`/blog/${post.slug}`} className="read-more">
                          Read More →
                        </Link>
                      </div>
                    </div>
                  </article>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="pagination">
                  <button
                    className={`pagination-btn ${currentPage === 1 ? 'disabled' : ''}`}
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                  >
                    ← Previous
                  </button>
                  
                  <div className="pagination-numbers">
                    {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                      <button
                        key={page}
                        className={`pagination-number ${currentPage === page ? 'active' : ''}`}
                        onClick={() => handlePageChange(page)}
                      >
                        {page}
                      </button>
                    ))}
                  </div>

                  <button
                    className={`pagination-btn ${currentPage === totalPages ? 'disabled' : ''}`}
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                  >
                    Next →
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </section>

      {/* Newsletter Subscription Section */}
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

export default Blog;