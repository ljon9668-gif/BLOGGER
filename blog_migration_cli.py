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

    def display_menu(self):
        print("\n" + "="*60)
        print("📝 Blog Migration Tool - CLI")
        print("="*60)
        print("1. View Dashboard")
        print("2. Add Source Blog")
        print("3. List Sources")
        print("4. Extract Content from Source")
        print("5. Rewrite Posts with AI")
        print("6. Publish to Blogger")
        print("7. View Posts by Status")
        print("8. Exit")
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

    def publish_posts(self):
        posts = self.db.get_posts_by_status('rewritten')

        if not posts:
            print("\nℹ️  No posts ready to publish. Rewrite posts first.")
            return

        print(f"\n🚀 Publish to Blogger ({len(posts)} ready)")
        print("-" * 60)

        blog_id = input("Enter your Blogger Blog ID: ").strip()

        if not blog_id:
            print("❌ Blog ID is required")
            return

        try:
            publish_count = int(input(f"How many posts to publish (max {len(posts)}): "))

            if publish_count <= 0 or publish_count > len(posts):
                print("❌ Invalid count")
                return

            print("\n📤 Publishing...")

            for i, post in enumerate(posts[:publish_count], 1):
                print(f"\n[{i}/{publish_count}] {post['rewritten_title'][:60]}...")

                try:
                    published_url = self.publisher.publish_post(
                        blog_id=blog_id,
                        title=post['rewritten_title'],
                        content=post['rewritten_content'],
                        labels=post.get('suggested_tags', [])
                    )

                    self.db.update_post_published(
                        post_id=post['id'],
                        published_url=published_url
                    )

                    print(f"  ✓ Published: {published_url}")

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
                choice = input("\nSelect option (1-8): ").strip()

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
                    self.publish_posts()
                elif choice == '7':
                    self.view_posts_by_status()
                elif choice == '8':
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("\n❌ Invalid option. Please select 1-8.")

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
