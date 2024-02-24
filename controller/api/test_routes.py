from unittest.mock import patch

import pytest
from election_service import election_grpc_pb2
from user_service import user_service_pb2

from controller import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_get_user_data_no_cookie(client):
    response = client.get('/api/get_user_data')
    assert response.status_code == 401
    assert response.json == {
        "status": "FAIL",
        "status_code": 10,
        "description": "No cookie",
        "data": {}
    }


@patch("controller.user_service_stub.get_rp")
@patch("controller.user_service_stub.get_avatar")
def test_get_user_data_with_cookie(mock_get_avatar, mock_get_rp, client):
    mock_get_rp.return_value = user_service_pb2.GetRpResponse(
        coins=100,
        prp=100,
        crp=100,
        level=1,
        first_name="Test",
        last_name="Test",
        login="test",
        status=0,
        description="Success"
    )
    mock_get_avatar.return_value = user_service_pb2.GetAvatarResponse(
        status=0,
        description="Success",
        avatar="test"
    )
    client.set_cookie('capy-uuid', 'test_uuid')
    response = client.get('/api/get_user_data')
    print(response.json)
    assert response.status_code == 200
    assert response.json == {
        "status": "Success",
        "status_code": 0,
        "description": "Success",
        "data": {
            "coins": 100,
            "prp": 100,
            "crp": 100,
            "level": 1,
            "first_name": "Test",
            "last_name": "Test",
            "login": "test",
            "avatar": "https://capyavatars.storage.yandexcloud.net/avatar/test_uuid/test"
        }
    }


def test_check_election_ok(client):
    mock_election_response = election_grpc_pb2.GetElectionResponse(status=0)
    with patch('controller.election_service_stub.GetElection', return_value=mock_election_response) as mock_get_election:
        response = client.get('/api/check_election')
        assert response.status_code == 200
        mock_get_election.assert_called_once()
        assert response.json == {
            "status": "Success",
            "status_code": 0,
            "description": "Success",
            "data": {
                "election_status": 0
            }
        }


def test_check_election_error(client):
    mock_election_response = election_grpc_pb2.GetElectionResponse(status=1)
    with patch('controller.election_service_stub.GetElection', return_value=mock_election_response) as mock_get_election:
        response = client.get('/api/check_election')
        assert response.status_code == 200
        mock_get_election.assert_called_once()
        assert response.json == {
            "status": "Success",
            "status_code": 0,
            "description": "Success",
            "data": {
                "election_status": 1
            }
        }
