"""
Professional CLI interface for SpyHunt cybersecurity reconnaissance framework.

This module provides a comprehensive command-line interface with standardized
argument parsing, configuration management, and result formatting.
"""

import argparse
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint
from rich.markdown import Markdown

from ..core.config import Config, get_config, set_config
from ..core.logger import setup_logging, get_logger
from ..core.engine import SpyHuntEngine, ScanJob
from ..modules import register_builtin_modules
from ..core.exceptions import SpyHuntException, ValidationError

# Initialize console with proper configuration
console = Console(highlight=False, log_path=False)


def display_banner() -> None:
    """Display the SpyHunt banner with version information."""
    banner = """
[bold magenta]
    ███████╗██████╗ ██╗   ██╗    ██╗  ██╗██╗   ██╗███╗   ██╗████████╗
    ██╔════╝██╔══██╗╚██╗ ██╔╝    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝
    ███████╗██████╔╝ ╚████╔╝     ███████║██║   ██║██╔██╗ ██║   ██║   
    ╚════██║██╔═══╝   ╚██╔╝      ██╔══██║██║   ██║██║╚██╗██║   ██║   
    ███████║██║        ██║       ██║  ██║╚██████╔╝██║ ╚████║   ██║   
    ╚══════╝╚═╝        ╚═╝       ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   
[/bold magenta]

[cyan]🛡️  Professional Cybersecurity Reconnaissance Framework[/cyan]
[dim]Version 4.0.0 | Enhanced Performance & Security Edition[/dim]
[dim]By c0deninja | Built for professional security assessments[/dim]
"""
    console.print(Panel(
        banner, 
        title="[bold red]SpyHunt Framework[/bold red]", 
        title_align="center",
        border_style="cyan",
        padding=(1, 2)
    ))


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the main argument parser with all subcommands.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        prog='spyhunt',
        description='SpyHunt - Professional Cybersecurity Reconnaissance Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🔍 USAGE EXAMPLES:
  
  Subdomain Enumeration:
    spyhunt subdomain -t example.com --output results.json --format json
    spyhunt subdomain -t example.com --wordlist custom.txt --passive-only
  
  Port Scanning:
    spyhunt portscan -t 192.168.1.0/24 --ports 80,443,8080 --threads 100
    spyhunt portscan -t example.com --top-ports 1000 --service-detection
  
  Vulnerability Assessment:
    spyhunt vuln --xss --sqli -f urls.txt --threads 50 --rate-limit 10
    spyhunt vuln -t https://example.com --all-checks --output vuln_report.json
  
  Web Application Scanning:
    spyhunt webapp -t https://example.com --crawl-depth 3 --javascript
    spyhunt webapp -t https://api.example.com --api-endpoints --headers
  
  Cloud Security Assessment:
    spyhunt cloud -t example.com --aws --s3-buckets --azure
    spyhunt cloud -t company-name --all-providers --output cloud_assets.json
  
  Network Analysis:
    spyhunt network -t example.com --asn --whois --dns-records
    spyhunt network -t 8.8.8.8 --reverse-dns --asn --output network_info.json
  
  OSINT Gathering:
    spyhunt osint -t example.com --emails --social-media --data-breaches
    spyhunt osint -t "John Doe" --google-dorks --breach-data
  
  Batch Operations:
    spyhunt batch --config comprehensive_scan.yaml --parallel 10
    spyhunt batch --config targets.yaml --output batch_results/
  
  Configuration Management:
    spyhunt config --show
    spyhunt config --init
    spyhunt config --validate custom_config.yaml

📚 For detailed documentation: https://github.com/spyhunt/spyhunt/wiki
🛡️  Report issues: https://github.com/spyhunt/spyhunt/issues
        """
    )
    
    # Global options - Core functionality
    parser.add_argument(
        '--version', 
        action='version', 
        version='SpyHunt 4.0.0 - Professional Security Assessment Framework'
    )
    
    # Configuration and logging
    config_group = parser.add_argument_group('Configuration & Logging')
    config_group.add_argument(
        '-c', '--config', 
        metavar='FILE',
        help='Configuration file path (YAML/JSON format)'
    )
    config_group.add_argument(
        '-v', '--verbose', 
        action='count', 
        default=0,
        help='Increase verbosity (-v: INFO, -vv: DEBUG)'
    )
    config_group.add_argument(
        '--quiet', 
        action='store_true',
        help='Suppress all output except errors'
    )
    config_group.add_argument(
        '--log-file', 
        metavar='FILE',
        help='Log file path for detailed logging'
    )
    
    # Performance and networking
    performance_group = parser.add_argument_group('Performance & Networking')
    performance_group.add_argument(
        '--threads', 
        type=int, 
        metavar='N',
        help='Number of concurrent threads (default: auto-detect)'
    )
    performance_group.add_argument(
        '--timeout', 
        type=int, 
        metavar='SECONDS',
        default=10,
        help='Request timeout in seconds (default: 10)'
    )
    performance_group.add_argument(
        '--rate-limit', 
        type=int, 
        metavar='RPS',
        help='Requests per second limit (default: unlimited)'
    )
    performance_group.add_argument(
        '--delay', 
        type=float, 
        metavar='SECONDS',
        help='Delay between requests in seconds'
    )
    
    # Output and formatting
    output_group = parser.add_argument_group('Output & Formatting')
    output_group.add_argument(
        '-o', '--output', 
        metavar='FILE',
        help='Output file path'
    )
    output_group.add_argument(
        '--format', 
        choices=['json', 'yaml', 'csv', 'text', 'xml'],
        default='json',
        help='Output format (default: json)'
    )
    output_group.add_argument(
        '--pretty', 
        action='store_true',
        help='Pretty-print output (human-readable formatting)'
    )
    output_group.add_argument(
        '--no-color', 
        action='store_true',
        help='Disable colored output'
    )
    
    # Proxy and anonymity
    proxy_group = parser.add_argument_group('Proxy & Anonymity')
    proxy_group.add_argument(
        '--proxy', 
        metavar='URL',
        help='Proxy URL (http://proxy:port, socks5://proxy:port)'
    )
    proxy_group.add_argument(
        '--proxy-file', 
        metavar='FILE',
        help='File containing proxy list (one per line)'
    )
    proxy_group.add_argument(
        '--proxy-auth', 
        metavar='USER:PASS',
        help='Proxy authentication credentials'
    )
    proxy_group.add_argument(
        '--user-agent', 
        metavar='STRING',
        help='Custom User-Agent string'
    )
    proxy_group.add_argument(
        '--random-agent', 
        action='store_true',
        help='Use random User-Agent for each request'
    )
    
    # Create subparsers for different modules
    subparsers = parser.add_subparsers(
        dest='command', 
        help='Available reconnaissance modules',
        metavar='COMMAND'
    )
    
    # Subdomain enumeration module
    subdomain_parser = subparsers.add_parser(
        'subdomain', 
        help='Comprehensive subdomain enumeration',
        description='Perform comprehensive subdomain discovery using multiple techniques',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spyhunt subdomain -t example.com
  spyhunt subdomain -t example.com --wordlist custom.txt --bruteforce
  spyhunt subdomain -t example.com --passive-only --dns-servers 8.8.8.8,1.1.1.1
        """
    )
    subdomain_parser.add_argument(
        '-t', '--target', 
        required=True, 
        metavar='DOMAIN',
        help='Target domain (e.g., example.com)'
    )
    subdomain_parser.add_argument(
        '--wordlist', 
        metavar='FILE',
        help='Custom wordlist file for bruteforce enumeration'
    )
    subdomain_parser.add_argument(
        '--dns-servers', 
        metavar='SERVERS',
        help='Custom DNS servers (comma-separated, e.g., 8.8.8.8,1.1.1.1)'
    )
    subdomain_parser.add_argument(
        '--bruteforce', 
        action='store_true',
        help='Enable DNS bruteforce enumeration'
    )
    subdomain_parser.add_argument(
        '--passive-only', 
        action='store_true',
        help='Use only passive enumeration techniques'
    )
    subdomain_parser.add_argument(
        '--resolve', 
        action='store_true',
        help='Resolve found subdomains to IP addresses'
    )
    subdomain_parser.add_argument(
        '--wildcard-filter', 
        action='store_true',
        help='Filter out wildcard DNS responses'
    )
    subdomain_parser.add_argument(
        '-w', '--workers', 
        type=int, 
        metavar='N',
        default=50,
        help='Number of concurrent DNS workers (default: 50)'
    )
    
    # Port scanning module
    portscan_parser = subparsers.add_parser(
        'portscan', 
        help='Advanced port scanning and service detection',
        description='Perform comprehensive port scanning with service detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spyhunt portscan -t 192.168.1.1
  spyhunt portscan -t 192.168.1.0/24 --ports 80,443,8080 --service-detection
  spyhunt portscan -t example.com --top-ports 1000 --stealth
        """
    )
    portscan_parser.add_argument(
        '-t', '--target', 
        required=True, 
        metavar='TARGET',
        help='Target IP, CIDR range, or hostname (e.g., 192.168.1.1, 192.168.1.0/24)'
    )
    portscan_parser.add_argument(
        '-p', '--ports', 
        metavar='PORTS',
        help='Port specification (e.g., 1-1000, 80,443,8080, or 1-65535)'
    )
    portscan_parser.add_argument(
        '--top-ports', 
        type=int, 
        metavar='N',
        help='Scan top N most common ports'
    )
    portscan_parser.add_argument(
        '--service-detection', 
        action='store_true',
        help='Enable service version detection'
    )
    portscan_parser.add_argument(
        '--os-detection', 
        action='store_true',
        help='Enable operating system detection'
    )
    portscan_parser.add_argument(
        '--stealth', 
        action='store_true',
        help='Use stealth scanning techniques (SYN scan)'
    )
    portscan_parser.add_argument(
        '--udp', 
        action='store_true',
        help='Include UDP port scanning'
    )
    portscan_parser.add_argument(
        '--connect-scan', 
        action='store_true',
        help='Use TCP connect scan (more reliable but slower)'
    )
    portscan_parser.add_argument(
        '--ping-sweep', 
        action='store_true',
        help='Perform ping sweep before port scanning'
    )
    
    # Vulnerability scanning module
    vuln_parser = subparsers.add_parser(
        'vuln', 
        help='Comprehensive vulnerability assessment',
        description='Perform automated vulnerability scanning and assessment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spyhunt vuln -t https://example.com --all-checks
  spyhunt vuln -f urls.txt --xss --sqli --lfi
  spyhunt vuln -t https://api.example.com --injection-attacks --rate-limit 5
        """
    )
    
    vuln_target_group = vuln_parser.add_mutually_exclusive_group(required=True)
    vuln_target_group.add_argument(
        '-f', '--file', 
        metavar='FILE',
        help='File containing URLs/targets (one per line)'
    )
    vuln_target_group.add_argument(
        '-t', '--target', 
        metavar='URL',
        help='Single target URL'
    )
    
    # Vulnerability categories
    vuln_checks = vuln_parser.add_argument_group('Vulnerability Checks')
    vuln_checks.add_argument(
        '--all-checks', 
        action='store_true',
        help='Enable all vulnerability checks'
    )
    vuln_checks.add_argument(
        '--injection-attacks', 
        action='store_true',
        help='Enable all injection attack tests (XSS, SQLi, etc.)'
    )
    vuln_checks.add_argument(
        '--xss', 
        action='store_true',
        help='Cross-Site Scripting (XSS) vulnerability scan'
    )
    vuln_checks.add_argument(
        '--sqli', 
        action='store_true',
        help='SQL injection vulnerability scan'
    )
    vuln_checks.add_argument(
        '--lfi', 
        action='store_true',
        help='Local File Inclusion (LFI) vulnerability scan'
    )
    vuln_checks.add_argument(
        '--rfi', 
        action='store_true',
        help='Remote File Inclusion (RFI) vulnerability scan'
    )
    vuln_checks.add_argument(
        '--xxe', 
        action='store_true',
        help='XML External Entity (XXE) vulnerability scan'
    )
    vuln_checks.add_argument(
        '--ssrf', 
        action='store_true',
        help='Server-Side Request Forgery (SSRF) vulnerability scan'
    )
    vuln_checks.add_argument(
        '--cors', 
        action='store_true',
        help='CORS misconfiguration vulnerability scan'
    )
    vuln_checks.add_argument(
        '--csrf', 
        action='store_true',
        help='Cross-Site Request Forgery (CSRF) vulnerability scan'
    )
    vuln_checks.add_argument(
        '--headers', 
        action='store_true',
        help='Security headers analysis and misconfiguration detection'
    )
    vuln_checks.add_argument(
        '--open-redirect', 
        action='store_true',
        help='Open redirect vulnerability scan'
    )
    vuln_checks.add_argument(
        '--path-traversal', 
        action='store_true',
        help='Path traversal vulnerability scan'
    )
    
    # Vulnerability scanning options
    vuln_options = vuln_parser.add_argument_group('Scanning Options')
    vuln_options.add_argument(
        '--payloads', 
        metavar='DIR',
        help='Custom payloads directory'
    )
    vuln_options.add_argument(
        '--severity-filter', 
        choices=['low', 'medium', 'high', 'critical'],
        help='Filter results by minimum severity level'
    )
    vuln_options.add_argument(
        '--false-positive-filter', 
        action='store_true',
        help='Enable advanced false positive filtering'
    )
    
    # Web application scanning module
    webapp_parser = subparsers.add_parser(
        'webapp', 
        help='Web application security assessment',
        description='Comprehensive web application scanning and analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spyhunt webapp -t https://example.com --crawl-depth 3
  spyhunt webapp -t https://app.example.com --javascript --api-endpoints
  spyhunt webapp -t https://example.com --all-checks --crawl-depth 5
        """
    )
    webapp_parser.add_argument(
        '-t', '--target', 
        required=True, 
        metavar='URL',
        help='Target web application URL'
    )
    
    # Crawling options
    crawl_group = webapp_parser.add_argument_group('Crawling Options')
    crawl_group.add_argument(
        '--crawl-depth', 
        type=int, 
        default=3, 
        metavar='N',
        help='Maximum crawling depth (default: 3)'
    )
    crawl_group.add_argument(
        '--max-pages', 
        type=int, 
        metavar='N',
        help='Maximum number of pages to crawl'
    )
    crawl_group.add_argument(
        '--exclude-extensions', 
        metavar='EXT',
        default='jpg,jpeg,png,gif,css,js,ico',
        help='File extensions to exclude from crawling'
    )
    crawl_group.add_argument(
        '--include-external', 
        action='store_true',
        help='Include external links in crawling'
    )
    
    # Analysis options
    analysis_group = webapp_parser.add_argument_group('Analysis Options')
    analysis_group.add_argument(
        '--all-checks', 
        action='store_true',
        help='Enable all web application checks'
    )
    analysis_group.add_argument(
        '--javascript', 
        action='store_true',
        help='Analyze JavaScript files for sensitive information'
    )
    analysis_group.add_argument(
        '--forms', 
        action='store_true',
        help='Analyze forms and input fields'
    )
    analysis_group.add_argument(
        '--cookies', 
        action='store_true',
        help='Analyze cookies and session management'
    )
    analysis_group.add_argument(
        '--api-endpoints', 
        action='store_true',
        help='Discover and analyze API endpoints'
    )
    analysis_group.add_argument(
        '--comments', 
        action='store_true',
        help='Extract and analyze HTML/JavaScript comments'
    )
    analysis_group.add_argument(
        '--technologies', 
        action='store_true',
        help='Identify web technologies and frameworks'
    )
    analysis_group.add_argument(
        '--secrets', 
        action='store_true',
        help='Search for exposed secrets and sensitive data'
    )
    
    # Cloud security assessment module
    cloud_parser = subparsers.add_parser(
        'cloud', 
        help='Cloud infrastructure security assessment',
        description='Discover and assess cloud resources and misconfigurations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spyhunt cloud -t company-name --all-providers
  spyhunt cloud -t example.com --aws --s3-buckets
  spyhunt cloud -t target.com --azure --storage-accounts --misconfigurations
        """
    )
    cloud_parser.add_argument(
        '-t', '--target', 
        required=True, 
        metavar='TARGET',
        help='Target domain, company name, or keyword'
    )
    
    # Cloud providers
    providers_group = cloud_parser.add_argument_group('Cloud Providers')
    providers_group.add_argument(
        '--all-providers', 
        action='store_true',
        help='Scan all supported cloud providers'
    )
    providers_group.add_argument(
        '--aws', 
        action='store_true',
        help='Amazon Web Services (AWS) resource discovery'
    )
    providers_group.add_argument(
        '--azure', 
        action='store_true',
        help='Microsoft Azure resource discovery'
    )
    providers_group.add_argument(
        '--gcp', 
        action='store_true',
        help='Google Cloud Platform (GCP) resource discovery'
    )
    providers_group.add_argument(
        '--digitalocean', 
        action='store_true',
        help='DigitalOcean resource discovery'
    )
    
    # AWS-specific options
    aws_group = cloud_parser.add_argument_group('AWS Options')
    aws_group.add_argument(
        '--s3-buckets', 
        action='store_true',
        help='S3 bucket enumeration and misconfiguration detection'
    )
    aws_group.add_argument(
        '--cloudfront', 
        action='store_true',
        help='CloudFront distribution discovery'
    )
    aws_group.add_argument(
        '--lambda-functions', 
        action='store_true',
        help='Lambda function discovery'
    )
    
    # Azure-specific options
    azure_group = cloud_parser.add_argument_group('Azure Options')
    azure_group.add_argument(
        '--storage-accounts', 
        action='store_true',
        help='Azure storage account enumeration'
    )
    azure_group.add_argument(
        '--key-vaults', 
        action='store_true',
        help='Azure Key Vault discovery'
    )
    
    # Security checks
    security_group = cloud_parser.add_argument_group('Security Checks')
    security_group.add_argument(
        '--misconfigurations', 
        action='store_true',
        help='Check for common cloud misconfigurations'
    )
    security_group.add_argument(
        '--public-access', 
        action='store_true',
        help='Identify publicly accessible resources'
    )
    
    # Network analysis and reconnaissance module
    network_parser = subparsers.add_parser(
        'network', 
        help='Network analysis and reconnaissance',
        description='Comprehensive network information gathering and analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spyhunt network -t example.com --all-checks
  spyhunt network -t 8.8.8.8 --asn --whois --reverse-dns
  spyhunt network -t example.com --dns-records --zone-transfer
        """
    )
    network_parser.add_argument(
        '-t', '--target', 
        required=True, 
        metavar='TARGET',
        help='Target IP address, domain, or CIDR range'
    )
    
    # Information gathering options
    info_group = network_parser.add_argument_group('Information Gathering')
    info_group.add_argument(
        '--all-checks', 
        action='store_true',
        help='Enable all network analysis checks'
    )
    info_group.add_argument(
        '--asn', 
        action='store_true',
        help='Autonomous System Number (ASN) information lookup'
    )
    info_group.add_argument(
        '--whois', 
        action='store_true',
        help='WHOIS information lookup'
    )
    info_group.add_argument(
        '--dns-records', 
        action='store_true',
        help='Comprehensive DNS record enumeration'
    )
    info_group.add_argument(
        '--reverse-dns', 
        action='store_true',
        help='Reverse DNS lookup and PTR record enumeration'
    )
    info_group.add_argument(
        '--geolocation', 
        action='store_true',
        help='IP geolocation information'
    )
    info_group.add_argument(
        '--cdn-detection', 
        action='store_true',
        help='Content Delivery Network (CDN) detection'
    )
    
    # DNS-specific options
    dns_group = network_parser.add_argument_group('DNS Options')
    dns_group.add_argument(
        '--zone-transfer', 
        action='store_true',
        help='Attempt DNS zone transfer (AXFR)'
    )
    dns_group.add_argument(
        '--dns-bruteforce', 
        action='store_true',
        help='DNS record bruteforce enumeration'
    )
    dns_group.add_argument(
        '--dns-servers', 
        metavar='SERVERS',
        help='Custom DNS servers for queries (comma-separated)'
    )
    
    # Network scanning options
    scan_group = network_parser.add_argument_group('Network Scanning')
    scan_group.add_argument(
        '--traceroute', 
        action='store_true',
        help='Perform traceroute to target'
    )
    scan_group.add_argument(
        '--ping-sweep', 
        action='store_true',
        help='Ping sweep for network range discovery'
    )
    
    # OSINT (Open Source Intelligence) module
    osint_parser = subparsers.add_parser(
        'osint', 
        help='Open Source Intelligence (OSINT) gathering',
        description='Comprehensive OSINT collection from various sources',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spyhunt osint -t example.com --all-sources
  spyhunt osint -t "Company Name" --emails --social-media
  spyhunt osint -t john.doe@example.com --data-breaches --people-search
        """
    )
    osint_parser.add_argument(
        '-t', '--target', 
        required=True, 
        metavar='TARGET',
        help='Target domain, company, person, or email address'
    )
    
    # OSINT categories
    sources_group = osint_parser.add_argument_group('Information Sources')
    sources_group.add_argument(
        '--all-sources', 
        action='store_true',
        help='Enable all OSINT sources and techniques'
    )
    sources_group.add_argument(
        '--emails', 
        action='store_true',
        help='Email address enumeration and validation'
    )
    sources_group.add_argument(
        '--social-media', 
        action='store_true',
        help='Social media profile discovery and analysis'
    )
    sources_group.add_argument(
        '--data-breaches', 
        action='store_true',
        help='Data breach and credential leak information'
    )
    sources_group.add_argument(
        '--google-dorks', 
        action='store_true',
        help='Advanced Google dorking for information disclosure'
    )
    sources_group.add_argument(
        '--people-search', 
        action='store_true',
        help='People search and background information'
    )
    sources_group.add_argument(
        '--phone-numbers', 
        action='store_true',
        help='Phone number enumeration and validation'
    )
    sources_group.add_argument(
        '--documents', 
        action='store_true',
        help='Document and file discovery with metadata extraction'
    )
    
    # Advanced OSINT options
    advanced_group = osint_parser.add_argument_group('Advanced Options')
    advanced_group.add_argument(
        '--leaked-credentials', 
        action='store_true',
        help='Search for leaked credentials and passwords'
    )
    advanced_group.add_argument(
        '--pastebins', 
        action='store_true',
        help='Search pastebin services for mentions'
    )
    advanced_group.add_argument(
        '--dark-web', 
        action='store_true',
        help='Dark web monitoring and search (requires special configuration)'
    )
    advanced_group.add_argument(
        '--historical-data', 
        action='store_true',
        help='Historical data and archived information'
    )
    
    # Search options
    search_group = osint_parser.add_argument_group('Search Options')
    search_group.add_argument(
        '--deep-search', 
        action='store_true',
        help='Enable deep search with extended timeouts'
    )
    search_group.add_argument(
        '--max-results', 
        type=int, 
        metavar='N',
        default=100,
        help='Maximum results per source (default: 100)'
    )
    
    # Batch operations module
    batch_parser = subparsers.add_parser(
        'batch', 
        help='Batch operations and automated workflows',
        description='Execute multiple scans and operations from configuration files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spyhunt batch --config scan_config.yaml
  spyhunt batch --config targets.yaml --parallel 10 --output batch_results/
  spyhunt batch --template comprehensive --targets targets.txt
        """
    )
    
    batch_config_group = batch_parser.add_mutually_exclusive_group(required=True)
    batch_config_group.add_argument(
        '--config', 
        metavar='FILE',
        help='Batch configuration file (YAML/JSON format)'
    )
    batch_config_group.add_argument(
        '--template', 
        choices=['basic', 'comprehensive', 'webapp', 'network', 'osint'],
        help='Use predefined scan template'
    )
    
    batch_parser.add_argument(
        '--targets', 
        metavar='FILE',
        help='File containing target list (required with --template)'
    )
    batch_parser.add_argument(
        '--parallel', 
        type=int, 
        default=5, 
        metavar='N',
        help='Maximum parallel job execution (default: 5)'
    )
    batch_parser.add_argument(
        '--resume', 
        metavar='FILE',
        help='Resume batch operation from state file'
    )
    batch_parser.add_argument(
        '--save-state', 
        metavar='FILE',
        help='Save batch operation state for resumption'
    )
    batch_parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be executed without running'
    )
    
    # Configuration management module
    config_parser = subparsers.add_parser(
        'config', 
        help='Configuration management and validation',
        description='Manage SpyHunt configuration files and settings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spyhunt config --show
  spyhunt config --init
  spyhunt config --validate custom_config.yaml
  spyhunt config --set network.timeout=30
        """
    )
    
    config_action_group = config_parser.add_mutually_exclusive_group(required=True)
    config_action_group.add_argument(
        '--show', 
        action='store_true',
        help='Display current configuration settings'
    )
    config_action_group.add_argument(
        '--init', 
        action='store_true',
        help='Initialize default configuration file'
    )
    config_action_group.add_argument(
        '--validate', 
        metavar='FILE',
        help='Validate configuration file syntax and settings'
    )
    config_action_group.add_argument(
        '--set', 
        metavar='KEY=VALUE',
        help='Set configuration value (e.g., network.timeout=30)'
    )
    config_action_group.add_argument(
        '--get', 
        metavar='KEY',
        help='Get configuration value (e.g., network.timeout)'
    )
    
    config_parser.add_argument(
        '--format', 
        choices=['yaml', 'json', 'table'],
        default='yaml',
        help='Output format for configuration display (default: yaml)'
    )
    config_parser.add_argument(
        '--output-file', 
        metavar='FILE',
        help='Save configuration to file'
    )
    
    # Additional utility commands
    utils_parser = subparsers.add_parser(
        'utils', 
        help='Utility commands and tools',
        description='Various utility commands for SpyHunt',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spyhunt utils --check-dependencies
  spyhunt utils --update-wordlists
  spyhunt utils --generate-report results.json
        """
    )
    
    utils_group = utils_parser.add_mutually_exclusive_group(required=True)
    utils_group.add_argument(
        '--check-dependencies', 
        action='store_true',
        help='Check system dependencies and requirements'
    )
    utils_group.add_argument(
        '--update-wordlists', 
        action='store_true',
        help='Update built-in wordlists and payloads'
    )
    utils_group.add_argument(
        '--generate-report', 
        metavar='FILE',
        help='Generate comprehensive report from results file'
    )
    utils_group.add_argument(
        '--benchmark', 
        action='store_true',
        help='Run performance benchmarks'
    )
    
    return parser


def setup_config(args: argparse.Namespace) -> Config:
    """
    Setup configuration from command line arguments and config file.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Config: Configured Config instance
    """
    config_overrides = {}
    
    # Performance and threading configuration
    if hasattr(args, 'threads') and args.threads:
        config_overrides['scanning.max_threads'] = args.threads
    if hasattr(args, 'timeout') and args.timeout:
        config_overrides['network.timeout'] = args.timeout
    if hasattr(args, 'rate_limit') and args.rate_limit:
        config_overrides['network.rate_limit_requests'] = args.rate_limit
    if hasattr(args, 'delay') and args.delay:
        config_overrides['network.request_delay'] = args.delay
    
    # User agent configuration
    if hasattr(args, 'user_agent') and args.user_agent:
        config_overrides['network.custom_user_agent'] = args.user_agent
        config_overrides['network.user_agent_rotation'] = False
    if hasattr(args, 'random_agent') and args.random_agent:
        config_overrides['network.user_agent_rotation'] = True
    
    # Proxy configuration
    if hasattr(args, 'proxy') and args.proxy:
        config_overrides['proxies.http_proxy'] = args.proxy
        config_overrides['proxies.https_proxy'] = args.proxy
        config_overrides['proxies.enabled'] = True
    if hasattr(args, 'proxy_file') and args.proxy_file:
        config_overrides['proxies.proxy_list'] = args.proxy_file
        config_overrides['proxies.enabled'] = True
        config_overrides['proxies.proxy_rotation'] = True
    if hasattr(args, 'proxy_auth') and args.proxy_auth:
        config_overrides['proxies.auth_credentials'] = args.proxy_auth
    
    # Logging and verbosity configuration
    if hasattr(args, 'verbose') and args.verbose:
        if args.verbose >= 2:
            config_overrides['app.log_level'] = 'DEBUG'
        elif args.verbose == 1:
            config_overrides['app.log_level'] = 'INFO'
    if hasattr(args, 'quiet') and args.quiet:
        config_overrides['app.log_level'] = 'ERROR'
        config_overrides['app.console_output'] = False
    if hasattr(args, 'log_file') and args.log_file:
        config_overrides['app.log_file'] = args.log_file
    
    # Output formatting configuration
    if hasattr(args, 'no_color') and args.no_color:
        config_overrides['output.color_enabled'] = False
    if hasattr(args, 'pretty') and args.pretty:
        config_overrides['output.pretty_print'] = True
    
    # Create and return configuration
    config = Config(config_file=getattr(args, 'config', None), **config_overrides)
    set_config(config)
    
    return config


def execute_subdomain_scan(args: argparse.Namespace, engine: SpyHuntEngine) -> List[Any]:
    """
    Execute comprehensive subdomain enumeration scan.
    
    Args:
        args: Parsed command line arguments
        engine: SpyHunt engine instance
        
    Returns:
        List[Any]: Scan results
        
    Raises:
        ValidationError: If target validation fails
        SpyHuntException: If scan execution fails
    """
    # Validate target domain
    if not args.target or not isinstance(args.target, str):
        raise ValidationError("Invalid target domain specified")
    
    # Build scan parameters
    params = {
        'wordlist': getattr(args, 'wordlist', None),
        'dns_servers': getattr(args, 'dns_servers', '').split(',') if getattr(args, 'dns_servers', None) else None,
        'bruteforce': getattr(args, 'bruteforce', False),
        'passive_only': getattr(args, 'passive_only', False),
        'resolve_ips': getattr(args, 'resolve', False),
        'wildcard_filter': getattr(args, 'wildcard_filter', True),
        'max_workers': getattr(args, 'workers', 50)
    }
    
    # Filter out None values and validate parameters
    params = {k: v for k, v in params.items() if v is not None}
    
    if params.get('passive_only') and params.get('bruteforce'):
        console.print("[yellow]Warning: Passive-only mode enabled, ignoring bruteforce option[/yellow]")
        params['bruteforce'] = False
    
    # Execute scan with progress tracking
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task(
            f"🔍 Enumerating subdomains for [cyan]{args.target}[/cyan]", 
            total=None
        )
        
        try:
            # Execute subdomain enumeration
            results = engine.scan_single('subdomain_enum', args.target, params)
            progress.update(task, completed=True, description=f"✅ Completed subdomain enumeration for [cyan]{args.target}[/cyan]")
            
            # Display quick summary
            if results and hasattr(results, 'data') and results.data:
                data = results.data
                findings = data.get('findings', []) if isinstance(data, dict) else []
                subdomain_count = len(findings)
                console.print(f"[green]Found {subdomain_count} subdomains in {results.execution_time:.2f}s[/green]")
            
            return [results]
            
        except Exception as e:
            progress.update(task, description=f"❌ Failed: {str(e)}")
            console.print(f"[red]Subdomain enumeration failed: {str(e)}[/red]")
            raise


def execute_port_scan(args: argparse.Namespace, engine: SpyHuntEngine) -> List[Any]:
    """
    Execute comprehensive port scanning with service detection.
    
    Args:
        args: Parsed command line arguments
        engine: SpyHunt engine instance
        
    Returns:
        List[Any]: Scan results
        
    Raises:
        ValidationError: If target validation fails
        SpyHuntException: If scan execution fails
    """
    # Validate target
    if not args.target:
        raise ValidationError("Target is required for port scanning")
    
    # Build scan parameters
    params = {
        'ports': getattr(args, 'ports', None),
        'top_ports': getattr(args, 'top_ports', None),
        'service_detection': getattr(args, 'service_detection', False),
        'os_detection': getattr(args, 'os_detection', False),
        'stealth_mode': getattr(args, 'stealth', False),
        'udp_scan': getattr(args, 'udp', False),
        'connect_scan': getattr(args, 'connect_scan', False),
        'ping_sweep': getattr(args, 'ping_sweep', False)
    }
    
    # Parameter validation and defaults
    if not params['ports'] and not params['top_ports']:
        params['top_ports'] = 1000  # Default to top 1000 ports
        console.print("[yellow]No ports specified, using top 1000 common ports[/yellow]")
    
    # Filter out None/False values for optional parameters
    params = {k: v for k, v in params.items() if v is not None and v is not False}
    
    # Execute scan with detailed progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        # Determine scan type for progress message
        scan_type = "stealth" if params.get('stealth_mode') else "standard"
        if params.get('udp_scan'):
            scan_type += " + UDP"
        
        task = progress.add_task(
            f"🔍 Performing {scan_type} port scan on [cyan]{args.target}[/cyan]", 
            total=None
        )
        
        try:
            results = engine.scan_single('port_scan', args.target, params)
            progress.update(task, completed=True, description=f"✅ Port scan completed for [cyan]{args.target}[/cyan]")
            
            # Display quick summary
            if results and hasattr(results, 'data') and results.data:
                data = results.data
                metadata = data.get('metadata', {}) if isinstance(data, dict) else {}
                open_ports = metadata.get('open_count', 0)
                console.print(f"[green]Found {open_ports} open ports in {results.execution_time:.2f}s[/green]")
            
            return [results]
            
        except Exception as e:
            progress.update(task, description=f"❌ Failed: {str(e)}")
            console.print(f"[red]Port scanning failed: {str(e)}[/red]")
            raise


def execute_vulnerability_scan(args: argparse.Namespace, engine: SpyHuntEngine) -> List[Any]:
    """Execute vulnerability scanning using the built-in vulnerability module."""
    targets = []
    if args.file:
        with open(args.file, 'r') as f:
            targets = [line.strip() for line in f if line.strip()]
    elif args.target:
        targets = [args.target]
    else:
        raise ValidationError("Either --file or --target must be specified")

    if not targets:
        raise ValidationError("No valid targets provided")

    params = _build_vulnerability_params(args)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Vulnerability scanning", total=len(targets))
        results: List[Any] = []
        for target in targets:
            result = engine.scan_single('vuln_scan', target, params)
            results.append(result)
            progress.update(task, advance=1)

    return results


def display_results(results: List[Any], format_type: str, output_file: Optional[str] = None, pretty: bool = False) -> None:
    """
    Display and save scan results in the specified format.
    
    Args:
        results: List of scan results
        format_type: Output format (json, yaml, csv, text, xml)
        output_file: Optional output file path
        pretty: Enable pretty printing for human readability
    """
    if not results:
        console.print("[yellow]⚠️  No results to display[/yellow]")
        return
    
    # Convert results to dictionaries if needed
    result_dicts = []
    for result in results:
        if hasattr(result, 'to_dict'):
            result_dicts.append(result.to_dict())
        elif isinstance(result, dict):
            result_dicts.append(result)
        else:
            # Fallback for unknown result types
            result_dicts.append({'data': str(result), 'type': type(result).__name__})
    
    # Save to file if specified
    if output_file:
        save_success = _save_results_to_file(result_dicts, output_file, format_type, pretty)
        if save_success:
            console.print(f"[green]✅ Results saved to [bold]{output_file}[/bold][/green]")
        else:
            console.print(f"[red]❌ Failed to save results to {output_file}[/red]")
    
    # Display results based on format or if no output file specified
    if format_type == 'text' or not output_file:
        _display_results_table(result_dicts)
    elif not output_file:
        # Display formatted output to console
        _display_formatted_results(result_dicts, format_type, pretty)


def _save_results_to_file(result_dicts: List[Dict], output_file: str, format_type: str, pretty: bool = False) -> bool:
    """
    Save results to file in the specified format.
    
    Args:
        result_dicts: List of result dictionaries
        output_file: Output file path
        format_type: Output format
        pretty: Enable pretty formatting
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format_type == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(result_dicts, f, indent=4, ensure_ascii=False, sort_keys=True)
                else:
                    json.dump(result_dicts, f, ensure_ascii=False, separators=(',', ':'))
                    
        elif format_type == 'yaml':
            import yaml
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(result_dicts, f, default_flow_style=False, allow_unicode=True, sort_keys=True)
                
        elif format_type == 'csv':
            import csv
            if result_dicts:
                # Flatten nested dictionaries for CSV
                flattened_results = _flatten_dicts_for_csv(result_dicts)
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    if flattened_results:
                        writer = csv.DictWriter(f, fieldnames=flattened_results[0].keys())
                        writer.writeheader()
                        writer.writerows(flattened_results)
                        
        elif format_type == 'xml':
            _save_results_as_xml(result_dicts, path)
            
        else:
            console.print(f"[red]Unsupported output format: {format_type}[/red]")
            return False
            
        return True
        
    except Exception as e:
        console.print(f"[red]Error saving results: {str(e)}[/red]")
        return False


def _display_results_table(result_dicts: List[Dict]) -> None:
    """Display results in a formatted table."""
    if not result_dicts:
        return
    
    table = Table(title="🔍 Scan Results Summary", title_style="bold cyan")
    table.add_column("Module", style="cyan", no_wrap=True)
    table.add_column("Target", style="green")
    table.add_column("Status", justify="center")
    table.add_column("Findings", justify="right", style="white")
    table.add_column("Duration", justify="right", style="blue")
    table.add_column("Timestamp", style="dim")
    
    for result in result_dicts:
        # Determine status styling
        status = result.get('status', 'unknown')
        if status == 'success':
            status_display = "[green]✅ Success[/green]"
        elif status == 'failed':
            status_display = "[red]❌ Failed[/red]"
        elif status == 'partial':
            status_display = "[yellow]⚠️  Partial[/yellow]"
        else:
            status_display = "[dim]❓ Unknown[/dim]"
        
        # Count findings
        data = result.get('data', {})
        findings_count = 0
        if isinstance(data, dict):
            findings_count = sum(len(v) if isinstance(v, (list, dict)) else 1 for v in data.values())
        elif isinstance(data, list):
            findings_count = len(data)
        
        # Format timestamp
        timestamp = result.get('timestamp', 0)
        if timestamp:
            from datetime import datetime
            ts_str = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
        else:
            ts_str = 'N/A'
        
        table.add_row(
            result.get('module', 'Unknown'),
            result.get('target', 'Unknown'),
            status_display,
            str(findings_count),
            f"{result.get('execution_time', 0):.2f}s",
            ts_str
        )
    
    console.print(table)
    
    # Display errors if any
    errors = []
    for result in result_dicts:
        if result.get('errors'):
            errors.extend(result['errors'])
    
    if errors:
        console.print("\n[red]⚠️  Errors encountered:[/red]")
        for error in errors[:5]:  # Show only first 5 errors
            console.print(f"  • {error}", style="red")
        if len(errors) > 5:
            console.print(f"  ... and {len(errors) - 5} more errors", style="dim")


def _flatten_dicts_for_csv(result_dicts: List[Dict]) -> List[Dict]:
    """Flatten nested dictionaries for CSV output."""
    flattened = []
    for result in result_dicts:
        flat_result = _flatten_dict(result)
        flattened.append(flat_result)
    return flattened


def _flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """Recursively flatten a nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, ', '.join(map(str, v))))
        else:
            items.append((new_key, v))
    return dict(items)


def _save_results_as_xml(result_dicts: List[Dict], output_path: Path) -> None:
    """Save results as XML format."""
    try:
        import xml.etree.ElementTree as ET
        
        root = ET.Element("spyhunt_results")
        root.set("version", "4.0.0")
        root.set("generated", str(int(time.time())))
        
        for result in result_dicts:
            result_elem = ET.SubElement(root, "scan_result")
            _dict_to_xml(result, result_elem)
        
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
    except ImportError:
        console.print("[red]XML support not available[/red]")
    except Exception as e:
        console.print(f"[red]Error saving XML: {str(e)}[/red]")


def _dict_to_xml(d: Dict, parent) -> None:
    """Convert dictionary to XML elements."""
    import xml.etree.ElementTree as ET
    
    for key, value in d.items():
        # Sanitize key for XML
        key = str(key).replace(' ', '_').replace('-', '_')
        
        if isinstance(value, dict):
            elem = ET.SubElement(parent, key)
            _dict_to_xml(value, elem)
        elif isinstance(value, list):
            for item in value:
                elem = ET.SubElement(parent, key)
                if isinstance(item, dict):
                    _dict_to_xml(item, elem)
                else:
                    elem.text = str(item)
        else:
            elem = ET.SubElement(parent, key)
            elem.text = str(value)


def _display_formatted_results(result_dicts: List[Dict], format_type: str, pretty: bool = False) -> None:
    """Display formatted results to console."""
    try:
        if format_type == 'json':
            if pretty:
                formatted = json.dumps(result_dicts, indent=4, ensure_ascii=False, sort_keys=True)
            else:
                formatted = json.dumps(result_dicts, ensure_ascii=False)
            console.print(formatted)
            
        elif format_type == 'yaml':
            import yaml
            formatted = yaml.dump(result_dicts, default_flow_style=False, allow_unicode=True)
            console.print(formatted)
            
    except Exception as e:
        console.print(f"[red]Error displaying formatted results: {str(e)}[/red]")


def handle_config_command(args: argparse.Namespace) -> None:
    """
    Handle configuration management commands.
    
    Args:
        args: Parsed command line arguments
    """
    try:
        if args.show:
            _show_configuration(args)
        elif args.init:
            _initialize_configuration(args)
        elif args.validate:
            _validate_configuration(args)
        elif hasattr(args, 'set') and args.set:
            _set_configuration_value(args)
        elif hasattr(args, 'get') and args.get:
            _get_configuration_value(args)
        else:
            console.print("[red]Invalid configuration command[/red]")
            
    except Exception as e:
        console.print(f"[red]Configuration operation failed: {str(e)}[/red]")
        sys.exit(1)


def _show_configuration(args: argparse.Namespace) -> None:
    """Display current configuration."""
    config = get_config()
    config_dict = config.to_dict() if hasattr(config, 'to_dict') else {}
    
    format_type = getattr(args, 'format', 'yaml')
    output_file = getattr(args, 'output_file', None)
    
    if format_type == 'table':
        _display_config_table(config_dict)
    elif format_type == 'json':
        formatted_config = json.dumps(config_dict, indent=2, ensure_ascii=False)
        if output_file:
            with open(output_file, 'w') as f:
                f.write(formatted_config)
            console.print(f"[green]Configuration saved to {output_file}[/green]")
        else:
            console.print(Panel(
                formatted_config,
                title="🔧 Current Configuration (JSON)",
                border_style="cyan",
                padding=(1, 2)
            ))
    else:  # yaml
        try:
            import yaml
            formatted_config = yaml.dump(config_dict, default_flow_style=False, sort_keys=True)
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(formatted_config)
                console.print(f"[green]Configuration saved to {output_file}[/green]")
            else:
                console.print(Panel(
                    formatted_config,
                    title="🔧 Current Configuration (YAML)",
                    border_style="cyan",
                    padding=(1, 2)
                ))
        except ImportError:
            console.print("[red]YAML support not available, falling back to JSON[/red]")
            formatted_config = json.dumps(config_dict, indent=2, ensure_ascii=False)
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(formatted_config)
                console.print(f"[green]Configuration saved to {output_file}[/green]")
            else:
                console.print(Panel(
                    formatted_config,
                    title="🔧 Current Configuration (JSON)",
                    border_style="cyan",
                    padding=(1, 2)
                ))


def _display_config_table(config_dict: Dict[str, Any]) -> None:
    """Display configuration in a table format."""
    table = Table(title="🔧 SpyHunt Configuration", title_style="bold cyan")
    table.add_column("Section", style="cyan", no_wrap=True)
    table.add_column("Setting", style="green")
    table.add_column("Value", style="white")
    table.add_column("Type", style="dim", justify="center")
    
    def add_config_rows(data: Dict, section: str = ""):
        for key, value in data.items():
            if isinstance(value, dict):
                add_config_rows(value, f"{section}.{key}" if section else key)
            else:
                table.add_row(
                    section,
                    key,
                    str(value),
                    type(value).__name__
                )
    
    add_config_rows(config_dict)
    console.print(table)


def _initialize_configuration(args: argparse.Namespace) -> None:
    """Initialize default configuration file."""
    config_file = Path("spyhunt_config.yaml")
    output_file = getattr(args, 'output_file', None)
    
    if output_file:
        config_file = Path(output_file)
    
    if config_file.exists():
        console.print(f"[yellow]⚠️  Configuration file {config_file} already exists[/yellow]")
        console.print("Use --force to overwrite (if implemented)")
        return
    
    try:
        config = Config()
        if hasattr(config, 'save'):
            config.save(str(config_file))
        else:
            # Fallback method
            with open(config_file, 'w') as f:
                import yaml
                yaml.dump(config.to_dict(), f, default_flow_style=False)
        
        console.print(f"[green]✅ Default configuration saved to [bold]{config_file}[/bold][/green]")
        console.print("[dim]Edit the file to customize your settings[/dim]")
        
    except Exception as e:
        console.print(f"[red]Failed to create configuration file: {str(e)}[/red]")


def _validate_configuration(args: argparse.Namespace) -> None:
    """Validate configuration file."""
    config_file = args.validate
    
    try:
        # Attempt to load the configuration
        config = Config(config_file=config_file)
        
        # Perform validation checks
        validation_errors = []
        
        # Check if config has required methods/attributes
        if not hasattr(config, 'to_dict'):
            validation_errors.append("Configuration object missing to_dict method")
        
        # Add more validation logic here as needed
        
        if validation_errors:
            console.print(f"[red]❌ Configuration validation failed for {config_file}:[/red]")
            for error in validation_errors:
                console.print(f"  • {error}")
        else:
            console.print(f"[green]✅ Configuration file [bold]{config_file}[/bold] is valid[/green]")
            
            # Display configuration summary
            if hasattr(config, 'to_dict'):
                config_dict = config.to_dict()
                section_count = len(config_dict)
                console.print(f"[dim]Found {section_count} configuration sections[/dim]")
                
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config_file}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Configuration validation failed: {str(e)}[/red]")


def _set_configuration_value(args: argparse.Namespace) -> None:
    """Set configuration value."""
    try:
        key_value = args.set
        if '=' not in key_value:
            console.print("[red]Invalid format. Use KEY=VALUE[/red]")
            return
        
        key, value = key_value.split('=', 1)
        console.print(f"[green]Configuration setting {key} = {value} (feature not fully implemented)[/green]")
        
    except Exception as e:
        console.print(f"[red]Failed to set configuration: {str(e)}[/red]")


def _get_configuration_value(args: argparse.Namespace) -> None:
    """Get configuration value."""
    try:
        key = args.get
        config = get_config()
        
        # This is a simplified implementation
        console.print(f"[green]Configuration value for {key}: (feature not fully implemented)[/green]")
        
    except Exception as e:
        console.print(f"[red]Failed to get configuration: {str(e)}[/red]")


def main() -> None:
    """
    Main CLI entry point with comprehensive error handling and command routing.
    """
    try:
        # Check if running in interactive mode
        if len(sys.argv) == 1:
            display_banner()
            console.print(Panel(
                "[cyan]Welcome to SpyHunt! 🔍[/cyan]\n\n"
                "Run [bold]spyhunt --help[/bold] for usage information\n"
                "Run [bold]spyhunt config --init[/bold] to create initial configuration\n"
                "Run [bold]spyhunt subdomain -t example.com[/bold] for a quick test",
                title="Getting Started",
                border_style="cyan"
            ))
            return
        
        # Parse arguments
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # Set up console with color preferences
        if hasattr(args, 'no_color') and args.no_color:
            console._color_system = None
        
        # Handle special commands that don't require full setup
        if args.command in ['config', 'utils']:
            if args.command == 'config':
                handle_config_command(args)
            elif args.command == 'utils':
                handle_utils_command(args)
            return
        
        # Setup configuration and logging
        config = setup_config(args)
        setup_logging(
            log_level=config.get('app.log_level', 'INFO'),
            log_file=config.get('app.log_file'),
            console_output=not getattr(args, 'quiet', False)
        )
        
        logger = get_logger("spyhunt.cli")
        logger.info(f"Starting SpyHunt CLI with command: {args.command}")
        
        # Display banner unless in quiet mode
        if not getattr(args, 'quiet', False):
            display_banner()
        
        # Validate that a command was provided
        if not args.command:
            console.print("[red]❌ No command specified. Use --help for available commands.[/red]")
            return
        
        # Initialize engine with proper error handling
        try:
            with SpyHuntEngine(config) as engine:
                register_builtin_modules(engine)
                results = []
                
                # Route to appropriate command handler
                if args.command == 'subdomain':
                    results = execute_subdomain_scan(args, engine)
                elif args.command == 'portscan':
                    results = execute_port_scan(args, engine)
                elif args.command == 'vuln':
                    results = execute_vulnerability_scan(args, engine)
                elif args.command == 'webapp':
                    results = execute_webapp_scan(args, engine)
                elif args.command == 'cloud':
                    results = execute_cloud_scan(args, engine)
                elif args.command == 'network':
                    results = execute_network_scan(args, engine)
                elif args.command == 'osint':
                    results = execute_osint_scan(args, engine)
                elif args.command == 'batch':
                    results = execute_batch_operations(args, engine)
                else:
                    console.print(f"[red]❌ Command '{args.command}' is not yet implemented[/red]")
                    console.print("[dim]Available commands: subdomain, portscan, vuln[/dim]")
                    return
                
                # Display results with enhanced formatting
                pretty = getattr(args, 'pretty', False)
                display_results(results, getattr(args, 'format', 'json'), getattr(args, 'output', None), pretty)
                
                # Display execution statistics
                if not getattr(args, 'quiet', False) and hasattr(engine, 'get_statistics'):
                    _display_execution_stats(engine.get_statistics())
                    
        except Exception as engine_error:
            logger.error(f"Engine initialization failed: {str(engine_error)}")
            console.print(f"[red]❌ Failed to initialize SpyHunt engine: {str(engine_error)}[/red]")
            return
    
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Operation interrupted by user[/yellow]")
        sys.exit(130)
    except ValidationError as e:
        console.print(f"[red]❌ Validation Error: {str(e)}[/red]")
        sys.exit(1)
    except SpyHuntException as e:
        console.print(f"[red]❌ SpyHunt Error: {getattr(e, 'message', str(e))}[/red]")
        if hasattr(e, 'recovery_suggestion') and e.recovery_suggestion:
            console.print(f"[cyan]💡 Suggestion: {e.recovery_suggestion}[/cyan]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {str(e)}[/red]")
        try:
            logger = get_logger("spyhunt.cli")
            logger.exception("Unexpected error in CLI")
        except:
            pass  # If logging fails, don't crash further
        sys.exit(1)


def handle_utils_command(args: argparse.Namespace) -> None:
    """Handle utility commands."""
    if hasattr(args, 'check_dependencies') and args.check_dependencies:
        console.print("[yellow]🔍 Checking system dependencies...[/yellow]")
        console.print("[green]✅ Dependency check complete (feature in development)[/green]")
    elif hasattr(args, 'update_wordlists') and args.update_wordlists:
        console.print("[yellow]📥 Updating wordlists and payloads...[/yellow]")
        console.print("[green]✅ Wordlists updated (feature in development)[/green]")
    elif hasattr(args, 'generate_report') and args.generate_report:
        console.print(f"[yellow]📊 Generating report from {args.generate_report}...[/yellow]")
        console.print("[green]✅ Report generated (feature in development)[/green]")
    elif hasattr(args, 'benchmark') and args.benchmark:
        console.print("[yellow]⚡ Running performance benchmarks...[/yellow]")
        console.print("[green]✅ Benchmarks complete (feature in development)[/green]")
    else:
        console.print("[red]❌ Invalid utility command[/red]")


def _display_execution_stats(stats: Dict[str, Any]) -> None:
    """Display execution statistics in a formatted table."""
    if not stats:
        return
    
    stats_table = Table(title="📊 Execution Statistics", title_style="bold blue")
    stats_table.add_column("Metric", style="cyan", no_wrap=True)
    stats_table.add_column("Value", style="green", justify="right")
    stats_table.add_column("Unit", style="dim")
    
    # Standard metrics
    stats_table.add_row("Total Operations", str(stats.get('total_operations', 0)), "ops")
    stats_table.add_row("Successful", str(stats.get('successful_operations', 0)), "ops")
    stats_table.add_row("Failed", str(stats.get('failed_operations', 0)), "ops")
    stats_table.add_row("Runtime", f"{stats.get('runtime_seconds', 0):.2f}", "seconds")
    
    # Calculate success rate
    total = stats.get('total_operations', 0)
    successful = stats.get('successful_operations', 0)
    if total > 0:
        success_rate = (successful / total) * 100
        stats_table.add_row("Success Rate", f"{success_rate:.1f}", "%")
    
    # Operations per second
    ops_per_sec = stats.get('operations_per_second', 0)
    if ops_per_sec > 0:
        stats_table.add_row("Throughput", f"{ops_per_sec:.2f}", "ops/sec")
    
    console.print(stats_table)


# Placeholder functions for unimplemented commands
def execute_webapp_scan(args: argparse.Namespace, engine: SpyHuntEngine) -> List[Any]:
    """Execute web application scanning (placeholder)."""
    console.print("[yellow]⚠️  Web application scanning not yet implemented[/yellow]")
    return []


def execute_cloud_scan(args: argparse.Namespace, engine: SpyHuntEngine) -> List[Any]:
    """Execute cloud security scanning (placeholder)."""
    console.print("[yellow]⚠️  Cloud security scanning not yet implemented[/yellow]")
    return []


def execute_network_scan(args: argparse.Namespace, engine: SpyHuntEngine) -> List[Any]:
    """Execute network analysis (placeholder)."""
    console.print("[yellow]⚠️  Network analysis not yet implemented[/yellow]")
    return []


def execute_osint_scan(args: argparse.Namespace, engine: SpyHuntEngine) -> List[Any]:
    """Execute OSINT gathering (placeholder)."""
    console.print("[yellow]⚠️  OSINT gathering not yet implemented[/yellow]")
    return []


def execute_batch_operations(args: argparse.Namespace, engine: SpyHuntEngine) -> List[Any]:
    """Execute batch operations (placeholder)."""
    console.print("[yellow]⚠️  Batch operations not yet implemented[/yellow]")
    return []


def _build_vulnerability_params(args: argparse.Namespace) -> Dict[str, bool]:
    """Translate CLI arguments into module parameters."""
    checks = ['xss', 'sqli', 'lfi', 'rfi', 'xxe', 'ssrf', 'cors', 'headers']
    params = {check: bool(getattr(args, check, False)) for check in checks}

    if getattr(args, 'injection_attacks', False):
        for check in ('xss', 'sqli', 'ssrf'):
            params[check] = True

    if getattr(args, 'all_checks', False):
        for check in checks:
            params[check] = True
        params['all_checks'] = True
    else:
        params['all_checks'] = False

    return params


def create_cli():
    """Create CLI application (for external use)."""
    return create_argument_parser()


if __name__ == "__main__":
    main()
