/*
  # Create Blog Migration System Tables

  1. New Tables
    - `sources`
      - `id` (uuid, primary key)
      - `url` (text, unique) - Source blog URL
      - `name` (text) - Friendly name for the source
      - `created_at` (timestamptz) - Creation timestamp
    
    - `posts`
      - `id` (uuid, primary key)
      - `source_id` (uuid, foreign key) - References sources table
      - `title` (text) - Original post title
      - `content` (text) - Original post content
      - `source_url` (text) - Original post URL
      - `rewritten_title` (text, nullable) - AI-rewritten title
      - `rewritten_content` (text, nullable) - AI-rewritten content
      - `meta_description` (text, nullable) - Generated meta description
      - `images` (jsonb) - Array of image URLs
      - `tags` (jsonb) - Array of original tags
      - `suggested_tags` (jsonb) - Array of AI-suggested tags
      - `status` (text) - Post status: extracted, rewritten, scheduled, published, failed
      - `scheduled_time` (timestamptz, nullable) - When to publish
      - `published_url` (text, nullable) - URL after publishing to Blogger
      - `created_at` (timestamptz) - Creation timestamp
      - `updated_at` (timestamptz) - Last update timestamp

  2. Security
    - Enable RLS on both tables
    - Add policies for public access (for simplicity in this migration tool)
    
  3. Indexes
    - Index on posts.status for filtering
    - Index on posts.source_id for joins
    - Index on posts.scheduled_time for scheduling queries
*/

CREATE TABLE IF NOT EXISTS sources (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  url text UNIQUE NOT NULL,
  name text NOT NULL,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS posts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id uuid REFERENCES sources(id) ON DELETE CASCADE,
  title text NOT NULL,
  content text NOT NULL,
  source_url text,
  rewritten_title text,
  rewritten_content text,
  meta_description text,
  images jsonb DEFAULT '[]'::jsonb,
  tags jsonb DEFAULT '[]'::jsonb,
  suggested_tags jsonb DEFAULT '[]'::jsonb,
  status text DEFAULT 'extracted',
  scheduled_time timestamptz,
  published_url text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_source_id ON posts(source_id);
CREATE INDEX IF NOT EXISTS idx_posts_scheduled_time ON posts(scheduled_time);

ALTER TABLE sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to sources"
  ON sources FOR SELECT
  USING (true);

CREATE POLICY "Allow public insert to sources"
  ON sources FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public update to sources"
  ON sources FOR UPDATE
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete from sources"
  ON sources FOR DELETE
  USING (true);

CREATE POLICY "Allow public read access to posts"
  ON posts FOR SELECT
  USING (true);

CREATE POLICY "Allow public insert to posts"
  ON posts FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public update to posts"
  ON posts FOR UPDATE
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete from posts"
  ON posts FOR DELETE
  USING (true);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_posts_updated_at
  BEFORE UPDATE ON posts
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();