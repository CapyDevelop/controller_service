import logging

import election_service.election_grpc_pb2 as election_pb2
import user_service.user_service_pb2 as user_pb2
from flasgger import swag_from
from flask import make_response, request

from controller import election_service_stub, user_service_stub

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


@api.get("/mock_candidates")
def candidates():
    avatars = [
        "https://s0.rbk.ru/v6_top_pics/media/img/5/90/756781807819905.webp",
        "https://www.newsler.ru/data/content/2022/124529/fa587f34b2eef1d2847300e8472d702f.RPPkxCdwIDkMKjtWDnCVwqu5LZH6AC7uLkE_vf0uMbo",
        "https://cdn.iportal.ru/news/2015/99/preview/373040953a4a814a9f983988a24f4a2b06e70980_1280_853_c.jpg",
        "https://static.tildacdn.com/tild3762-3361-4530-b338-636461613366/1663115153_50-mykale.jpg",
        "https://media.tinkoff.ru/stories/media/images/744dcd9447deeb0a8f10e024eb8616e5.png",
        "https://cdn-st1.rtr-vesti.ru/vh/pictures/hd/413/562/0.jpg",
        "https://natworld.info/wp-content/uploads/2018/02/vodosvinka-ili-kapibara.jpg"
    ]
    nicknames = [
        "cherylls",
        "wilfredo",
        "suzibill",
        "arrowwhi",
        "garroshm",
        "sharnasv",
        "victarim"
    ]
    abouts = [
        "Lorem ipsum dolor sit amet, consectetur adipisicing elit. A architecto deserunt est facilis harum illo incidunt minima modi nobis, obcaecati officiis provident quas, quasi quis reiciendis sapiente sunt temporibus, vero!",
        "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Eligendi nobis sunt, ullam ut velit voluptatibus! Ad blanditiis debitis dolores et explicabo, fuga id odio placeat rerum sunt? Ab, aspernatur aut, cupiditate, deserunt labore laboriosam mollitia nam officia repudiandae temporibus voluptas voluptates voluptatibus. Fugiat in, maxime nesciunt porro quas qui unde.",
        "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Corporis earum enim et facere fugit illo inventore nisi quae totam vitae. Amet corporis est ex libero molestiae nemo nulla sequi sunt!",
        "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Eligendi, fugiat?",
        """Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aliquid, neque, numquam? Commodi consectetur consequatur ducimus, ea eaque ex fuga id ipsa laborum nihil omnis, quibusdam quis similique, sint tenetur velit vero? Ducimus eius error et illo ipsa, itaque laudantium obcaecati quidem repellendus repudiandae rerum sapiente, tenetur voluptatum. At consectetur dicta dolorum eaque laboriosam quasi recusandae. Accusantium aspernatur consectetur, 
        distinctio maiores minus possimus qui? Aliquam amet blanditiis, dignissimos eius ipsum laudantium molestiae nobis quam reprehenderit tempore! Ab aperiam aspernatur at commodi, dolorum eius, fugit iusto laboriosam laborum natus obcaecati quisquam reiciendis rerum sapiente soluta totam voluptate voluptates. Amet asperiores ipsam sapiente?""",
        "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Ex facere magni tenetur. Ab adipisci amet consequuntur debitis esse est eum exercitationem ipsam, labore laborum, minus nihil, obcaecati officia officiis provident quis quisquam ratione rem repellat sapiente sequi sint sit totam veniam voluptatum? Accusantium aliquam, aliquid beatae, consequatur dolore ducimus enim eos eum explicabo natus nesciunt nihil porro quisquam rem repellat reprehenderit similique unde voluptatum? Dolor expedita itaque neque, odio quas ut voluptatem? Neque sint, voluptates.",
        "Lorem ipsum dolor sit amet, consectetur adipisicing elit. A ad asperiores assumenda delectus deserunt dolorem, dolorum et eum ex exercitationem explicabo facere illum inventore labore laboriosam libero mollitia nam nulla officia provident quam quasi quod reiciendis repellat sunt ullam vel. Ab consectetur debitis dignissimos, distinctio doloribus eaque illum libero perferendis ratione rerum sed sequi temporibus.",
    ]
    return {
        "status": 0,
        "data": [{
            "image": avatars[i],
            "nickname": nicknames[i],
            "about": abouts[i]
        } for i in range(7)]
    }
