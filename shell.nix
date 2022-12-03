{ pkgs ? import <nixpkgs> { }
}:

pkgs.mkShell {
  nativeBuildInputs = [ pkgs.python3Packages.virtualenv ];
}
