import os
from flask import Blueprint, render_template

from bio3dbeacon.database.models import ModelStructure

frontend_bp = Blueprint('frontend_bp', __name__,
                        template_folder='templates', static_folder='static')


@frontend_bp.route('/')
def index():
    return render_template('index.html', title='Home')


@frontend_bp.route('/apidocs', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_root():
    return render_template('api.html', title='API')


@frontend_bp.route('/browse')
def browse():
    models = ModelStructure.query.all()
    for m in models:
        m.original_basename = os.path.basename(m.original_path)

    return render_template('browse.html', models=models, title='Browse')


@frontend_bp.route('/add_data')
def add_data():
    return render_template('add_data.html', title='Add Data')


@frontend_bp.route('/about')
def about():
    return render_template('about.html', title='About')
