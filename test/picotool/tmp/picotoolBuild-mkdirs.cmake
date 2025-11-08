# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "/app/_deps/picotool-src"
  "/app/_deps/picotool-build"
  "/app/_deps"
  "/app/test/picotool/tmp"
  "/app/test/picotool/src/picotoolBuild-stamp"
  "/app/test/picotool/src"
  "/app/test/picotool/src/picotoolBuild-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/app/test/picotool/src/picotoolBuild-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/app/test/picotool/src/picotoolBuild-stamp${cfgdir}") # cfgdir has leading slash
endif()
