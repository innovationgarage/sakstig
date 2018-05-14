# An objectpath query and templating engine

SakStig is an [objectpath](http://objectpath.org) implementation that uses proper querysets and supports querying
any python object that supports the dict or list interfaces (the default implementation only supports the real dict and list types).

## SakStig Example usage

    localhost$ sakstig "$.store.book.*.price + 3" examples/test.json
    7
    8
    9

In test.json:

    {
	    "store": {
		    "book": [
			    {"price": 4, "title": "foo"},
			    {"price": 5, "title": "bar"},
			    {"price": 6, "title": "fie"},
        ]
      }
    }
    
### QuerySets

A QuerySet is simply a list of (intermediate) query results. At each step of the query execution, a QuerySet is processed, creating a new QuerySet. The operation might be to just filter the QuerySet, or to map entries into say their children, or to form a new QuerySet containing all the children of all the elements of the previous QuerySet.

    import sakstig
    results = sakstig.QuerySet([my_data]).execute("$.store.book.*[@.price > 4].title")
    for result in results:
        print result

As can be seen above, not only does a query return a QuerySet, it also takes one as input, meaning the first thing you have to do when using SakStig is to construct a QuerySet.

Note that while a QuerySet inherits from the python list type, it isn't to be seen as a list. In particular, if your query matches a single node in your data that is a list, execute() will return a QuerySet with one element that is that list. Warning: This is different from other objectpath implementations!

## SakForm templating

A SakForm template is a valid JSON document. It is applied to a data
JSON document to produce an output JSON document. Values in the
template are copied to the output verbatim, except for the special
object member "$", which allows you to do powerfull transformations
using SakStig expressions.

* [SakForm examples](SakForm_examples.md)
* [SakForm semantics](SakForm_semantics.md)
