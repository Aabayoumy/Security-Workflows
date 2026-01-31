# AD-Workflow

A modern documentation site for Active Directory workflows, built with [Hugo](https://gohugo.io/) and the [Hextra](https://hextra.site/) theme.

## Overview

This project serves as the centralized repository for AD security research and operational workflows. Content is migrated from Obsidian and optimized for web-based documentation.

## Getting Started

### Prerequisites

- [Hugo Extended](https://gohugo.io/installation/)

### Installation

1. Clone the repository with submodules:
   ```bash
   git clone --recursive <repository-url>
   ```
2. Navigate to the project:
   ```bash
   cd AD-Workflow
   ```

### Running Locally

To start the development server:
```bash
hugo server -D
```
The site will be available at `http://localhost:1313`.

## Migration from Obsidian

A utility script `migrate_obsidian.py` is available locally to move markdown files from your Obsidian vault to this project. 

**Note:** The script is ignored by Git to keep the repository focused on content and configuration.

### Usage
```bash
python3 migrate_obsidian.py "/path/to/vault/note.md"
```

## Theme

This site uses the [Hextra](https://github.com/imfing/hextra) theme. Documentation for the theme can be found [here](https://imfing.github.io/hextra/).
