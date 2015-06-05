pareto.uidfixer
===============

Find relative links in a Plone site and replace them with 'resolveuid' ones.
This product finds all links that point to items within the site, or links
that contain 'resolveuid' as part of the URL, then uses traversal and the
redirection tool (portal_redirection) to get to the object linked to. If
that fails, the link is kept in-tact and is reported, if an object is found,
the link is converted to a proper 'resolveuid' one and saved.

Installation
------------

Simply add pareto.uidfixer to your buildout.cfg::

    eggs =
        ...
        pareto.uidfixer
    zcml =
        ...
        pareto.uidfixer

(where '...' are previously available entries, if any, if the sections don't
yet exist, create).

Then run buildout again, and the product should be added.

Basic usage
-----------

After running buildout, you can add '/@@uidfixer' behind any URL on the site to
fix the links on the object the URL points to, recursively (so all containing
objects will be fixed). Note that you will need to log in as administrator to
use the view. The view will present a 'fix' button, press it to get a list of
all fixed and all unfixable items, unfixable items (if any) are marked red.

The results
-----------

The results page shows a table with all the results, with pairs of rows per
found relative link. Each pair starts with a row of a single cell containing
a clickable, colored URL to the _document containing the broken link_ (so not
the link target). If the URL is blue, the relative link was resolved and the
link was converted to a resolveuid one. If the URL is red, the link was not
resolved, in which case you can click the URL to visit the document and
manually fix it. The row below the one with the full URL consists of a small
cell containing the field name, if the link was found in an Archetypes field,
then a cell containing the unmodified path that was (or is if the link could
not be resolved), and finally a cell containing an absolute url to the
object if the link was resolved (or text 'not resolved' if it wasn't).

Questions, remarks, etc.
------------------------

For questions, remarks, etc. send a mail to guido.wesdorp at pareto dot nl.
