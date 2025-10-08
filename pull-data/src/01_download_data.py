#!/usr/bin/env python3
"""
download_sackmann_atp.py

Download Jeff Sackmann's atp_matches_YYYY.csv files from:
https://github.com/JeffSackmann/tennis_atp

Default: downloads years 2011..2024 inclusive.

Usage:
    python download_sackmann_atp.py
    python download_sackmann_atp.py --start 2015 --end 2020 --outdir ./data/atp

Notes:
- Attribution: Jeff Sackmann (tennis_atp). Data licensed CC BY-NC-SA (check repo README).
- Requires: requests. tqdm is optional (for progress bars).
"""

from __future__ import annotations
import argparse
import os
import sys
import requests
from requests.adapters import HTTPAdapter, Retry

# Try to import tqdm for a better progress display (optional)
try:
    from tqdm import tqdm
except Exception:
    tqdm = None  # fallback


BASE_RAW_URL = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_{year}.csv"

# Chunk size when streaming download
CHUNK_SIZE = 8192


def create_session(retries: int = 3, backoff_factor: float = 0.3) -> requests.Session:
    s = requests.Session()
    retries_cfg = Retry(total=retries, backoff_factor=backoff_factor,
                        status_forcelist=[429, 500, 502, 503, 504],
                        allowed_methods=frozenset(["GET", "HEAD"]))
    s.mount("https://", HTTPAdapter(max_retries=retries_cfg))
    s.mount("http://", HTTPAdapter(max_retries=retries_cfg))
    # set a sensible User-Agent
    s.headers.update({"User-Agent": "sackmann-downloader/1.0 (+https://github.com/yourname)"})
    return s


def sane_file_check(path: str) -> bool:
    """
    Quick sanity check: ensure file is not an HTML error page and not empty.
    Return True if seems OK, False otherwise.
    """
    try:
        with open(path, "rb") as f:
            start = f.read(512)
            if not start:
                return False
            # GitHub 404 raw responses are HTML pages; look for "<!DOCTYPE html" or "<html"
            if b"<!DOCTYPE html" in start or b"<html" in start:
                return False
            # also check for CSV-like header (commonly "tourney_id" or "tourney_name" etc.)
            # Not strictly required — just a mild heuristic:
            if b"," not in start:
                # suspicious if no commas in first 512 bytes
                return False
    except Exception:
        return False
    return True


def download_file(session: requests.Session, url: str, outpath: str) -> None:
    """
    Download a file with streaming and write it to outpath.
    """
    resp = session.get(url, stream=True, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code} for {url}")

    total = resp.headers.get("Content-Length")
    total = int(total) if total and total.isdigit() else None

    # Write to a temporary file then rename on success
    tmp_path = outpath + ".part"
    with open(tmp_path, "wb") as fh:
        if tqdm and total:
            with tqdm(total=total, unit='B', unit_scale=True, desc=os.path.basename(outpath)) as pbar:
                for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        fh.write(chunk)
                        pbar.update(len(chunk))
        elif tqdm and not total:
            with tqdm(unit='B', unit_scale=True, desc=os.path.basename(outpath)) as pbar:
                for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        fh.write(chunk)
                        pbar.update(len(chunk))
        else:
            # no tqdm: simple write
            for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    fh.write(chunk)

    # move tmp to final
    os.replace(tmp_path, outpath)


def main(start_year: int = 2011, end_year: int = 2024, outdir: str = "atp_matches"):
    os.makedirs(outdir, exist_ok=True)
    session = create_session()

    print(f"Downloading Jeff Sackmann ATP match CSVs {start_year}..{end_year} into '{outdir}'")
    failures = []
    for year in range(start_year, end_year + 1):
        filename = f"atp_matches_{year}.csv"
        url = BASE_RAW_URL.format(year=year)
        outpath = os.path.join(outdir, filename)
        # Skip if already exists and passes sane check
        if os.path.exists(outpath) and sane_file_check(outpath):
            print(f"Skipping {filename} (already exists and looks OK).")
            continue
        try:
            print(f"Downloading {filename} ...")
            download_file(session, url, outpath)
            if not sane_file_check(outpath):
                raise RuntimeError("Sanity check failed (download may be HTML 404 or empty).")
            print(f"Saved: {outpath}")
        except Exception as e:
            print(f"ERROR downloading {filename}: {e}")
            failures.append((year, str(e)))

    if failures:
        print("\nSome downloads failed:")
        for year, reason in failures:
            print(f" - {year}: {reason}")
        print("You can re-run the script to retry failed years.")
        sys.exit(2)
    else:
        print("\nAll files downloaded successfully.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Download Jeff Sackmann tennis_atp match CSVs (2011-2024).")
    p.add_argument("--start", type=int, default=2011, help="Start year (inclusive).")
    p.add_argument("--end", type=int, default=2024, help="End year (inclusive).")
    p.add_argument("--outdir", type=str, default="atp_matches", help="Output directory for CSV files.")
    args = p.parse_args()
    main(start_year=args.start, end_year=args.end, outdir=args.outdir)
