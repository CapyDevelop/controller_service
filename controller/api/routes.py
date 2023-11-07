import user_service.user_service_pb2 as user_pb2
from flask import request

from controller import user_service_stub

from . import api
from controller.utils import generate_response


@api.get("/get_user_data")
def get_user_data():
    capy_uuid = request.cookies.get("capy-uuid")
    if not capy_uuid:
        return generate_response(status_code=10), 401
    rp_request = user_pb2.GetRpRequest(capy_uuid=capy_uuid)
    rp_response = user_service_stub.get_rp(rp_request)
    if rp_response.status != 0:
        return generate_response(status="FAIL", status_code=1, description=""), 401
    data = {
        "coins": rp_response.coins,
        "prp": rp_response.prp,
        "crp": rp_response.crp,
        "level": rp_response.level,
        "first_name": rp_response.first_name,
        "last_name": rp_response.last_name,
        "login": rp_response.login,
    }
    return generate_response(data=data)
