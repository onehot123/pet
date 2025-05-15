from flask import Blueprint, render_template, request, jsonify, current_app
import requests
import json

pet_hospital_bp = Blueprint('pet_hospital', __name__, url_prefix='/pet_hospital')

@pet_hospital_bp.route('/')
def index():
    return render_template('pet_hospital/index.html')

@pet_hospital_bp.route('/detail/<hospital_id>')
def detail(hospital_id):
    """宠物医院详情页"""
    # 这里可以从数据库或API获取医院详情数据
    # 示例数据
    hospital = {
        'id': hospital_id,
        'name': '爱宠动物医院',
        'address': '北京市朝阳区建国路88号',
        'phone': '010-12345678',
        'hours': '9:00-19:00 (周一至周日)',
        'website': 'www.aichongwu.com',
        'rating': 4.8,
        'image_url': None,  # 使用默认图片
        'services': ['常规体检', '疫苗接种', '绝育手术', '皮肤病治疗', '口腔保健', '寄养服务', 'X光检查', '血液检查', '微创手术'],
        'description': '爱宠动物医院成立于2010年，是一家专业的宠物医疗机构。医院拥有先进的医疗设备和经验丰富的兽医团队，致力于为您的宠物提供最专业的医疗服务。我们的宗旨是：爱心、责任、专业、创新。',
        'reviews': [
            {'author': '张先生', 'date': '2023-10-15', 'content': '医生很专业，环境也很好，给我家猫咪做了绝育手术，恢复得很好。', 'rating': 5},
            {'author': '李女士', 'date': '2023-09-28', 'content': '服务态度很好，价格合理，宠物看病很方便。', 'rating': 4},
            {'author': '王先生', 'date': '2023-08-15', 'content': '医生很耐心，解答了我很多关于宠物健康的问题，非常感谢。', 'rating': 5}
        ]
    }
    
    return render_template('pet_hospital/detail.html', hospital=hospital)

@pet_hospital_bp.route('/api/search', methods=['POST'])
def search_hospitals():
    """搜索宠物医院API"""
    data = request.get_json()
    city = data.get('city', '')
    keyword = data.get('keyword', '宠物医院')
    
    # 这里可以接入第三方API获取医院数据
    # 示例数据
    hospitals = [
        {
            'id': '1',
            'name': '爱宠动物医院',
            'address': f'{city}市朝阳区建国路88号',
            'phone': '010-12345678',
            'rating': 4.8,
            'lat': 39.9185,
            'lng': 116.4605
        },
        {
            'id': '2',
            'name': '康宠宠物医院',
            'address': f'{city}市海淀区中关村大街1号',
            'phone': '010-87654321',
            'rating': 4.6,
            'lat': 39.9825,
            'lng': 116.3167
        }
    ]
    
    return jsonify({
        'status': 'success',
        'data': hospitals
    }) 