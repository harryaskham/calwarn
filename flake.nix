{
  description = "Trigger Telegram messages for calendar events";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs { system = system; config.allowUnfree = true; };
    in {
      devShells = {
        default = pkgs.callPackage ./shell.nix { };
      };
      packages = rec {
        calwarn = pkgs.callPackage ./default.nix { };
        default = calwarn;
      };
    });
}
