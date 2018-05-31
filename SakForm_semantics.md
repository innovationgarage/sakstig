# Template semantics
A template consist of JSON entities which are evaluated recursively on some input queryset available as `$` to SakStig expressions. Initially, the template context `@template()` is set to the same as `$`. The output is a queryset.

## The template is an object

### If the template contains a member named `$`

  * The value of `template.$` is evaluated as a SakStig expression to form an `input` queryset.
  * If the template does not contain any other members than `$`, `input` is returned and evaluation ends.
  * Each `input` entry is transformed to form a new queryset which is returned.

`input` entry transform:

  * `@template` is set to a queryset containing only the current `input` entry.
  * A new empty `output` object is created.
  * For each `member` of the template:
    - `member.value` is evaluated recursively as a template to form a `value` queryset.
    - If `value` is the empty queryset, the member is ignored.
    - `output[member.name]` is set to the first entry in the `value` queryset.
   
### If the template does not contain a member named `$`

  * A new empty `output_object` is created
  * For each `member` of the template:
    - `member.value` is evaluated recursively as a template to form a `value` queryset.
    - If `value` is the empty queryset, the member is ignored.
    - `output_object[member.name]` is set to the first entry in the `value` queryset.
  * `output_object` is returned as a single member of a queryset.

## The template is an array
  * Each array member is evaluated recursively as a template.
  * All the resulting querysets are concatenated and converted into a JSON array
    which is returned as a single member of a queryset.

## Other values
All other values are returned verbatim as a single member of a queryset.
