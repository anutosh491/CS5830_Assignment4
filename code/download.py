import subprocess
import os
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import yaml

def download_data(base_url, year, download_directory, output_file_path, max_download_count):
    # Retrieve HTML page with CSV file links for a specific year
    target_url = base_url + str(year)
    subprocess.run(["curl", "-L", "-o", output_file_path, target_url])

    # Read and parse the downloaded HTML file
    with open(output_file_path, 'r') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract CSV links based on memory criteria
    csv_links = []
    for row in soup.find_all('tr')[2:]:  # Skip header rows
        cells = row.find_all('td')
        if cells and cells[2].text.endswith('M'):  # Check for memory size in MB
            file_link = urljoin(target_url + '/', cells[0].text.strip())
            file_size = float(cells[2].text.replace('M', '').strip())
            csv_links.append((file_link, file_size))

    # Filter and limit the CSV links by file size
    filtered_links = [link for link, size in csv_links if size > 45][:max_download_count]

    # Create directory for downloading files
    os.makedirs(download_directory, exist_ok=True)

    # Download CSV files that meet the criteria
    for link in filtered_links:
        response = requests.get(link)
        if response.status_code == 200:
            filename = os.path.join(download_directory, os.path.basename(link))
            download_file(response, filename)

def download_file(response, filename):
    # Download a file with progress indication
    total_size = int(response.headers.get('content-length', 0))
    progress = tqdm(total=total_size, unit='iB', unit_scale=True, desc=os.path.basename(filename))
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(1024):
            file.write(chunk)
            progress.update(len(chunk))
    progress.close()

def main():
    # Load configuration from YAML file
    config = yaml.safe_load(open("params.yaml"))
    download_data(
        base_url=config["data_source"]["base_url"],
        year=config["data_source"]["year"],
        download_directory=config["data_source"]["temp_dir"],
        output_file_path=config["data_source"]["output"],
        max_download_count=config["data_source"]["max_files"]
    )

if _name_ == "_main_":
    main()
