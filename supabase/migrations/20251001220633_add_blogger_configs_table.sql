/*
  # Add Blogger Configuration Table

  1. New Tables
    - `blogger_configs`
      - `id` (uuid, primary key)
      - `blog_name` (text) - Friendly name for the blog
      - `blog_id` (text, nullable) - Blogger Blog ID for API publishing
      - `api_key` (text, nullable) - Blogger API key
      - `email_address` (text, nullable) - Blogger email address (e.g., name.secretkey@blogger.com)
      - `smtp_server` (text) - SMTP server (default: smtp.gmail.com)
      - `smtp_port` (integer) - SMTP port (default: 587)
      - `smtp_username` (text, nullable) - SMTP username for sending email
      - `smtp_password` (text, nullable) - SMTP password
      - `publish_method` (text) - Method: 'api' or 'email'
      - `is_default` (boolean) - Is this the default configuration
      - `created_at` (timestamptz) - Creation timestamp
      - `updated_at` (timestamptz) - Last update timestamp

  2. Security
    - Enable RLS on blogger_configs table
    - Add policies for public access (for simplicity)

  3. Important Notes
    - Users can store multiple blogger configurations
    - One configuration can be marked as default
    - API method requires blog_id and api_key
    - Email method requires email_address, smtp credentials
*/

CREATE TABLE IF NOT EXISTS blogger_configs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  blog_name text NOT NULL,
  blog_id text,
  api_key text,
  email_address text,
  smtp_server text DEFAULT 'smtp.gmail.com',
  smtp_port integer DEFAULT 587,
  smtp_username text,
  smtp_password text,
  publish_method text DEFAULT 'api' CHECK (publish_method IN ('api', 'email')),
  is_default boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_blogger_configs_default ON blogger_configs(is_default) WHERE is_default = true;

ALTER TABLE blogger_configs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to blogger_configs"
  ON blogger_configs FOR SELECT
  USING (true);

CREATE POLICY "Allow public insert to blogger_configs"
  ON blogger_configs FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public update to blogger_configs"
  ON blogger_configs FOR UPDATE
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete from blogger_configs"
  ON blogger_configs FOR DELETE
  USING (true);

CREATE OR REPLACE FUNCTION update_blogger_configs_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_blogger_configs_updated_at
  BEFORE UPDATE ON blogger_configs
  FOR EACH ROW
  EXECUTE FUNCTION update_blogger_configs_updated_at();
