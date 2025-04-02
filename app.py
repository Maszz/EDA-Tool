from app_manager import AppManager

# Create the app instance
app_manager = AppManager()
app = app_manager.app
server = app_manager.app.server  # Gunicorn requires a WSGI server object

if __name__ == "__main__":
    app.run(debug=True)
