import requests
from pathlib import Path
from unittest.mock import Mock

from from_fhwa.downloader import download_dataset
from from_fhwa.state_fips_rec import StateDataset


def test_download_dataset_creates_file(tmp_path, monkeypatch):
    """
    Verify that download_dataset:
    - Downloads content from the URL
    - Saves it using the filename from the URL
    - Writes bytes correctly
    """

    # --- Arrange ---
    fake_content = b"test file contents"

    mock_response = Mock()
    mock_response.iter_content = lambda chunk_size: [fake_content]
    mock_response.raise_for_status = Mock()

    def mock_get(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(requests, "get", mock_get)

    dataset = StateDataset(
        state_abbr="CA",
        year=2024,
        dataset_type="bridge_element_data",
        url="https://example.com/test_file.zip",
    )


    # --- Act ---
    downloaded_path = download_dataset(dataset, tmp_path)

    # --- Assert ---
    assert downloaded_path.exists()
    assert downloaded_path.name == "test_file.zip"
    assert downloaded_path.read_bytes() == fake_content
