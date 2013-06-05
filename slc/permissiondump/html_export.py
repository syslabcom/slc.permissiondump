# -*- coding: utf-8 -*-

from shutil import copytree
from shutil import ignore_patterns
from shutil import rmtree
from slc.permissiondump import HTML_OUT
from slc.permissiondump import OUTPUT_DIR
from slc.permissiondump import ROLES_DUMP

import argparse
import json
import os
import sys


PRE_HTML = """
<!DOCTYPE html>

<html>

  <head>
    <meta charset="utf-8">
    <title>Permission Dump</title>
    <script type="text/javascript" src="static/jquery.js"></script>
    <script type="text/javascript" src="static/jquery-ui.custom.js"></script>
    <link href="static/ui.dynatree.css" rel="stylesheet" type="text/css"
        id="skinSheet">
    <script type="text/javascript"
        src="static/jquery.dynatree.min.js"></script>

    <script type="text/javascript">
        $(function () {
            $("#tree").dynatree({});
        });
    </script>
  </head>

  <body>
    <div id="tree">
      <ul id="treeData" style="display: none;">
"""

POST_HTML = """
      </ul>
    </div>

  </body>
</html>
"""


def write_html(roles_file, html_file):
    """Write the exported roles to html for display with dynatree.

    :param roles_file: file with roles dump as created by dump_roles.py
    """
    with open(roles_file) as input_file:
        lines = input_file.readlines()

    with open(html_file, 'w') as output_file:
        output_file.write(PRE_HTML)
        _write_level(lines, 0, output_file)
        output_file.write(POST_HTML)


def _is_child(path1, path2):
    """Check if node1 is a child of node2.

    :param path1: path of node1
    :param path2: path of node2
    :returns: True if node1 is a child of node2, False otherwise
    """
    is_child = \
        len(path1) > len(path2) and \
        path1.startswith(path2) and \
        path1[len(path2)] == '/'

    return is_child


def _level(url):
    """Return item's hierarchy level based on its path.

    :param url: item's portal URL
    :returns: item's depth level
    """
    # NOTE: we subtract 3 because of the double slash before the domain part
    # in the URL and because we consider root level as level 0
    return url.count('/') - 3


def _write_level(lines, i, output_file):
    """Construct HTML representing one level of object hierarchy.

    For every item recursively construct its children (sublevel).

    :param lines: lines with local roles info for each object
    :param i: position of the object
    :param output_file: an open file for writing the HTML output to
    :returns: index in `lines` at which the algorithm should continue
    """
    while i < len(lines):

        node1 = json.loads(lines[i]).popitem()
        if i + 1 < len(lines):
            node2 = json.loads(lines[i + 1]).popitem()
        else:
            node2 = None

        if node2 is None:
            # last line reached, output node1, close open levels as needed
            output_file.write(
                '<li>\n{0!s} ### {1!s}\n</li>\n'.format(
                    node1[0], node1[1]
                ))

            level_diff = _level(node1[0])
            output_file.write('</ul>\n</li>\n' * level_diff)
            i += 1

        elif _is_child(node2[0], node1[0]):
            # node2 is node1's child, write it and start a new hierarchy level
            output_file.write(
                '<li class="folder">\n{0!s} ### {1!s}\n<ul>\n'.format(
                    node1[0], node1[1]
                ))
            i = _write_level(lines, i + 1, output_file)

        elif _level(node1[0]) == _level(node2[0]):
            # node2 is node1's sibling, simply write it and move on
            output_file.write(
                '<li>\n{0!s} ### {1!s}\n</li>\n'.format(
                    node1[0], node1[1]
                ))
            i += 1

        else:
            # node2 is above node1 in hierachy, end current hierarchy level
            output_file.write(
                '<li>\n{0!s} ### {1!s}\n</li>\n'.format(
                    node1[0], node1[1]
                ))

            # XXX: minor inefficiency  _level called twice for each node
            level_diff = _level(node1[0]) - _level(node2[0])
            output_file.write('</ul>\n</li>\n' * level_diff)

            return i + 1  # move back up in levels

    return i


def parse_args():
    """Parse command line arguments passed to script invocation."""
    parser = argparse.ArgumentParser(
        description='Convert role dump into a HTML tree view.')

    parser.add_argument(
        '--output-dir', dest='output_dir', default=OUTPUT_DIR,
        help='output directory')

    # NOTE: the script is invoked by zope with some additional arguments which
    # we don't need, so we choose to ignore them instead of raising an error.
    # That's why we use parse_known_args instead of parse_args.
    args, unknown = parser.parse_known_args()
    return args


def main(app, cmd_args):
    """Module's main entry point (zopectl.command).

    :param app: zope root application object
    :param cmd_args: list of command line arguments used to invoke the command
    """
    args = parse_args()
    output_dir = args.output_dir

    roles_file = os.path.join(output_dir, ROLES_DUMP)
    if not os.path.exists(roles_file):
        raise Exception(
            'Roles dump file ({0}) not found.'
            .format(os.path.join(output_dir, ROLES_DUMP))
        )

    # NOTE: if roles_file exists, output_dir exists as well so no need to check
    html_file = os.path.join(output_dir, HTML_OUT)

    orig_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(10000)  # XXX: config?

    print('Exporting to HTML...')
    write_html(roles_file, html_file)
    print('...export to HTML complete.')

    sys.setrecursionlimit(orig_limit)

    print('Copying JS and CSS assets...')
    src_dir = os.path.join(os.path.dirname(__file__), 'static')
    dest_dir = os.path.join(output_dir, 'static')

    if os.path.exists(dest_dir):
        rmtree(dest_dir)
    copytree(src_dir, dest_dir, ignore=ignore_patterns('.*'))
    print('...JS and CSS assets copying complete')
