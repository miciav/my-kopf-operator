import pytest
from unittest.mock import MagicMock, patch
from operator.handlers import create_fn, update_fn, delete_fn, check_pods
import kr8s


@pytest.fixture
def mock_kr8s_api():
    """Fixture to mock the kr8s API."""
    with patch('kr8s.api') as mock_api:
        yield mock_api


@pytest.mark.asyncio
async def test_create_fn(mock_kr8s_api):
    """Test the create handler."""
    mock_api_instance = MagicMock()
    mock_kr8s_api.return_value = mock_api_instance

    spec = {
        'replicas': 2,
        'image': 'nginx',
        'port': 80,
        'expose': True,
        'checkIntervalSeconds': 30
    }
    name = 'test-app'
    namespace = 'default'
    logger = MagicMock()

    result = create_fn(spec, name, namespace, logger)

    assert result == {'status': 'created'}
    assert mock_api_instance.create.call_count == 2  # Deployment and Service


@pytest.mark.asyncio
async def test_update_fn(mock_kr8s_api):
    """Test the update handler."""
    mock_api_instance = MagicMock()
    mock_kr8s_api.return_value = mock_api_instance

    mock_deployment = MagicMock()
    mock_api_instance.get.return_value = mock_deployment

    spec = {
        'replicas': 3,
        'image': 'nginx:latest',
        'port': 8080,
        'expose': True,
        'checkIntervalSeconds': 60
    }
    name = 'test-app'
    namespace = 'default'
    logger = MagicMock()

    result = update_fn(spec, {}, name, namespace, logger)

    assert result == {'status': 'updated'}
    assert mock_api_instance.patch.call_count == 1
    assert mock_deployment.spec.replicas == 3


@pytest.mark.asyncio
async def test_delete_fn(mock_kr8s_api):
    """Test the delete handler."""
    mock_api_instance = MagicMock()
    mock_kr8s_api.return_value = mock_api_instance

    name = 'test-app'
    namespace = 'default'
    logger = MagicMock()

    result = delete_fn(name, namespace, logger)

    assert result == {'status': 'deleted'}
    assert mock_api_instance.delete.call_count == 2  # Deployment and Service


@pytest.mark.asyncio
async def test_check_pods_timer(mock_kr8s_api):
    """Test the timer function for checking pods."""
    mock_api_instance = MagicMock()
    mock_kr8s_api.return_value = mock_api_instance

    mock_deployment = MagicMock()
    mock_deployment.status = {'readyReplicas': 1}
    mock_api_instance.get.return_value = mock_deployment

    spec = {'replicas': 2, 'checkIntervalSeconds': 30}
    name = 'test-app'
    namespace = 'default'
    logger = MagicMock()
    body = {
        "metadata": {
            "name": name,
            "namespace": namespace
        }
    }

    result = await check_pods(spec, name, namespace, {}, logger, body=body)

    assert 'Warning' in result['status']
