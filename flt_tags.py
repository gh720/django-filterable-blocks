from django import template
from django.template.base import FilterExpression, kwarg_re
from django.utils.safestring import mark_safe
import sys

register = template.Library()


def interpolate(parser, tokens):
    args = []
    kwargs = {}
    for token in tokens:
        match = kwarg_re.match(token)
        if match:
            kwargs[match.group(1)] = FilterExpression(match.group(2), parser)
        else:
            args.append(FilterExpression(token, parser))
    return (args, kwargs)


def do_filterable(parser, input, endblock):
    tokens = input.split_contents()
    tag_name = tokens.pop(0)
    block_tags = ['.']
    if tokens:
        block_tags = [btag for btag in tokens.pop(0).split(',') if btag != '']

    args, kwargs = interpolate(parser, tokens)

    if endblock:
        nodelist = parser.parse(('endflt_block',))
        parser.delete_first_token()
        return FilterableBlock(set(block_tags), nodelist)
    else:
        value = tokens[0] if tokens else ''
        return FilterableVar(set(block_tags), value[1:-1])


def do_flt_block(parser, token):
    return do_filterable(parser, token, True)


def do_flt_var(parser, token):
    return do_filterable(parser, token, False)


def get_filter_tags(context):
    tags = context.get('flt_tags', 'gen')
    return set(tags.split(','))

def block_filter(diag, filter_tags, block_tags):
    diag.setdefault('tags_used', dict())
    diag.setdefault('tags_not_used', dict())
    include=False
    for tag in block_tags:
        if tag in filter_tags:
            include=True
            diag['tags_not_used'].pop(tag,None)
            diag['tags_used'].setdefault(tag,1)
        elif tag not in diag['tags_used']:
            print ('not used: %s' % (tag), file=sys.stderr)
            diag['tags_not_used'].setdefault(tag,1)
    return include

class FilterableVar(template.Node):

    def __init__(self, block_tags, str_value):
        self.block_tags = block_tags
        self.str_value = str_value

    def render(self, context):
        config = context.get('config', {})
        include = block_filter(context.get('diag', {}), get_filter_tags(context), self.block_tags)
        if (include):
            return mark_safe(self.str_value or '')
        elif config.get('comment'):
            return mark_safe('<!--%s-->' % (self.str_value or ''))
        return ''


class FilterableBlock(template.Node):
    def __init__(self, block_tags, nodelist):
        self.block_tags = block_tags
        self.nodelist = nodelist

    def render(self, context):
        config = context.get('config', {})
        include = block_filter(context.get('diag', {}), get_filter_tags(context), self.block_tags)
        if (include):
            content = self.nodelist.render(context)
            return content
        elif config.get('comment'):
            content = self.nodelist.render(context)
            return '<!--%s-->' % (content)
        return ''
    
register.tag('flt_block', do_flt_block)
register.tag('flt_var', do_flt_var)
