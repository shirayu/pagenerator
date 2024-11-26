#!/usr/bin/env python
import argparse
import json
import os
import string
from pathlib import Path

import markdown


def get_title(text: str) -> str:
    for line in text.split("\n"):
        line = line.lstrip().rstrip()
        if line.startswith("#"):
            return line[1:].lstrip()
    return ""


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

    content_html = markdown.markdown(
        content_text,
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

    d = {"content": content_html, "title": title, "bread": bread}
    thisdict = get_mydict(
        mydict=mydict,
        input_filename=input_filename,
    )
    d.update(thisdict)

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
    oparser.add_argument("--dict", dest="mydict", help="Keywords list", default="{}", type=str)
    opts = oparser.parse_args()

    mydict = json.loads(opts.mydict)

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
