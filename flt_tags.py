from django import template
from django.template.base import FilterExpression, kwarg_re
from django.utils.safestring import mark_safe

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


def get_flt_tags(context):
    tags = context.get('flt_tags', 'gen')
    return set(tags.split(','))


# class FilterableVarBase(template.Node):

class FilterableVar(template.Node):

    def __init__(self, flt_tags, str_value):
        self.flt_tags = flt_tags
        self.str_value = str_value

    def render(self, context):
        tag_set = get_flt_tags(context)
        if (tag_set & self.flt_tags):
            return mark_safe(self.str_value or '')
        return ''


class FilterableBlock(template.Node):
    def __init__(self, flt_tags, nodelist):
        self.flt_tags = flt_tags
        self.nodelist = nodelist

    def render(self, context):
        # try:
        #     limit = int(self.limit.resolve(context))
        # except (ValueError, TypeError):
        #     limit = -1

        # from_string = self.old.resolve(context)
        # to_string = conditional_escape(self.new.resolve(context))
        # Those should be checked for stringness. Left as an exercise.
        tag_set = get_flt_tags(context)
        if (tag_set & self.flt_tags):
            content = self.nodelist.render(context)
            return content
        return ''

        # content = mark_safe(content.replace(from_string, to_string, limit))
        return content

register.tag('flt_block', do_flt_block)
register.tag('flt_var', do_flt_var)
