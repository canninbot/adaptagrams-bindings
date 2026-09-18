#!/bin/sh
set -eu

repository_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
destination="$repository_root/r/vendor"

rm -rf "$destination"
mkdir -p "$destination/cpp/include/adaptagrams" "$destination/cpp/src"
mkdir -p "$destination/third_party/adaptagrams/cola"

cp "$repository_root/CMakeLists.txt" "$destination/CMakeLists.txt"
cp "$repository_root/cpp/include/adaptagrams/adapter.hpp" \
    "$destination/cpp/include/adaptagrams/adapter.hpp"
cp "$repository_root/cpp/src/adapter.cpp" "$destination/cpp/src/adapter.cpp"

for library in libavoid libcola libvpsc; do
    mkdir -p "$destination/third_party/adaptagrams/cola/$library"
    find "$repository_root/third_party/adaptagrams/cola/$library" \
        -maxdepth 1 -type f \( -name '*.cpp' -o -name '*.h' \) \
        -exec cp '{}' "$destination/third_party/adaptagrams/cola/$library/" \;
done

cp "$repository_root/third_party/adaptagrams/cola/libavoid/LICENSE.LGPL" \
    "$destination/ADAPTAGRAMS-LICENSE.LGPL"

echo "R package native sources synchronized from the pinned upstream tree."
