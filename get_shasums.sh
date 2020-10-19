echo "Choose package:
1: edgedb-cli
2: expo-cli
3: routahe"
read number
name=""
url=""

case $number in
  1)
    name="edgedb-cli"
    echo "Give pgkver: "
    read pkgver
    url=https://github.com/edgedb/edgedb-cli/archive/v$pkgver.tar.gz
    ;;
  2)
    name="expo-cli"
    echo "Give pgkver: "
    read pkgver
    url=https://registry.npmjs.org/expo-cli/-/expo-cli-$pkgver.tgz
    ;;
  3)
    name="routahe"
    echo "Give pgkver: "
    read pkgver
    url=https://registry.npmjs.org/routahe/-/routahe-$pkgver.tgz
    ;;
  *)
    echo "Unknown package, exiting"
    exit 1
esac

echo "Getting sha512sums for $name, v. $pkgver"
curl --output - $url | sha512sum -
