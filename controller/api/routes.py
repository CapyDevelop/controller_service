import logging

import user_service.user_service_pb2 as user_pb2
from flask import make_response, request

from controller import user_service_stub

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s')

from controller.utils import generate_response

from . import api


@api.get("/get_user_data")
def get_user_data():
    logging.info("[ | API | GET USER DATA ] - Get user data request. ----- START -----")
    capy_uuid = request.cookies.get("capy-uuid")
    logging.info(f"[ | API | GET USER DATA ] - READ COOKIE - UUID: {capy_uuid}")
    if not capy_uuid:
        logging.info("[ | API | GET USER DATA ] - Not such cookie. ----- END -----")
        return generate_response(status_code=10), 401
    logging.info("[ | API | GET USER DATA ] - Start request to user_service (get_rp method)")
    rp_request = user_pb2.GetRpRequest(capy_uuid=capy_uuid)
    rp_response = user_service_stub.get_rp(rp_request)
    logging.info("[ | API | GET USER DATA ] - Receive response from user_service (get_rp method)")
    if rp_response.status == 13:
        logging.info("[ | API | GET USER DATA ] - Error response from user_service (get_rp method). ----- END -----")
        response = make_response(generate_response(status="FAIL", status_code=13,
                                                   description="Ваш токен устарел. Необходимо авторизоваться заново"))
        response.set_cookie("capy-uuid", "", samesite="None", secure=True)
        return response, 200
    if rp_response.status != 0:
        logging.info("[ | API | GET USER DATA ] - Error response from user_service (get_rp method). ----- END -----")
        return generate_response(status="FAIL", status_code=1, description=rp_response.description), 401
    logging.info("[ | API | GET USER DATA ] - Success response from user_service (get_rp method). ----- END -----")
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
