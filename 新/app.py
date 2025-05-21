from flask import Flask, render_template, url_for, request, flash, redirect
import os
import logging
import traceback
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from werkzeug.utils import secure_filename

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 用于flash消息

# 配置上传文件存储路径
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 数据库配置
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dogs.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定义数据模型
class DogBreed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    breed_id = db.Column(db.String(50), unique=True, nullable=False)  # 使用中文名作为ID
    chinese_name = db.Column(db.String(100), nullable=False)  # 中文名
    alias = db.Column(db.String(200))  # 别名
    origin = db.Column(db.String(100))  # 原产地
    weight = db.Column(db.String(100))  # 体重
    height = db.Column(db.String(100))  # 身高
    tail_feature = db.Column(db.String(200))  # 尾部特征
    eye_feature = db.Column(db.String(200))  # 眼睛特征
    ear_feature = db.Column(db.String(200))  # 耳朵特征
    coat_color = db.Column(db.String(200))  # 毛色
    function = db.Column(db.String(200))  # 功能
    image = db.Column(db.String(200))  # 图片文件名
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'breed_id': self.breed_id,
            'chinese_name': self.chinese_name,
            'alias': self.alias,
            'origin': self.origin,
            'weight': self.weight,
            'height': self.height,
            'tail_feature': self.tail_feature,
            'eye_feature': self.eye_feature,
            'ear_feature': self.ear_feature,
            'coat_color': self.coat_color,
            'function': self.function,
            'image': self.image
        }

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def import_from_excel(file_path):
    """从Excel文件导入数据到数据库"""
    try:
        # 读取Excel文件
        logger.info(f"开始读取Excel文件: {file_path}")
        df = pd.read_excel(file_path)
        
        # 验证必要的列是否存在
        required_columns = ['中文名', '别名', '原产地', '体重', '身高', '尾部特征', '眼睛特征', '耳朵特征', '毛色', '功能']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Excel文件缺少必要的列: {', '.join(missing_columns)}")
        
        # 导入数据到数据库
        success_count = 0
        update_count = 0
        
        for _, row in df.iterrows():
            # 使用中文名作为breed_id，转换为拼音或英文标识符
            chinese_name = str(row['中文名']).strip()
            breed_id = chinese_name.lower().replace(' ', '_')  # 这里可以添加中文转拼音的功能
            
            # 检查是否已存在
            existing_breed = DogBreed.query.filter_by(breed_id=breed_id).first()
            if existing_breed:
                # 更新现有记录
                existing_breed.chinese_name = chinese_name
                existing_breed.alias = str(row['别名'])
                existing_breed.origin = str(row['原产地'])
                existing_breed.weight = str(row['体重'])
                existing_breed.height = str(row['身高'])
                existing_breed.tail_feature = str(row['尾部特征'])
                existing_breed.eye_feature = str(row['眼睛特征'])
                existing_breed.ear_feature = str(row['耳朵特征'])
                existing_breed.coat_color = str(row['毛色'])
                existing_breed.function = str(row['功能'])
                update_count += 1
            else:
                # 创建新记录
                new_breed = DogBreed(
                    breed_id=breed_id,
                    chinese_name=chinese_name,
                    alias=str(row['别名']),
                    origin=str(row['原产地']),
                    weight=str(row['体重']),
                    height=str(row['身高']),
                    tail_feature=str(row['尾部特征']),
                    eye_feature=str(row['眼睛特征']),
                    ear_feature=str(row['耳朵特征']),
                    coat_color=str(row['毛色']),
                    function=str(row['功能']),
                    image=f"{breed_id}.jpg"  # 默认图片名称
                )
                db.session.add(new_breed)
                success_count += 1
        
        db.session.commit()
        logger.info(f"数据导入完成！新增: {success_count} 条, 更新: {update_count} 条")
        return True, f"数据导入成功！新增: {success_count} 条, 更新: {update_count} 条"
            
    except Exception as e:
        db.session.rollback()
        error_msg = f"导入失败: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return False, error_msg

def get_image_url(breed):
    """检查图片是否存在，如果不存在返回默认图片URL"""
    try:
        image_path = os.path.join('static', 'images', breed.image)
        logger.debug(f"Checking image path: {image_path}")
        if os.path.exists(image_path):
            return url_for('static', filename='images/' + breed.image)
        logger.warning(f"Image not found: {image_path}")
        return url_for('static', filename='images/default_dog.jpg')
    except Exception as e:
        logger.error(f"Error in get_image_url: {str(e)}")
        logger.error(traceback.format_exc())
        return url_for('static', filename='images/default_dog.jpg')

@app.route('/')
def index():
    try:
        logger.debug("Accessing index route")
        breeds = DogBreed.query.all()
        breeds_with_images = {
            breed.breed_id: {**breed.to_dict(), 'image_url': get_image_url(breed)}
            for breed in breeds
        }
        return render_template('index.html', breeds=breeds_with_images)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        logger.error(traceback.format_exc())
        return f"发生错误：{str(e)}", 500

@app.route('/breed/<breed_id>')
def breed_detail(breed_id):
    try:
        logger.debug(f"Accessing breed detail route for breed_id: {breed_id}")
        breed = DogBreed.query.filter_by(breed_id=breed_id).first()
        if breed:
            breed_dict = breed.to_dict()
            breed_dict['image_url'] = get_image_url(breed)
            return render_template('breed_detail.html', breed=breed_dict, breed_id=breed_id)
        return '品种未找到', 404
    except Exception as e:
        logger.error(f"Error in breed_detail route: {str(e)}")
        logger.error(traceback.format_exc())
        return f"发生错误：{str(e)}", 500

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error occurred: {str(error)}")
    logger.error(traceback.format_exc())
    return f"服务器内部错误：{str(error)}", 500

def init_db():
    """初始化数据库"""
    try:
        with app.app_context():
            # 检查数据库文件是否存在
            if not os.path.exists(db_path):
                logger.info("数据库文件不存在，正在创建...")
                db.create_all()
                logger.info("数据库创建成功！")
            else:
                logger.info("数据库文件已存在")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# 初始化数据库
init_db()

if __name__ == '__main__':
    app.run(debug=True) 