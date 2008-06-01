=========================
plone.recipe.zope2install
=========================

Overview
========

ZC Buildout recipe for installing Zope 2.

Example
=======

Let's start with the most basic example::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = zope2
    ... find-links =
    ...     http://dist.plone.org/
    ...
    ... [zope2]
    ... recipe = plone.recipe.zope2install
    ... url = file:///tmp/Zope-2.9.7-final.tgz
    ... """)

If we run the buildout it returns::

    >>> print system(buildout)
    Installing zope2.
    running build_ext
    creating zope.proxy
    copying zope/proxy/proxy.h -> zope.proxy
    building 'AccessControl.cAccessControl' extension
    creating build
    creating build/temp.linux-i686-2.4
    creating build/temp.linux-i686-2.4/AccessControl
    ...

Let's have a look at the different folders created::

    >>> ls(sample_buildout, 'parts')
    d  zope2

    >>> ls(sample_buildout, 'develop-eggs')
    -  plone.recipe.zope2install.egg-link

    >>> ls(sample_buildout, 'parts', 'zope2')
    d  Extensions
    -  README.txt
    -  ZopePublicLicense.txt
    -  configure
    d  doc
    d  inst
    d  lib
    -  log.ini
    -  setup.py
    d  skel
    -  test.py
    d  utilities


