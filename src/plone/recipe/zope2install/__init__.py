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
import sys
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

        if (self.svn is None and
            buildout['buildout'].get('zope-directory') is not None):
            # if we use a download, then we look for a directory with shared
            # Zope installations. TODO Sharing of SVN checkouts is not yet
            # supported
            _, _, urlpath, _, _, _ = urlparse.urlparse(self.url)
            fname = urlpath.split('/')[-1]
            # cleanup the name a bit
            for s in ('.tar', '.bz2', '.gz', '.tgz'):
                fname = fname.replace(s, '')
            # Include the Python version Zope is compiled with into the
            # download cache name, so you can have the same Zope version
            # compiled with for example Python 2.3 and 2.4 but still share it
            ver = sys.version_info[:2]
            pystring = 'py%s.%s' % (ver[0], ver[1])
            options['location'] = os.path.join(
                buildout['buildout']['zope-directory'],
                '%s-%s' % (fname, pystring))
            options['shared-zope'] = 'true'
        else:
            # put it into parts
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'],
                self.name)
        # We look for a download cache, where we put the downloaded tarball
        buildout['buildout'].setdefault(
            'download-cache',
            os.path.join(buildout['buildout']['directory'], 'downloads'))

        skip_fake_eggs = self.options.get('skip-fake-eggs', '')
        self.skip_fake_eggs = [e for e in skip_fake_eggs.split('\n') if e]

        additional = self.options.get('additional-fake-eggs', '')
        self.additional_fake_eggs = [e for e in additional.split('\n') if e]

        self.fake_zope_eggs = bool(options.get('fake-zope-eggs', False))
        # Automatically activate fake eggs
        if self.skip_fake_eggs or self.additional_fake_eggs:
            self.fake_zope_eggs = True

    def install(self):
        options = self.options
        location = options['location']
        download_dir = self.buildout['buildout']['download-cache']

        if os.path.exists(location):
            # if the zope installation exists and is shared, then we are done
            # and don't return a path, so the shared installation doesn't get
            # deleted on uninstall
            if options.get('shared-zope') == 'true':
                # We update the fake eggs in case we have special skips or
                # additions
                if self.fake_zope_eggs:
                    print 'Creating fake eggs'
                    self.fakeEggs()
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
                if len(files) == 0:
                    raise ValueError('Broken Zope tarball named %s' % fname)
                shutil.move(os.path.join(tmp, files[0]), location)
            finally:
                shutil.rmtree(tmp)

        os.chdir(location)
        assert os.spawnl(
            os.P_WAIT, options['executable'], options['executable'],
            'setup.py',
            'build_ext', '-i',
            ) == 0

        if self.fake_zope_eggs:
            print 'Creating fake eggs'
            self.fakeEggs()
        if self.url and options.get('shared-zope') == 'true':
            # don't return path if the installation is shared, so it doesn't
            # get deleted on uninstall
            return []
        return location

    def _getInstalledLibs(self, location, prefix):
        installedLibs = []
        for lib in os.listdir(location):
            name = '%s.%s' % (prefix, lib)
            if (os.path.isdir(os.path.join(location, lib)) and
                name not in self.skip_fake_eggs and
                name not in [libInfo.name for libInfo in self.libsToFake]):
                # Only add the package if it's not yet in the list and it's
                # not in the skip list
                installedLibs.append(FakeLibInfo(name))
        return installedLibs

    def fakeEggs(self):
        zope2Location = self.options['location']
        zopeLibZopeLocation = os.path.join(zope2Location, 'lib', 'python',
                                           'zope')
        zopeLibZopeAppLocation = os.path.join(zope2Location, 'lib', 'python',
                                              'zope', 'app')
        self.libsToFake = []
        for lib in self.additional_fake_eggs:
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

        # Delete fake eggs, when we don't want them anymore
        for name in self.skip_fake_eggs:
            fake_egg_file = os.path.join(developEggDir, '%s.egg-info' % name)
            if os.path.exists(fake_egg_file):
                os.remove(fake_egg_file)

    def update(self):
        options = self.options
        location = options['location']
        shared = options.get('shared-zope')
        if os.path.exists(location):
            # Don't do anything in offline mode
            if self.buildout['buildout'].get('offline') == 'true' or \
               self.buildout['buildout'].get('newest') == 'false':
                if self.fake_zope_eggs:
                    print 'Updating fake eggs'
                    self.fakeEggs()
                return location

            # If we downloaded a tarball, we don't need to do anything while
            # updating, otherwise we have a svn checkout and should run
            # 'svn up' and see if there has been any changes so we recompile
            # the c extensions
            if self.url:
                if self.fake_zope_eggs:
                    print 'Updating fake eggs'
                    self.fakeEggs()
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

            if self.fake_zope_eggs:
                print 'Updating fake eggs'
                self.fakeEggs()

        return location
