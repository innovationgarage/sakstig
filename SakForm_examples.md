We'll be using the following test.json for all examples below:

    {
	    "store": {
		    "book": [
			    {"price": 4, "title": "foo"},
			    {"price": 5, "title": "bar"},
			    {"price": 6, "title": "fie"},
        ]
      }
    }

# Examples
In its simplest form, $ allows you to extract a value from the data
document:

    >>> sakform.transform(data,
    ...     {"price": {"$": "$.store.book[0].price"},
    ...      "description": "First book price"})
    {"price": 4, "description": "First book price"}

Normally, if the exression returns multiple matches, only the first
one is used. However, whenever {"$": "expression"} is used inside a
list, all results are merged into the list:

    >>> sakform.transform(data,
    ...    {"prices": [47, {"$": "$.store.book.*.price"}, 11],
    ...     "description": "Book prices"})
    {"prices": [47, 4, 5, 6, 11], "description": "Book prices"}

If the object containing '$' also contains other members, a mapping is
performed on the matches, replacing them with an object with those
members. The matched object is however available as @template() from
within SakStig expressions inside these members:

    >>> sakform.transform(data,
    ...    {"books": [{
    ...        "$": "$.store.book.*",
    ...        "BOOK_PRICE": {"$": "@template().price"}}]})
    {"books": [{"BOOK_PRICE": 4}, {"BOOK_PRICE": 5}, {"BOOK_PRICE": 6}]}
