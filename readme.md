# Website Copier with Local Asset Download

This Python script recursively downloads a website's local HTML pages and assets (images, CSS, JavaScript, fonts, etc.) into a local folder for offline browsing. It skips external CDN and third-party links like Google Fonts and Analytics.

## Features

- Recursively downloads linked local pages and assets with proper folder structure.
- Parses CSS files to download fonts and images referenced inside.
- Skips external CDN/third-party URLs automatically.
- Shows a live progress bar for pages processed.
- Prints detailed logs for files downloaded and skipped.
- Skips broken pages (404 error) gracefully.

## Requirements

- Python 3.7+
- Packages listed in `requirements.txt`

## Setup

1. Clone the repository:
