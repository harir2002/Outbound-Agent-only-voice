import sys
sys.path.insert(0, '.')

try:
    from app.core.config import settings
    with open('config_test_result.txt', 'w') as f:
        f.write("✅ Config loaded successfully!\n")
        f.write(f"Environment: {settings.ENVIRONMENT}\n")
        f.write(f"Backend Port: {settings.BACKEND_PORT}\n")
    print("Success! Check config_test_result.txt")
except Exception as e:
    with open('config_test_result.txt', 'w') as f:
        f.write(f"❌ Error: {type(e).__name__}\n")
        f.write(f"Message: {str(e)}\n\n")
        import traceback
        f.write(traceback.format_exc())
    print("Error! Check config_test_result.txt for details")
