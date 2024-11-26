
# PAGENERATOR : A simple web page generator

## How to use

Give one markdown file and a template file.
This will make a web page.

This will use the first line which starts with ``#`` for the page title.

## Basic conversion

```bash
pagenerator -i source.md -t template.html -o output.html
```

## Recursive conversion

When you give ``-R`` option, this converts files recursively.

```bash
pagenerator -i ./source_dir -o ./out_dir -t ./template.html -R --breads tr/
```

## Recursive conversion with breadcrumbs

When you give directory names with ``--breads`` option (You can designate more than one.),
the breadcrumb list will be generated for HTML files under their directories.

```bash
pagenerator -i ./source_dir -o ./out_dir -t ./template.html -R --breads sub/
```

Be aware to put ``index.md`` or ``index.mkd`` under their directories to get the directory description for the breadcrumb list.
