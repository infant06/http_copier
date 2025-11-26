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
git clone https://github.com/yourusername/website-copier.git
cd website-copier

text

2. Create and activate a virtual environment (venv):
On Windows Powershell:
python -m venv venv
.\venv\Scripts\Activate

text

On Linux/macOS:
python3 -m venv venv
source venv/bin/activate

text

3. Install requirements:
pip install -r requirements.txt

text

## Usage

Edit the script `copier.py` and set the target website URL and output folder:

start = "https://example.com/" # Replace with the site you want to download
out_dir = "./mirror_output" # Your local folder to save the site

text

Run the script:

python copier.py

text

The script will show a progress bar and log assets/pages downloaded. Browse the output folder locally with HTML files and assets preserved.

## Notes

- Make sure you have permission to scrape/mirror the target website respecting its terms of service.
- Large sites may take considerable time and disk space.
- Currently, the script skips certain files like videos or archives as crawlable pages but downloads all asset files referenced.
- Feel free to report bugs or request features via issues.

---

# requirements.txt

requests
beautifulsoup4
tqdm

text
---

This README.md covers setup, usage, requirements, and key script behavior. Let me know if you want it customized further!
