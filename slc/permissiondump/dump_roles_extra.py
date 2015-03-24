# -*- coding: utf-8 -*-

from Acquisition import aq_parent
from Products.CMFCore.interfaces import IFolderish
from plone.dexterity.interfaces import IDexterityContainer
from slc.permissiondump import PORTAL_NAME
from slc.permissiondump import OUTPUT_DIR
from slc.permissiondump import ROLES_DUMP

from logging import getLogger
import argparse
import json
import os

log = getLogger('permissiondump')
cnt = 0

def filter_roles(roles):
    filtered_user_roles = []
    for user_role in roles:
        user_roles = []
        for role in user_role[1]:
            if role != 'Owner':
                user_roles.append(role)
        if user_roles != []:
            filtered_user_roles.append([user_role[0], user_roles])
    return filtered_user_roles

def get_local_roles(node, root=False):
    """Recursive generator which traverses the database and yields local
    roles for all objects.

    :param node: current object in the tree
    """

    global cnt
    local_roles = node.get_local_roles()
    filtered_user_roles = filter_roles(local_roles)
    inherit_roles = int(not getattr(node, "__ac_local_roles_block__", None))
    if cnt and cnt % 1000 == 0:
        log.warning('Dumped %d lines' % cnt)
    # If we don't inherit roles, but have the same roles as the parent,
    # consider this equivalent to inheritance
    identical = 0
    if not root:
        parent = aq_parent(node)
        parent_roles = filter_roles(parent.get_local_roles())
        # if the permissions are different, then we assume not inheriting was done for a reason
        if parent_roles == filtered_user_roles:
            identical = 1
    if filtered_user_roles == []:
        local_settings = 0
    else:
        local_settings = 1
    path = node.getPhysicalPath()
    yield json.dumps({
        '/'.join(path): filtered_user_roles, 'inherit': inherit_roles, 'type': node.portal_type,
        'same_as_parent': identical, 'level': len(path) - 2, 'local_settings': local_settings,
    })
    cnt += 1

    if IDexterityContainer.providedBy(node):
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
        f.write('[')
        for line in get_local_roles(portal, root=True):
            f.write(line + ',\n')
        f.write(']')
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
    global cnt
    cnt = 0
    args = parse_args()
    output_dir = args.output_dir
    portal_name = args.portal_name
    log.warning('starting dump')
    log.warning('Args: ' + str(args))

    if portal_name not in app:
        raise Exception(
            'Plone site not found, please check the name again '
            '({0}). NOTE: the name is case sensitive!'.format(portal_name)
        )

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    roles_file = os.path.join(output_dir, ROLES_DUMP)
    export_local_roles(app[portal_name], roles_file)
