# -*- coding: utf-8 -*-

from Products.CMFCore.interfaces import IFolderish
from slc.permissiondump import PORTAL_NAME
from slc.permissiondump import OUTPUT_DIR
from slc.permissiondump import ROLES_DUMP

import argparse
import json
import os


def get_local_roles(node, p_utils):
    """Recursive generator which traverses the database and yields local
    roles for all objects.

    :param node: current object in the tree
    :param p_utils: the plone utils tool
    """
    roles = p_utils.getInheritedLocalRoles(node)

    # NOTE: we don't use dict comprehension to retain compatibilty w/ py2.6
    roles_info = {}
    for item in roles:
        key = '{0[2]} {0[3]}'.format(item)
        roles_info[key] = item[1]

    yield json.dumps({node.absolute_url(): roles_info})

    if IFolderish.providedBy(node):
        children = node.listFolderContents()

        for child in children:
            for obj in get_local_roles(child, p_utils):
                yield obj


def export_local_roles(portal, p_utils, roles_file):
    """Export local roles to a text file.

    :param portal: portal object to export the roles for
    :param p_utils: the plone utils tool
    :param roles_file: full filename of the file to dump roles to
    """
    with open(roles_file, 'w') as f:
        for line in get_local_roles(portal, p_utils):
            f.write(line + '\n')
    print 'Roles export complete.'


def parse_args():
    """Parse command line arguments passed to script invocation."""
    parser = argparse.ArgumentParser(
        description='Dump all objects\' roles to a JSON-formatted file.')

    parser.add_argument(
        '--output-dir', dest='output_dir', default=OUTPUT_DIR,
        help='output directory [{0}]'.format(OUTPUT_DIR))

    parser.add_argument(
        '--portal-name', dest='portal_name', default=PORTAL_NAME,
        help='portal name [{0}]'.format(PORTAL_NAME))

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
    portal_name = args.portal_name

    if portal_name not in app:
        raise Exception(
            'Plone site not found, please check the name again '
            '({0}). NOTE: the name is case sensitive!'.format(portal_name)
        )

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    p_utils = app[portal_name].plone_utils
    roles_file = os.path.join(output_dir, ROLES_DUMP)
    export_local_roles(app[portal_name], p_utils, roles_file)
