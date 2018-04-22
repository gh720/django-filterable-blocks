# coding: utf-8
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
        'APP_DIRS': False,
        'OPTIONS': {
            'libraries': {
                'filterable_blocks': 'filterable_blocks.filterable_blocks',
            },
            'builtins': [ 'filterable_blocks.filterable_blocks'] ,
        },
    },
])

django.setup()

register = template.Library()

parser = argparse.ArgumentParser()
parser.add_argument('-c','--comment', action='store_true', required=False)
parser.add_argument('-t','--tags', required=True)
args, uargs = parser.parse_known_args()

include_set=set()
exclude_set=set()
for tag in (args.tags or '.').split(','):
    if not tag:
        continue
    elif tag[0]=='!':
        exclude_set.add(tag[1:])
    else:
        include_set.add(tag)

with open(uargs[0], 'r', encoding='utf-8') as f:
    tpl = f.read()

template = Template(tpl)

diag = {}
config = {}
if args.comment:
    config['comment']=1
ctx_data = {"include": include_set, 'exclude': exclude_set, 'diag': diag, 'config': config }

context = Context(ctx_data)

result = template.render(context)
out = str(result)
sys.stdout.buffer.write(out.encode('utf-8'))
sys.stdout.flush()
pp(diag, stream=sys.stderr)


