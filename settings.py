from os import environ, path
from otree import __version__
from settings_sessions import DEMO_SESSIONS

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc=""
)

# Language, currency and timezone settings
LANGUAGE_CODE = 'zh-hans'
REAL_WORLD_CURRENCY_CODE = 'CNY'
USE_POINTS = True
POINTS_DECIMAL_PLACES = 3
REAL_WORLD_CURRENCY_DECIMAL_PLACES = 2

USE_TZ = True
TIME_ZONE = 'Asia/Shanghai'

ROOMS = []

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = '^dsjjqrha$^-5%flo93!%+z^3ki$^_wq739ad6!#)1!ms*a6v2'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']

# ================ Show the branch on DEMO page ================
#                    (Do not modify below)
try:
    with open(path.join(path.dirname(__file__), '.git/HEAD')) as f:
        CUR_BRANCH = f.readline().strip().split('/')[-1].upper()
except Exception as e:
    print(e)
    print('This currently is not in a git-managed directory. (Default: MAIN)')
    CUR_BRANCH = 'MAIN'
notice = '' if CUR_BRANCH == 'MAIN' else \
    'Notice: This branch is <b class="text-danger">TEST-ONLY</b>.<br>'
DEMO_PAGE_INTRO_HTML = f"""
<h3>[{CUR_BRANCH}]</h3>
{notice}
oTree game platform.
oTree version: <code>{__version__}</code>
"""

# ================ Construct sessions in DEMO ================
#                    (Do not modify below)
# Select sessions according OTREE_SESSIONS in environment.
# If no OTREE_SESSIONS is configured, the default value is current branch and MAIN branch.
# Accepted value of OTREE_SESSIONS:
#     ALL
#     MAIN
#     DEV_*
#     etc.
_conf = environ.get('OTREE_SESSIONS',
                    default=CUR_BRANCH + ('' if CUR_BRANCH == 'MAIN' else ', MAIN')).strip().upper()
DEMO_SESSIONS_CONFIG = list(DEMO_SESSIONS.keys()) if _conf == 'ALL' else _conf.replace(' ', '').split(',')
DEMO_SESSIONS_CONFIG = list(filter(lambda x: x != 'MAIN', DEMO_SESSIONS_CONFIG)) + \
                       (['MAIN'] if 'MAIN' in DEMO_SESSIONS_CONFIG else list())

SESSION_CONFIGS = []
for demo_config in DEMO_SESSIONS_CONFIG:
    for session in DEMO_SESSIONS.get(demo_config, list()):
        session['display_name'] = ('' if demo_config == 'MAIN' else '[{}] '.format(demo_config)) + \
                                  session['display_name']
        SESSION_CONFIGS.append(session)

# Add default doc to 'doc'
