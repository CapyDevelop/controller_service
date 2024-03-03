import os

import auth_service.authservice_pb2_grpc as auth_pb2_grpc
import coalition_service.coalition_service_pb2_grpc as coalition_pb2_grpc
import election_service.election_grpc_pb2_grpc as election_pb2_grpc
import grpc
import storage.storage_service_pb2_grpc as storage_pb2_grpc
import user_service.user_service_pb2_grpc as user_pb2_grpc
from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask
from flask_cors import CORS

load_dotenv()
CORS_ORIGIN = [
    "*"
]

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=CORS_ORIGIN)
Swagger(app)

auth_service_channel = grpc.insecure_channel(
    f"{os.getenv('AUTH_SERVICE_HOST')}:{os.getenv('AUTH_SERVICE_PORT')}"
)
auth_service_stub = auth_pb2_grpc.AuthServiceStub(auth_service_channel)

coalition_service_channel = grpc.insecure_channel(
    f"{os.getenv('COALITION_SERVICE_HOST')}:{os.getenv('COALITION_SERVICE_PORT')}"
)
coalition_service_stub = coalition_pb2_grpc.CoalitionServiceStub(coalition_service_channel)

user_service_channel = grpc.insecure_channel(
    f"{os.getenv('USER_SERVICE_HOST')}:{os.getenv('USER_SERVICE_PORT')}")
user_service_stub = user_pb2_grpc.UserServiceStub(user_service_channel)

election_service_channel = grpc.insecure_channel(
    f"{os.getenv('ELECTION_SERVICE_HOST')}:{os.getenv('ELECTION_SERVICE_PORT')}")
election_service_stub = election_pb2_grpc.ElectionServiceStub(election_service_channel)

storage_service_channel = grpc.insecure_channel(
    f"{os.getenv('STORAGE_SERVICE_HOST')}:{os.getenv('STORAGE_SERVICE_PORT')}")
storage_service_stub = storage_pb2_grpc.StorageServiceStub(storage_service_channel)

from controller.api import api

app.register_blueprint(api)

from controller.auth import auth

app.register_blueprint(auth)
