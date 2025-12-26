#!/bin/bash
# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                    SpyHunt v4.0 - Universal Installer                      ║
# ║        A comprehensive Network Scanner & Vulnerability Assessment tool     ║
# ║                      https://github.com/Pymmdrza/SpyHunt                   ║
# ╚════════════════════════════════════════════════════════════════════════════╝

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Version
SPYHUNT_VERSION="4.0.3"
REPO_URL="https://github.com/Pymmdrza/SpyHunt"
INSTALL_DIR="${HOME}/.local/share/spyhunt"
BIN_DIR="${HOME}/.local/bin"

# Banner
print_banner() {
    echo -e "${CYAN}"
    cat << "EOF"
   _____ _____  __     __ _    _ _    _ _   _ _______ 
  / ____|  __ \ \ \   / /| |  | | |  | | \ | |__   __|
 | (___ | |__) | \ \_/ / | |__| | |  | |  \| |  | |   
  \___ \|  ___/   \   /  |  __  | |  | | .  ` |  | |   
  ____) | |        | |   | |  | | |__| | |\  |  | |   
 |_____/|_|        |_|   |_|  |_|\____/|_| \_|  |_|   
                                                       
EOF
    echo -e "${WHITE}        Network Scanner & Vulnerability Assessment Tool${NC}"
    echo -e "${PURPLE}                    Version: ${SPYHUNT_VERSION}${NC}"
    echo -e "${YELLOW}            https://github.com/Pymmdrza/SpyHunt${NC}"
    echo ""
}

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
            PKG_MANAGER="apt-get"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
            PKG_MANAGER="yum"
        elif [ -f /etc/arch-release ]; then
            OS="arch"
            PKG_MANAGER="pacman"
        elif [ -f /etc/alpine-release ]; then
            OS="alpine"
            PKG_MANAGER="apk"
        elif [ -f /etc/fedora-release ]; then
            OS="fedora"
            PKG_MANAGER="dnf"
        else
            OS="linux"
            PKG_MANAGER="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PKG_MANAGER="brew"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
        PKG_MANAGER="choco"
    else
        OS="unknown"
        PKG_MANAGER="unknown"
    fi
    
    log_info "Detected OS: ${OS}"
}

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        log_warning "Running as root is not recommended.  Consider running as a normal user."
        SUDO=""
    else
        SUDO="sudo"
    fi
}

# Check and install Python
check_python() {
    log_info "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d.  -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 7 ]; then
            log_success "Python ${PYTHON_VERSION} found"
            PYTHON_CMD="python3"
            return 0
        else
            log_warning "Python ${PYTHON_VERSION} found, but version 3.7+ is required"
        fi
    fi
    
    log_info "Installing Python 3..."
    install_python
}

install_python() {
    case $OS in
        debian)
            $SUDO apt-get update
            $SUDO apt-get install -y python3 python3-pip python3-venv
            ;;
        redhat)
            $SUDO yum install -y python3 python3-pip
            ;;
        fedora)
            $SUDO dnf install -y python3 python3-pip
            ;;
        arch)
            $SUDO pacman -Sy --noconfirm python python-pip
            ;;
        alpine)
            $SUDO apk add --no-cache python3 py3-pip
            ;;
        macos)
            if !  command -v brew &> /dev/null; then
                log_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install. sh)"
            fi
            brew install python3
            ;;
        *)
            log_error "Unable to install Python automatically.  Please install Python 3.7+ manually."
            exit 1
            ;;
    esac
    PYTHON_CMD="python3"
    log_success "Python installed successfully"
}

# Install system dependencies
install_dependencies() {
    log_info "Installing system dependencies..."
    
    case $OS in
        debian)
            $SUDO apt-get update
            $SUDO apt-get install -y git curl wget nmap libffi-dev libssl-dev build-essential
            ;;
        redhat)
            $SUDO yum install -y git curl wget nmap libffi-devel openssl-devel gcc
            ;;
        fedora)
            $SUDO dnf install -y git curl wget nmap libffi-devel openssl-devel gcc
            ;;
        arch)
            $SUDO pacman -Sy --noconfirm git curl wget nmap base-devel
            ;;
        alpine)
            $SUDO apk add --no-cache git curl wget nmap build-base libffi-dev openssl-dev
            ;;
        macos)
            brew install git curl wget nmap
            ;;
        *)
            log_warning "Please install git, curl, wget, and nmap manually if not already installed."
            ;;
    esac
    
    log_success "System dependencies installed"
}

# Create directories
create_directories() {
    log_info "Creating installation directories..."
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    log_success "Directories created"
}

# Clone or update repository
clone_repository() {
    log_info "Downloading SpyHunt..."
    
    if [ -d "$INSTALL_DIR/SpyHunt" ]; then
        log_info "Existing installation found.  Updating..."
        cd "$INSTALL_DIR/SpyHunt"
        git pull origin main || git pull origin master
    else
        cd "$INSTALL_DIR"
        git clone --depth 1 "$REPO_URL. git"
    fi
    
    log_success "SpyHunt downloaded successfully"
}

# Install Python dependencies
install_python_deps() {
    log_info "Installing Python dependencies..."
    
    cd "$INSTALL_DIR/SpyHunt"
    
    # Create virtual environment (optional but recommended)
    if [ "$USE_VENV" = true ]; then
        log_info "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        source venv/bin/activate
        PIP_CMD="venv/bin/pip"
    else
        PIP_CMD="$PYTHON_CMD -m pip"
    fi
    
    # Upgrade pip
    $PIP_CMD install --upgrade pip
    
    # Install package
    $PIP_CMD install -e . 
    
    log_success "Python dependencies installed"
}

# Install via pip (alternative method)
install_via_pip() {
    log_info "Installing SpyHunt via pip..."
    $PYTHON_CMD -m pip install --upgrade pip
    $PYTHON_CMD -m pip install spyhunt
    log_success "SpyHunt installed via pip"
}

# Create wrapper script
create_wrapper() {
    log_info "Creating executable wrapper..."
    
    cat > "$BIN_DIR/spyhunt" << 'WRAPPER'
#!/bin/bash
INSTALL_DIR="${HOME}/.local/share/spyhunt/SpyHunt"

if [ -d "$INSTALL_DIR/venv" ]; then
    source "$INSTALL_DIR/venv/bin/activate"
fi

python3 -m spyhunt "$@"
WRAPPER

    chmod +x "$BIN_DIR/spyhunt"
    log_success "Wrapper script created at $BIN_DIR/spyhunt"
}

# Add to PATH
configure_path() {
    log_info "Configuring PATH..."
    
    # Detect shell
    SHELL_NAME=$(basename "$SHELL")
    
    case $SHELL_NAME in
        bash)
            SHELL_RC="$HOME/.bashrc"
            ;;
        zsh)
            SHELL_RC="$HOME/.zshrc"
            ;;
        fish)
            SHELL_RC="$HOME/.config/fish/config.fish"
            ;;
        *)
            SHELL_RC="$HOME/.profile"
            ;;
    esac
    
    # Add to PATH if not already present
    if ! grep -q "$BIN_DIR" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# SpyHunt" >> "$SHELL_RC"
        echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$SHELL_RC"
        log_success "Added $BIN_DIR to PATH in $SHELL_RC"
    else
        log_info "PATH already configured"
    fi
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    export PATH="$PATH:$BIN_DIR"
    
    if command -v spyhunt &> /dev/null || [ -f "$BIN_DIR/spyhunt" ]; then
        log_success "SpyHunt installed successfully!"
        echo ""
        echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║              Installation Complete!                             ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${WHITE}Usage:${NC}"
        echo -e "  ${CYAN}spyhunt --help${NC}              Show help message"
        echo -e "  ${CYAN}spyhunt -u example.com${NC}      Scan a target"
        echo ""
        echo -e "${YELLOW}Note:  Run 'source $SHELL_RC' or restart your terminal to use spyhunt${NC}"
        echo ""
    else
        log_error "Installation verification failed"
        exit 1
    fi
}

# Uninstall function
uninstall() {
    log_info "Uninstalling SpyHunt..."
    
    # Remove installation directory
    rm -rf "$INSTALL_DIR/SpyHunt"
    
    # Remove wrapper
    rm -f "$BIN_DIR/spyhunt"
    
    # Remove pip package
    $PYTHON_CMD -m pip uninstall spyhunt -y 2>/dev/null || true
    
    log_success "SpyHunt uninstalled successfully"
}

# Show help
show_help() {
    print_banner
    echo "Usage: ./install.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --pip          Install via pip (simpler method)"
    echo "  --venv         Use virtual environment"
    echo "  --uninstall    Remove SpyHunt"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  curl -sSL https://raw.githubusercontent.com/Pymmdrza/SpyHunt/main/install. sh | bash"
    echo "  ./install.sh --pip"
    echo "  ./install.sh --venv"
    echo ""
}

# Main installation function
main() {
    print_banner
    
    # Parse arguments
    USE_VENV=false
    USE_PIP=false
    
    for arg in "$@"; do
        case $arg in
            --help|-h)
                show_help
                exit 0
                ;;
            --pip)
                USE_PIP=true
                ;;
            --venv)
                USE_VENV=true
                ;;
            --uninstall)
                detect_os
                check_root
                check_python
                uninstall
                exit 0
                ;;
        esac
    done
    
    log_info "Starting SpyHunt installation..."
    echo ""
    
    detect_os
    check_root
    check_python
    install_dependencies
    
    if [ "$USE_PIP" = true ]; then
        install_via_pip
    else
        create_directories
        clone_repository
        install_python_deps
        create_wrapper
        configure_path
    fi
    
    verify_installation
}

# Run main
main "$@"
