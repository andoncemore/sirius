import os
import datetime
import flask
import logging
from gevent import pool
import flask_login as login
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
import twitter as twitter_api

from sirius.models import user as user_model
from sirius.models.db import db

logger = logging.getLogger(__name__)

api_key=os.environ.get('TWITTER_CONSUMER_KEY', 'DdrpQ1uqKuQouwbCsC6OMA4oF')
api_secret=os.environ.get('TWITTER_CONSUMER_SECRET', 'S8XGuhptJ8QIJVmSuIk7k8wv3ULUfMiCh9x1b19PmKSsBh1VDM')

# TODO move the consumer_key/secret to flask configuration. The
# current key is a test app that redirects to 127.0.0.1:8000.
blueprint = make_twitter_blueprint(
    api_key=api_key,
    api_secret=api_secret,
)

# @blueprint.route('/twitter/login')
# def twitter_login():
#     # Clear token, see https://github.com/mitsuhiko/flask-oauth/issues/48:
#     flask.session.pop('twitter_token', None)
#     flask.session.pop('twitter_screen_name', None)

#     return twitter.authorize(callback=flask.url_for('twitter_oauth.oauth_authorized',
#         next=flask.request.args.get('next') or flask.request.referrer or None))

@blueprint.route('/twitter/logout')
def twitter_logout():
    flask.session.pop('user_id', None)
    flask.flash('You were signed out')
    return flask.redirect('/')


def process_authorization(token, token_secret, screen_name, next_url):
    """Process the incoming twitter oauth data. Validation has already
    succeeded at this point and we're just doing the book-keeping."""

    flask.session['twitter_token'] = (token, token_secret)
    flask.session['twitter_screen_name'] = screen_name

    oauth = user_model.TwitterOAuth.query.filter_by(
        screen_name=screen_name,
    ).first()

    # Create local user model for keying resources (e.g. claim codes)
    # if we haven't seen this twitter user before.
    if oauth is None:
        new_user = user_model.User(
            username=screen_name,
        )

        oauth = user_model.TwitterOAuth(
            user=new_user,
            screen_name=screen_name,
            token=token,
            token_secret=token_secret,
            last_friend_refresh=datetime.datetime.utcnow(),
        )

        # Fetch friends list from twitter. TODO: error handling.
        friends = get_friends(new_user)
        oauth.friends = friends

        db.session.add(new_user)
        db.session.add(oauth)
        db.session.commit()

    login.login_user(oauth.user)

    flask.flash("Successfully signed in! Hi, @%s." % screen_name)

    return flask.redirect(next_url)


def get_friends(user):
    return get_friends_using_tokens(oauth_token=user.twitter_oauth.token, oauth_token_secret=user.twitter_oauth.token_secret)

def get_friends_using_tokens(oauth_token, oauth_token_secret):
    api = twitter_api.Twitter(auth=twitter_api.OAuth(
        oauth_token,
        oauth_token_secret,
        api_key,
        api_secret,
    ))
    # Twitter allows lookup of 100 users at a time so we need to
    # chunk:
    chunk = lambda l, n: [l[x:x+n] for x in range(0, len(l), n)]
    friend_ids = list(api.friends.ids()['ids'])

    greenpool = pool.Pool(4)

    # Look up in parallel. Note that twitter has pretty strict 15
    # requests/second rate limiting.
    friends = []
    for result in greenpool.imap(
            lambda ids: api.users.lookup(user_id=','.join(str(id) for id in ids)),
            chunk(friend_ids, 100)):
        for r in result:
            friends.append(user_model.Friend(
                screen_name=r['screen_name'],
                name=r['name'],
                profile_image_url=r['profile_image_url'],
            ))

    return sorted(friends)


@oauth_authorized.connect_via(blueprint)
def twitter_logged_in(blueprint, token):
    # TODO: I think this comes via sesstion these days?
    next_url = flask.request.args.get('next') or '/'

    if token is None:
        flask.flash("Twitter didn't authorize our sign-in request.", category="error")
        return flask.redirect(next_url)

    process_authorization(
        token['oauth_token'],
        token['oauth_token_secret'],
        token['screen_name'],
        next_url,
    )

    return False

# notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def twitter_error(blueprint, message, response):
    logger.debug("we got a problem")
    msg = (
        "OAuth error from {name}! "
        "message={message} response={response}"
    ).format(
        name=blueprint.name,
        message=message,
        response=response,
    )
    logger.debug(msg)
    flask.flash(msg, category="error")