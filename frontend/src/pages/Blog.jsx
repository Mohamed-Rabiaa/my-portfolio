/**
 * Blog Page Component
 * 
 * This file contains the Blog page component that displays a paginated list of blog posts
 * fetched from the backend API. It includes features like post filtering, pagination,
 * and a newsletter subscription section.
 * 
 * @author Your Name
 * @version 1.0.0
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './Blog.css';

/**
 * Blog Component
 * 
 * Renders the blog page with a list of blog posts, pagination controls,
 * and a newsletter subscription section. Fetches posts from the backend API
 * and handles loading states and pagination.
 * 
 * @component
 * @returns {JSX.Element} The rendered blog page
 */
const Blog = () => {
  /** @type {Array} Array of blog posts fetched from the API */
  const [posts, setPosts] = useState([]);
  
  /** @type {boolean} Loading state indicator */
  const [loading, setLoading] = useState(true);
  
  /** @type {number} Current page number for pagination */
  const [currentPage, setCurrentPage] = useState(1);
  
  /** @type {number} Total number of pages available */
  const [totalPages, setTotalPages] = useState(1);

  /**
   * Effect hook to fetch blog posts when component mounts or page changes
   * Makes API call to backend to retrieve paginated blog posts
   */
  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/v1/blog/posts/?page=${currentPage}`);
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

  /**
   * Formats a date string into a readable format
   * 
   * @param {string} dateString - The date string to format
   * @returns {string} Formatted date string (e.g., "January 15, 2024")
   */
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  /**
   * Truncates content to a specified maximum length
   * 
   * @param {string} content - The content to truncate
   * @param {number} maxLength - Maximum length before truncation (default: 150)
   * @returns {string} Truncated content with ellipsis if needed
   */
  const truncateContent = (content, maxLength = 150) => {
    if (!content || content.length <= maxLength) return content || '';
    return content.substr(0, maxLength) + '...';
  };

  /**
   * Handles pagination page changes
   * 
   * @param {number} page - The page number to navigate to
   */
  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Loading state display
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
      {/* Blog Hero Section - Main header with title and description */}
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

      {/* Blog Posts Section - Main content area with posts grid */}
      <section className="blog-posts">
        <div className="container">
          {posts.length === 0 ? (
            // Empty state when no posts are available
            <div className="no-posts">
              <h2>No blog posts found</h2>
              <p>Check back later for new content!</p>
            </div>
          ) : (
            <>
              {/* Posts Grid - Display blog posts in a grid layout */}
              <div className="posts-grid">
                {posts.map((post) => (
                  <article key={post.id} className="post-card">
                    {/* Post Image - Featured image or placeholder */}
                    <div className="post-image">
                      {post.featured_image ? (
                        <img src={post.featured_image} alt={post.title} />
                      ) : (
                        <div className="post-placeholder">
                          <span>No Image</span>
                        </div>
                      )}
                    </div>
                    
                    {/* Post Content - Title, meta, excerpt, and tags */}
                    <div className="post-content">
                      {/* Post Meta - Date and category information */}
                      <div className="post-meta">
                        <span className="post-date">{formatDate(post.created_at)}</span>
                        <span className="post-category">{post.category?.name || post.category}</span>
                      </div>
                      
                      {/* Post Title - Linked to full post */}
                      <h2 className="post-title">
                        <Link to={`/blog/${post.slug}`}>{post.title}</Link>
                      </h2>
                      
                      {/* Post Excerpt - Truncated content preview */}
                      <p className="post-excerpt">
                        {truncateContent(post.content)}
                      </p>
                      
                      {/* Post Footer - Tags and read more link */}
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

              {/* Pagination Controls - Navigation between pages */}
              {totalPages > 1 && (
                <div className="pagination">
                  {/* Previous Page Button */}
                  <button
                    className={`pagination-btn ${currentPage === 1 ? 'disabled' : ''}`}
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                  >
                    ← Previous
                  </button>
                  
                  {/* Page Numbers */}
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

                  {/* Next Page Button */}
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

      {/* Newsletter Subscription Section - Email signup form */}
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