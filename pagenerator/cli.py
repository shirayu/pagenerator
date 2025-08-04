#!/usr/bin/env python
import argparse
import json
import os
import re
import string
import sys
from pathlib import Path

import markdown


def get_title(text: str) -> str:
    for line in text.split("\n"):
        line = line.lstrip().rstrip()
        if line.startswith("#"):
            return line.lstrip("#").lstrip()
    return ""


def get_og_description(text: str) -> str:
    # Remove code blocks to avoid false matches
    code_block_pattern = r"```.*?```"
    text_without_code = re.sub(code_block_pattern, "", text, flags=re.DOTALL)

    patterns = [r"<!--\s*og:description:\s*(.+?)\s*-->", r"<!--\s*og:description\s+(.+?)\s*-->"]
    for pattern in patterns:
        match = re.search(pattern, text_without_code, re.IGNORECASE | re.DOTALL)
        if match:
            description = match.group(1).strip()
            # Replace newlines with <br> tags for og:description
            description = re.sub(r"\s*\n\s*", "<br>", description)
            return description
    return ""


def check_unsupported_meta_tags(text: str) -> None:
    supported_tags = {"og:description"}

    # Remove code blocks to avoid false matches
    code_block_pattern = r"```.*?```"
    text_without_code = re.sub(code_block_pattern, "", text, flags=re.DOTALL)

    # Find all xx:yy format tags in comments
    patterns = [
        r"<!--\s*([a-zA-Z_][a-zA-Z0-9_]*):([a-zA-Z_][a-zA-Z0-9_]*):\s*(.+?)\s*-->",
        r"<!--\s*([a-zA-Z_][a-zA-Z0-9_]*):([a-zA-Z_][a-zA-Z0-9_]*)\s+(.+?)\s*-->",
    ]
    found_tags = set()

    for pattern in patterns:
        matches = re.finditer(pattern, text_without_code, re.IGNORECASE)
        for match in matches:
            tag_name = f"{match.group(1).lower()}:{match.group(2).lower()}"
            if tag_name not in supported_tags:
                found_tags.add(tag_name)

    if found_tags:
        sorted_tags = sorted(found_tags)
        print(f"警告: 未対応のメタタグが見つかりました: {', '.join(sorted_tags)}", file=sys.stderr)


def remove_meta_comments(text: str) -> str:
    # Original patterns for backward compatibility (still only removes og/twitter tags)
    patterns = [r"<!--\s*(og|twitter):[^:]+:\s*(.+?)\s*-->", r"<!--\s*(og|twitter):[^:]+\s+(.+?)\s*-->"]
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text


def get_mydict(
    *,
    mydict: dict,
    input_filename: str,
):
    thisdict = mydict.copy()
    for k, v in list(thisdict.items()):
        if ":" in k:
            myprefix, myk = k.split(":", 1)
            if input_filename.startswith(myprefix):
                thisdict[myk] = v
            del thisdict[k]
    return thisdict


def convert(
    *,
    input_filename: str,
    template_name,
    output_name,
    bread=None,
    force=False,
    mydict: dict,
):
    isinstance(force, bool)

    (head, _) = os.path.split(output_name)
    if len(head) != 0:
        Path(head).mkdir(exist_ok=True, parents=True)

    with Path(input_filename).open() as fp:
        content_text = fp.read()
        title = get_title(content_text)
        og_description = get_og_description(content_text)
        check_unsupported_meta_tags(content_text)
    with Path(template_name).open() as fp:
        template = string.Template(fp.read())

    if output_name == "-":
        pass
    else:
        if (
            not force
            and os.path.exists(output_name)
            and os.stat(input_filename).st_mtime < os.stat(output_name).st_mtime
            and os.stat(template_name).st_mtime < os.stat(output_name).st_mtime
        ):
            return title

    content_text_cleaned = remove_meta_comments(content_text)
    content_html = markdown.markdown(
        content_text_cleaned,
        extensions=[
            "fenced_code",
            "tables",
            "footnotes",
        ],
    )
    if bread is None:
        bread = ""
    elif bread != "":
        bread += f"""<li class="bread" itemprop="title">{title}</li>"""
        bread = f"""<ul id="breadCrumb" itemscope="" itemtype="https://schema.org/BreadcrumbList">{bread}</ul>"""

    thisdict = get_mydict(
        mydict=mydict,
        input_filename=input_filename,
    )

    # Use default og_description from dict if not found in content
    if not og_description and "og_description" in thisdict:
        og_description = thisdict["og_description"]

    d = {"content": content_html, "title": title, "bread": bread, "og_description": og_description}

    # Add other dict values but preserve og_description that was already determined
    for key, value in thisdict.items():
        if key != "og_description":
            d[key] = value

    html = template.substitute(d)

    with Path(output_name).open("w") as outf:
        outf.write(html)

    return title


def get_bread(pathroot, titles):
    paths = pathroot.split("/")
    rets = []

    for i in range(1, len(paths)):
        key = "/".join(paths[:i])
        mytitle: str = titles[key]
        rets.append("""\n""")
        rets.append(
            """<li class="bread" itemprop="itemListElement"  """
            """itemscope="" itemtype="https://schema.org/ListItem">\n"""
        )
        rets.append(f"""<meta itemprop="position" content="{i}" />\n""")
        rets.append(f"""<a href="/{key}" itemprop="item"><span itemprop="name">{mytitle}</span></a></li>""")
    ret = "".join(rets)
    return ret


def clean_path(path):
    if path.endswith("/"):
        path = path[:-1]
    elif path.endswith("/index"):
        path = path[: -len("/index")]
    return path


def get_index_position(files):
    try:
        myindex = files.index("index.md")
        return myindex
    except ValueError:
        pass
    return -1


def recursive(
    *,
    input_filename,
    template_name,
    output_name,
    breads: list[str],
    force=False,
    mydict: dict,
):
    isinstance(force, bool)

    titles = {}

    for root, _, files in os.walk(input_filename):
        # swap filenames to get names of index.md first
        index_pos = get_index_position(files)
        if index_pos != -1:
            files[0], files[index_pos] = files[index_pos], files[0]

        for fname in files:
            myfilename = os.path.join(root, fname)
            myoutname0 = myfilename[len(input_filename) + 1 :]
            (myoutroot, myoutext) = os.path.splitext(myoutname0)
            if myoutext not in [".md", ".mkd"]:
                continue
            myoutname = os.path.join(output_name, myoutroot + ".html")
            myoutroot2 = clean_path(myoutroot)

            mybread = None
            flg = False
            for bread in breads:
                if myoutroot.startswith(bread):
                    mybread = get_bread(myoutroot2, titles)
                    flg = True
                    break

            title = convert(
                input_filename=myfilename,
                template_name=template_name,
                output_name=myoutname,
                bread=mybread,
                force=force,
                mydict=mydict,
            )

            if flg:
                titles[myoutroot2] = title
            print(myfilename, myoutname, title)


def main():
    oparser = argparse.ArgumentParser(description="A generator of a web page")

    oparser.add_argument("-i", "--input", dest="input", type=str, help="", required=True)
    oparser.add_argument("-o", "--output", dest="output", type=str, help="", required=True)
    oparser.add_argument("-t", "--template", dest="template", type=str, help="", required=True)

    oparser.add_argument(
        "-R",
        dest="recursive",
        action="store_true",
        help="Convert recursively",
        default=False,
    )
    oparser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        help="Force generation",
        default=False,
    )
    oparser.add_argument(
        "--breads",
        dest="breads",
        action="append",
        help="Make breadCrumb for this prefix paths",
        default=[],
        type=str,
    )
    oparser.add_argument("--dict", dest="mydict", help="Keywords JSON file path", default=None, type=Path)
    opts = oparser.parse_args()

    if opts.mydict:
        with opts.mydict.open() as fp:
            mydict = json.load(fp)
    else:
        mydict = {}

    if opts.recursive:
        recursive(
            input_filename=opts.input,
            template_name=opts.template,
            output_name=opts.output,
            breads=opts.breads,
            force=opts.force,
            mydict=mydict,
        )
    else:
        convert(
            input_filename=opts.input,
            template_name=opts.template,
            output_name=opts.output,
            force=opts.force,
            mydict=mydict,
        )


if __name__ == "__main__":
    main()
