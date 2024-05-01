{ pkgs ? import <nixpkgs> { }, stdenv ? pkgs.stdenv, fetchurl ? pkgs.fetchurl }:
stdenv.mkDerivation {
  name = "testhello";

  src = fetchurl {
    url = "mirror://gnu/hello/hello-2.3.tar.bz2";
    sha256 = "0c7vijq8y68bpr7g6dh1gny0bff8qq81vnp4ch8pjzvg56wb3js1";
  };

  patchPhase = ''
    sed -i 's/Hello, world!/Hello, cache-server tester!/g' src/hello.c
  '';
}