ObjectPath does not differntiate between multiple results, and results
that are lists. However while SakStig does, for compatibility reasons
there are some operators that by default do not differentiate. In
addition, there are some other quirks to the language.

You can turn off these behaviours by supplying extra flags to
QuerySet.execute. You can turn of all of these behaviours by supplying
the flag

    compatibility = False

You can turn off this behavior for the "in" and "not in" operators
with

    in_queryset=False

which will make the in operator only consider membership in a list,
not a queryset (use is for that inside a filter).

ObjectPath automatically looks inside lists when looking for object
members, partially because of there being no difference between lists
and querysets. This means that $.foo.bar in {"foo": [{"bar":1}]} will
yield 1.

You can turn off this behavior with

    autoflatten_lists=False

which will make the . operator only look directly inside objects.

sum() and avg() ignores items that are not of a uniform type (same
type as the first item). This is not analogous to how the + operator
works, which is unintuitive.

You can make these work just like the + operator with

    aggregate_casts=True

which will make e.g. sum([1, "2", 3]) == 6, not 4.

In ObjectPath, foo.* returns foo, however, this is not generally usefull, and by setting

    nop_star=False

foo.* will return a queryset containing all the values of foo as individual items.

In ObjectPath, "$.* + 2" does not do addition on all items, but rather
just appends 2 as an item, as would "$.*, 2" do. To make addition
distribute across all values of both querysets (perform a cross join),
set

    add_as_join=False

In objectpath obj[5] can either extract the fifth element of an array,
or the fifth result of a query. To make it take the fith element of
all array results of a query instead, set

    index_filter_queryset=False

To include non-dictionaries in results from the ".." operator, set

    descendant_leaves=True
