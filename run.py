from app import app

if __name__ == "__main__":
    print("Starting Flask application...")
    # 获取本机IP地址
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Please visit http://{local_ip}:5001 or http://127.0.0.1:5001")
    app.run(debug=True, port=5001, host='0.0.0.0') 