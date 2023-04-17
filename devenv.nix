{ pkgs, ... }:

{
  # https://devenv.sh/packages/
  packages = [
     pkgs.git 
     pkgs.go-task
     pkgs.direnv
  ];

  scripts.devenv-install.exec = "nix profile install --accept-flake-config github:cachix/devenv/latest";
  scripts.t.exec = "task";

  scripts.direnv-allow.exec = "direnv allow";
  scripts.direnv-reload.exec = "direnv reload";

  devcontainer.enable = true;

  languages.python.enable = true;
  languages.python.poetry.enable = true;
}
