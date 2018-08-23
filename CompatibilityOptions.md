ObjectPath does not differntiate between multiple results, and results
that are lists. However while SakStig does, for compatibility reasons there
are some operators that by default do not differentiate.

You can turn off this behavior with

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
