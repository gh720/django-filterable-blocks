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
#parser.add_argument('-f','--foo', help='Description', required=True)
#parser.add_argument('-b','--bar', help='Description', required=True)
args, uargs = parser.parse_known_args()


with open(uargs[0], 'r', encoding='utf-8') as f:
    tpl = f.read()

# tpl_with_load = "{%% load flt_tags %%}%s" % (tpl)
template = Template(tpl)
context = Context({"my_name": "Adrian"})
template.render(context)
# "My name is Adrian."
context = Context({"my_name": "Dolores"})
result = template.render(context)
out = str(result)# strip('\ufeff')
sys.stdout.buffer.write(out.encode('utf-8'))
sys.stdout.flush()

