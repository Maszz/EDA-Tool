from app_manager import AppManager

# Create the app instance
app_manager = AppManager()
app = app_manager.app

if __name__ == "__main__":
    app.run_server(debug=True)
