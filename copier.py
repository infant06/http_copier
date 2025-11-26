import os
import re
import urllib.parse as urlparse
from collections import deque

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

SESSION = requests.Session()

CDN_PATTERNS = [
    r"fonts\.googleapis\.com",
    r"fonts\.gstatic\.com",
    r"ajax\.googleapis\.com",
    r"google-analytics\.com",
    r"googletagmanager\.com",
    r"cdnjs\.cloudflare\.com",
    r"jsdelivr\.net",
]

def is_cdn(url: str) -> bool:
    return any(re.search(p, url) for p in CDN_PATTERNS)

def is_same_origin(base, target):
    b = urlparse.urlparse(base)
    t = urlparse.urlparse(target)
    return (t.netloc == "" or t.netloc == b.netloc) and (t.scheme in ("", b.scheme))

def normalize_url(base_url, link):
    return urlparse.urljoin(base_url, link)

def local_path_for_url(root_dir, base_url, url):
    parsed = urlparse.urlparse(url)
    path = parsed.path

    if not path or path.endswith("/"):
        path = path + "index.html"

    if path.endswith("/"):
        path += "index.html"

    if parsed.query:
        base, ext = os.path.splitext(path)
        safe_query = re.sub(r"[^0-9A-Za-z]+", "_", parsed.query)
        path = f"{base}_{safe_query}{ext}"

    local_path = os.path.join(root_dir, parsed.netloc or urlparse.urlparse(base_url).netloc, path.lstrip("/"))
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    return local_path

def download_binary(url, local_path):
    if os.path.exists(local_path):
        return
    resp = SESSION.get(url, stream=True, timeout=15)
    resp.raise_for_status()
    with open(local_path, "wb") as f:
        for chunk in resp.iter_content(8192):
            if chunk:
                f.write(chunk)

def extract_urls_from_css(css_text):
    urls = re.findall(r'url\(([^)]+)\)', css_text, re.IGNORECASE)
    cleaned = [u.strip(' \'"') for u in urls]
    return cleaned

def process_css(base_url, css_url, root_dir):
    try:
        resp = SESSION.get(css_url, timeout=15)
        resp.raise_for_status()
        css_text = resp.text
        asset_urls = extract_urls_from_css(css_text)
        for asset_url in asset_urls:
            abs_asset_url = normalize_url(css_url, asset_url)
            if not is_same_origin(base_url, abs_asset_url):
                continue
            if is_cdn(abs_asset_url):
                continue
            local_asset_path = local_path_for_url(root_dir, base_url, abs_asset_url)
            try:
                print(f" Downloading CSS asset: {abs_asset_url}")
                download_binary(abs_asset_url, local_asset_path)
            except Exception as e:
                print(f"  Failed CSS asset {abs_asset_url}: {e}")
    except Exception as e:
        print(f"Failed to process CSS {css_url}: {e}")

def process_html(base_url, url, root_dir):
    print(f"Processing page: {url}")
    resp = SESSION.get(url, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    asset_attrs = [
        ("img", "src"),
        ("script", "src"),
        ("link", "href"),
        ("source", "src"),
        ("video", "src"),
        ("audio", "src"),
        ("iframe", "src"),
        ("embed", "src"),
    ]

    to_visit = []

    for tag, attr in asset_attrs:
        for el in soup.find_all(tag):
            link = el.get(attr)
            if not link:
                continue

            abs_url = normalize_url(url, link)

            if not is_same_origin(base_url, abs_url):
                continue
            if is_cdn(abs_url):
                continue

            asset_local = local_path_for_url(root_dir, base_url, abs_url)
            rel_path = os.path.relpath(asset_local, os.path.dirname(local_path_for_url(root_dir, base_url, url)))
            el[attr] = rel_path.replace("\\", "/")

            try:
                print(f" Downloading asset: {abs_url}")
                download_binary(abs_url, asset_local)
                if abs_url.endswith(".css"):
                    process_css(base_url, abs_url, root_dir)
            except Exception as e:
                print(f"  Failed asset {abs_url}: {e}")

    for a in soup.find_all("a", href=True):
        href = a["href"]
        abs_url = normalize_url(base_url, href)

        if not is_same_origin(base_url, abs_url):
            continue
        if is_cdn(abs_url):
            continue

        path = urlparse.urlparse(abs_url).path.lower()
        if any(path.endswith(ext) for ext in [
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg",
            ".css", ".js", ".ico", ".pdf", ".zip", ".tar", ".gz",
            ".mp4", ".mp3", ".wav", ".ogg", ".flv"
        ]):
            continue

        to_visit.append(abs_url)

    local_html = local_path_for_url(root_dir, base_url, url)
    with open(local_html, "w", encoding="utf-8") as f:
        f.write(str(soup))

    return to_visit

def crawl_site(start_url, output_dir):
    visited = set()
    queue = deque([start_url])
    base_url = start_url
    progress = tqdm(desc="Pages", unit="page")

    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)

        try:
            new_links = process_html(base_url, current, output_dir)
            progress.update(1)
            for nl in new_links:
                if nl not in visited and nl not in queue:
                    queue.append(nl)
        except Exception as e:
            print(f"Error processing {current}: {e}")

    progress.close()

if __name__ == "__main__":
    start = "https://example.com/"  # Replace with your URL
    out_dir = "./mirror_output"     # Replace with your output folder
    crawl_site(start, out_dir)
