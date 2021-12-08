import logging
import os
import pdb
import queue
from urllib.parse import urlparse
from pathlib import Path
from threading import Thread

import typer
import requests
import urllib3.util
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from requests.packages.urllib3 import Retry

# TODO
# - maximum depth instead of max requests?
# - pass python objects instead of strings
# - use function download_file()
# - add more tags and attributes: <img src=" etc
# - more type hints
# - handle IO exceptions
# see https://github.com/jay/wget/blob/master/src/html-url.c#L139

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/96.0.4664.55 Safari/537.36"
)

retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])

indexed_pages = set()


def mkdir_by_url(url: str, base_dir: str):
    """Creates directory based on the URL path structure if one does not exist."""
    url_parsed = urlparse(url)
    dir_path = base_dir + "/" + url_parsed.netloc
    if url_parsed.path:
        dir_path += url_parsed.path
    # pdb.set_trace()
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    return dir_path


# Not currently in use
def download_file(url) -> str:
    """Download file by URL. Suitable for large files as it performs the download in chunks."""
    local_filename = url.split("/")[-1]  # TODO: get filename from Content-Disposition header
    local_temp_filename = local_filename + ".part"
    with requests.get(
        url,
        stream=True,  # defer downloading the response body until you access the Response.content
    ) as r:
        r.raise_for_status()
        with open(local_temp_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):  # 8 kb chunks
                f.write(chunk)
        os.rename(local_temp_filename, local_filename)
    return local_filename


def get_content(url: str) -> bytes:
    try:
        session = requests.Session()
        session.mount("http://", HTTPAdapter(max_retries=retries))
        r = session.get(url, headers={"User-Agent": USER_AGENT})
        return r.content
    except Exception as e:
        print(e)
        return b""


# TODO: Add <img src= etc
def get_links(html: BeautifulSoup, url: str) -> list:
    links = []
    tags_with_href = ["a", "img", "embed", "area"]
    for tag in tags_with_href:
        for link in html.findAll(tag):
            href = link.get("href")
            if href:
                if href.startswith("#"):
                    pass
                elif href.startswith("//"):
                    if href.split("//")[0] == url.split("//")[1]:
                        links.append("https:" + href)
                elif href.startswith("/"):
                    links.append(url + href)
                else:
                    links.append(link.get("href"))
    return links



def crawl(url: str, queue: queue.Queue, base_dir: str):
    """Crawler that collects links from a page within the initial URL and recursively downloads them."""
    indexed_pages.add(url)
    print(f"Crawling URL: {url}")
    resource_content = get_content(url)
    file_path = mkdir_by_url(url, base_dir) + "/" + url.split("/")[-1]
    if file_path[-1] == "/":
        file_path = file_path[:-2] + ".html"
    with open(file_path, "wb") as f:
        f.write(resource_content)
    parsed_html = BeautifulSoup(resource_content, "html.parser")
    links = get_links(parsed_html, url)
    filtered_links = [
        link for link in links if link.startswith(url)
    ]  # keep only links within the original URL
    print(f"{len(filtered_links)} links were found")
    for link in filtered_links:
        if link not in indexed_pages:
            queue.put(link)


def start_worker(i, queue, max_requests, base_dir):
    while True:
        url = queue.get()
        if len(indexed_pages) < max_requests and url not in indexed_pages:
            crawl(url, queue, base_dir)
        queue.task_done()  # Notify the queue that the task has been completed successfully


app = typer.Typer()


@app.command()
def cli_start(
    start_url: str,
    destination: str,
    max_requests: int = 128,
    parallel_workers: int = 4,
    verbose: bool = False,
):
    """
    Recursive website crawler. Supports parametrization of the number of simultaneous threads,
    setting a directory for downloading files, limiting maximum number of requests within one session
    and verbose output.
    See crawler.py --help for more details on parameters.
    """
    Path(destination).mkdir(parents=True, exist_ok=True)
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    q = queue.Queue()
    for w in range(parallel_workers):
        Thread(
            target=start_worker, args=(w, q, max_requests, destination), daemon=True
        ).start()
    q.put(start_url)
    q.join()
    print("Success")


if __name__ == "__main__":
    app()
