from flask import Flask
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from app.config import Config
from app.routes.login import login_bp
from app.routes.dashboard import dashboard_bp
from app.routes.signup import signup_bp
from app.blocklist import BLOCKLIST
from app.routes.earthquake_detection import earthquake_bp
from app.routes.claim_insurance import claim_bp
# Initialize extensions (without app context)
jwt = JWTManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with app context
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Register Blueprints
    app.register_blueprint(login_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(signup_bp)
    app.register_blueprint(earthquake_bp)
    app.register_blueprint(claim_bp) 
    # Check if token is revoked
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return jti in BLOCKLIST

    # Response for revoked tokens
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"msg": "Token has been revoked"}), 401

    return app

