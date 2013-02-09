# -*- coding: utf-8 -*-
from distutils.dir_util import copy_tree
import string
import os
import shutil
import subprocess
from django.conf import settings
from django.core.management.base import BaseCommand


class CloneManager(object):
    def __init__(self, base_path):
        self.path = base_path
        if not self.path.endswith('/'):
            self.path += '/'

        self.cloned_libs = {}
        self.fnull = open(os.devnull, "w")


    def __del__(self):
        self.fnull.close()


    def get_lock(self):
        try:
            os.mkdir(self.path + '_tmp')
        except IOError:
            return False
        return True


    def free_lock(self):
        shutil.rmtree('%s_tmp' % self.path)

    def clone_library(self, library, version=None):
        """
            :param library: نام کتابخانه
            :type library: str
        """
        if not version: version = 'HEAD'

        if library in self.cloned_libs.keys():
            if self.cloned_libs[library] == version:
                return
            else:
                #TODO: remove previous version
                pass

        #TODO: handle git not being in path, or requiring key password
        subprocess.call('cd %s_tmp && git clone git@git.arsh.co:arshlib__%s && cd arshlib__%s && git checkout %s' % (
            self.path, library, library, version), shell=True, stdout=self.fnull, stderr=self.fnull)
        self.cloned_libs[library] = version


    def open_file(self, library, file_path):
        """
            :param library: نام کتابخانه
            :type library: str
            :param file_path: آدرس و نام فایل نسبت به ریشه‌ی کتابخانه
            :type file_path: str
        """
        if not library in self.cloned_libs.keys():
            self.clone_library(library)
        return open('%s_tmp/arshlib__%s/%s' % (self.path, library, file_path))


class Command(BaseCommand):
    help = 'Package manager for arsh libraries.'

    def __init__(self):
        super(Command, self).__init__()
        self.LIB_DIR = settings.BASEPATH + 'lib/arsh/'
        self.clone = CloneManager(self.LIB_DIR)
        self.fnull = open(os.devnull, "w")

    def __del__(self):
        self.fnull.close()

    def get_last_version(self, library):
        try:
            return self.parse_lib_versions(library)[library]['version']
        except IOError, KeyError:
            return 'N/A'


    def get_available_versions(self, library):
        p = subprocess.Popen(["git", "ls-remote", "git@git.arsh.co:arshlib__" + library], stdout=subprocess.PIPE,
            stderr=self.fnull)
        p.wait()
        versions = []
        head = None
        for line in p.stdout.readlines():
            line = line.strip()
            parts = line.split('\t')
            ind = line.find('refs/tags/v')
            if ind >= 0:
                nv = line[ind + 10:]
                if len(nv) > 1 and nv[1] in string.digits:
                    versions.append(nv)
            else:
                if parts[1] == 'HEAD':
                    head = parts[0]

        if head:
            versions.append(head[:7])
        return versions


    def parse_lib_versions(self, library):
        libs = {}
        if isinstance(library, str):
            versions_file = self.clone.open_file(library, 'lib/versions.txt')
        else:
            versions_file = library
        for line in versions_file.readlines():
            l = line.strip().split(' ')
            libs[l[0]] = {'name': l[0], 'version': l[1]}
        return libs


    def dump_lib_versions(self, filename, libs):
        lib_versions = open(filename, 'w')
        for lib, info in libs.items():
            lib_versions.write('%s %s\n' % (lib, info['version']))
        lib_versions.close()


    def is_compatible(self, v1, v2, lib='', auto=False):
        if v1 == v2: return True
        if auto:
            if not v2: return False
            if not v1: return True
            vp1 = v1.split('.')
            vp2 = v2.split('.')
            for i in range(min(len(vp1), len(vp2), 2)):
                if vp1[i] != vp2[i]:
                    return False
            return True
        else:
            yn = raw_input("""You have version %s of library: `%s`,
            but the library requires version %s, do you want to change locally
             installed version to %s? [y/n]""" % (v1, lib, v2, v2))
            if yn == 'y':
                return True
            return False


    def handle(self, *args, **options):
        if not self.clone.get_lock():
            self.stdout.write("Can not get lock for installing libs, delete lib/_tmp directory to force installation.")
            return

        try:
            LIB_DIR = self.LIB_DIR
            ext_libs = os.walk(LIB_DIR).next()[1]
            local_versions_file = LIB_DIR + '../versions.txt'
            open(local_versions_file, 'a').close()
            libs = self.parse_lib_versions(open(local_versions_file))

            action = args[0] if len(args) > 0 else ''
            if action == 'info':
                self.stdout.write('Registered Libraries:\n')
                self.stdout.write('\tLibrary Name            Installed Version\n')
                self.stdout.write('\t============            =================\n')
                for lib, info in libs.items():
                    self.stdout.write('\t' + lib + ' ' * (24 - len(lib)) + info['version'])
                    self.stdout.write('  \t(latest: %s)\n' % self.get_last_version(lib))
                self.stdout.write('\nUnregistered Libraries:\n')
                for lib in ext_libs:
                    if not lib in libs.keys():
                        if lib == 'lib': continue
                        self.stdout.write('\t%s (latest: %s)\n' % (lib, self.get_last_version(lib)))
            elif action == 'install':
                # بررسی ورودی‌های خط فرمان
                switches = []
                nargs = [args[0]]
                for arg in args[1:]:
                    if arg.startswith('__'):
                        switches.append(arg[2:])
                    else:
                        nargs.append(arg)
                if len(nargs) < 2:
                    self.stdout.write(u'Please enter name of the library you want to install.')
                    return
                lib = nargs[1]
                version = None if len(nargs) == 2 else nargs[2]

                self.clone.clone_library(lib, version=version)
                try:
                    package_libs = self.parse_lib_versions(lib)
                except IOError:
                    raise ValueError(
                        'The library `%s` does not have a lib/versions.txt file and is not supported by arshlib tool.' % lib)

                for til in os.walk('%s/_tmp/arshlib__%s/lib/arsh/' % (LIB_DIR, lib)).next()[1]:
                    type_name = 'dependency' if til != lib else 'package'
                    self.stdout.write('processing %s: %s...\n' % (type_name, til))
                    til_version = package_libs.get(til, {'version': None})['version']
                    if not til_version:
                        self.stdout.write('[Warning] Invalid package format: can not extract version for `%s`\n' % til)
                    if not til in ext_libs:
                        self.stdout.write("installing %s: %s\n" % (type_name, til))
                        copy_tree('%s_tmp/arshlib__%s/lib/arsh/%s' % (LIB_DIR, lib, til), LIB_DIR + til)
                        libs[til] = {'version': til_version}
                    else:
                        current_version = libs.get(til, {'version': None})['version']
                        forced = 'force' in switches
                        if not forced and not current_version and not til_version:
                            self.stdout.write(
                                '[Warning] no versioning data for existing %s:`%s`, skipping' % (type_name, til))
                        elif forced or self.is_compatible(current_version, til_version, lib=lib):
                            if forced or not current_version or (
                                current_version.find('.') >= 0 and current_version < til_version):
                                self.stdout.write(
                                    "upgrading %s %s: %s->%s%s\n" % (type_name, til, current_version, til_version,
                                                                     ' (forced upgrade)' if forced else ''))
                                shutil.rmtree('%s%s' % (LIB_DIR, til))
                                copy_tree('%s_tmp/arshlib__%s/lib/arsh/%s' % (LIB_DIR, lib, til), LIB_DIR + til)
                                libs[til] = {'version': til_version}
                        else:
                            self.stdout.write(
                                "[Warning] skipping installed %s: `%s`, backward incompatible upgrade: %s->%s\n" % (
                                    type_name, til, current_version, til_version))
                self.dump_lib_versions(LIB_DIR + '../versions.txt', libs)
            else:
                self.stdout.write("Invalid action: %(action)s\ntry: info, install" % {'action': action})
        finally:
            self.clone.free_lock()
