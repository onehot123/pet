from flask import Flask, render_template
from routes.pet_info import pet_info_bp
from routes.pet_knowledge import pet_knowledge_bp  
from routes.pet_hospital import pet_hospital_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# 注册蓝图
app.register_blueprint(pet_info_bp)
app.register_blueprint(pet_knowledge_bp)
app.register_blueprint(pet_hospital_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True) 