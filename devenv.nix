{ pkgs, ... }:

{
  # https://devenv.sh/packages/
  packages = [
     pkgs.git 
     pkgs.go-task
     pkgs.direnv
  ];

  devcontainer.enable = true;

  languages.go.enable = true;

  languages.python.enable = true;
  languages.python.venv.enable = true;
  languages.python.poetry.enable = true;
  languages.python.poetry.install.enable = true;
}
