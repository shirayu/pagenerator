#!/usr/bin/env python

import argparse
import codecs
import json
import os
import string
import sys
from pathlib import Path

import markdown


def get_title(text):
    for line in text.split("\n"):
        line = line.lstrip().rstrip()
        if line.startswith("#"):
            return line[1:].lstrip()
    return ""


def get_mydict(mydict, input_filename):
    thisdict = mydict.copy()
    for k, v in list(thisdict.items()):
        if ":" in k:
            myprefix, myk = k.split(":", 1)
            if input_filename.startswith(myprefix):
                thisdict[myk] = v
            del thisdict[k]
    return thisdict


def convert(
    input_filename,
    template_name,
    output_name,
    encoding="UTF-8",
    bread=None,
    force=False,
    mydict={},
):
    isinstance(force, bool)

    (head, tail) = os.path.split(output_name)
    if len(head) != 0:
        Path(head).mkdir(exist_ok=True, parents=True)

    with codecs.open(input_filename, "r", encoding) as fp:
        content_text = fp.read()
        title = get_title(content_text)
    with codecs.open(template_name, "r", encoding) as fp:
        template = string.Template(fp.read())

    if output_name == "-":
        sys.stdout = codecs.getwriter("utf_8")(sys.stdout)  # noqa
        myout = sys.stdout
    else:
        if (
            not force
            and os.path.exists(output_name)
            and os.stat(input_filename).st_mtime < os.stat(output_name).st_mtime
            and os.stat(template_name).st_mtime < os.stat(output_name).st_mtime
        ):
            return title

        myout = codecs.open(output_name, "w", encoding)

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
        bread += """<li class="bread" itemprop="title">%s</li>""" % title
        bread = (
            """<ul id="breadCrumb" itemscope="" itemtype="https://schema.org/BreadcrumbList">%s</ul>"""
            % bread
        )

    d = {"content": content_html, "title": title, "bread": bread}
    thisdict = get_mydict(mydict, input_filename)
    d.update(thisdict)

    html = template.substitute(d)

    myout.write(html)

    return title


def get_bread(pathroot, titles):
    paths = pathroot.split("/")
    rets = []

    for i in range(1, len(paths)):
        key = "/".join(paths[:i])
        mytitle = titles[key]
        rets.append("""\n""")
        rets.append(
            """<li class="bread" itemprop="itemListElement"  """
            """itemscope="" itemtype="https://schema.org/ListItem">\n"""
        )
        rets.append("""<meta itemprop="position" content="%d" />\n""" % i)
        rets.append(
            """<a href="/%s" itemprop="item">"""
            """<span itemprop="name">%s</span></a></li>""" % (key, mytitle)
        )

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
        return -1
    return -1


def recursive(
    input_filename,
    template_name,
    output_name,
    encoding="UTF-8",
    breads=[],
    force=False,
    mydict={},
):
    isinstance(force, bool)

    titles = {}

    for root, dirs, files in os.walk(input_filename):
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
                myfilename,
                template_name,
                myoutname,
                encoding,
                bread=mybread,
                force=force,
                mydict=mydict,
            )

            if flg:
                titles[myoutroot2] = title
            print(myfilename, myoutname, title)


def main():
    oparser = argparse.ArgumentParser(description="A generator of a web page")

    oparser.add_argument(
        "-i", "--input", dest="input", type=str, help="", required=True
    )
    oparser.add_argument(
        "-o", "--output", dest="output", type=str, help="", required=True
    )
    oparser.add_argument(
        "-t", "--template", dest="template", type=str, help="", required=True
    )

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
    oparser.add_argument(
        "--dict", dest="mydict", help="Keywords list", default="{}", type=str
    )
    opts = oparser.parse_args()

    mydict = json.loads(opts.mydict)

    if opts.recursive:
        recursive(
            opts.input,
            opts.template,
            opts.output,
            breads=opts.breads,
            force=opts.force,
            mydict=mydict,
        )
    else:
        convert(opts.input, opts.template, opts.output, force=opts.force, mydict=mydict)


if __name__ == "__main__":
    main()
