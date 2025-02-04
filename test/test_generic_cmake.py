# Copyright (c) 2019, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=invalid-name, too-few-public-methods, bad-continuation

"""Test cases for the generic_cmake module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.generic_cmake import generic_cmake
from hpccm.toolchain import toolchain

class Test_generic_cmake(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default generic_cmake building block"""
        g = generic_cmake(
            cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                        '-D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda',
                        '-D GMX_BUILD_OWN_FFTW=ON',
                        '-D GMX_GPU=ON',
                        '-D GMX_MPI=OFF',
                        '-D GMX_OPENMP=ON',
                        '-D GMX_PREFER_STATIC_LIBS=ON',
                        '-D MPIEXEC_PREFLAGS=--allow-run-as-root'],
            directory='gromacs-2018.2',
            prefix='/usr/local/gromacs',
            url='https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz')
        self.assertEqual(str(g),
r'''# https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v2018.2.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/gromacs-2018.2/build && cd /var/tmp/gromacs-2018.2/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/gromacs -D CMAKE_BUILD_TYPE=Release -D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda -D GMX_BUILD_OWN_FFTW=ON -D GMX_GPU=ON -D GMX_MPI=OFF -D GMX_OPENMP=ON -D GMX_PREFER_STATIC_LIBS=ON -D MPIEXEC_PREFLAGS=--allow-run-as-root /var/tmp/gromacs-2018.2 && \
    cmake --build /var/tmp/gromacs-2018.2/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/gromacs-2018.2/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/v2018.2.tar.gz /var/tmp/gromacs-2018.2''')

    @ubuntu
    @docker
    def test_no_url(self):
        """missing url"""
        with self.assertRaises(RuntimeError):
            g = generic_cmake()

    @ubuntu
    @docker
    def test_invalid_package(self):
        """invalid package url"""
        with self.assertRaises(RuntimeError):
            g = generic_cmake(url='https://foo/bar.sh')

    @ubuntu
    @docker
    def test_build_directory(self):
        """build directory option"""
        g = generic_cmake(
            build_directory='/tmp/build',
            directory='spdlog-1.4.2',
            url='https://github.com/gabime/spdlog/archive/v1.4.2.tar.gz')
        self.assertEqual(str(g),
r'''# https://github.com/gabime/spdlog/archive/v1.4.2.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/gabime/spdlog/archive/v1.4.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v1.4.2.tar.gz -C /var/tmp -z && \
    mkdir -p /tmp/build && cd /tmp/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local /var/tmp/spdlog-1.4.2 && \
    cmake --build /tmp/build --target all -- -j$(nproc) && \
    cmake --build /tmp/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/v1.4.2.tar.gz /var/tmp/spdlog-1.4.2 /tmp/build''')    

    @ubuntu
    @docker
    def test_pre_and_post(self):
        """Preconfigure and postinstall options"""
        g = generic_cmake(
            directory='/var/tmp/spdlog-1.4.2',
            postinstall=['echo "post"'],
            preconfigure=['echo "pre"'],
            prefix='/usr/local/spdlog',
            url='https://github.com/gabime/spdlog/archive/v1.4.2.tar.gz')
        self.assertEqual(str(g),
r'''# https://github.com/gabime/spdlog/archive/v1.4.2.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/gabime/spdlog/archive/v1.4.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v1.4.2.tar.gz -C /var/tmp -z && \
    cd /var/tmp/spdlog-1.4.2 && \
    echo "pre" && \
    mkdir -p /var/tmp/spdlog-1.4.2/build && cd /var/tmp/spdlog-1.4.2/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/spdlog /var/tmp/spdlog-1.4.2 && \
    cmake --build /var/tmp/spdlog-1.4.2/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/spdlog-1.4.2/build --target install -- -j$(nproc) && \
    cd /usr/local/spdlog && \
    echo "post" && \
    rm -rf /var/tmp/v1.4.2.tar.gz /var/tmp/spdlog-1.4.2''')    

    @ubuntu
    @docker
    def test_environment_and_toolchain(self):
        """environment and toolchain"""
        tc = toolchain(CC='gcc', CXX='g++', FC='gfortran')
        g = generic_cmake(
            cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                        '-D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda',
                        '-D GMX_BUILD_OWN_FFTW=ON',
                        '-D GMX_GPU=ON',
                        '-D GMX_MPI=OFF',
                        '-D GMX_OPENMP=ON',
                        '-D GMX_PREFER_STATIC_LIBS=ON',
                        '-D MPIEXEC_PREFLAGS=--allow-run-as-root'],
            directory='gromacs-2018.2',
            environment={'FOO': 'BAR'},
            prefix='/usr/local/gromacs',
            toolchain=tc,
            url='https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz')
        self.assertEqual(str(g),
r'''# https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v2018.2.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/gromacs-2018.2/build && cd /var/tmp/gromacs-2018.2/build && FOO=BAR CC=gcc CXX=g++ FC=gfortran cmake -DCMAKE_INSTALL_PREFIX=/usr/local/gromacs -D CMAKE_BUILD_TYPE=Release -D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda -D GMX_BUILD_OWN_FFTW=ON -D GMX_GPU=ON -D GMX_MPI=OFF -D GMX_OPENMP=ON -D GMX_PREFER_STATIC_LIBS=ON -D MPIEXEC_PREFLAGS=--allow-run-as-root /var/tmp/gromacs-2018.2 && \
    cmake --build /var/tmp/gromacs-2018.2/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/gromacs-2018.2/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/v2018.2.tar.gz /var/tmp/gromacs-2018.2''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        g = generic_cmake(
            cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                        '-D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda',
                        '-D GMX_BUILD_OWN_FFTW=ON',
                        '-D GMX_GPU=ON',
                        '-D GMX_MPI=OFF',
                        '-D GMX_OPENMP=ON',
                        '-D GMX_PREFER_STATIC_LIBS=ON',
                        '-D MPIEXEC_PREFLAGS=--allow-run-as-root'],
            directory='gromacs-2018.2',
            prefix='/usr/local/gromacs',
            url='https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz')
        r = g.runtime()
        self.assertEqual(r,
r'''# https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz
COPY --from=0 /usr/local/gromacs /usr/local/gromacs''')
