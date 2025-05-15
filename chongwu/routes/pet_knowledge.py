from flask import Blueprint, render_template, request

pet_knowledge_bp = Blueprint('pet_knowledge', __name__, url_prefix='/pet_knowledge')

@pet_knowledge_bp.route('/')
def index():
    return render_template('pet_knowledge/index.html') 