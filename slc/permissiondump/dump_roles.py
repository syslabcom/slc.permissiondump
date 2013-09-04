# -*- coding: utf-8 -*-

from Products.CMFCore.interfaces import IFolderish
from slc.permissiondump import PORTAL_NAME
from slc.permissiondump import OUTPUT_DIR
from slc.permissiondump import ROLES_DUMP

import argparse
import json
import os


def get_local_roles(node):
    """Recursive generator which traverses the database and yields local
    roles for all objects.

    :param node: current object in the tree
    """
    local_roles = node.get_local_roles()
    filtered_user_roles =[]
    for user_role in local_roles:
        user_roles = []
        for role in user_role[1]:
            if role != 'Owner':
                user_roles.append(role)
        if user_roles != []:
            filtered_user_roles.append([user_role[0], user_roles])
    yield json.dumps({node.absolute_url(): filtered_user_roles})

    if IFolderish.providedBy(node):
        children = node.listFolderContents()

        for child in children:
            for obj in get_local_roles(child):
                yield obj



def export_local_roles(portal, roles_file):
    """Export local roles to a text file.

    :param portal: portal object to export the roles for
    :param roles_file: full filename of the file to dump roles to
    """
    with open(roles_file, 'w') as f:
        for line in get_local_roles(portal):
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

    roles_file = os.path.join(output_dir, ROLES_DUMP)
    export_local_roles(app[portal_name], roles_file)
