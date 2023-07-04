{ pkgs, ... }:

{
  # https://devenv.sh/packages/
  packages = [
     pkgs.git 
     pkgs.go-task
     pkgs.direnv
  ];

  devcontainer.enable = true;
  devcontainer.settings.image = "ghcr.io/gsantoro/devenv:latest";

  languages.go.enable = true;

  languages.python.enable = true;
  languages.python.venv.enable = true;
  languages.python.poetry.enable = true;
  languages.python.poetry.install.enable = true;

  scripts.elastic-package-install.exec = "go install github.com/elastic/elastic-package@latest";
}
