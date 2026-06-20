#!/usr/bin/env python3
import json, os, shutil, sys

def build():
    pages_path = 'data/pages.json'
    if not os.path.exists(pages_path):
        print("ERROR: pages.json not found")
        sys.exit(1)
    with open(pages_path, 'r') as f:
        pages = json.load(f)
    with open('theme/base.html', 'r') as f:
        template = f.read()
    if os.path.exists('build'):
        shutil.rmtree('build')
    os.makedirs('build')
    for page in pages:
        slug = page['slug']
        title = page.get('title', '')
        meta_description = page.get('meta_description', '')
        content = page.get('body_content', '')
        canonical_slug = '' if slug == 'index' else slug + '/'
        html = template.replace('{{ content }}', content)
        html = html.replace('{{ title }}', title)
        html = html.replace('{{ meta_description }}', meta_description)
        html = html.replace('{{ canonical_slug }}', canonical_slug)
        out_dir = os.path.join('build', slug) if slug else 'build'
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, 'index.html'), 'w') as f:
            f.write(html)
    if os.path.exists('assets'):
        shutil.copytree('assets', 'build/assets', dirs_exist_ok=True)
    # Generate robots.txt
    robots = "User-agent: *\nAllow: /\nSitemap: https://mikes-house-clearance.co.uk/sitemap.xml\n"
    with open('build/robots.txt', 'w') as f:
        f.write(robots)
    # Generate sitemap.xml
    sitemap_urls = ''
    for page in pages:
        slug = page['slug']
        if slug == 'index':
            url = 'https://mikes-house-clearance.co.uk/'
        elif slug:
            url = f'https://mikes-house-clearance.co.uk/{slug}/'
        else:
            continue
        sitemap_urls += f'  <url>\n    <loc>{url}</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n'
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap_urls}</urlset>'
    with open('build/sitemap.xml', 'w') as f:
        f.write(sitemap)
    # Homepage slug fix
    homepage_src = 'build/index/index.html'
    if os.path.exists(homepage_src):
        shutil.copy(homepage_src, 'build/index.html')
        print('Homepage copied: build/index/index.html -> build/index.html')
    print(f"Built {len(pages)} pages")
    print("Generated robots.txt")
    print("Generated sitemap.xml")

if __name__ == '__main__':
    build()
