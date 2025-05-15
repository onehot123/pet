from flask import Blueprint, render_template, request

pet_info_bp = Blueprint('pet_info', __name__, url_prefix='/pet_info')

@pet_info_bp.route('/')
def index():
    return render_template('pet_info/index.html') 