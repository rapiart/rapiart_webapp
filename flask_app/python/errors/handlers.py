from flask import Blueprint, render_template

errors = Blueprint('erros', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', title='Erro 404'), 404

@errors.app_errorhandler(405)
def error_405(error):
    return render_template('errors/404.html', title='Erro 405'), 405

@errors.app_errorhandler(400)
def error_400(error):
    return render_template('errors/404.html', title='Erro 400'), 400

@errors.app_errorhandler(500)
def error_500(error):
    return render_template('errors/404.html', title='Erro 500'), 500