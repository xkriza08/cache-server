{ pkgs ? import <nixpkgs> {} }:
pkgs.callPackage ./cache-server.nix {}
