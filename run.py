"""
启动文件
用于启动后端 API 服务
"""
from api.app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

