
SakStig follows the semantics of [objectpath](http://objectpath.org) for the expressions themselves.
However, it deviates at the Python API level as well as philosophically by operating on (and returning) querysets
instead of individual objects.

A QuerySet is simply a list of (intermediate) query results. At each step of the query execution, a QuerySet is processed,
creating a new QuerySet. The operation might be to just filter the QuerySet, or to map entries into say their children,
or to form a new QuerySet containing all the children of all the elements of the previous QuerySet.

    import sakstig
    results = sakstig.QuerySet([my_data]).execute("$.store.book.*[@.price > 4].title")
    for result in results:
        print result

As can be seen above, not only does a query return a QuerySet, it also takes one as input, meaning the first thing
you have to do when using SakStig is to construct a QuerySet.

Note that while a QuerySet inherits from the python list type, it isn't to be seen as a list. In particular, if your
query matches a single node in your data that is a list, execute() will return a QuerySet with one element that is that list.
Warning: This is different from other objectpath implementations!
