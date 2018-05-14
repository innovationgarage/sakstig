# An objectpath query and templating engine

# SakStig path expressions
SakStig is an [objectpath](http://objectpath.org) implementation that uses proper querysets and supports querying
any python object that supports the dict or list interfaces (the default implementation only supports the real dict and list types).

* [SakStig examples](SakStig_examples.md)
* [SakStig semantics](SakStig_semantics.md)

## SakForm templating

A SakForm template is a valid JSON document. It is applied to a data
JSON document to produce an output JSON document. Values in the
template are copied to the output verbatim, except for the special
object member "$", which allows you to do powerfull transformations
using SakStig expressions.

* [SakForm examples](SakForm_examples.md)
* [SakForm semantics](SakForm_semantics.md)
