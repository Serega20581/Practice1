import os
import sys
import pytest

# ensure project root is on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from server import app as flask_app


@pytest.fixture
def client():
    with flask_app.test_client() as c:
        yield c


def test_health(client):
    rv = client.get('/health')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data.get('status') == 'ok'
