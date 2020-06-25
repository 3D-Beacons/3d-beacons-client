from flask import render_template

from . import frontend_bp


@frontend_bp.route('/')
@frontend_bp.route('/index')
def index():
    user = {'username': 'Ian'}
    return render_template('index.html', user=user)
