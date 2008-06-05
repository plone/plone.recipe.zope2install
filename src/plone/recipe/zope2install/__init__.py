##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os
import re
import shutil
import tempfile
import urllib2
import urlparse
import setuptools.archive_util

EGG_INFO_CONTENT = """Metadata-Version: 1.0
Name: %s
Version: %s
"""


class FakeLibInfo(object):
    """
    a really simple to store informations about libraries to be faked
    as eggs.
    """
    version = ''
    name = ''

    def __init__(self, name, version='0.0'):
        self.version = version
        self.name = name


class Recipe:

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

        python = buildout['buildout']['python']
        options['executable'] = buildout[python]['executable']
        self.svn = options.get('svn', None)
        self.url = options.get('url', None)
        assert self.svn or self.url

        # if we use a download, then we look for a directory with shared Zope
        # installations
        if self.svn is None and \
           buildout['buildout'].get('zope-directory') is not None:
            _, _, urlpath, _, _, _ = urlparse.urlparse(self.url)
            fname = urlpath.split('/')[-1]
            # cleanup the name a bit
            for s in ('.tar', '.bz2', '.gz', '.tgz'):
                fname = fname.replace(s, '')
            options['location'] = os.path.join(
                buildout['buildout']['zope-directory'],
                fname)
            options['shared-zope'] = 'true'
        else:
            # put it into parts
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'],
                self.name)
        # We look for a download directory, where we put the downloaded tarball
        # This is the same as the gocept.download and distros recipes use
        buildout['buildout'].setdefault(
                    'download-cache',
                    os.path.join(buildout['buildout']['directory'],
                                 'downloads'))

    def install(self):
        options = self.options
        location = options['location']
        download_dir = self.buildout['buildout']['download-cache']

        if os.path.exists(location):
            # if the zope installation exists and is shared, then we are done
            # and don't return a path, so the shared installation doesn't get
            # deleted on uninstall
            if options.get('shared-zope') == 'true':
                return []
            else:
                shutil.rmtree(location)

        if self.svn:
            assert os.system('svn co %s %s' % (options['svn'], location)) == 0
        else:
            if not os.path.isdir(download_dir):
                os.mkdir(download_dir)

            _, _, urlpath, _, _, _ = urlparse.urlparse(self.url)
            tmp = tempfile.mkdtemp('buildout-'+self.name)
            try:
                fname = os.path.join(download_dir, urlpath.split('/')[-1])
                # Have we already downloaded the file
                if not os.path.exists(fname):
                    f = open(fname, 'wb')
                    try:
                        f.write(urllib2.urlopen(self.url).read())
                    except:
                        os.remove(fname)
                        raise
                    f.close()

                setuptools.archive_util.unpack_archive(fname, tmp)
                # The Zope tarballs have a Zope-<version> folder at the root
                # level, so we need to move that one into the right place.
                files = os.listdir(tmp)
                shutil.move(os.path.join(tmp, files[0]), location)
            finally:
                shutil.rmtree(tmp)

        os.chdir(location)
        assert os.spawnl(
            os.P_WAIT, options['executable'], options['executable'],
            'setup.py',
            'build_ext', '-i',
            ) == 0

        if options.get('fake-zope-eggs') == 'true':
            print 'Creating fake eggs'
            self.fakeEggs()
        if self.url and options.get('shared-zope') == 'true':
            # don't return path if the installation is shared
            return []
        return location

    def _getInstalledLibs(self, location, prefix):
        installedLibs = []
        for lib in os.listdir(location):
            if os.path.isdir(os.path.join(location, lib)) and\
               "%s.%s" % (prefix, lib) not in [libInfo.name for libInfo in \
                                               self.libsToFake]:
                installedLibs.append(FakeLibInfo("%s.%s" % (prefix, lib)))
        return installedLibs

    def fakeEggs(self):
        zope2Location = self.options['location']
        zopeLibZopeLocation = os.path.join(zope2Location, 'lib', 'python',
                                           'zope')
        zopeLibZopeAppLocation = os.path.join(zope2Location, 'lib', 'python',
                                              'zope', 'app')
        self.libsToFake = []
        for lib in self.options.get('additional-fake-eggs', '').split('\n'):
            # 2 forms available:
            #  * additional-fake-eggs = myEgg
            #  * additional-fake-eggs = myEgg=0.4
            if '=' in lib:
                lib = lib.strip().split('=')
                eggName = lib[0].strip()
                version = lib[1].strip()
                libInfo = FakeLibInfo(eggName, version)
            else:
                eggName = lib.strip()
                libInfo = FakeLibInfo(eggName)

            self.libsToFake.append(libInfo)

        self.libsToFake += self._getInstalledLibs(zopeLibZopeLocation, 'zope')
        self.libsToFake += self._getInstalledLibs(zopeLibZopeAppLocation,
                                             'zope.app')
        developEggDir = self.buildout['buildout']['develop-eggs-directory']
        for libInfo in self.libsToFake:
            fakeLibEggInfoFile = os.path.join(developEggDir,
                                              '%s.egg-info' % libInfo.name)
            fd = open(fakeLibEggInfoFile, 'w')
            fd.write(EGG_INFO_CONTENT % (libInfo.name, libInfo.version))
            fd.close()

    def update(self):
        options = self.options
        location = options['location']
        shared = options.get('shared-zope')
        if os.path.exists(location):
            # Don't do anything in offline mode
            if self.buildout['buildout'].get('offline') == 'true' or \
               self.buildout['buildout'].get('newest') == 'false':
                return location

            # If we downloaded a tarball, we don't need to do anything while
            # updating, otherwise we have a svn checkout and should run
            # 'svn up' and see if there has been any changes so we recompile
            # the c extensions
            if self.url:
                return location

            os.chdir(location)
            i, o = os.popen4('svn up')
            i.close()
            change = re.compile('[AUM] ').match
            for l in o:
                if change(l):
                    o.read()
                    o.close()
                    break
                else:
                    # No change, so all done
                    o.close()
                    return location

            assert os.spawnl(
                os.P_WAIT, options['executable'], options['executable'],
                'setup.py',
                'build_ext', '-i',
                ) == 0

            if options.get('fake-zope-eggs') == 'true':
                print 'Creating fake eggs'
                self.fakeEggs()

        return location
