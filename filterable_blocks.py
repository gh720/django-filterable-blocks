# coding: utf-8
from django import template
from django.template.base import FilterExpression, kwarg_re
from django.utils.safestring import mark_safe
from django.template.exceptions import TemplateSyntaxError

register = template.Library()


def interpolate(parser, tokens):
    ''' make django.template.Variable's from the input tokens '''
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
    ''' A Django template API function
        returns a django.template.None derived class
    '''
    tokens = input.split_contents()
    tag_name = tokens.pop(0)
    block_tags = ['.']
    if tokens:
        block_tags = [btag for btag in tokens.pop(0).split(',') if btag != '']

    args, kwargs = interpolate(parser, tokens)

    if endblock:
        nodelist = parser.parse(('end_flt_block',))
        parser.delete_first_token()
        return FilterableBlock(set(block_tags), nodelist)
    else:
        value = tokens[0] if tokens else ''
        return FilterableVar(set(block_tags), value[1:-1])


def do_flt_block(parser, token):
    return do_filterable(parser, token, True)

def do_flt_var(parser, token):
    return do_filterable(parser, token, False)

def get_include_tags(context):
    ''' Returns the set of inclusion tags from context '''
    tags = context.get('include', 'gen')
    return set(tags.split(','))


def get_exclude_tags(context):
    ''' Returns the set of exclusion tags from context '''
    tags = context.get('exclude', 'gen')
    return set(tags.split(','))


def block_filter(include_tags, exclude_tags, block_tags, diag):
    """ The function determines if a block needs to be included

    Args:
        include_tags set[str]: tags that should match block_tags for the block to be included
        exclude_tags set[str]: tags that should match block_tags for the block to be excluded

    Returns:
        bool: True - the block has to be included, False - otherwise

    """
    diag.setdefault('tags_used', dict())
    diag.setdefault('tags_not_used', dict())
    include = None
    exclude = None

    # 1. Exclusion has priority over inclusion.
    # 2. Exclusion is the default rule
    for tag in block_tags:
        if tag in exclude_tags:
            exclude = True
            diag['tags_not_used'].pop(tag, None)
            diag['tags_used'].setdefault(tag, 1)
        elif tag in include_tags:
            include = True
            diag['tags_not_used'].pop(tag, None)
            diag['tags_used'].setdefault(tag, 1)
        elif tag not in diag['tags_used']:
            diag['tags_not_used'].setdefault(tag, 1)

    if exclude is not None:
        return not exclude
    return include or False


class FilterableVar(template.Node):
    '''
    render a value from a flt_var tag  {% flt_var tags 'value' %}
    '''
    def __init__(self, block_tags, str_value):
        self.block_tags = block_tags
        self.str_value = str_value

    def render(self, context):
        config = context.get('config', {})
        i_tags = get_include_tags(context)
        x_tags = get_exclude_tags(context)
        include = block_filter(i_tags, x_tags, self.block_tags, context.get('diag', {}))
        if (include):
            return mark_safe(self.str_value or '')
        elif config.get('comment'):
            return mark_safe('<!--%s-->' % (self.str_value or ''))
        return ''


class FilterableBlock(template.Node):
    '''
    render contents of a flt_block tag  {% flt_block tags %} ... {% end_flt_block %}
    '''
    def __init__(self, block_tags, nodelist):
        self.block_tags = block_tags
        self.nodelist = nodelist

    def render(self, context):
        config = context.get('config', {})
        i_tags = get_include_tags(context)
        x_tags = get_exclude_tags(context)
        include = block_filter(i_tags, x_tags, self.block_tags, context.get('diag', {}), )
        if (include):
            content = self.nodelist.render(context)
            return content
        elif config.get('comment'):
            content = self.nodelist.render(context)
            return '<!--%s-->' % (content)
        return ''


register.tag('flt_block', do_flt_block)
register.tag('flt_var', do_flt_var)
