# coding: utf-8
import django
from django.conf import settings
from django import template

from unittest import TestCase

if not settings.configured:
    settings.configure(TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': False,
            'OPTIONS': {
                'libraries': {
                    'filterable_blocks': 'filterable_blocks',
                },
                'builtins': ['filterable_blocks'],
            },
        },
    ])

django.setup()

class test_base_c(TestCase):

    def setUp(self):
        pass

    def render(self,ctx_data):
        context = template.Context(ctx_data)
        result = self.template.render(context)
        return str(result)


class tests_logic_c(test_base_c):

    def setUp(self):
        super().setUp()
        self.diag = {}
        self.template = template.Template('''
            {% flt_var i1 'inclusion1' %}
            {% flt_var i1,i2,i3 'inclusion123' %}
            {% flt_var i1,i4 'inclusion14' %}
            {% flt_var i4 'inclusion4' %}
            {% flt_var x1 'exclusion1' %}
            {% flt_var x1,x2,x3 'exclusion123' %}
            {% flt_var x1,x4 'exclusion14' %}
            {% flt_var x4 'exclusion4' %}
        ''')

    def test_inclusion(self):
        diag = {};config = {}
        for ctx_data in ([
            {"include": 'i1,i2,i3', 'diag': diag, 'config': config}
            , {"include": 'i3,i1,i2', 'diag': diag, 'config': config}
            ]):
            result = self.render(ctx_data)
            msg = "inclusion test failed for: %s" % (str(ctx_data))
            self.assertRegex(result, r'\binclusion1\b', msg=msg)
            self.assertRegex(result, r'\binclusion123\b', msg=msg)
            self.assertRegex(result, r'\binclusion14\b', msg=msg)
            self.assertNotRegex(result, r'\binclusion4\b', msg=msg)

    def test_exclusion(self):
        diag = {};config = {}
        for ctx_data in ([
            {"include": 'i1,i2,i3,x1,x2,x3,x4', "exclude": 'x1,x2,x3', 'diag': diag, 'config': config}
        ]):
            result = self.render(ctx_data)
            msg = "exclusion test failed for: %s" % (str(ctx_data))
            self.assertRegex(result, r'\binclusion14\b', msg=msg)
            self.assertNotRegex(result, r'\binclusion4\b', msg=msg)
            self.assertRegex(result, r'\bexclusion4\b', msg=msg)
            self.assertNotRegex(result, r'\bexclusion(?!4)\d+\b', msg=msg)


class tests_nesting_c(test_base_c):

    def setUp(self):
        super().setUp()
        self.diag = {}
        self.template = template.Template('''
        {% flt_var i1 'inclusion1' %}
        {% flt_block i1 %}inc_block1{% end_flt_block %}
        {% flt_block i1,i2 %}
            {% flt_var i1 'nested1_inclusion1_should_render' %} 
            {% flt_var i2 'nested1_inclusion2_should_not_render' %}
        {% end_flt_block %}
        {% flt_block i1 %}
            block_should_render
            {% flt_block i2 %}
                {% flt_block i1 %}
                    block_should_not_render
                {% end_flt_block %}
            {% end_flt_block %}
        {% end_flt_block %}
        ''')

    def test_nesting(self):
        diag = {};config = {}
        for ctx_data in ([
            {"include": 'i1', 'diag': diag, 'config': config}
        ]):
            result = self.render(ctx_data)
            msg = "nesting test failed for: %s" % (str(ctx_data))
            self.assertNotRegex(result, r'should_not_render', msg=msg)
            self.assertRegex(result, r'\bnested1_inclusion1_should_render\b', msg=msg)
            self.assertRegex(result, r'\bblock_should_render\b', msg=msg)



class tests_options_c(test_base_c):

    def setUp(self):
        super().setUp()
        self.diag = {}
        self.template = template.Template('''
            {% flt_var i1 'inclusion1' %}
            {% flt_var i1,i2,i3 'inclusion123' %}
            {% flt_var i1,i4 'inclusion14' %}
            {% flt_var i4 'inclusion4' %}
        ''')

    def test_comment(self):
        diag = {};config = {'comment':1}
        for ctx_data in ([
            {"include": 'i1,i2,i3', 'diag': diag, 'config': config}
            ]):
            result = self.render(ctx_data)
            msg = "inclusion test failed for: %s" % (str(ctx_data))
            self.assertRegex(result, r'<!--inclusion4-->', msg=msg)

