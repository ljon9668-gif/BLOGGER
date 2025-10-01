# 🚀 Quick Start Guide

## For Local Development (VSCode)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

The `.env` file is already configured with:
- ✅ Supabase connection
- ✅ Gemini API key
- ✅ Blogger API key

### 3. Run the Application

**Option A: Web Interface (Recommended)**
```bash
streamlit run app.py
```
Open browser to `http://localhost:8501`

**Option B: Command Line**
```bash
python blog_migration_cli.py
```

---

## For Google Colab

### 1. Upload the Notebook

1. Go to [Google Colab](https://colab.research.google.com)
2. Upload `blog_migration_colab.ipynb`

### 2. Run All Cells

- Click "Runtime" → "Run all"
- Follow the interactive prompts

---

## First Time Usage

### Step 1: Add a Source Blog

Enter the homepage URL of the blog you want to migrate:
```
https://yourblog.blogspot.com
```

### Step 2: Extract Content

- Select the source
- Choose how many posts to extract (e.g., 10)
- Wait for extraction to complete

### Step 3: Rewrite with AI

- Select how many posts to rewrite
- AI will process each post automatically
- This may take a few minutes

### Step 4: Publish to Blogger

- Get your Blog ID from Blogger dashboard URL:
  - Go to blogger.com
  - Select your blog
  - URL will be: `blogger.com/blog/posts/YOUR_BLOG_ID`
- Enter the Blog ID
- Select how many posts to publish

---

## Finding Your Blogger Blog ID

1. Go to [blogger.com](https://www.blogger.com)
2. Select your blog
3. Look at the URL in your browser
4. Copy the number after `/blog/posts/`

Example:
```
https://www.blogger.com/blog/posts/1234567890123456789
                                    ^^^^^^^^^^^^^^^^^^^
                                    This is your Blog ID
```

---

## Tips

- **Start small**: Test with 5-10 posts first
- **Review rewrites**: Check the quality before bulk processing
- **Monitor progress**: Use the dashboard to track status
- **Batch processing**: Process 10-20 posts at a time for best results

---

## Troubleshooting

**"Module not found"**
```bash
pip install -r requirements.txt
```

**"Supabase connection error"**
- Check internet connection
- Verify `.env` file exists with correct credentials

**"No posts extracted"**
- Try adding `/feed` to the blog URL
- Verify the blog is publicly accessible

**"Gemini API error"**
- Check API key in `.env`
- Verify you haven't exceeded quota

---

## Example Workflow

```bash
# 1. Start the web interface
streamlit run app.py

# In the browser:
# 2. Add source: https://example.blogspot.com
# 3. Extract: 10 posts
# 4. Rewrite: 10 posts with AI
# 5. Publish: 5 posts to Blogger
```

---

## Need Help?

Check the full [README.md](README.md) for detailed documentation.
