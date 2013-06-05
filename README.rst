Visualize a tree of local roles assigned on Plone items.

INSTALL
=======

Add this egg to buildout's egg list and run the buildout.

USAGE
=====

For usage description run the following:

::
    $ bin/instance dump_roles --help

To dump roles to a file, run the following:

::
    $ bin/instance dump_roles --output-dir OUTDIR --portal-name PORTAL

This command dumps permissions from Plone site PORTAL to a file called
local_roles.txt located in OUTDIR. If directory does not exist, it is
automatically created.

NOTE: specifying the output directory is optional, it defaults to directory
"output" in the same directory from where the script is run.
Plone site name is optional as well and defaults to "Plone".

To generate HTML tree view run the following:

::
    $ bin/instance html_export --output-dir OUTDIR

The OUTDIR, if specified, must refer to the same output directory that was
used to dump role info in previous step. Directory's default name is again
"output".

Open the created HTML `<OUTDIR>/local_roles_tree.html` directly from the
filesystem with your browser.

NOTE: in case of large files this might take some time, because synatree.js
script  must walk through the DOM and do its work. It might appear in the
meantime that the browser is unresponsive - it's just doing its work.
