#!/bin/bash
# builds origin vanilla + bakasu for the cmf phone 1 (tetris).
# needs an aosp clang (r596125 works) and pahole >= 1.25 on PATH.
# keep DEBUG_INFO_BTF on: without it __user/__rcu lose their btf type tags,
# every struct-taking export gets a different crc and the rom's modules refuse to load.
set -euo pipefail
git submodule update --init KernelSU
: > .scmversion
export KBUILD_BUILD_USER=${KBUILD_BUILD_USER:-chakra} KBUILD_BUILD_HOST=${KBUILD_BUILD_HOST:-origin}
M="make O=out ARCH=arm64 LLVM=1 LLVM_IAS=1 CROSS_COMPILE=aarch64-linux-gnu-"
$M gki_defconfig
scripts/config --file out/.config -e KSU -d LTO_CLANG_FULL -e LTO_CLANG_THIN \
    -e DEBUG_INFO_BTF -d LOCALVERSION_AUTO --set-str LOCALVERSION "-Origin-Vanilla-BakaSU"
$M olddefconfig
$M -j"$(nproc)"
strings out/arch/arm64/boot/Image | grep -m1 'Linux version'
