import auth_service.authservice_pb2 as pb2

from controller import auth_service_stub

from . import api


@api.get("/test")
def test():
    grpc_request = pb2.LoginRequest(username="test", password="test")
    grpc_response = auth_service_stub.login(grpc_request)
    return grpc_response.description
