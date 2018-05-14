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

    localhost$ sakstig "$.store.book.*.price + 3" test.json
    7
    8
    9

    >>> with open("test.json") as f:
    ...    for result in sakstig.QuerySet([f.read()]).execute("$.store.book.*.price + 3"):
    ...        print result
    7
    8
    9
