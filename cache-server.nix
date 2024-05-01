{ lib
, python310Packages
}:

python310Packages.buildPythonApplication rec {
  pname = "cache-server";
  version = "1.0";
  pyproject = true;

  src = ./.;

  nativeBuildInputs = [
    python310Packages.setuptools
  ];

  propagatedBuildInputs = [
    python310Packages.pyjwt
    python310Packages.websockets
    python310Packages.ed25519
  ];
}
