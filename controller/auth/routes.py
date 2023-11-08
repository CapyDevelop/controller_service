import logging

import auth_service.authservice_pb2 as pb2
from flask import make_response, request

from controller import auth_service_stub

from . import auth

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s')


def validate_login_data(data):
    if not data.get("username") or not data.get("password"):
        logging.info("Not such data")
        return None
    return data


@auth.post("/login")
def login():
    logging.info("[ | API | Login ] - Login request. ----- START -----")
    data = validate_login_data(request.json)
    if not data:
        logging.info("[ | API | Login ] - Not such data. ----- END -----")
        return {
            "status": "FAIL",
            "status_code": 2,
            "message": "Not such data",
            "data": {}
        }, 400
    username = data["username"]
    password = data["password"]
    logging.info("[ | API | Login ] - Start request to auth_server")
    grpc_request = pb2.LoginRequest(username=username, password=password)
    grpc_response = auth_service_stub.login(grpc_request)
    logging.info("[ | API | Login ] - Receive response from auth_server")
    if grpc_response.status != 0:
        logging.info("[ | API | Login ] - Error response from rRPC server. ----- END -----")
        return {
            "status": "FAIL",
            "status_code": 1,
            "message": grpc_response.description,
            "data": {}
        }
    logging.info("[ | API | Login ] - Success response from rRPC server. ----- END -----")
    response = make_response({
        "status": "OK",
        "status_code": 0,
        "message": "Success",
        "data": {}
    })
    response.set_cookie("capy-uuid", grpc_response.uuid,
                        samesite="None", secure=True)
    return response


@auth.get("/check_signin")
def check_signin():
    is_uuid = request.cookies.get("capy-uuid")
    print(is_uuid)
    if not is_uuid:
        return {
            "status": "FAIL",
            "status_code": 2,
            "message": "Not enough uuid",
            "data": {}
        }, 200
    return {
        "status": "OK",
        "status_code": 0,
        "message": "Success",
        "data": {}
    }, 200


@auth.get("/logout")
def logout():
    is_uuid = request.cookies.get("capy-uuid")
    print(is_uuid)
    if not is_uuid:
        return {
            "status": "FAIL",
            "status_code": 2,
            "message": "Not enough uuid",
            "data": {}
        }, 200
    response = make_response({
        "status": "OK",
        "status_code": 0,
        "message": "Success",
        "data": {}
    })
    response.set_cookie("capy-uuid", "", samesite="None", secure=True)
    return response
