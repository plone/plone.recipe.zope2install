=========================
plone.recipe.zope2install
=========================

Overview
========

ZC Buildout recipe for installing Zope 2.

Example
=======

Let's start with the most basic example. We will fetch here a random Zope tarball::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = zope2
    ... find-links =
    ...     http://dist.plone.org/
    ...
    ... [zope2]
    ... recipe = plone.recipe.zope2install
    ... url = http://www.zope.org/Products/Zope/2.9.7/Zope-2.9.7-final.tgz
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

Fake Zope Eggs Example
======================

Zope 2 isn't eggified yet, Zope 3 does. That can become a problem if you want to install some egg with depedencies related to Zope 3 eggs (such as zope.interface, zope.component, ...)

This buildout recipe can help you by adding some fake egg link to zope libraries (installed inside zope/lib/python/zope/...) so that setuptools can see that the dependencies are already satisfied and it won't fetch them anymore.

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
    ... url = http://www.zope.org/Products/Zope/2.9.7/Zope-2.9.7-final.tgz
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
    creating build/temp.linux-i686-2.4
    creating build/temp.linux-i686-2.4/AccessControl
    ...

Now if we list all the developped egg we have:

    >>> ls(sample_buildout, 'develop-eggs')
    -  .egg-info
    -  plone.recipe.zope2install.egg-link
    -  zope.app.adapter.egg-info
    -  zope.app.annotation.egg-info
    -  zope.app.apidoc.egg-info
    -  zope.app.applicationcontrol.egg-info
    -  zope.app.appsetup.egg-info
    -  zope.app.authentication.egg-info
    -  zope.app.basicskin.egg-info
    -  zope.app.broken.egg-info
    -  zope.app.cache.egg-info
    -  zope.app.component.egg-info
    -  zope.app.container.egg-info
    -  zope.app.content.egg-info
    -  zope.app.content_types.egg-info
    -  zope.app.copypastemove.egg-info
    -  zope.app.datetimeutils.egg-info
    -  zope.app.debug.egg-info
    -  zope.app.decorator.egg-info
    -  zope.app.dependable.egg-info
    -  zope.app.dtmlpage.egg-info
    -  zope.app.dublincore.egg-info
    -  zope.app.egg-info
    -  zope.app.error.egg-info
    -  zope.app.event.egg-info
    -  zope.app.exception.egg-info
    ...

Let's have a look at the content of one of them::

    >>> cat(sample_buildout, 'develop-eggs', 'zope.app.adapter.egg-info')
    Metadata-Version: 1.0
    Name: zope.app.adapter
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
    ... url = http://www.zope.org/Products/Zope/2.9.7/Zope-2.9.7-final.tgz
    ... fake-zope-eggs = true
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
    creating build/temp.linux-i686-2.4
    creating build/temp.linux-i686-2.4/AccessControl
    ...

Let's check if the additionnal fake egg exists:

    >>> cat(sample_buildout, 'develop-eggs', 'ZODB3.egg-info')
    Metadata-Version: 1.0
    Name: ZODB3
    Version: 0.0

Sometimes you are required to have a specific version of an egg, this is done like this:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = zope2
    ... find-links =
    ...     http://dist.plone.org/
    ...
    ... [zope2]
    ... recipe = plone.recipe.zope2install
    ... url = http://www.zope.org/Products/Zope/2.9.7/Zope-2.9.7-final.tgz
    ... fake-zope-eggs = true
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
    creating build/temp.linux-i686-2.4
    creating build/temp.linux-i686-2.4/AccessControl
    ...

    >>> cat(sample_buildout, 'develop-eggs', 'ZODB3.egg-info')
    Metadata-Version: 1.0
    Name: ZODB3
    Version: 3.7

    >>> cat(sample_buildout, 'develop-eggs', 'zope.app.tree.egg-info')
    Metadata-Version: 1.0
    Name: zope.app.tree
    Version: 1.7

