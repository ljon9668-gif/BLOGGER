#!/usr/bin/env python3
"""
Blog Migration CLI Tool
Automated blog content migration with AI-powered rewriting
"""

import os
import sys
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

from database import Database
from content_extractor import ContentExtractor
from ai_rewriter import AIRewriter
from blogger_publisher import BloggerPublisher
from unified_publisher import UnifiedPublisher
from email_publisher import EmailPublisher

load_dotenv()

class BlogMigrationCLI:
    def __init__(self):
        self.db = Database()
        self.extractor = ContentExtractor()

        gemini_key = os.getenv('GEMINI_API_KEY')
        blogger_key = os.getenv('BLOGGER_API_KEY')

        if not gemini_key or not blogger_key:
            print("❌ Error: GEMINI_API_KEY and BLOGGER_API_KEY must be set in .env file")
            sys.exit(1)

        self.rewriter = AIRewriter(gemini_key)
        self.publisher = BloggerPublisher(blogger_key)
        self.unified_publisher = UnifiedPublisher()

    def display_menu(self):
        print("\n" + "="*60)
        print("📝 Blog Migration Tool - CLI")
        print("="*60)
        print("1. View Dashboard")
        print("2. Add Source Blog")
        print("3. List Sources")
        print("4. Extract Content from Source")
        print("5. Rewrite Posts with AI")
        print("6. Manage Blogger Configurations")
        print("7. Publish to Blogger")
        print("8. View Posts by Status")
        print("9. Exit")
        print("="*60)

    def show_dashboard(self):
        stats = self.db.get_statistics()

        print("\n📊 Dashboard")
        print("-" * 60)
        print(f"Total Sources:    {stats['total_sources']}")
        print(f"Extracted Posts:  {stats['total_extracted']}")
        print(f"Published Posts:  {stats['total_published']}")
        print(f"Pending Posts:    {stats['total_pending']}")
        print("-" * 60)

    def add_source(self):
        print("\n➕ Add Source Blog")
        url = input("Enter blog URL: ").strip()
        name = input("Enter source name (optional): ").strip() or url

        if self.db.add_source(url, name):
            print(f"✅ Added source: {name}")
        else:
            print("❌ Source already exists or invalid")

    def list_sources(self):
        sources = self.db.get_all_sources()

        if not sources:
            print("\nℹ️  No sources found. Add sources first.")
            return

        print(f"\n📚 Sources ({len(sources)})")
        print("-" * 60)
        for i, source in enumerate(sources, 1):
            post_count = self.db.get_source_post_count(source['id'])
            print(f"{i}. {source['name']}")
            print(f"   URL: {source['url']}")
            print(f"   Posts: {post_count}")
            print()

    def extract_content(self):
        sources = self.db.get_all_sources()

        if not sources:
            print("\n❌ No sources available. Add sources first.")
            return

        print("\n📥 Extract Content")
        print("-" * 60)

        for i, source in enumerate(sources, 1):
            print(f"{i}. {source['name']}")

        try:
            choice = int(input("\nSelect source number: ")) - 1
            if choice < 0 or choice >= len(sources):
                print("❌ Invalid selection")
                return

            max_posts = int(input("Maximum posts to extract (default 10): ") or "10")

            source = sources[choice]
            print(f"\n🔍 Extracting content from {source['name']}...")

            posts = self.extractor.extract_from_url(source['url'], max_posts)

            added_count = 0
            duplicate_count = 0

            for post in posts:
                if not self.db.is_duplicate(post['title'], post['url']):
                    self.db.add_post(
                        source_id=source['id'],
                        title=post['title'],
                        content=post['content'],
                        source_url=post['url'],
                        images=post.get('images', []),
                        tags=post.get('tags', [])
                    )
                    added_count += 1
                    print(f"  ✓ {post['title'][:60]}...")
                else:
                    duplicate_count += 1

            print(f"\n✅ Extracted {added_count} new posts")
            if duplicate_count > 0:
                print(f"ℹ️  Skipped {duplicate_count} duplicates")

        except ValueError:
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    def rewrite_posts(self):
        posts = self.db.get_posts_by_status('extracted')

        if not posts:
            print("\nℹ️  No posts to rewrite. Extract content first.")
            return

        print(f"\n✍️  Rewrite Posts ({len(posts)} available)")
        print("-" * 60)

        try:
            process_count = int(input(f"How many posts to process (max {len(posts)}): "))

            if process_count <= 0 or process_count > len(posts):
                print("❌ Invalid count")
                return

            print("\n🤖 Processing with AI...")

            for i, post in enumerate(posts[:process_count], 1):
                print(f"\n[{i}/{process_count}] {post['title'][:60]}...")

                try:
                    rewritten = self.rewriter.rewrite_post(
                        title=post['title'],
                        content=post['content'],
                        optimize_seo=True,
                        improve_readability=True,
                        generate_meta=True,
                        suggest_tags=True
                    )

                    self.db.update_post_rewritten(
                        post_id=post['id'],
                        rewritten_title=rewritten['title'],
                        rewritten_content=rewritten['content'],
                        meta_description=rewritten.get('meta_description'),
                        suggested_tags=rewritten.get('tags', [])
                    )

                    print(f"  ✓ Rewritten: {rewritten['title'][:60]}...")

                except Exception as e:
                    print(f"  ✗ Error: {str(e)}")

            print(f"\n✅ Processed {process_count} posts!")

        except ValueError:
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    def manage_blogger_configs(self):
        print("\n⚙️ Manage Blogger Configurations")
        print("-" * 60)
        print("1. Add New Configuration")
        print("2. List Configurations")
        print("3. Delete Configuration")
        print("4. Back to Main Menu")

        try:
            choice = int(input("\nSelect option: "))

            if choice == 1:
                self._add_blogger_config()
            elif choice == 2:
                self._list_blogger_configs()
            elif choice == 3:
                self._delete_blogger_config()
            elif choice == 4:
                return
            else:
                print("❌ Invalid option")

        except ValueError:
            print("❌ Invalid input")

    def _add_blogger_config(self):
        print("\n➕ Add Blogger Configuration")
        blog_name = input("Blog Name: ").strip()

        print("\nPublishing Method:")
        print("1. API (Blogger API Key)")
        print("2. Email (Send via SMTP)")

        try:
            method_choice = int(input("Select method (1 or 2): "))

            if method_choice == 1:
                blog_id = input("Blogger Blog ID: ").strip()
                api_key = input("Blogger API Key: ").strip()
                is_default = input("Set as default? (y/n): ").lower() == 'y'

                if self.db.add_blogger_config(
                    blog_name=blog_name,
                    publish_method="api",
                    blog_id=blog_id,
                    api_key=api_key,
                    is_default=is_default
                ):
                    print(f"✅ Configuration '{blog_name}' added!")
                else:
                    print("❌ Failed to add configuration")

            elif method_choice == 2:
                print("\nEmail Configuration:")
                print(EmailPublisher.get_blogger_email_help())
                email_address = input("Blogger Email Address (e.g., blog.key@blogger.com): ").strip()
                smtp_server = input("SMTP Server (default: smtp.gmail.com): ").strip() or "smtp.gmail.com"
                smtp_port = int(input("SMTP Port (default: 587): ") or "587")
                smtp_username = input("SMTP Username (your email): ").strip()
                smtp_password = input("SMTP Password: ").strip()
                is_default = input("Set as default? (y/n): ").lower() == 'y'

                if not EmailPublisher.validate_blogger_email(email_address):
                    print("❌ Invalid Blogger email format")
                    return

                if self.db.add_blogger_config(
                    blog_name=blog_name,
                    publish_method="email",
                    email_address=email_address,
                    smtp_server=smtp_server,
                    smtp_port=smtp_port,
                    smtp_username=smtp_username,
                    smtp_password=smtp_password,
                    is_default=is_default
                ):
                    print(f"✅ Configuration '{blog_name}' added!")
                else:
                    print("❌ Failed to add configuration")
            else:
                print("❌ Invalid choice")

        except ValueError:
            print("❌ Invalid input")

    def _list_blogger_configs(self):
        configs = self.db.get_all_blogger_configs()

        if not configs:
            print("\nℹ️  No configurations found")
            return

        print(f"\n📋 Blogger Configurations ({len(configs)})")
        print("-" * 60)

        for i, config in enumerate(configs, 1):
            default_mark = "⭐ " if config['is_default'] else "   "
            print(f"{default_mark}{i}. {config['blog_name']} ({config['publish_method'].upper()})")
            if config['publish_method'] == 'api':
                print(f"    Blog ID: {config['blog_id']}")
            else:
                print(f"    Email: {config['email_address']}")
            print()

    def _delete_blogger_config(self):
        configs = self.db.get_all_blogger_configs()

        if not configs:
            print("\nℹ️  No configurations to delete")
            return

        self._list_blogger_configs()

        try:
            choice = int(input("\nSelect configuration number to delete: ")) - 1
            if 0 <= choice < len(configs):
                config_id = configs[choice]['id']
                if self.db.delete_blogger_config(config_id):
                    print("✅ Configuration deleted!")
                else:
                    print("❌ Failed to delete configuration")
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid input")

    def publish_posts(self):
        posts = self.db.get_posts_by_status('rewritten')

        if not posts:
            print("\nℹ️  No posts ready to publish. Rewrite posts first.")
            return

        configs = self.db.get_all_blogger_configs()
        if not configs:
            print("❌ No Blogger configurations found. Add one first (option 6).")
            return

        print(f"\n🚀 Publish to Blogger ({len(posts)} ready)")
        print("-" * 60)

        print("\nSelect Configuration:")
        for i, config in enumerate(configs, 1):
            default_mark = "⭐ " if config['is_default'] else "   "
            print(f"{default_mark}{i}. {config['blog_name']} ({config['publish_method'].upper()})")

        try:
            config_choice = int(input("\nSelect configuration number: ")) - 1
            if config_choice < 0 or config_choice >= len(configs):
                print("❌ Invalid selection")
                return

            selected_config = configs[config_choice]
            publish_count = int(input(f"How many posts to publish (max {len(posts)}): "))

            if publish_count <= 0 or publish_count > len(posts):
                print("❌ Invalid count")
                return

            print("\n📤 Publishing...")

            for i, post in enumerate(posts[:publish_count], 1):
                print(f"\n[{i}/{publish_count}] {post['rewritten_title'][:60]}...")

                try:
                    published_url = self.unified_publisher.publish_post(
                        config=selected_config,
                        title=post['rewritten_title'],
                        content=post['rewritten_content'],
                        labels=post.get('suggested_tags', []),
                        images=post.get('images', [])
                    )

                    self.db.update_post_published(
                        post_id=post['id'],
                        published_url=published_url
                    )

                    print(f"  ✓ {published_url}")

                except Exception as e:
                    print(f"  ✗ Error: {str(e)}")

            print(f"\n✅ Published {publish_count} posts!")

        except ValueError:
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    def view_posts_by_status(self):
        print("\n📋 View Posts by Status")
        print("-" * 60)
        print("1. Extracted (not yet rewritten)")
        print("2. Rewritten (ready to publish)")
        print("3. Published")

        try:
            choice = int(input("\nSelect status: "))

            status_map = {
                1: 'extracted',
                2: 'rewritten',
                3: 'published'
            }

            if choice not in status_map:
                print("❌ Invalid selection")
                return

            status = status_map[choice]
            posts = self.db.get_posts_by_status(status, limit=50)

            if not posts:
                print(f"\nℹ️  No posts with status '{status}'")
                return

            print(f"\n{status.upper()} Posts ({len(posts)})")
            print("-" * 60)

            for i, post in enumerate(posts, 1):
                title = post.get('rewritten_title') or post['title']
                print(f"{i}. {title[:70]}...")
                if post.get('published_url'):
                    print(f"   URL: {post['published_url']}")
                print()

        except ValueError:
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    def run(self):
        print("\n🚀 Blog Migration Tool - Starting...")

        while True:
            try:
                self.display_menu()
                choice = input("\nSelect option (1-9): ").strip()

                if choice == '1':
                    self.show_dashboard()
                elif choice == '2':
                    self.add_source()
                elif choice == '3':
                    self.list_sources()
                elif choice == '4':
                    self.extract_content()
                elif choice == '5':
                    self.rewrite_posts()
                elif choice == '6':
                    self.manage_blogger_configs()
                elif choice == '7':
                    self.publish_posts()
                elif choice == '8':
                    self.view_posts_by_status()
                elif choice == '9':
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("\n❌ Invalid option. Please select 1-9.")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {str(e)}")

def main():
    cli = BlogMigrationCLI()
    cli.run()

if __name__ == "__main__":
    main()
