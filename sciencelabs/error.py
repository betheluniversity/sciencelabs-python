# Packages
from flask import render_template
from flask import session as flask_session

# Local
from sciencelabs import app, sentry


def error_render_template(template_path, error, code=None):
    sentry.captureException()

    if code:
        if code in [500, 503]:
            if not app.config['UNIT_TESTING']:
                app.logger.error("%s -- %s" % flask_session['username'], str(error))

    else:
        app.logger.error('Unhandled Exception: %s', str(error))
        code = 500

    return render_template(template_path,
                           sentry_event_id=sentry.last_event_id,
                           public_dsn=sentry.client.get_public_dsn('https')), code


@app.errorhandler(403)
def permission_denied(e):
    return error_render_template('error/403.html', e, 403)


@app.errorhandler(404)
def page_not_found(e):
    return error_render_template('error/404.html', e, 404)


@app.errorhandler(500)
def server_error(e):
    return error_render_template('error/500.html', e, 500)


@app.errorhandler(503)
def transport_error(e):
    return error_render_template('error/503.html', e, 503)
