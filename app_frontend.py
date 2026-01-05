import os
import requests
from flask import Flask, render_template, jsonify

# 自動鎖定路徑，避免 Windows 系統路徑錯誤
base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
            static_folder=os.path.join(base_dir, 'frontend', 'static'),
            template_folder=os.path.join(base_dir, 'frontend', 'templates'))

# 1. 頁面路由：負責顯示網頁
@app.route('/')
def index():
    return render_template('index.html')

# 2. 數據 API：負責提供數據給圖表與地圖
@app.route('/api/data')
def get_data():
    # app.py 模擬數據部分
    data = {
    "ranking": {
        "labels": ["項目 C", "項目 D", "項目 B", "項目 G", "項目 E", "項目 F", "項目 A"],
        "values": [92, 85, 78, 70, 63, 55, 45]
    },
    "charts": {
        "section1": {"labels": ["類別 A", "B", "C", "D"], "values": [400, 300, 300, 200]},
        "section2": {"labels": ["一月", "二月", "三月", "四月", "五月", "六月"], "values": [400, 300, 600, 800, 500, 900]},
        "section3": {"labels": ['週一', '週二', '週三', '週四', '週五'],
            "main": [200, 300, 250, 400, 350], 
            "sub": [150, 220, 180, 350, 280],
            "stats": {"growth": "+23%", "peak": "400"}
        },
        "section4": {"labels": ["數學", "中文", "英文", "地理", "物理", "歷史"], "values": [120, 98, 86, 99, 85, 65]},
        "section5": {
            "labels": ["一月", "二月", "三月", "四月"],
            "prodA": [45, 59, 80, 81],
            "prodB": [28, 48, 40, 19]
        },
        "section6": {
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "external": [30, 45, 35, 50],
            "internal": [20, 25, 20, 30],
            "other": [10, 15, 10, 10]
        },
        "section7": [
            {"x": 10, "y": 20}, {"x": 15, "y": 10}, {"x": 20, "y": 30},
            {"x": 25, "y": 25}, {"x": 30, "y": 40}, {"x": 35, "y": 35}
        ]
    },
    "map": {
        "USA": 850, "CHN": 720, "JPN": 450,
        "DEU": 380, "BRA": 290, "AUS": 210, "QAT": 150
    },
    "map_names": {  
        "USA": "美國", "CHN": "中國", "JPN": "日本", 
        "DEU": "德國", "BRA": "巴西", "AUS": "澳洲", 
        "QAT": "卡達", "TWN": "台灣"
    },
    "tables": {
        "table1": [["一月", "125k", "+12%"], ["二月", "142k", "+8%"]],
        "table2": [["產品 A", "1234", "4.8"], ["產品 B", "987", "4.5"]]
        }
    }
    
    return jsonify(data)

# # API連線寫法
# BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:8000')

# @app.route('/api/data')
# def get_data():
#     try:
#         # 後端拼接 API 路徑
#         # 注意：埠號要改成 8000
#         target_url = f"{BACKEND_URL}/api/backend_mysql_route" 
        
#         response = requests.get(target_url, timeout=5)
        
#         if response.status_code == 200:
#             return jsonify(response.json())
#         return jsonify({"error": "Backend API error"}), 500
#     except Exception as e:
#         return jsonify({"error": f"Connection failed: {str(e)}"}), 500

if __name__ == '__main__':
    # 啟動開發伺服器
    app.run(debug=True, host='0.0.0.0', port=3000)