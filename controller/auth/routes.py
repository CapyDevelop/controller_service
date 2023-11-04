import auth_service.authservice_pb2 as pb2
from flask import request

from controller import auth_service_stub

from . import auth


def validate_login_data(data):
    if not data.get("username") or not data.get("password"):
        return None
    return data


@auth.post("/login")
def login():
    data = validate_login_data(request.json)
    if not data:
        return {
            "status": "FAIL",
            "status_code": 2,
            "message": "Not such data",
            "data": {}
        }, 400
    username = data["username"]
    password = data["password"]
    grpc_request = pb2.LoginRequest(username=username, password=password)
    grpc_response = auth_service_stub.login(grpc_request)
    if grpc_response.status != 0:
        return {
            "status": "FAIL",
            "status_code": 1,
            "message": grpc_response.description,
            "data": {}
        }, 401
    return {
        "status": "OK",
        "status_code": 0,
        "message": "Success",
        "data": {}
    }
