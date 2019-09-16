
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

# Extracting items from QuerySets and turning QuerySets into lists

List items can be extracted into a QuerySet using the `*` operator.
`MyList.*` will return a QuerySet holding all items from all lists in the
QuerySet `MyList`.

A QuerySet can be turned into a list, and returned as a single item
inside a new QuerySet using the normal list constructor operation.
`[MyQuerySet]` will return a QuerySet containing a single list, which
in turn contains as its items all items in the QuerySet `MyQuerySet`.

# QuerySet union

SakStig supports an extension to the ObjectPath syntax to merge
QuerySets. The `,` operator takes two expressions and forms the union
of their reults. Note that in a function argument, array or dictionary
context, you must surround this type of expression by parenthesis as
it would otherwize be ambigous.

# Additional functions

SakStig supports some additional functions as well as some additional
usages of existing functions beyond what ObjectPath does:

* String functions can be applied to arrays and vice versa where it
  makes sense.

* sort(array, key) can use a path expression as key, e.g. sort(array,
  @.given_name + @.surname)

* map(array, path) evaluates the path for each array element,
  producing a new array. Example:

    >>> sakstig.QuerySet([[1, 2, 3]]).execute("map($, @+1)")
    [2, 3, 4]

* reduce(array, path, [initial]) evaluates path for on a list
  containing the first two elements of array, then on a list
  containing the result of that and the third element, etc
  recursively. If initial is supplied, its value is prepended to the
  array before the reduction begins. Example:

    >>> sakstig.QuerySet([[1, 2, 3, 4]]).execute("reduce($, @[0] * @[1])")
    24
