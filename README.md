# An objectpath query and templating engine engine

SakStig is an [objectpath](http://objectpath.org) implementation that uses proper querysets and supports querying
any python object that supports the dict or list interfaces (the default implementation only supports the real dict and list types).

## SakStig Example usage

    localhost$ sakstig "$.store.book.*.price + 3" examples/test.json
    7
    8

In test.json:

    {
	    "store": {
		    "book": [
			    {"price": 4},
			    {"price": 5}
        ]
      }
    }
    
          
## SakForm templating

A SakForm template is a valid JSON document. It is applied to a data
JSON document to produce an output JSON document. Values in the
template are copied to the output verbatim, except for the special
object member "$", which has special semantics and allows you to do
powerfull transformations using SakStig expressions.

We'll be using the same test.json from above for all examples below.

In its simplest form, $ allows you to extract a value from the data
document:

    >>> sakform.transform(data, {"price": {"$": "$.store.book[0].price"}, "description": "First book price"})
    {"price": 4, "description": "First book price"}

Normally, if the exression returns multiple matches, only the first
one is used. However, whenever {"$": "expression"} is used inside a
list, all results are merged into the list:

    >>> sakform.transform(data, {"prices": [47, {"$": "$.store.book.*.price"}, 11], "description": "Book prices"})
    {"prices": [47, 4, 5, 11], "description": "Book prices"}

If the object containing '$' also contains other members, a mapping is
performed on the matches, replacing them with an object with those
members. The matched object is however available as @template() from
within SakStig expressions inside these members:

    >>> sakform.transform(data, {"books": [{"$": "$.store.book.*", "BOOK_PRICE": {"$": "@template().price"}}]})
    {"books": [{"BOOK_PRICE": 4}, {"BOOK_PRICE": 5}]}

