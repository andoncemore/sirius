from flask.ext import login

from sirius.models import user

manager = login.LoginManager()


@manager.user_loader
def load_user(user_id):
    return user.User.query.get(user_id)

@manager.request_loader
def load_user_from_request(request):
    api_key = request.args.get('api_key')
    if api_key:
        selected_user = user.User.query.filter_by(api_key=api_key).first()
        if selected_user and selected_user.api_key != None:
            return selected_user
    return None
