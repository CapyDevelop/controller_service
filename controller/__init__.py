import os

import auth_service.authservice_pb2_grpc as pb2_grpc
import grpc
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv


load_dotenv()
CORS_ORIGIN = [
    "*"
]

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=CORS_ORIGIN)

auth_service_channel = grpc.insecure_channel(
    f"{os.getenv('AUTH_SERVICE_HOST')}:{os.getenv('AUTH_SERVICE_PORT')}"
)
auth_service_stub = pb2_grpc.AuthServiceStub(auth_service_channel)

from controller.api import api

app.register_blueprint(api)

from controller.auth import auth

app.register_blueprint(auth)
