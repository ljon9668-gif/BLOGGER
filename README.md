# 📝 Blog Migration Tool

Automated blog content migration system with AI-powered rewriting using Gemini AI. Extract content from any blog, rewrite it to avoid plagiarism, and publish automatically to Blogger.

## ✨ Features

- **Universal Content Extraction**: Works with RSS feeds or direct web scraping
- **AI-Powered Rewriting**: Uses Google Gemini to completely rewrite content
- **SEO Optimization**: Generates optimized titles, meta descriptions, and tags
- **Automated Publishing**: Direct integration with Blogger API
- **Multiple Interfaces**: Streamlit web UI, Google Colab notebook, and CLI
- **Cloud Database**: Uses Supabase for reliable data persistence
- **Duplicate Detection**: Prevents re-processing of existing content
- **Batch Processing**: Handle multiple posts efficiently

## 🚀 Quick Start

### Option 1: Streamlit Web Interface (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the web interface
streamlit run app.py
```

### Option 2: Google Colab (No Installation Required)

1. Open `blog_migration_colab.ipynb` in Google Colab
2. Run all cells in order
3. Follow the interactive prompts

### Option 3: Command Line Interface

```bash
# Install dependencies
pip install -r requirements.txt

# Run CLI
python blog_migration_cli.py
```

## 📋 Prerequisites

### Required API Keys

1. **Gemini API Key**: Get from [Google AI Studio](https://aistudio.google.com/apikey)
2. **Blogger API Key**: Get from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
3. **Supabase Account**: Already configured (credentials in `.env`)

### Environment Setup

Create a `.env` file in the project root:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_api_key
BLOGGER_API_KEY=your_blogger_api_key
```

## 📖 Usage Guide

### 1. Add Source Blogs

Enter the homepage URL of any blog you want to migrate from:
- Blogger: `https://yourblog.blogspot.com`
- WordPress: `https://yoursite.com`
- Any blog with RSS: `https://site.com/feed`

### 2. Extract Content

The tool will:
- Try RSS feed first (fastest)
- Fall back to web scraping if needed
- Extract titles, content, images, and tags
- Store everything in Supabase

### 3. Rewrite with AI

For each post:
- Complete rewrite to avoid plagiarism
- SEO-optimized titles and descriptions
- Suggested relevant tags
- Improved readability

### 4. Publish to Blogger

- Enter your Blogger Blog ID
- Publish manually or in batches
- Track published URLs
- Schedule future publications

## 🏗️ Architecture

### Components

```
blog_migration_tool/
├── app.py                      # Streamlit web interface
├── blog_migration_cli.py       # Command-line interface
├── blog_migration_colab.ipynb  # Google Colab notebook
├── database.py                 # Supabase database layer
├── content_extractor.py        # RSS and web scraping
├── ai_rewriter.py              # Gemini AI integration
├── blogger_publisher.py        # Blogger API integration
├── scheduler.py                # Post scheduling logic
├── utils.py                    # Helper functions
└── .env                        # Configuration
```

### Database Schema

**Sources Table**:
- `id`: UUID primary key
- `url`: Source blog URL
- `name`: Friendly name
- `created_at`: Timestamp

**Posts Table**:
- `id`: UUID primary key
- `source_id`: Foreign key to sources
- `title`: Original title
- `content`: Original content
- `rewritten_title`: AI-generated title
- `rewritten_content`: AI-generated content
- `meta_description`: SEO description
- `tags`: Original tags (JSONB)
- `suggested_tags`: AI-suggested tags (JSONB)
- `images`: Image URLs (JSONB)
- `status`: extracted | rewritten | published
- `published_url`: Blogger post URL
- `scheduled_time`: When to publish
- `created_at`, `updated_at`: Timestamps

## 🔧 Advanced Configuration

### Content Extraction

Modify `content_extractor.py` to:
- Adjust maximum posts per extraction
- Customize article link detection
- Change image extraction limits
- Add custom CSS selectors

### AI Rewriting

Adjust prompts in `ai_rewriter.py`:
- Change writing style
- Adjust SEO optimization level
- Modify tag generation
- Control content length

### Publishing

Configure in `blogger_publisher.py`:
- Draft vs. immediate publish
- Custom HTML formatting
- Image processing
- Label management

## 📊 Post Status Flow

```
[Source Blog]
    ↓
[Extract] → status: extracted
    ↓
[AI Rewrite] → status: rewritten
    ↓
[Publish] → status: published
```

## 🛠️ Troubleshooting

### Common Issues

**"No posts extracted"**
- Check if the blog URL is accessible
- Try adding `/feed` or `/rss` to the URL
- Verify the blog has public posts

**"Gemini API Error"**
- Verify your API key is correct
- Check API quota limits
- Ensure the key has Gemini access enabled

**"Blogger API Error"**
- Confirm your Blog ID is correct
- Check API key permissions
- Verify the blog exists and is accessible

**"Database connection failed"**
- Check Supabase credentials in `.env`
- Verify internet connection
- Check Supabase project status

## 📦 Dependencies

Core libraries:
- `supabase`: Database client
- `streamlit`: Web interface
- `google-genai`: Gemini AI
- `google-api-python-client`: Blogger API
- `feedparser`: RSS parsing
- `beautifulsoup4`: HTML parsing
- `trafilatura`: Content extraction
- `pandas`: Data handling

## 🔐 Security Notes

- Never commit `.env` file to version control
- Keep API keys secure
- Use environment variables for sensitive data
- Supabase RLS policies protect data access

## 🎯 Best Practices

1. **Start Small**: Test with 5-10 posts first
2. **Review Rewrites**: Check AI-generated content quality
3. **Batch Processing**: Process 10-20 posts at a time
4. **Monitor Quotas**: Watch API usage limits
5. **Backup Data**: Export important migrations

## 📈 Scaling Tips

- Use batch processing for large migrations
- Schedule posts over days/weeks
- Monitor API rate limits
- Consider upgrading Gemini quota for bulk work

## 🤝 Contributing

This is a migration tool for personal use. Modify as needed for your specific requirements.

## 📄 License

MIT License - Use freely for personal or commercial projects.

## 🆘 Support

For issues:
1. Check this README
2. Review error messages
3. Verify all API keys are correct
4. Check Supabase connection

## 🎉 Success Stories

Perfect for:
- Migrating old blogs to new platforms
- Refreshing outdated content
- SEO optimization of existing posts
- Content syndication
- Blog consolidation

---

**Made with ❤️ for bloggers who want to modernize their content**
