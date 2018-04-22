# Filterable blocks for the Django template engine.

This project stems from an adhoc effort to make a filterable template based on standalone use of the Django templating engine.

It implements Django template tags named `flt_block` and `flt_var`.
I call them blocks for the rest of this document.

## The idea:


* Assign a block a set of block tags, which are just words (don't confuse them for Django tags).
* Choose what blocks to include into a rendering by specifying a set of filter tags (just words too).

**Example template (test.tpl):**

    {% flt_block in1,in2 %}
        included if inclusion tags have in1 or in2
        {% flt_var in1 'included if in1 is in the inclusion tags' %}
        {% flt_var in2 'included if in2 is in the inclusion tags ' %}
        {% flt_block in1,ex1 %}
            This one would not be included if ex1 is in the exclusion tags
            {% flt_block in1 %}
                If the parent has not been included in the rendering the child won't be too.
            {% end_flt_block %}
        {% end_flt_block %}
    {% end_flt_block %}

There are inclusion and exclusion filter tags.  
If an exclusion or inclusion tag set has common elements with a block tag set than the block is excluded or included correspondingly.  
Exclusion has a priority over inclusion. 
By default all blocks are excluded.

**Given the the above template:**

Running p3 template_gen.py  -t in1 test.tpl produces:

    included if inclusion tags have in1 or in2
    included if in1 is in the inclusion tags

        This one would not be included if ex1 is in the exclusion tags

            If the parent has not been included in the rendering the child won't be too.

Running p3 template_gen.py  -t in1,!ex1 test1.tpl produces:

    included if inclusion tags have in1 or in2
    included if in1 is in the inclusion tags

### Tests can be run like:

`python -m unittest tests.test`
