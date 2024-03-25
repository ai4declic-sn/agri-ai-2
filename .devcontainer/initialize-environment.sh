#!/usr/bin/bash

# Initialise git
git config --global --add safe.directory $PWD
git init
# Check if Git username is set
git_username=$(git config --global user.name)
if [ -z "$git_username" ]; then
    echo "Git username is not set."
    read -p "Enter your Git username: " username
    git config --global user.name "$username"
else
    echo "Git username is set to: $git_username"
fi
# Check if Git email is set
git_email=$(git config --global user.email)
if [ -z "$git_email" ]; then
    echo "Git email is not set."
    read -p "Enter your Git email: " email
    git config --global user.email "$email"
else
    echo "Git email is set to: $git_email"
fi


# Initialise poetry
poetry install --no-root --no-interaction --no-cache --with 'dev, jnb, kd, ds'

# Initialise starship
mkdir -p ~/.config/fish/
echo 'starship init fish | source' >~/.config/fish/config.fish
starship preset no-runtime-versions >~/.config/starship.toml
