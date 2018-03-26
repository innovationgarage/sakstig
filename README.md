# An objectpath query engine

SakStig is an [objectpath](http://objectpath.org) implementation that uses proper querysets and supports querying
any python object that supports the dict or list interfaces (the default implementation only supports the real dict and list types).

# Example usage

    cat test.json | python sakstig.py "$.store.book.*.price + 3"

In test.json:

    {
	    "store": {
		    "book": [
			    {"price": 4},
			    {"price": 5}
        ]
      }
    }
    
          
