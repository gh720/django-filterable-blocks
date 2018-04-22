import django
from django.conf import settings
from django import template
from django.template import Context, Template
import argparse
import sys

from pprint import pprint as pp

settings.configure(TEMPLATES=[
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': False, # we have no apps
        'OPTIONS': {
            'libraries': {
                'flt_tags': 'flt_tags',
            },
            'builtins': [ 'flt_tags'] ,
        },
    },
])

django.setup()

register = template.Library()

parser = argparse.ArgumentParser()
parser.add_argument('-c','--comment', action='store_true', required=False)
parser.add_argument('-t','--tags', required=True)
args, uargs = parser.parse_known_args()

tags = set( (args.tags or '.').split(','))

with open(uargs[0], 'r', encoding='utf-8') as f:
    tpl = f.read()

template = Template(tpl)

diag = {}
config = {}
if args.comment:
    config['comment']=1
ctx_data = {"flt_tags": ','.join(tags), 'diag': diag, 'config': config }

context = Context(ctx_data)

result = template.render(context)
out = str(result) # strip('\ufeff')
sys.stdout.buffer.write(out.encode('utf-8'))
sys.stdout.flush()
pp(diag, stream=sys.stderr)


