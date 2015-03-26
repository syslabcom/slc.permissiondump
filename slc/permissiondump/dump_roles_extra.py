# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from Products.CMFCore.interfaces._content import IFolderish
from logging import getLogger
from slc.permissiondump import OUTPUT_DIR
from slc.permissiondump import PORTAL_NAME
from slc.permissiondump import ROLES_DUMP
from staralliance.theme import utils
from staralliance.theme.utils import get_members_for_group

import argparse
import json
import os
import unicodecsv


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


def roles2str(roles):
    """ Format the roles for the CSV file
    """
    return ", ".join(
        [": ".join([str(i[0]), "<{0}>".format(str(", ".join(i[1])))])
         for i in roles]
    )

#", ".join([": ".join([str(i[0]), "<{0}>".format(str(", ".join(i[1])))]) for i in roles])


def dump_local_roles(node, root=False):
    """Recursive generator which traverses the database and yields local
    roles for all objects.

    :param node: current object in the tree
    """
    global cnt

    url = node.absolute_url()
    if url.startswith("star/cms") or url.startswith("star/portal_vocabularies"):
        return

    # if node.id == 'workspaces':
    #     import pdb; pdb.set_trace()

    local_roles = node.get_local_roles()
    filtered_user_roles = filter_roles(local_roles)
    for i in filtered_user_roles:
        # cheap way to test if we have a group, rather than a user
        if "@" not in i:
            group_name = i[0]
            roles = i[1]
            members = sorted(get_members_for_group(group_name).keys())
            member_names = ", ".join(members)
            group_and_members = u"{0} ({1})".format(group_name, member_names)
            index = filtered_user_roles.index(i)
            filtered_user_roles[index] = [group_and_members, roles]

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
    if filtered_user_roles != [] \
       and node.portal_type not in [
           'staralliance.types.workspace', 'staralliance.types.superspace']:
        path = node.getPhysicalPath()
        yield {
            'path': '/'.join(path),
            'roles': roles2str(filtered_user_roles),
            'inherit': inherit_roles,
            'type': node.portal_type,
            'same_as_parent': identical,
            'modified': str(node.modified()),
            'creator': node.Creator(),
            'workspace_name': utils.get_workspace_or_contract(node).Title(),
        }
        cnt += 1

    if IFolderish.providedBy(node):
        #listFolderContents() listed nothing for star/workspaces
        children = [i for i in node.objectValues() if hasattr(i, 'portal_type')]

        for child in children:
            for obj in dump_local_roles(child):
                yield obj


def export_local_roles(portal, roles_file):
    """Export local roles to a text file.

    :param portal: portal object to export the roles for
    :param roles_file: full filename of the file to dump roles to
    """
    with open(roles_file, 'w') as csvfile:
        fieldnames = [
            'path', 'roles', 'inherit', 'type', 'same_as_parent', 'modified', 'creator',
            'workspace_name',
        ]
        writer = unicodecsv.writer(csvfile, encoding='utf-8')

        writer.writerow(fieldnames)
        for line in dump_local_roles(portal, root=True):
            try:
                writer.writerow([line[fieldname] for fieldname in fieldnames])
            except:
                import pdb; pdb.set_trace()

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

    # Set the site, to keep star.api happy, which is used by get_members_for_group
    from zope.app.component.hooks import setSite
    portal = app[portal_name]
    setSite(portal)

    roles_file = os.path.join(output_dir, ROLES_DUMP)
    export_local_roles(portal['workspaces'], roles_file)
