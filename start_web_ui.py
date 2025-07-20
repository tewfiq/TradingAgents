#!/usr/bin/env python3
"""
TradingAgents Web UI Startup Script
Advanced UXD GUI launcher with configuration and health checks
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path
import pkg_resources
import importlib.util

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'chainlit>=1.0.0',
        'plotly>=5.0.0',
        'yfinance>=0.2.0',
        'pandas>=1.5.0',
        'numpy>=1.20.0'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            pkg_name = package.split('>=')[0]
            importlib.import_module(pkg_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\nInstall missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required dependencies are installed!")
    return True

def setup_environment():
    """Set up environment variables for optimal performance."""
    
    # Chainlit configuration
    os.environ.setdefault("CHAINLIT_HOST", "0.0.0.0")
    os.environ.setdefault("CHAINLIT_PORT", "8000")
    os.environ.setdefault("CHAINLIT_HEADLESS", "false")
    
    # Performance optimizations
    os.environ.setdefault("CHAINLIT_ENABLE_TELEMETRY", "false")
    os.environ.setdefault("CHAINLIT_WATCH", "false")
    
    # Set working directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🔧 Environment configured successfully!")

def display_startup_banner():
    """Display the startup banner with terminal styling."""
    
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           🚀 TradingAgents Advanced UXD GUI 🚀                  ║
║                                                                  ║
║              Multi-Agents LLM Financial Trading Framework       ║
║                        Web Interface Launcher                   ║
║                                                                  ║
║  ┌────────────────────────────────────────────────────────────┐  ║
║  │  Terminal-Inspired Design  │  Real-time Agent Orchestration │  ║
║  │  Interactive Dashboards    │  Advanced Data Visualization   │  ║
║  │  Mobile-Responsive UI      │  Professional Trading Tools    │  ║
║  └────────────────────────────────────────────────────────────┘  ║
║                                                                  ║
║                Built by Tauric Research                         ║
║              © Multi-Agent Trading Platform                     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """
    
    print(banner)

def check_ports():
    """Check if the required port is available."""
    import socket
    
    port = int(os.environ.get("CHAINLIT_PORT", "8000"))
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('localhost', port))
        if result == 0:
            print(f"⚠️  Port {port} is already in use!")
            print(f"   The web interface may not start properly.")
            print(f"   You can change the port by setting CHAINLIT_PORT environment variable.")
            return False
    
    print(f"✅ Port {port} is available!")
    return True

def print_startup_info():
    """Print startup information and URLs."""
    
    host = os.environ.get("CHAINLIT_HOST", "0.0.0.0")
    port = os.environ.get("CHAINLIT_PORT", "8000")
    
    print("\n" + "="*70)
    print("🌐 TradingAgents Web UI Starting...")
    print("="*70)
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🌍 Local URL: http://localhost:{port}")
    if host == "0.0.0.0":
        print(f"🌐 Network URL: http://<your-ip>:{port}")
    print("="*70)
    print("\n🎯 Features Available:")
    print("   • 🔧 Interactive Configuration Builder")
    print("   • 📊 Real-time Agent Orchestration Dashboard") 
    print("   • 📈 Advanced Trading Charts & Analytics")
    print("   • 📱 Mobile-Responsive Terminal-Inspired Design")
    print("   • ⚡ Live Status Updates & Progress Tracking")
    print("   • 📄 Rich Report Generation & Export")
    print("\n💡 Quick Start:")
    print("   1. Click 'Configure Analysis' to set up parameters")
    print("   2. Select your desired analysts and settings")
    print("   3. Click 'Start Analysis' to begin multi-agent workflow")
    print("   4. Monitor real-time progress in the dashboard")
    print("\n" + "="*70)

def run_health_check():
    """Run a quick health check of the system."""
    
    print("\n🔍 Running system health check...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required!")
        return False
    print(f"✅ Python {sys.version.split()[0]}")
    
    # Check working directory
    if not Path("web_ui.py").exists():
        print("❌ web_ui.py not found in current directory!")
        return False
    print("✅ Main application file found")
    
    # Check configuration files
    if Path(".chainlit/config.toml").exists():
        print("✅ Chainlit configuration found")
    else:
        print("⚠️  Chainlit configuration not found (using defaults)")
    
    if Path("public/terminal-theme.css").exists():
        print("✅ Terminal theme CSS found")
    else:
        print("⚠️  Terminal theme CSS not found (using default styling)")
    
    # Check components
    if Path("components/trading_dashboard.py").exists():
        print("✅ Trading dashboard components found")
    else:
        print("⚠️  Trading dashboard components not found")
    
    print("✅ Health check completed!")
    return True

def main():
    """Main startup function."""
    
    # Display banner
    display_startup_banner()
    
    # Run health check
    if not run_health_check():
        print("\n❌ Health check failed! Please fix the issues above.")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Check ports
    check_ports()
    
    # Print startup information
    print_startup_info()
    
    # Start the web UI
    try:
        print("\n🚀 Starting TradingAgents Web UI...")
        print("   Press Ctrl+C to stop the server")
        print("\n" + "-"*70)
        
        # Use chainlit run command
        cmd = ["chainlit", "run", "web_ui.py", "--host", "0.0.0.0", "--port", "8000"]
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n\n🛑 TradingAgents Web UI stopped by user")
        print("👋 Thank you for using TradingAgents!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to start web UI: {e}")
        print("\nTroubleshooting tips:")
        print("   • Check if all dependencies are installed: pip install -r requirements.txt")
        print("   • Verify port 8000 is not in use by another application")
        print("   • Ensure you're in the correct directory with web_ui.py")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()