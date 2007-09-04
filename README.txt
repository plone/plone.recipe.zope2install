*************************
plone.recipe.zope2install
*************************

Options
*******

To specify which Zope 2 to use, use one of the following options:

url
    The URL to a tarball to use for the Zope 2 installation.

svn
    The URL for an subversion checkout to use for the Zope 2 installation.

If you use many buildouts with the same Zope 2 version, then you can add
"zope-directory" in the "buildout" section in your ~/.buildout/default.cfg
file like this:

[buildout]
zope-directory = /home/me/buildout/zope

For installations from tarballs that directory will be used instead of the
parts directory in your buildout. Each version of Zope will get it's own
directory but if it's already installed the existing one will be reused.
