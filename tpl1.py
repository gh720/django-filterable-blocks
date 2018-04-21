import django
from django.conf import settings
from django import template
from django.template import Context, Template
from django.template.base import FilterExpression, kwarg_re
from django.template import TemplateSyntaxError
import argparse


settings.configure(TEMPLATES=[
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['.'], # if you want the templates from a file
        'APP_DIRS': False, # we have no apps
    },
])

django.setup()

register = template.Library()



parser = argparse.ArgumentParser()
#parser.add_argument('-f','--foo', help='Description', required=True)
#parser.add_argument('-b','--bar', help='Description', required=True)
args, uargs = parser.parse_known_args()



def parse_tag(input, parser):
    tokens = input.split_contents()
    tag_name = tokens.pop(0)
    args = []
    kwargs = {}
    for token in tokens:
        match = kwarg_re.match(token)
        if match:
            kwargs[match.group(1)]=FilterExpression(match.group(2), parser)
        else:
            args.append(FilterExpression(token, parser))
    return (tag_name, args, kwargs)

register.tag('replace', do_replace)


def do_replace(parser, token):
    tag_name, args, kwargs = parse_tag(token, parser)

    usage = '{% {tag_name} [limit] old="fromstring" new="tostring" %} ... {% end{tag_name} %}'.format(tag_name=tag_name)
    if len(args) > 1 or set(kwargs.keys()) != {'old', 'new'}:
        raise TemplateSyntaxError("Usage: %s" % usage)

    if args:
        limit = args[0]
    else:
        limit = FilterExpression('-1', parser)
    
    nodelist = parser.parse(('end_replace',))
    parser.delete_first_token()
    
    return ReplaceNode(nodelist, limit=limit, old=kwargs['from'], new=kwargs['to'])

class ReplaceNode(template.Node):
    
    def __init__(self, nodelist, limit, old, new):
        self.nodelist = nodelist
        self.limit = limit
        self.old = old
        self.new = new

    def render(self, context):  
        # Evaluate the arguments in the current context
        try:
            limit = int(self.limit.resolve(context))
        except (ValueError, TypeError):
            limit = -1

        from_string = self.old.resolve(context)
        to_string = conditional_escape(self.new.resolve(context))
# Those should be checked for stringness. Left as an exercise.

        content = self.nodelist.render(context)
        content = mark_safe(content.replace(from_string, to_string, limit))
        return content

register.tag('replace', do_replace)


with open(uargs, 'r'):
    tpl = r.read()

template = Template(tpl)
context = Context({"my_name": "Adrian"})
template.render(context)
# "My name is Adrian."
context = Context({"my_name": "Dolores"})
print (template.render(context))

