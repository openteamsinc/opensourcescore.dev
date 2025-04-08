from fastapi.testclient import TestClient
from unittest.mock import ANY
from .app import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "version": ANY,
        "html_docs_url": "https://opensourcescore.dev/docs",
        "source_code_url": ANY,
    }
