import os

from dotenv import load_dotenv

from controller import app

if __name__ == "__main__":
    load_dotenv()
    app.run(host='0.0.0.0', port=os.getenv("PORT"), debug=os.getenv("DEBUG"))
