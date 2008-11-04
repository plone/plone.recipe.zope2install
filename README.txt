plone.recipe.zope2install
=========================

Options
-------

To specify which Zope 2 to use, use one of the following options:

`url`
    The URL to a tarball to use for the Zope 2 installation.

`svn`
    The URL for an subversion checkout to use for the Zope 2 installation.

`location`
    The path to a local, existing Zope 2 installation. Note: For this to work
    Zope must have been built with the same Python used to run buildout.

`fake-zope-eggs`
    If set to true, add fake egg links to Zope 3 libraries, so that setuptools
    can see and use them for dependencies lookup.

`additional-fake-eggs`
    Specify an optional list of additional fake eggs. Only include packages
    which are available on the Python path. Typical examples include ZODB3
    or zdaemon.

    You can also specify an explicit version to fake for an egg. For example::

        additional-fake-eggs =
            ZODB3 = 3.7.1
            zope.annotation = 3.3.2

    Otherwise the faked eggs will always have version 0.0.

`skip-fake-eggs`
    Specify an optional list of packages, for whom no fake egg is created.
    This allows to pull in new versions of some of the Zope packages via
    normal version requirements.

If you use many buildouts with the same Zope 2 version, then you can add
"zope-directory" in the "buildout" section in your ~/.buildout/default.cfg
file like this::

    [buildout]
    zope-directory = /home/me/buildout/zope

For installations from a tarball that directory will be used instead of the
parts directory in your buildout. Each version of Zope will get it's own
directory but if it's already installed the existing one will be reused.

Exported variables
------------------

The following variables are set by this recipe and can be used in other parts.

`location`
    The path to the Zope installation root.

Reporting bugs or asking questions
----------------------------------

We have a shared bug tracker and help desk on Launchpad:
https://bugs.launchpad.net/collective.buildout/
