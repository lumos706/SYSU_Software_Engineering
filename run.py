from app import create_app
from flask import url_for
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
