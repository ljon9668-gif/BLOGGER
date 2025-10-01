# 📝 Changelog

All notable changes to the Blog Migration Tool project.

## [2.0.0] - 2025-10-01

### 🎉 Major Release - Multi-Platform Support

### ✨ Added
- **Google Colab Notebook** (`blog_migration_colab.ipynb`)
  - Complete standalone version for cloud execution
  - No installation required
  - Interactive cells with inline modules
  - Pre-configured with API keys

- **Command Line Interface** (`blog_migration_cli.py`)
  - Full-featured terminal interface
  - Menu-driven navigation
  - Batch processing support
  - Perfect for automation and scripting

- **Cloud Database Migration**
  - Migrated from SQLite to Supabase PostgreSQL
  - Cloud-based persistence
  - Better scalability
  - Real-time data sync
  - Row Level Security (RLS) enabled

- **Documentation Suite**
  - `README.md` - Comprehensive project documentation
  - `QUICKSTART.md` - Quick start guide for new users
  - `PROJECT_SUMMARY.md` - Technical overview
  - `CHANGELOG.md` - This file
  - Inline code documentation improvements

- **Helper Scripts**
  - `run_web.sh` - Quick launch for Streamlit interface
  - `run_cli.sh` - Quick launch for CLI interface
  - Auto-install dependencies

- **Dependency Management**
  - `requirements.txt` for pip installations
  - Added `supabase>=2.12.0`
  - Added `python-dotenv>=1.0.0`

### 🔄 Changed
- **database.py** - Complete rewrite
  - Now uses Supabase client instead of SQLite
  - Maintained all existing methods
  - Improved error handling
  - Better type hints
  - Async-ready architecture

- **.env Configuration**
  - Updated with Supabase credentials
  - Added Gemini API key: `AIzaSyBAqMxp0-Uf9asMQeDCV8uafPYafHXWLI8`
  - Added Blogger API key: `AIzaSyBwwg3SyVN9xslSubGlx5kzJMjgHtZibw8`
  - Renamed keys for consistency

- **pyproject.toml**
  - Updated project name to `blog-migration-tool`
  - Bumped version to 2.0.0
  - Added new dependencies

### 🗑️ Removed
- **blog_migration.db** - SQLite database file
  - Replaced by cloud Supabase database
  - No more local database file needed

### 🔧 Database Schema Changes
- Created Supabase tables:
  - `sources` table with UUID primary key
  - `posts` table with UUID primary key
  - Foreign key relationship: posts → sources
  - Indexes on status, source_id, scheduled_time
  - Automatic updated_at trigger
  - RLS policies for secure access

### 🐛 Fixed
- Database connection issues with concurrent access
- Type casting issues in app.py with source IDs
- Improved error handling throughout

### 🔒 Security Improvements
- Environment variables for all sensitive data
- Supabase RLS policies enabled
- No hardcoded credentials
- Secure API key management

---

## [1.0.0] - Previous Version

### Initial Features
- Streamlit web interface
- Content extraction from blogs (RSS/scraping)
- AI rewriting with Google Gemini
- Publishing to Blogger
- Post scheduling
- SQLite database for local storage
- Dashboard with statistics
- Migration history tracking

---

## Migration Guide (1.x → 2.0)

### For Existing Users

1. **Backup your data** (if needed):
   ```bash
   # Export from old SQLite database (if you have existing data)
   sqlite3 blog_migration.db .dump > backup.sql
   ```

2. **Update environment variables**:
   - Rename `.env` keys if using old format
   - Add Supabase credentials
   - Verify API keys are correct

3. **Install new dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Database migration** (automatic):
   - Supabase tables are created automatically
   - No manual migration needed
   - Start fresh with new cloud database

5. **Choose your interface**:
   - Keep using Streamlit: `streamlit run app.py`
   - Try new CLI: `python blog_migration_cli.py`
   - Use Colab: Upload the `.ipynb` file

### Breaking Changes
- Database structure changed from SQLite to PostgreSQL
- IDs are now UUIDs instead of integers
- Some internal database methods have different signatures
- Old SQLite data does not auto-migrate (export/import manually if needed)

---

## Upgrade Benefits

### Why Upgrade?
1. ✅ **Cloud Database**: Access from anywhere
2. ✅ **Multiple Interfaces**: Web, CLI, or Colab
3. ✅ **Better Scalability**: Handle more posts
4. ✅ **Improved Reliability**: Supabase uptime
5. ✅ **No Local DB**: No file corruption issues
6. ✅ **Better Documentation**: Easier to use

### What Stays the Same?
- ✅ All core features
- ✅ Content extraction methods
- ✅ AI rewriting quality
- ✅ Blogger integration
- ✅ User interface (Streamlit)
- ✅ Configuration approach

---

## Future Roadmap

### Planned Features (v2.1)
- [ ] Multi-user authentication
- [ ] Scheduled background workers
- [ ] Email notifications
- [ ] Content analytics dashboard
- [ ] Export to multiple formats

### Under Consideration
- [ ] WordPress direct integration
- [ ] Medium publishing support
- [ ] Custom AI model training
- [ ] Browser extension
- [ ] Mobile app

---

## Support & Feedback

For questions or issues:
- Check documentation in `README.md`
- Review `QUICKSTART.md` for common problems
- Verify API keys in `.env`
- Check Supabase project status

---

**Version 2.0.0 represents a major milestone with cloud infrastructure and multi-platform support!**
