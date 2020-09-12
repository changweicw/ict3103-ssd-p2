#not using, gave up trying to use assets and blueprints

from flask import current_app as app
from flask_assets import Bundle


def compile_static_assets(assets):
    assets.auto_build = True
    assets.debug = False

    common_bundle = Bundle(
        'assets/css/*.min.css',
        'assets/css/vendor/*.min.css',
        output='style/css/styles.css'
    )

    js = Bundle(
        'assets/js/main.js',
        'assets/js/plugins.min.js',
        'assets/js/vendor/jquery-3.5.1.min.js',
        'assets/js/vendor/modernizr-3.7.1.min.js',
        output='gen/packed.js'
    )

    assets.register('js_all', js)
    assets.register('cs_all',common_bundle)
    common_bundle.build()
    js.build()
    return assets