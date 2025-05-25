import logging
import os

import pytest
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    path = os.path.join(str(pytestconfig.rootdir), "tests", "docker-compose.test.yml")
    assert os.path.isfile(path), f"docker-compose file not found: {path}"
    return path


def is_responsive(url):
    def _inner():
        try:
            logger.info(f"Checking if {url}/health is responsive...")
            response = requests.get(f"{url}/health", timeout=5)
            logger.info(f"Got response with status code: {response.status_code}")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.info(f"Request failed: {e}")
            return False

    return _inner


@pytest.fixture(scope="session")
def api_url(docker_ip, docker_services):
    """Get the URL for the API service."""
    host = docker_ip
    port = docker_services.port_for("api", 8000)
    url = f"http://{host}:{port}"

    logger.info(f"Waiting for API at {url} to be responsive...")
    try:
        docker_services.wait_until_responsive(
            timeout=30.0, pause=1.0, check=is_responsive(url)
        )
        logger.info(f"API at {url} is now responsive!")
        return url
    except Exception as e:
        logger.error(f"Timeout waiting for API: {e}")
        logger.info("Checking container status...")

        raise
