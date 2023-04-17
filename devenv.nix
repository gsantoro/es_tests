{ pkgs, ... }:

{
  # https://devenv.sh/packages/
  packages = [
     pkgs.git 
     pkgs.go-task
  ];

  enterShell = ''
    elastic-package-install
  '';

  scripts.elastic-package-install.exec = "go install github.com/elastic/elastic-package@latest";

  devcontainer.enable = true;

  languages.python.enable = true;
  languages.python.poetry.enable = true;
}
