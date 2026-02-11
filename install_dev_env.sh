#!/bin/bash

# Exit on error
set -e

echo "Starting Development Environment Setup..."

# Install SDKMAN if not present
if [ ! -d "$HOME/.sdkman" ]; then
    echo "Installing SDKMAN..."
    curl -s "https://get.sdkman.io" | bash
else
    echo "SDKMAN already installed."
fi

# Source SDKMAN
export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"

# Install Kotlin
if ! command -v kotlinc &> /dev/null; then
    echo "Installing Kotlin..."
    sdk install kotlin 2.0.0
else
    echo "Kotlin already installed: $(kotlinc -version)"
fi

# Install Gradle
if ! command -v gradle &> /dev/null; then
    echo "Installing Gradle..."
    sdk install gradle 8.5
else
    echo "Gradle already installed: $(gradle -version)"
fi

echo "Development Environment Setup Complete!"
echo "Please verify with: kotlinc -version && gradle -version"
