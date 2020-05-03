from conans import ConanFile
import os
from conans.tools import download
from conans.tools import unzip
from conans.tools import replace_in_file
from conans import CMake

class luaConan(ConanFile):
    name = "lua"
    version = "5.3.5"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    url="http://github.com/mpapierski/conan-lua"
    license="https://www.lua.org/license.html"
    exports="FindLua.cmake"
    unzipped_name = "lua-%s" % version
    zip_name = "%s.tar.gz" % unzipped_name
    requires = "readline/7.0@bincrafters/stable"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    def source(self):
        url = "https://www.lua.org/ftp/%s" % self.zip_name
        download(url, self.zip_name)
        unzip(self.zip_name)
        os.unlink(self.zip_name)
        readline = '-I {} -L {}'.format(self.deps_cpp_info['readline'].include_paths[0],
                                        self.deps_cpp_info['readline'].lib_paths[0])
        replace_in_file(os.path.join(self.unzipped_name, 'src', 'Makefile'),
                'MYCFLAGS=',
                'MYCFLAGS={}'.format(readline))
        replace_in_file(os.path.join(self.unzipped_name, 'src', 'Makefile'),
                'SYSLIBS="-Wl,-E -ldl -lreadline"',
                'SYSLIBS="-Wl,-E {} -ldl -lreadline -lncurses"'.format(readline))

    def build(self):
        self.target = {
                "Macos":"macosx",
                "Linux": "linux",
                "Windows":"mingw"
        }[str(self.settings.os)]
        cmd = "cd %s && make %s local" % (self.unzipped_name, self.target)
        self.run(cmd)

    def package(self):
        self.copy("FindLua.cmake", ".", ".")

        # Headers
        self.copy(pattern="*.h", dst="include", src="%s/install/include" % self.unzipped_name, keep_path=True)
        self.copy(pattern="*.hpp", dst="include", src="%s/install/include" % self.unzipped_name, keep_path=True)

        # libs
        self.copy(pattern="*.a", dst="lib", src="%s/install/lib" % self.unzipped_name, keep_path=True)
        self.copy(pattern="*.lib", dst="lib", src="%s/install/lib" % self.unzipped_name, keep_path=True)

        # binaries
        self.copy(pattern="lua*", dst="bin", src="%s/install/bin" % self.unzipped_name, keep_path=True)

    def package_info(self):
        self.cpp_info.libs = ['lua']
