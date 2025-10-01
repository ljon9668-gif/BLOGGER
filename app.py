import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from database import Database
from content_extractor import ContentExtractor
from ai_rewriter import AIRewriter
from blogger_publisher import BloggerPublisher
from scheduler import PostScheduler
from utils import validate_url, extract_domain

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = Database()

if 'extractor' not in st.session_state:
    st.session_state.extractor = ContentExtractor()

if 'rewriter' not in st.session_state:
    gemini_api_key = os.getenv("GEMINI_API_KEY", "AIzaSyBAqMxp0-Uf9asMQeDCV8uafPYafHXWLI8")
    st.session_state.rewriter = AIRewriter(gemini_api_key)

if 'publisher' not in st.session_state:
    blogger_api_key = os.getenv("BLOGGER_API_KEY", "AIzaSyBwwg3SyVN9xslSubGlx5kzJMjgHtZibw8")
    st.session_state.publisher = BloggerPublisher(blogger_api_key)

if 'scheduler' not in st.session_state:
    st.session_state.scheduler = PostScheduler(st.session_state.db)

# Page configuration
st.set_page_config(
    page_title="Blog Migration Tool",
    page_icon="📝",
    layout="wide"
)

# Main title
st.title("📝 Blog Content Migration Tool")
st.markdown("Migrate and rewrite blog content with AI-powered optimization")

# Sidebar navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Add Source Blogs", "Extract Content", "Rewrite & Publish", "Schedule Posts", "Migration History"]
)

# Dashboard Page
if page == "Dashboard":
    st.header("📊 Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    stats = st.session_state.db.get_statistics()
    
    with col1:
        st.metric("Total Sources", stats['total_sources'])
    
    with col2:
        st.metric("Extracted Posts", stats['total_extracted'])
    
    with col3:
        st.metric("Published Posts", stats['total_published'])
    
    with col4:
        st.metric("Pending Posts", stats['total_pending'])
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("Recent Activity")
    recent_posts = st.session_state.db.get_recent_posts(10)
    
    if recent_posts:
        df = pd.DataFrame(recent_posts)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(df[['title', 'source_url', 'status', 'created_at']], use_container_width=True)
    else:
        st.info("No posts yet. Start by adding source blogs!")

# Add Source Blogs Page
elif page == "Add Source Blogs":
    st.header("➕ Add Source Blogs")
    
    st.markdown("Enter blog URLs or RSS feed URLs to extract content from:")
    
    source_url = st.text_input("Blog/RSS Feed URL", placeholder="https://example.com/feed or https://blog.example.com")
    source_name = st.text_input("Source Name (optional)", placeholder="My Old Blog")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Add Source", type="primary"):
            if source_url:
                if validate_url(source_url):
                    name = source_name if source_name else extract_domain(source_url)
                    if st.session_state.db.add_source(source_url, name):
                        st.success(f"✅ Source '{name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ This source already exists!")
                else:
                    st.error("❌ Invalid URL format!")
            else:
                st.error("❌ Please enter a URL!")
    
    st.markdown("---")
    
    # Display existing sources
    st.subheader("Existing Sources")
    sources = st.session_state.db.get_all_sources()
    
    if sources:
        for source in sources:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{source['name']}**")
                st.caption(source['url'])
            
            with col2:
                post_count = st.session_state.db.get_source_post_count(source['id'])
                st.metric("Posts", post_count)
            
            with col3:
                if st.button("🗑️ Delete", key=f"del_{source['id']}"):
                    st.session_state.db.delete_source(source['id'])
                    st.success("Source deleted!")
                    st.rerun()
    else:
        st.info("No sources added yet.")

# Extract Content Page
elif page == "Extract Content":
    st.header("📥 Extract Content")
    
    sources = st.session_state.db.get_all_sources()
    
    if not sources:
        st.warning("⚠️ No sources available. Please add source blogs first!")
    else:
        source_names = {s['id']: s['name'] for s in sources}
        selected_source_id = st.selectbox(
            "Select Source to Extract From",
            options=list(source_names.keys()),
            format_func=lambda x: source_names[x]
        )
        
        max_posts = st.number_input("Maximum Posts to Extract", min_value=1, max_value=100, value=10)
        
        if st.button("🔍 Extract Content", type="primary"):
            source = next(s for s in sources if s['id'] == selected_source_id)
            
            with st.spinner(f"Extracting content from {source['name']}..."):
                try:
                    posts = st.session_state.extractor.extract_from_url(source['url'], max_posts)
                    
                    added_count = 0
                    duplicate_count = 0
                    
                    for post in posts:
                        # Check for duplicates
                        if not st.session_state.db.is_duplicate(post['title'], post['url']):
                            st.session_state.db.add_post(
                                source_id=selected_source_id,
                                title=post['title'],
                                content=post['content'],
                                source_url=post['url'],
                                images=post.get('images', []),
                                tags=post.get('tags', [])
                            )
                            added_count += 1
                        else:
                            duplicate_count += 1
                    
                    st.success(f"✅ Extracted {added_count} new posts!")
                    if duplicate_count > 0:
                        st.info(f"ℹ️ Skipped {duplicate_count} duplicate posts")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error extracting content: {str(e)}")
        
        st.markdown("---")
        
        # Show extracted posts from this source
        st.subheader("Extracted Posts (Not Yet Rewritten)")
        source_posts = st.session_state.db.get_posts_by_source(selected_source_id, status='extracted')
        
        if source_posts:
            for post in source_posts:
                with st.expander(f"{post['title'][:80]}..."):
                    st.write(f"**Source URL:** {post['source_url']}")
                    st.write(f"**Status:** {post['status']}")
                    st.write(f"**Content Preview:** {post['content'][:200]}...")
        else:
            st.info("No extracted posts from this source yet.")

# Rewrite & Publish Page
elif page == "Rewrite & Publish":
    st.header("✍️ Rewrite & Publish")
    
    # Get destination blog ID
    st.subheader("Blogger Configuration")
    destination_blog_id = st.text_input(
        "Destination Blogger Blog ID",
        help="Find this in your Blogger dashboard URL: blogger.com/blog/posts/YOUR_BLOG_ID"
    )
    
    if not destination_blog_id:
        st.warning("⚠️ Please enter your destination Blogger Blog ID to continue.")
    else:
        # Get posts ready for rewriting
        posts_to_rewrite = st.session_state.db.get_posts_by_status('extracted')
        
        if not posts_to_rewrite:
            st.info("ℹ️ No posts available for rewriting. Please extract content first!")
        else:
            st.subheader("Posts Ready for Rewriting")
            st.write(f"Found {len(posts_to_rewrite)} posts to process")
            
            # Rewriting options
            col1, col2 = st.columns(2)
            
            with col1:
                optimize_seo = st.checkbox("Optimize for SEO", value=True)
                improve_readability = st.checkbox("Improve Readability", value=True)
            
            with col2:
                generate_meta = st.checkbox("Generate Meta Descriptions", value=True)
                suggest_tags = st.checkbox("Suggest Tags", value=True)
            
            # Batch processing
            process_count = st.number_input(
                "Number of posts to process",
                min_value=1,
                max_value=len(posts_to_rewrite),
                value=min(5, len(posts_to_rewrite))
            )
            
            publish_immediately = st.checkbox("Publish Immediately", value=False)
            
            if st.button("🚀 Rewrite & Process", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, post in enumerate(posts_to_rewrite[:process_count]):
                    status_text.text(f"Processing: {post['title'][:50]}...")
                    
                    try:
                        # Rewrite content with AI
                        rewritten = st.session_state.rewriter.rewrite_post(
                            title=post['title'],
                            content=post['content'],
                            optimize_seo=optimize_seo,
                            improve_readability=improve_readability,
                            generate_meta=generate_meta,
                            suggest_tags=suggest_tags
                        )
                        
                        # Update post in database
                        st.session_state.db.update_post_rewritten(
                            post_id=post['id'],
                            rewritten_title=rewritten['title'],
                            rewritten_content=rewritten['content'],
                            meta_description=rewritten.get('meta_description'),
                            suggested_tags=rewritten.get('tags', [])
                        )
                        
                        # Publish if requested
                        if publish_immediately:
                            try:
                                published_url = st.session_state.publisher.publish_post(
                                    blog_id=destination_blog_id,
                                    title=rewritten['title'],
                                    content=rewritten['content'],
                                    labels=rewritten.get('tags', [])
                                )
                                
                                st.session_state.db.update_post_published(
                                    post_id=post['id'],
                                    published_url=published_url
                                )
                                
                            except Exception as e:
                                st.error(f"Failed to publish '{post['title']}': {str(e)}")
                        
                    except Exception as e:
                        st.error(f"Failed to rewrite '{post['title']}': {str(e)}")
                    
                    progress_bar.progress((idx + 1) / process_count)
                
                status_text.text("Processing complete!")
                st.success(f"✅ Successfully processed {process_count} posts!")
                st.rerun()
            
            # Show preview of posts
            st.markdown("---")
            st.subheader("Preview Posts")
            
            for post in posts_to_rewrite[:3]:
                with st.expander(f"📄 {post['title'][:60]}..."):
                    st.write(f"**Original Title:** {post['title']}")
                    st.write(f"**Content Preview:** {post['content'][:300]}...")
                    st.write(f"**Source:** {post['source_url']}")

# Schedule Posts Page
elif page == "Schedule Posts":
    st.header("📅 Schedule Posts")
    
    # Get destination blog ID
    destination_blog_id = st.text_input(
        "Destination Blogger Blog ID",
        help="Find this in your Blogger dashboard URL"
    )
    
    if not destination_blog_id:
        st.warning("⚠️ Please enter your destination Blogger Blog ID to continue.")
    else:
        # Get rewritten posts that haven't been published
        ready_posts = st.session_state.db.get_posts_by_status('rewritten')
        
        if not ready_posts:
            st.info("ℹ️ No posts ready for scheduling. Please rewrite posts first!")
        else:
            st.subheader("Scheduling Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                start_date = st.date_input("Start Publishing From", value=datetime.now().date())
                posts_per_day = st.number_input("Posts Per Day", min_value=1, max_value=10, value=1)
            
            with col2:
                start_time = st.time_input("Publishing Time", value=datetime.now().time())
                total_posts = st.number_input(
                    "Total Posts to Schedule",
                    min_value=1,
                    max_value=len(ready_posts),
                    value=min(10, len(ready_posts))
                )
            
            if st.button("📅 Create Publishing Schedule", type="primary"):
                schedule = st.session_state.scheduler.create_schedule(
                    posts=ready_posts[:total_posts],
                    start_date=start_date,
                    start_time=start_time,
                    posts_per_day=posts_per_day
                )
                
                st.success(f"✅ Created schedule for {len(schedule)} posts!")
                
                # Display schedule
                st.subheader("Publishing Schedule")
                schedule_df = pd.DataFrame(schedule)
                st.dataframe(schedule_df[['title', 'scheduled_time']], use_container_width=True)
                
                # Save schedule to database
                for item in schedule:
                    st.session_state.db.update_post_scheduled(
                        post_id=item['post_id'],
                        scheduled_time=item['scheduled_time']
                    )
                
                st.info("💡 Schedule saved! Posts will be published at the scheduled times.")
            
            st.markdown("---")
            
            # Manual publish section
            st.subheader("Publish Now")
            st.write("Select posts to publish immediately:")
            
            for post in ready_posts[:5]:
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.write(f"**{post['title']}**")
                    st.caption(f"Rewritten on: {post['updated_at']}")
                
                with col2:
                    if st.button("Publish", key=f"pub_{post['id']}"):
                        try:
                            published_url = st.session_state.publisher.publish_post(
                                blog_id=destination_blog_id,
                                title=post['rewritten_title'] or post['title'],
                                content=post['rewritten_content'] or post['content'],
                                labels=post['suggested_tags'] or []
                            )
                            
                            st.session_state.db.update_post_published(
                                post_id=post['id'],
                                published_url=published_url
                            )
                            
                            st.success(f"✅ Published: {published_url}")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Failed to publish: {str(e)}")

# Migration History Page
elif page == "Migration History":
    st.header("📜 Migration History")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "extracted", "rewritten", "scheduled", "published", "failed"]
        )
    
    with col2:
        source_filter = st.selectbox(
            "Filter by Source",
            ["All"] + [s['name'] for s in st.session_state.db.get_all_sources()]
        )
    
    with col3:
        limit = st.number_input("Show Posts", min_value=10, max_value=1000, value=50)
    
    # Get filtered posts
    if status_filter == "All":
        posts = st.session_state.db.get_all_posts(limit=limit)
    else:
        posts = st.session_state.db.get_posts_by_status(status_filter, limit=limit)
    
    if source_filter != "All":
        source_id = next(
            (s['id'] for s in st.session_state.db.get_all_sources() if s['name'] == source_filter),
            None
        )
        if source_id:
            posts = [p for p in posts if p['source_id'] == source_id]
    
    st.subheader(f"Found {len(posts)} posts")
    
    if posts:
        # Create DataFrame for display
        df_data = []
        for post in posts:
            df_data.append({
                'ID': post['id'],
                'Title': post['title'][:60] + '...' if len(post['title']) > 60 else post['title'],
                'Status': post['status'],
                'Source URL': post['source_url'][:40] + '...' if post['source_url'] and len(post['source_url']) > 40 else post['source_url'],
                'Published URL': post['published_url'][:40] + '...' if post.get('published_url') and len(post['published_url']) > 40 else '',
                'Created': post['created_at'][:10] if post['created_at'] else ''
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
        
        # Export options
        st.markdown("---")
        st.subheader("Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export to CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"migration_history_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("🗑️ Clear All Data"):
                if st.checkbox("I confirm I want to delete all migration data"):
                    st.session_state.db.clear_all_data()
                    st.success("✅ All data cleared!")
                    st.rerun()
    else:
        st.info("No posts found matching the filters.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "Blog Migration Tool v1.0\n\n"
    "Powered by Gemini AI & Blogger API\n\n"
    "This tool helps you migrate and optimize blog content automatically."
)
