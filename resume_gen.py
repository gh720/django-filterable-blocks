import django
from django.conf import settings
from django import template
from django.template import Context, Template
import argparse
import sys

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
parser.add_argument('-t','--tags', required=True)
args, uargs = parser.parse_known_args()

tags = set( (args.tags or '.').split(','))

with open(uargs[0], 'r', encoding='utf-8') as f:
    tpl = f.read()

template = Template(tpl)
context = Context({"flt_tags": ','.join(tags)})
result = template.render(context)
out = str(result) # strip('\ufeff')
sys.stdout.buffer.write(out.encode('utf-8'))
sys.stdout.flush()

