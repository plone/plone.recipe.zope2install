=========================
plone.recipe.zope2install
=========================

Overview
========

ZC Buildout recipe for installing Zope 2.

Example
=======

Let's start with the most basic example. We will fetch here a random
Zope tarball::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = zope2
    ... find-links =
    ...     http://dist.plone.org/
    ...
    ... [zope2]
    ... recipe = plone.recipe.zope2install
    ... url = http://www.zope.org/Products/Zope/2.10.6/Zope-2.10.6-final.tgz
    ... """)

If we run the buildout it returns::

    >>> print system(buildout)
    Installing zope2.
    running build_ext
    creating zope.proxy
    copying zope/proxy/proxy.h -> zope.proxy
    building 'AccessControl.cAccessControl' extension
    creating build
    creating build/...
    creating build/.../AccessControl
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
    -  setup.pyc
    d  skel
    -  test.py
    -  test.pyc
    -  testing.log
    d  utilities

Fake Zope Eggs Example
======================

Zope 2 isn't eggified yet, Zope 3 does. That can become a problem if you want
to install some egg with depedencies related to Zope 3 eggs (such as
zope.interface, zope.component, ...)

This buildout recipe can help you by adding some fake eggs to Zope libraries
(installed inside zope/lib/python/zope/...) so that setuptools can see that
the dependencies are already satisfied and it won't fetch them anymore.

Just add it to your buildout config like this::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = zope2
    ... find-links =
    ...     http://dist.plone.org/
    ...
    ... [zope2]
    ... recipe = plone.recipe.zope2install
    ... url = http://www.zope.org/Products/Zope/2.10.6/Zope-2.10.6-final.tgz
    ... fake-zope-eggs = true
    ... """)

Now if we run the buildout again::

    >>> print system(buildout)
    Uninstalling zope2.
    Installing zope2.
    running build_ext
    creating zope.proxy
    copying zope/proxy/proxy.h -> zope.proxy
    building 'AccessControl.cAccessControl' extension
    creating build
    creating build/...
    creating build/.../AccessControl
    ...

Now if we list all the developed eggs we have:

    >>> ls(sample_buildout, 'develop-eggs')
    -  plone.recipe.zope2install.egg-link
    -  zope.annotation.egg-info
    -  zope.app.annotation.egg-info
    -  zope.app.apidoc.egg-info
    -  zope.app.applicationcontrol.egg-info
    ...

Let's have a look at the content of one of them::

    >>> cat(sample_buildout, 'develop-eggs', 'zope.annotation.egg-info')
    Metadata-Version: 1.0
    Name: zope.annotation
    Version: 0.0

You might also want to add other fake eggs to your buildout, to do so use the
additional-fake-eggs option, for example::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = zope2
    ... find-links =
    ...     http://dist.plone.org/
    ...
    ... [zope2]
    ... recipe = plone.recipe.zope2install
    ... url = http://www.zope.org/Products/Zope/2.10.6/Zope-2.10.6-final.tgz
    ... additional-fake-eggs = ZODB3
    ... """)

    >>> print system(buildout)
    Uninstalling zope2.
    Installing zope2.
    running build_ext
    creating zope.proxy
    copying zope/proxy/proxy.h -> zope.proxy
    building 'AccessControl.cAccessControl' extension
    creating build
    creating build/...
    creating build/.../AccessControl
    ...

Let's check if the additional fake egg exists:

    >>> cat(sample_buildout, 'develop-eggs', 'ZODB3.egg-info')
    Metadata-Version: 1.0
    Name: ZODB3
    Version: 0.0

If you need to have a specific version of an egg, this can be done like this:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = zope2
    ... find-links =
    ...     http://dist.plone.org/
    ...
    ... [zope2]
    ... recipe = plone.recipe.zope2install
    ... url = http://www.zope.org/Products/Zope/2.10.6/Zope-2.10.6-final.tgz
    ... additional-fake-eggs = ZODB3=3.7
    ...                        zope.app.tree = 1.7
    ... """)

    >>> print system(buildout)
    Uninstalling zope2.
    Installing zope2.
    running build_ext
    creating zope.proxy
    copying zope/proxy/proxy.h -> zope.proxy
    building 'AccessControl.cAccessControl' extension
    creating build
    creating build/...
    creating build/.../AccessControl
    ...

    >>> cat(sample_buildout, 'develop-eggs', 'ZODB3.egg-info')
    Metadata-Version: 1.0
    Name: ZODB3
    Version: 3.7

    >>> cat(sample_buildout, 'develop-eggs', 'zope.app.tree.egg-info')
    Metadata-Version: 1.0
    Name: zope.app.tree
    Version: 1.7

In some cases you might also want to ignore some of the packages shipped
with the Zope tarball::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = zope2
    ... find-links =
    ...     http://dist.plone.org/
    ...
    ... [zope2]
    ... recipe = plone.recipe.zope2install
    ... url = http://www.zope.org/Products/Zope/2.10.6/Zope-2.10.6-final.tgz
    ... skip-fake-eggs =
    ...     zope.annotation
    ...     zope.app.apidoc
    ... """)

Let's run the buildout::

    >>> print system(buildout)
    Uninstalling zope2.
    Installing zope2.
    running build_ext
    creating zope.proxy
    copying zope/proxy/proxy.h -> zope.proxy
    building 'AccessControl.cAccessControl' extension
    creating build
    creating build/...
    creating build/.../AccessControl
    ...

Now if we list all the developed eggs we have:

    >>> ls(sample_buildout, 'develop-eggs')
    -  ZODB3.egg-info
    -  plone.recipe.zope2install.egg-link
    -  zope.app.annotation.egg-info
    -  zope.app.applicationcontrol.egg-info
    ...
