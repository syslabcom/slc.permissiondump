Visualize a tree of local roles assigned on Plone items
=======================================================

NOTE: this package is still in beta and has not been thoroughly tested yet

Usage (TODO: improve?):
 * add this egg to buildout's egg list, run buildout
 * when the egg is installed, run bin/instance dump_roles --output-dir OUTDIR
 --portal-name PORTAL to dump permissions from Plone site PORTAL to a file
 called local_roles.txt located in OUTDIR. If directory does not exist, it is
 automatically created.

 NOTE: specifying the output directory is optional, it defaults to directory
 "output" in the same directory from where the script is run.
 Plone site name is optional as well and defaults to "Plone".

 You can also run bin/instance dump_roles --help for usage description.
 * run bin/instance html_export --output-dir OUTDIR to generate HTML tree
 view from the previously created roles dump file. The OUTDIR, if specified,
 must refer to the same output directory that was used to dump role info in
 in previous step. Directory's default  name is again "output".
 * Open the created HTML from the filesystem with your browser:
 <OUTDIR>/local_roles_tree.html

 NOTE: in case of large files this might take some time, because synatree.js
 script  must walk through the DOM and do its work. It might appear in the
 meantime that the browser is unresponsive - it's just doing its work.


