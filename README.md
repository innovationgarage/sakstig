# An objectpath query and templating engine

# Installation

Note: SakStig only supports Python 3.

    pip install sakstig
    
# SakStig path expressions
SakStig is an [objectpath](http://objectpath.org) implementation that uses proper querysets and supports querying
any python object that supports the dict or list interfaces (the default implementation only supports the real dict and list types).

* [SakStig examples](SakStig_examples.md)
* [SakStig semantics](SakStig_semantics.md)

## ObjectPath compatibility

You can turn off some of the [ObjectPath compatibility
features](CompatibilityOptions.md) to get more homogenous semantics.

## SakForm templating

A SakForm template is a valid JSON document. It is applied to a data
JSON document to produce an output JSON document. Values in the
template are copied to the output verbatim, except for the special
object member "$", which allows you to do powerfull transformations
using SakStig expressions.

* [SakForm examples](SakForm_examples.md)
* [SakForm semantics](SakForm_semantics.md)

# Tests

This repository uses the tests of ObjectPath to verify compatibility.
To run the tests you need to clone ObjectPath into a subdirectory of this repository:

    git clone git@github.com:adriank/ObjectPath.git
    pip install nose
    nosetests -v tests
