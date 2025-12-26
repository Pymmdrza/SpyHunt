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
NC='\033[0m'

# Version and URLs
SPYHUNT_VERSION="4.0.3"
REPO_URL="https://github.com/Pymmdrza/SpyHunt.git"
INSTALL_DIR="${HOME}/.local/share/spyhunt"
BIN_DIR="${HOME}/.local/bin"
VENV_DIR="${INSTALL_DIR}/venv"

# Banner
print_banner() {
    echo -e "${CYAN}"
    cat << "EOF"
   _____ _____  __     __ _    _ _    _ _   _ _______ 
  / ____|  __ \ \ \   / /| |  | | |  | | \ | |__   __|
 | (___ | |__) | \ \_/ / | |__| | |  | |  \| |  | |   
  \___ \|  ___/   \   /  |  __  | |  | | . ` |  | |   
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
        PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d.  -f1)
        PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
        
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
            $SUDO apt-get install -y python3 python3-pip python3-venv python3-full
            ;;
        redhat)
            $SUDO yum install -y python3 python3-pip python3-virtualenv
            ;;
        fedora)
            $SUDO dnf install -y python3 python3-pip python3-virtualenv
            ;;
        arch)
            $SUDO pacman -Sy --noconfirm python python-pip python-virtualenv
            ;;
        alpine)
            $SUDO apk add --no-cache python3 py3-pip py3-virtualenv
            ;;
        macos)
            if !  command -v brew &> /dev/null; then
                log_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
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
            $SUDO apt-get install -y git curl wget nmap libffi-dev libssl-dev build-essential python3-venv
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
        git clone --depth 1 "$REPO_URL"
    fi
    
    log_success "SpyHunt downloaded successfully"
}

# Create and setup virtual environment
setup_venv() {
    log_info "Creating virtual environment..."
    
    # Remove old venv if exists
    if [ -d "$VENV_DIR" ]; then
        rm -rf "$VENV_DIR"
    fi
    
    # Create new virtual environment
    $PYTHON_CMD -m venv "$VENV_DIR"
    
    # Activate venv
    source "$VENV_DIR/bin/activate"
    
    log_success "Virtual environment created at $VENV_DIR"
}

# Install Python dependencies
install_python_deps() {
    log_info "Installing Python dependencies..."
    
    cd "$INSTALL_DIR/SpyHunt"
    
    # Always use virtual environment (required for Python 3.12+)
    setup_venv
    
    # Upgrade pip in venv
    "$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel
    
    # Install package
    "$VENV_DIR/bin/pip" install -e .
    
    log_success "Python dependencies installed"
}

# Install via pipx (alternative method for modern systems)
install_via_pipx() {
    log_info "Installing SpyHunt via pipx..."
    
    # Install pipx if not available
    if ! command -v pipx &> /dev/null; then
        log_info "Installing pipx..."
        case $OS in
            debian)
                $SUDO apt-get update
                $SUDO apt-get install -y pipx
                pipx ensurepath
                ;;
            macos)
                brew install pipx
                pipx ensurepath
                ;;
            *)
                $PYTHON_CMD -m pip install --user pipx
                $PYTHON_CMD -m pipx ensurepath
                ;;
        esac
    fi
    
    # Install spyhunt via pipx
    pipx install spyhunt || pipx upgrade spyhunt
    
    log_success "SpyHunt installed via pipx"
}

# Create wrapper script
create_wrapper() {
    log_info "Creating executable wrapper..."
    
    cat > "$BIN_DIR/spyhunt" << EOF
#!/bin/bash
# SpyHunt wrapper script
# Automatically activates virtual environment and runs spyhunt

VENV_DIR="$VENV_DIR"
INSTALL_DIR="$INSTALL_DIR/SpyHunt"

if [ -f "\$VENV_DIR/bin/activate" ]; then
    source "\$VENV_DIR/bin/activate"
    python -m spyhunt "\$@"
else
    echo "Error: Virtual environment not found at \$VENV_DIR"
    echo "Please reinstall SpyHunt:  curl -sSL https://raw.githubusercontent.com/Pymmdrza/SpyHunt/main/install.sh | bash"
    exit 1
fi
EOF

    chmod +x "$BIN_DIR/spyhunt"
    log_success "Wrapper script created at $BIN_DIR/spyhunt"
}

# Add to PATH
configure_path() {
    log_info "Configuring PATH..."
    
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
    
    if !  grep -q "$BIN_DIR" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# SpyHunt" >> "$SHELL_RC"
        if [ "$SHELL_NAME" = "fish" ]; then
            echo "set -gx PATH \$PATH $BIN_DIR" >> "$SHELL_RC"
        else
            echo "export PATH=\"\$PATH: $BIN_DIR\"" >> "$SHELL_RC"
        fi
        log_success "Added $BIN_DIR to PATH in $SHELL_RC"
    else
        log_info "PATH already configured"
    fi
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    export PATH="$PATH:$BIN_DIR"
    
    if [ -f "$BIN_DIR/spyhunt" ]; then
        # Test if spyhunt works
        if "$BIN_DIR/spyhunt" --help &> /dev/null; then
            log_success "SpyHunt installed and working!"
        else
            log_success "SpyHunt installed successfully!"
        fi
        
        echo ""
        echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║              Installation Complete!                             ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${WHITE}Installation Details:${NC}"
        echo -e "  ${CYAN}Install Directory: ${NC}  $INSTALL_DIR/SpyHunt"
        echo -e "  ${CYAN}Virtual Environment:${NC} $VENV_DIR"
        echo -e "  ${CYAN}Executable:${NC}         $BIN_DIR/spyhunt"
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
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
        log_success "Removed $INSTALL_DIR"
    fi
    
    # Remove wrapper
    if [ -f "$BIN_DIR/spyhunt" ]; then
        rm -f "$BIN_DIR/spyhunt"
        log_success "Removed $BIN_DIR/spyhunt"
    fi
    
    # Try to uninstall via pipx
    if command -v pipx &> /dev/null; then
        pipx uninstall spyhunt 2>/dev/null || true
    fi
    
    log_success "SpyHunt uninstalled successfully"
}

# Show help
show_help() {
    print_banner
    echo "Usage: ./install.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --pipx         Install via pipx (recommended for system-wide use)"
    echo "  --uninstall    Remove SpyHunt"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  curl -sSL https://raw.githubusercontent.com/Pymmdrza/SpyHunt/main/install.sh | bash"
    echo "  ./install.sh --pipx"
    echo "  ./install.sh --uninstall"
    echo ""
}

# Main installation function
main() {
    print_banner
    
    USE_PIPX=false
    
    for arg in "$@"; do
        case $arg in
            --help|-h)
                show_help
                exit 0
                ;;
            --pipx)
                USE_PIPX=true
                ;;
            --uninstall)
                detect_os
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
    
    if [ "$USE_PIPX" = true ]; then
        install_via_pipx
    else
        create_directories
        clone_repository
        install_python_deps
        create_wrapper
        configure_path
        verify_installation
    fi
}

main "$@"
