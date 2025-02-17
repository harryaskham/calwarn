{ pkgs, python3Packages, ... }:

python3Packages.buildPythonApplication {
  pname = "calwarn";
  version = "0.1.0";
  srcs = ./.;
  pyproject = true;
  nativeBuildInputs = (with pkgs; [
  ]) ++ (with python3Packages; [
    setuptools
  ]);
  nativeCheckInputs = with python3Packages; [
    types-requests
  ];
  dependencies = with python3Packages; [
    icalendar
    requests
  ];
  doCheck = true;
}
