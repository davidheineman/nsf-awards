import argparse
import os
import requests
import zipfile
import json
import pandas as pd
from io import BytesIO

from tqdm import tqdm
from datasets import Dataset
from huggingface_hub import login

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

NSF_URL = "https://www.nsf.gov/awardsearch/download?DownloadFileName={year}&All=true&isJson=true"

def download_nsf_awards(current_dir, min_year=1960, max_year=None):
    """Download NSF award data"""
    current_year = pd.Timestamp.now().year
    if max_year is None:
        max_year = current_year

    data_dir = os.path.join(current_dir, "data") 
    os.makedirs(data_dir, exist_ok=True)

    years = range(min_year, max_year + 1)
    pbar = tqdm(years, desc="Downloading NSF awards")
    for year in pbar:
        pbar.set_description(f"Downloading year {year}")
        
        year_dir = os.path.join(data_dir, str(year))
        os.makedirs(year_dir, exist_ok=True)

        url = NSF_URL.format(year=year)

        response = requests.get(url)
        if response.status_code == 200:
            with zipfile.ZipFile(BytesIO(response.content)) as z:
                z.extractall(year_dir)
        else:
            print(f"Failed to download data for year {year}")


def load_nsf_awards_to_df(current_dir, parquet_path):
    """Load NSF JSON into DataFrame"""
    all_data = []
    data_dir = os.path.join(current_dir, "data")

    # Get total number of files for progress bar
    total_files = sum(
        len([f for f in os.listdir(os.path.join(data_dir, year_dir)) if f.endswith('.json')])
        for year_dir in os.listdir(data_dir)
        if os.path.isdir(os.path.join(data_dir, year_dir))
    )

    with tqdm(total=total_files, desc="Loading NSF awards") as pbar:
        for year_dir in os.listdir(data_dir):
            year_path = os.path.join(data_dir, year_dir)
            if os.path.isdir(year_path):
                for filename in os.listdir(year_path):
                    if filename.endswith('.json'):
                        file_path = os.path.join(year_path, filename)
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            all_data.append(data)
                        pbar.update(1)

    df = pd.DataFrame(all_data)

    df.to_parquet(parquet_path)

    return df


def push_to_hub(parquet_path, dataset_name):
    """Push dataframe to HF"""
    df = pd.read_parquet(parquet_path)

    dataset = Dataset.from_pandas(df)
    
    login(new_session=False)
    dataset.push_to_hub(
        dataset_name,
        private=False
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download and process NSF awards data')
    parser.add_argument('--min-year', type=int, default=1960,
                        help='Minimum year to download data from (default: 1960)')
    parser.add_argument('--max-year', type=int, default=None,
                        help='Maximum year to download data from (default: None)')
    parser.add_argument('--repo', type=str, default="davidheineman/nsf-awards",
                        help='HuggingFace repository to upload to (default: davidheineman/nsf-awards)')
    args = parser.parse_args()

    parquet_path = os.path.join(DATA_DIR, "nsf.parquet")

    download_nsf_awards(DATA_DIR, min_year=args.min_year, max_year=args.max_year)
    df = load_nsf_awards_to_df(DATA_DIR, parquet_path)
    print(df.head())
    push_to_hub(parquet_path, args.repo)