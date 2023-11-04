from flask import Flask
from flask_cors import CORS

CORS_ORIGIN = [
    "http://localhost:3000",
    "http://localhost:5000",
]

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=CORS_ORIGIN)

from controller.api import api

app.register_blueprint(api)
