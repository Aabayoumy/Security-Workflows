import os
import re
import shutil
import sys
from datetime import datetime

# Configuration
VAULT_PATH = '/Users/abayoumy/GLOBAL BRANDS - Gbrands-Security Team - AD-Workflow'
PROJECT_ROOT = '/Users/abayoumy/Projects/AD-Workflow'
CONTENT_DIR = os.path.join(PROJECT_ROOT, 'content/docs')
STATIC_ASSETS_DIR = os.path.join(PROJECT_ROOT, 'static')
VAULT_ASSETS_DIR = os.path.join(VAULT_PATH, 'assets')

# Ensure directories exist
os.makedirs(CONTENT_DIR, exist_ok=True)
os.makedirs(STATIC_ASSETS_DIR, exist_ok=True)

def migrate_file(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    filename = os.path.basename(file_path)
    base_name = filename.lower().replace(' ', '-').replace('.md', '')
    
    # Create page bundle directory
    page_bundle_dir = os.path.join(CONTENT_DIR, base_name)
    os.makedirs(page_bundle_dir, exist_ok=True)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Handle Images: ![[image.png]]
    def replace_obsidian_image(match):
        image_name = match.group(1)
        # Handle cases with sizes like ![[image.png|300]]
        if '|' in image_name:
            image_name = image_name.split('|')[0]
        
        # Search for image in vault
        found_src_path = None
        # Try local assets directory relative to the file first
        local_assets = os.path.join(os.path.dirname(file_path), 'assets')
        if os.path.exists(os.path.join(local_assets, image_name)):
            found_src_path = os.path.join(local_assets, image_name)
        # Then try global assets
        elif os.path.exists(os.path.join(VAULT_ASSETS_DIR, image_name)):
            found_src_path = os.path.join(VAULT_ASSETS_DIR, image_name)
        
        if found_src_path:
            # Shorten name if it starts with "Pasted image"
            final_image_name = image_name
            if image_name.startswith('Pasted image '):
                final_image_name = image_name.split(' ')[-1]
            
            shutil.copy2(found_src_path, os.path.join(page_bundle_dir, final_image_name))
            return f'![{final_image_name}]({final_image_name})'
        return match.group(0)

    content = re.sub(r'!\[\[(.*?)\]\]', replace_obsidian_image, content)


    # 2. Handle Standard Image links: ![](assets/image.png)
    def replace_standard_image(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        image_name = os.path.basename(image_path)
        
        src_path = os.path.join(VAULT_PATH, image_path)
        if os.path.exists(src_path):
            # Shorten name if it starts with "Pasted image"
            final_image_name = image_name
            if image_name.startswith('Pasted image '):
                final_image_name = image_name.split(' ')[-1]
            
            shutil.copy2(src_path, os.path.join(page_bundle_dir, final_image_name))
            return f'![{alt_text}]({final_image_name})'
        return match.group(0)

    content = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_standard_image, content)

    # 3. Handle Links: [[Note Name]] -> [Note Name]({{< relref "note-name.md" >}})
    def replace_obsidian_link(match):
        link_text = match.group(1)
        # Handle links with aliases: [[Note Name|Alias]]
        if '|' in link_text:
            note_name, alias = link_text.split('|', 1)
        else:
            note_name = link_text
            alias = link_text
        
        # Convert "Note Name" to "note-name.md"
        safe_name = note_name.strip().replace(' ', '-').lower()
        if not safe_name.endswith('.md'):
            safe_name += '.md'
        
        return f'[{alias}]({{{{< relref "{safe_name}" >}}}})'

    content = re.sub(r'\[\[(.*?)\]\]', replace_obsidian_link, content)

    # 4. Handle Frontmatter
    title = filename.replace('.md', '').replace('-', ' ').title()
    # Use yesterday's date to avoid Hugo's "future date" rendering issue
    from datetime import timedelta
    date_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
    
    frontmatter = f"""---
title: "{title}"
date: {date_str}
draft: false
---

"""
    # Remove existing frontmatter if it exists to avoid duplication
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]

    final_content = frontmatter + content.strip()

    # Save to Hugo content directory as Page Bundle (index.md)
    dest_path = os.path.join(page_bundle_dir, 'index.md')
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"Successfully migrated: {filename} -> {dest_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 migrate_obsidian.py <path_to_md_file>")
    else:
        migrate_file(sys.argv[1])
