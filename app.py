from flask import Flask, render_template, jsonify, request
import psutil
import platform
import json
import os
from datetime import datetime

# ============ 初始化应用 ============
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
CONFIG_FILE = os.path.expanduser('~/.lxjai_config.json')

# ============ 配置管理 ============
def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {
        "api_key": "YOUR_API_KEY",
        "model": "gpt-3.5-turbo",
        "security_level": 2,
        "timeout": 30
    }

def save_config(config):
    """保存配置文件"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

# ============ 路由定义 ============
@app.route('/')
def index():
    """主控制面板"""
    return render_template('dashboard.html')

@app.route('/api/status')
def system_status():
    """获取系统状态"""
    return jsonify({
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "os": f"{platform.system()} {platform.release()}",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/config', methods=['GET', 'POST'])
def config_manager():
    """配置管理接口"""
    if request.method == 'GET':
        return jsonify(load_config())
    elif request.method == 'POST':
        new_config = request.json
        current_config = load_config()
        current_config.update(new_config)
        save_config(current_config)
        return jsonify({'status': 'success'})

@app.route('/api/execute', methods=['POST'])
def execute_command():
    """执行命令接口"""
    command = request.json.get('command', '')
    return jsonify({
        "result": f"Executed: {command}",
        "timestamp": datetime.now().isoformat()
    })

# ============ 运行入口 ============
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
