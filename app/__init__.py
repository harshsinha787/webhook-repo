from flask import Flask

from app.webhook.routes import webhook

from app.extensions import mongo


# Creating our flask app
def create_app():

    app = Flask(__name__)
    # Configure URL for a local database named webhook_db
    app.config["MONGO_URI"] = "mongodb://localhost:27017/webhook_db"
    # Initialize mongo with app
    mongo.init_app(app)
    
    # registering all the blueprints
    app.register_blueprint(webhook)
    
    return app
