from flask import Blueprint, render_template, current_app, abort
from flask_plugins import Plugin
from flask.ext.login import login_required, login_user, logout_user, \
    current_user
from pybossa.core import newsletter

__plugin__ = "NewsletterPlugin"
__version__ = "0.0.1"


blueprint = Blueprint("newsletter", __name__)
print __name__


@blueprint.route('/newsletter')
@login_required
def newsletter_subscribe():
    """
    Register method for subscribing user to PyBossa newsletter.

    Returns a Jinja2 template

    """
    # Save that we've prompted the user to sign up in the newsletter
    if newsletter.app and current_user.is_authenticated():
        next_url = request.args.get('next') or url_for('home.home')
        user = user_repo.get(current_user.id)
        if current_user.newsletter_prompted is False:
            user.newsletter_prompted = True
            user_repo.update(user)
        if request.args.get('subscribe') == 'True':
            newsletter.subscribe_user(user)
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


class NewsletterPlugin(Plugin):

    def setup(self):
        current_app.register_blueprint(blueprint, url_prefix="/account")

    def install(self):
        print 'ole'

print NewsletterPlugin
