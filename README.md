
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

## Meta information with HTML comments

You can specify meta information like Open Graph and Twitter Card data using HTML comments in your Markdown files. These comments will be processed and removed from the final HTML output.

### og:description

Specify page descriptions for Open Graph meta tags:

```markdown
# Page Title

<!-- og:description: This is a page description for social media sharing -->

Your page content here...
```

The `og:description` content will be available as the `$og_description` template variable.

### Supported meta comment formats

- **og:description**: `<!-- og:description: Your description -->` or `<!-- og:description Your description -->`
- **Other og: tags**: `<!-- og:title: Page Title -->`, `<!-- og:image: https://example.com/image.jpg -->`
- **Twitter Card**: `<!-- twitter:card: summary_large_image -->`, `<!-- twitter:site @yoursite -->`

### Template usage

In your HTML template, use the template variables:

```html
<meta property="og:description" content="$og_description">
<meta name="description" content="$og_description">
```

### Key features

- **Compatibility focused**: Supports both colon and space formats for compatibility with other software
- **First occurrence only**: Only the first `og:description` comment is used
- **Clean HTML output**: Meta comments are automatically removed from generated HTML
- **Case insensitive**: Works with both lowercase and uppercase comment formats
- **Code block safe**: Comments inside code blocks are ignored
