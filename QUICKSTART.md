# SpyHunt - Quick Start Guide

Get started with SpyHunt in minutes!

## Installation

### Using pip (Recommended)

```bash
pip install spyhunt
```

That's it! SpyHunt is now installed and ready to use.

### Verify Installation

```bash
spyhunt --help
```

You should see the SpyHunt help menu with all available options.

## Basic Usage

### 1. Subdomain Enumeration

Find subdomains for a target domain:

```bash
spyhunt -s example.com --save subdomains.txt
```

### 2. Check for Live Hosts

Probe which subdomains are live:

```bash
spyhunt -p subdomains.txt --save live_hosts.txt
```

### 3. Scan for Vulnerabilities

#### XSS Scanner
```bash
spyhunt --xss "https://example.com/page?param=value"
```

#### SQL Injection Scanner
```bash
spyhunt --sqli "https://example.com/page?id=1"
```

#### XXE Scanner (New in v4.0)
```bash
spyhunt --xxe https://example.com/api/xml
```

#### SSRF Scanner (New in v4.0)
```bash
spyhunt --ssrf "https://example.com/api?url=test"
```

#### SSTI Scanner (New in v4.0)
```bash
spyhunt --ssti "https://example.com/page?template=test"
```

#### NoSQL Injection Scanner (New in v4.0)
```bash
spyhunt --nosqli "https://example.com/api?id=test"
```

#### CRLF Injection Scanner (New in v4.0)
```bash
spyhunt --crlf "https://example.com/redirect?url=test"
```

### 4. Directory Bruteforcing

Find hidden directories and files:

```bash
spyhunt --directorybrute example.com --wordlist /path/to/wordlist.txt --threads 50
```

### 5. Port Scanning

Scan a CIDR range for open ports:

```bash
spyhunt --cidr_notation 192.168.1.0/24 --ports 80,443,8080,8443
```

### 6. Cloud Security

Scan for exposed AWS S3 buckets:

```bash
spyhunt --s3-scan example.com
```

Scan for Azure resources:

```bash
spyhunt --azure_scan example.com
```

Scan for GCP storage:

```bash
spyhunt --gcp-scan example.com
```

## Common Workflows

### Bug Bounty Recon Workflow

```bash
# Step 1: Enumerate subdomains
spyhunt -s target.com --save subdomains.txt

# Step 2: Find live hosts
spyhunt -p subdomains.txt --save live.txt

# Step 3: Scan for vulnerabilities
spyhunt --xxe https://api.target.com/xml --save xxe.json
spyhunt --ssrf "https://api.target.com/fetch?url=test" --save ssrf.json
spyhunt --xss "https://target.com/search?q=test" --save xss.json
spyhunt --sqli "https://target.com/product?id=1" --save sqli.json

# Step 4: Check for misconfigurations
spyhunt -co live.txt --save cors.txt
spyhunt -hh live.txt --save host_header.txt
```

### Web Application Security Assessment

```bash
# Crawl the website
spyhunt -wc https://example.com --depth 3 --save urls.txt

# Find JavaScript files
spyhunt -j example.com --save js_files.txt

# Scan JavaScript for sensitive info
spyhunt -javascript example.com --save js_secrets.txt

# Check security headers
spyhunt -sh example.com

# Test for common vulnerabilities
spyhunt --xss "https://example.com/search?q=test"
spyhunt --sqli "https://example.com/page?id=1"
spyhunt -ph example.com?id= # Path traversal
spyhunt -or example.com # Open redirect
```

### Network Security Assessment

```bash
# Scan network range
spyhunt --cidr_notation 10.0.0.0/24 --ports 21,22,80,443,3306,3389,8080

# Nmap scan
spyhunt -n example.com

# FTP scanning
spyhunt -fs ftp.example.com --ftp-userlist users.txt --ftp-passlist passwords.txt

# SMB scanning
spyhunt --smb_auto --smb-target 10.0.0.100
```

## Tips and Tricks

### 1. Use Verbose Mode

Get more detailed output:

```bash
spyhunt -s example.com -v
```

### 2. Adjust Concurrency

Control the number of concurrent requests:

```bash
spyhunt -s example.com -c 50
```

### 3. Use Proxies

Route traffic through a proxy:

```bash
spyhunt --xss "https://example.com?q=test" --proxy http://proxy.com:8080
```

Or use a proxy file:

```bash
spyhunt --brute-user-pass example.com/login --proxy-file proxies.txt
```

### 4. Custom Headers

Add custom headers to requests:

```bash
spyhunt -ch example.com
```

### 5. Save All Results

Always save your results for later analysis:

```bash
spyhunt -s example.com --save results.txt
```

### 6. SSL Verification

By default, SSL verification is enabled. To disable for testing:

```bash
spyhunt --xxe https://self-signed.local/api --insecure
```

**Warning:** Only use `--insecure` in controlled testing environments.

## External Dependencies

Some SpyHunt features require external tools. Install them using:

```bash
# Clone the repository
git clone https://github.com/Pymmdrza/spyhunt.git
cd spyhunt

# Run the installer (requires sudo on Linux/Mac)
sudo python3 install.py
```

This installs:
- nuclei
- subfinder
- httpx
- waybackurls
- and other tools

## Configuration

### Shodan Integration

To use Shodan features, set your API key:

```bash
spyhunt -s example.com --shodan-api YOUR_SHODAN_KEY
```

### IPInfo Integration

For IP information lookups:

```bash
spyhunt --ipinfo example.com --token YOUR_IPINFO_TOKEN
```

## Output Formats

SpyHunt supports various output formats:

### Text Files
```bash
spyhunt -s example.com --save results.txt
```

### JSON
```bash
spyhunt --xxe https://example.com/api --save results.json
```

## Getting Help

### Show All Options
```bash
spyhunt --help
```

### Update SpyHunt
```bash
spyhunt -u
```

### Check Version
```bash
python -c "import spyhunt; print(spyhunt.__version__)"
```

## Common Issues

### Issue: "Command not found"

**Solution:** Make sure pip's bin directory is in your PATH:

```bash
# Linux/Mac
export PATH="$HOME/.local/bin:$PATH"

# Add to ~/.bashrc or ~/.zshrc for permanent effect
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Issue: Permission Denied

**Solution:** Use `--user` flag during installation:

```bash
pip install --user spyhunt
```

### Issue: Import Errors

**Solution:** Reinstall with all dependencies:

```bash
pip uninstall spyhunt
pip install spyhunt --upgrade
```

## Next Steps

1. **Read the Full Documentation:** Check `README.md` for comprehensive usage examples
2. **Learn About New Features:** See what's new in v4.0
3. **Join the Community:** Star the project on GitHub and contribute!

## Security Notice

**Important:** SpyHunt is a powerful security tool. Always:

- ✅ Get proper authorization before scanning
- ✅ Use only on systems you own or have permission to test
- ✅ Follow responsible disclosure practices
- ✅ Comply with local laws and regulations

Unauthorized scanning may be illegal in your jurisdiction.

## Support

- **GitHub Issues:** [https://github.com/Pymmdrza/spyhunt/issues](https://github.com/Pymmdrza/spyhunt/issues)
- **Documentation:** [https://github.com/Pymmdrza/spyhunt](https://github.com/Pymmdrza/spyhunt)

---

**Happy Hunting! 🕵️**

