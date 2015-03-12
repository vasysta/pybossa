from flask import Blueprint, render_template, current_app, abort, redirect, url_for, request, flash
from flask.ext.plugins import Plugin, connect_event
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext
from pybossa.core import newsletter as newsletter_service
from pybossa.core import user_repo

__plugin__ = "NewsletterPlugin"
__version__ = "0.0.1"


blueprint = Blueprint("newsletter", __name__)


@blueprint.route('/newsletter')
@login_required
def newsletter_subscribe():
    """
    Register method for subscribing user to PyBossa newsletter.

    Returns a Jinja2 template

    """
    # Save that we've prompted the user to sign up in the newsletter
    if newsletter_service.app and current_user.is_authenticated():
        next_url = request.args.get('next') or url_for('home.home')
        user = user_repo.get(current_user.id)
        if current_user.newsletter_prompted is False:
            user.newsletter_prompted = True
            user_repo.update(user)
        if request.args.get('subscribe') == 'True':
            newsletter_service.subscribe_user(user)
            flash("You are subscribed to our newsletter!")
            return redirect(next_url)
        elif request.args.get('subscribe') == 'False':
            return redirect(next_url)
        else:
            return render_template('account/newsletter.html',
                                   title=gettext("Subscribe to our Newsletter"),
                                   next=next_url)
    else:
        return abort(404)

def redirect_to_newsletter_subscribe_on_signin(data):
    user = data['user']
    next_url = data['next']
    if newsletter_service.app:
        if user.newsletter_prompted is False:
            if True:
                return redirect(url_for('newsletter.newsletter_subscribe',
                                        next=next_url))

def redirect_to_newsletter_subscribe_on_account_confirmation(data):
    if newsletter_service.app:
        return redirect(url_for('newsletter.newsletter_subscribe'))


class NewsletterPlugin(Plugin):

    def setup(self):
        current_app.register_blueprint(blueprint, url_prefix="/account")
        connect_event('user-signed-in', redirect_to_newsletter_subscribe_on_signin)
        connect_event('account-confirmed', redirect_to_newsletter_subscribe_on_account_confirmation)

    def install(self):
        pass
