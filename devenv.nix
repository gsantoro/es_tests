{ pkgs, ... }:

{
  # https://devenv.sh/packages/
  packages = [
     pkgs.git 
     pkgs.go 
     pkgs.go-task
     pkgs.direnv
  ];

  scripts.direnv-allow.exec = "direnv allow";
  scripts.direnv-reload.exec = "direnv reload";

  devcontainer.enable = true;

  languages.python.enable = true;
  languages.python.venv.enable = true;
  languages.python.poetry.enable = true;
  languages.python.poetry.install.enable = true;
}
