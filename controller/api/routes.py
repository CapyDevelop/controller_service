import logging
import time

import election_service.election_grpc_pb2 as election_pb2
import storage.storage_service_pb2 as storage_pb2
import user_service.user_service_pb2 as user_pb2
from flasgger import swag_from
from flask import make_response, request
from werkzeug.utils import secure_filename

from controller import (election_service_stub, storage_service_stub,
                        user_service_stub)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s')

from controller.utils import generate_response

from . import api


@swag_from({
    "tags": ["User"],
    "description": "Get user data",
    "parameters": [
        {
            "name": "capy-uuid",
            "in": "cookie",
            "type": "string",
            "required": True,
        }
    ],
    "responses": {
        "200": {
            "description": "OK",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["OK", "FAIL"],
                        "example": "OK"
                    },
                    "description": {
                        "type": "string",
                        "example": "Success"
                    },
                    "data": {
                        "type": "object",
                        "properties": {
                            "coins": {
                                "type": "integer",
                                "example": 100
                            },
                            "prp": {
                                "type": "integer",
                                "example": 100
                            },
                            "crp": {
                                "type": "integer",
                                "example": 100
                            },
                            "level": {
                                "type": "integer",
                                "example": 1
                            },
                            "first_name": {
                                "type": "string",
                                "example": "Ivan"
                            },
                            "last_name": {
                                "type": "string",
                                "example": "Ivanov"
                            },
                            "login": {
                                "type": "string",
                                "example": "ivanov"
                            }
                        }
                    },
                    "status_code": {
                        "type": "integer",
                        "example": 0
                    }
                }
            }
        },
        "401": {
            "description": "Unauthorized",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["FAIL"],
                        "example": "FAIL"
                    },
                    "description": {
                        "type": "string",
                        "example": "Unauthorized"
                    },
                    "data": {
                        "type": "object",
                        "properties": {}
                    },
                    "status_code": {
                        "type": "integer",
                        "example": 10
                    }
                }
            }
        }
    }
})
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
    req = user_pb2.GetAvatarRequest(capy_uuid=capy_uuid)
    res = user_service_stub.get_avatar(req)
    avatar = None
    if not res or not res.avatar:
        logging.info("[ | API | GET USER DATA ] - No Set avatar. Take default ----- END -----")
        avatar = "https://capyavatars.storage.yandexcloud.net/avatar/default/default.webp"
    else:
        logging.info("[ | API | GET USER DATA ] - Avatar set ----- END -----")
        avatar = f"https://capyavatars.storage.yandexcloud.net/avatar/{capy_uuid}/{res.avatar}"
    logging.info("[ | API | GET USER DATA ] - Success response from user_service (get_rp method). ----- END -----")
    data = {
        "coins": rp_response.coins,
        "prp": rp_response.prp,
        "crp": rp_response.crp,
        "level": rp_response.level,
        "first_name": rp_response.first_name,
        "last_name": rp_response.last_name,
        "login": rp_response.login,
        "avatar": avatar
    }
    return generate_response(data=data)


@api.get("/check_election")
def check_election():
    election_request = election_pb2.Empty()
    election_response = election_service_stub.GetElection(election_request)
    return generate_response(data={"election_status": election_response.status})


@api.get("/check_uuid")
def check_uuid():
    tmp_uuid = request.cookies.get("tmp-uuid")
    capy_uuid = request.cookies.get("capy-uuid")
    print(tmp_uuid, capy_uuid)
    if not tmp_uuid and not capy_uuid:
        return {"status": 1}

    return {"status": 0}


@api.post("/register_candidate")
def register_candidate():
    tmp_uuid = request.cookies.get("tmp-uuid")
    capy_uuid = request.cookies.get("capy-uuid")

    about = request.json.get("about")

    if not tmp_uuid and not capy_uuid:
        return {"status": 1}

    if not about:
        return {"status": 2}

    if tmp_uuid:
        req = election_pb2.SetCandidateRequest(uuid=tmp_uuid, about=about)
        res = election_service_stub.SetCandidateTmp(req)
        return {"status": res.status, "description": res.description}
    if capy_uuid:
        req = election_pb2.SetCandidateRequest(uuid=capy_uuid, about=about)
        res = election_service_stub.SetCandidateCapy(req)
        return {"status": res.status, "description": res.description}


@api.get("/check_register")
def check_register():
    tmp_uuid = request.cookies.get("tmp-uuid")
    capy_uuid = request.cookies.get("capy-uuid")

    print(tmp_uuid, capy_uuid)

    if not tmp_uuid and not capy_uuid:
        return {"status": 0}

    if tmp_uuid:
        req = election_pb2.CheckCandidateRequest(uuid=tmp_uuid)
        res = election_service_stub.CheckCandidateTmp(req)
        return {"status": res.status}
    elif capy_uuid:
        req = election_pb2.CheckCandidateRequest(uuid=capy_uuid)
        res = election_service_stub.CheckCandidateCapy(req)
        return {"status": res.status}


@api.post("/send_code")
def send_mail():
    nickname = request.json.get("nickname")
    if not nickname:
        return {"status": 1}

    req = election_pb2.SendPasswordRequest(mail=nickname)
    res = election_service_stub.SendPassword(req)

    return {"status": res.status, "description": res.description}


@api.post("/confirm_code")
def confirm_code():
    nickname = request.json.get("nickname")
    code = request.json.get("code")

    if not nickname or not code:
        return {"status": 1, "description": "Недостаточно данных"}

    req = election_pb2.ConfirmPasswordRequest(mail=nickname, password=code)
    res = election_service_stub.ConfirmPassword(req)
    response = make_response({
        "status": res.status,
        "description": res.description
    })
    response.set_cookie("tmp-uuid", res.uuid,
                        samesite="None", secure=True)
    return response


@api.get("/candidates")
def candidates():
    print("req")
    data = election_service_stub.GetCandidates(election_pb2.Empty())
    return {
        "status": data.status,
        "data": [{
            "avatar": candidate.avatar,
            "id": candidate.id,
            "about": candidate.about,
            "login": candidate.login
        } for candidate in data.candidates],
        "description": data.description
    }


@api.post("/vote")
def vote():
    tmp_uuid = request.cookies.get("tmp-uuid")
    capy_uuid = request.cookies.get("capy-uuid")

    id = request.json.get("id")

    print(tmp_uuid, capy_uuid)

    if not tmp_uuid and not capy_uuid:
        return {"status": 1, "description": "Вы не авторизованы для этой операции"}

    if not id:
        return {"status": 1, "description": "Не указано за кого голосовать"}

    if tmp_uuid:
        req = election_pb2.VoteRequest(uuid=tmp_uuid, candidate_id=id)
        res = election_service_stub.VoteTmp(req)
        return {
            "status": res.status,
            "description": res.description
        }
    if capy_uuid:
        req = election_pb2.VoteRequest(uuid=capy_uuid, candidate_id=id)
        res = election_service_stub.VoteCapy(req)
        return {
            "status": res.status,
            "description": res.description
        }


@api.get("/my_voice")
def my_voice():
    tmp_uuid = request.cookies.get("tmp-uuid")
    capy_uuid = request.cookies.get("capy-uuid")

    print(tmp_uuid, capy_uuid)

    if not tmp_uuid and not capy_uuid:
        return {"status": 1, "description": "Вы не авторизованы для этой операции", "data": [], "count": 0}

    if tmp_uuid:
        req = election_pb2.MyCandidateRequest(uuid=tmp_uuid)
        res = election_service_stub.MyCandidatesTmp(req)
        return {
            "data": [{
                "avatar": candidate.avatar,
                "id": candidate.id,
                "about": candidate.about,
                "login": candidate.login
            } for candidate in res.candidates],
            "status": res.status,
            "count": res.count,
            "description": res.description
        }
    if capy_uuid:
        req = election_pb2.MyCandidateRequest(uuid=capy_uuid)
        res = election_service_stub.MyCandidatesCapy(req)
        return {
            "data": [{
                "avatar": candidate.avatar,
                "id": candidate.id,
                "about": candidate.about,
                "login": candidate.login
            } for candidate in res.candidates],
            "status": res.status,
            "count": res.count,
            "description": res.description
        }


@api.get("/vote_statistic")
def vote_statistic():
    tmp_uuid = request.cookies.get("tmp-uuid")
    capy_uuid = request.cookies.get("capy-uuid")

    print(tmp_uuid, capy_uuid)

    if not tmp_uuid and not capy_uuid:
        return {"status": 1,
                "description": "Вы не авторизованы для этой операции",
                "data": {},
                "all_capybaras": 0,
                "count_voter": 0,
                "percent_voter": 0}

    res = election_service_stub.GetStatistic(election_pb2.Empty())
    return {
        "status": 0,
        "description": "OK",
        "data": [{
            "nickname": i.nickname,
            "count": i.count,
            "percent": i.percent
        } for i in res.candidates],
        "all_capybaras": res.all_capybaras,
        "count_voter": res.count_voter,
        "percent_voter": res.percent_voter
    }


def prepare(file, capy_uuid, filename):
    while True:
        piece = file.read(1024)
        if not piece:
            break
        yield storage_pb2.PutRequest(uuid=capy_uuid, filename=filename, data=piece)


@api.post("/upload")
def upload():
    capy_uuid = request.cookies.get("capy-uuid")

    if not capy_uuid:
        return {"status": 1, "description": "Вы не авторизованы для этой операции"}

    avatar = request.files.get("avatar")

    if not avatar:
        return {"status": 1, "description": "Не указан файл"}

    fn = secure_filename(avatar.filename)
    fn_ext = fn.rsplit('.', 1)[1].lower() if '.' in fn else ''
    t = time.time()
    filename = f'{int(t)}.{fn_ext}' if fn_ext else str(int(t))
    res = storage_service_stub.Put(prepare(avatar, capy_uuid, filename))

    return {"status": res.status, "description": res.description}
