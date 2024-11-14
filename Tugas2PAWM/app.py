from app import create_app
from app.routes.progress_routes import progress_bp

app.register_blueprint(progress_bp, url_prefix='/progress')
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)


