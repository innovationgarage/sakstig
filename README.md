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
object member "$", which has special semantics and allows you to do
powerfull transformations using SakStig expressions.

### Examples
We'll be using the same test.json from above for all examples below.

In its simplest form, $ allows you to extract a value from the data
document:

    >>> sakform.transform(data, {"price": {"$": "$.store.book[0].price"}, "description": "First book price"})
    {"price": 4, "description": "First book price"}

Normally, if the exression returns multiple matches, only the first
one is used. However, whenever {"$": "expression"} is used inside a
list, all results are merged into the list:

    >>> sakform.transform(data, {"prices": [47, {"$": "$.store.book.*.price"}, 11], "description": "Book prices"})
    {"prices": [47, 4, 5, 6, 11], "description": "Book prices"}

If the object containing '$' also contains other members, a mapping is
performed on the matches, replacing them with an object with those
members. The matched object is however available as @template() from
within SakStig expressions inside these members:

    >>> sakform.transform(data, {"books": [{"$": "$.store.book.*", "BOOK_PRICE": {"$": "@template().price"}}]})
    {"books": [{"BOOK_PRICE": 4}, {"BOOK_PRICE": 5}, {"BOOK_PRICE": 6}]}

### Template semantics
A template consist of JSON entities which are evaluated recursively on some input queryset available as `$` to SakStig expressions. Initially, the template context `@template()` is set to the same as `$`. The output is a queryset.

#### The template is an object

* If the template contains a member named `$`, its value is evaluated as a SakStig expression, and @template()
  is set to the queryset result for the rest of the template evaluation (including recursive evaluations).
  Otherwize `@template()` is left unchanged.
* If the template does not contain any other members than `$`, the value of `@template()` is returned and evaluation ends.
* Each queryset entry in `@template()` is transformed and the resulting queryset returned:
 * A new empty output object is created.
 * For each member of the template:
  * The template member value is evaluated as a template recursively.
   * If the recursive evaluation generates an empty queryset, the member is ignored
   * Otherwize the a member with the same name is created in the output object and set to the first value of the queryset.

#### The template is an array
* Each array member is evaluated recursively as a template.
* All the resulting querysets are concatenated and converted into a JSON array
  which is returned as a single member of a queryset.

#### Other values
All other values are returned verbatim as a single member of a queryset.
