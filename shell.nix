{ pkgs ? import <nixpkgs> {} }:

with pkgs.lib;

let
  pythonPkgs = (ps: with ps; [virtualenv]);
  pythonEnv = pkgs.python3.withPackages pythonPkgs;
  venv = ".venv";
in pkgs.mkShell {
    doCheck = false;
    buildInputs = [pythonEnv];
    shellHook = ''
      VENV=${venv}
      if test ! -d $VENV; then
        python -m venv $VENV
      fi
      source ./$VENV/bin/activate
      pip install -r requirements.txt
    '';
  }
