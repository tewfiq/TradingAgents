#!/usr/bin/env python3
"""
Script de lancement pour TradingAgents Web GUI
Lance le service backend et l'interface web automatiquement
"""

import subprocess
import time
import threading
import signal
import sys
import os
import requests
import webbrowser
from pathlib import Path

class TradingGUILauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True
        
    def check_port_available(self, port):
        """Vérifier si un port est disponible."""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result != 0
        except:
            return True
    
    def wait_for_service(self, url, timeout=30):
        """Attendre qu'un service soit disponible."""
        print(f"⏳ Waiting for service at {url}...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    print(f"✅ Service available at {url}")
                    return True
            except:
                pass
            time.sleep(1)
        
        print(f"❌ Service not available at {url} after {timeout}s")
        return False
    
    def start_backend(self):
        """Démarrer le service backend."""
        print("🚀 Starting TradingAgents Backend Service...")
        
        if not self.check_port_available(8001):
            print("⚠️  Port 8001 is already in use. Checking if it's our backend...")
            try:
                response = requests.get("http://localhost:8001/api/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "TradingAgents" in data.get("service", ""):
                        print("✅ TradingAgents backend already running!")
                        return None
            except:
                pass
            
            print("❌ Port 8001 is occupied by another service!")
            print("   Please stop the other service or change the port.")
            return None
        
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, "trading_service.py"
            ], cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print("📡 Backend service starting...")
            return self.backend_process
            
        except FileNotFoundError:
            print("❌ trading_service.py not found!")
            print("   Make sure you're in the correct directory.")
            return None
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            return None
    
    def start_frontend(self):
        """Démarrer l'interface web."""
        print("🌐 Starting Web GUI Frontend...")
        
        if not self.check_port_available(8000):
            print("⚠️  Port 8000 is already in use!")
            print("   The web interface might already be running.")
            print("   Check http://localhost:8000")
            return None
        
        try:
            # Essayer avec chainlit
            self.frontend_process = subprocess.Popen([
                "chainlit", "run", "trading_web_gui.py", 
                "--host", "0.0.0.0", "--port", "8000"
            ], cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print("🎨 Frontend starting...")
            return self.frontend_process
            
        except FileNotFoundError:
            print("❌ Chainlit not found! Installing...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "chainlit"], check=True)
                print("✅ Chainlit installed successfully!")
                return self.start_frontend()
            except Exception as e:
                print(f"❌ Failed to install chainlit: {e}")
                return None
        except Exception as e:
            print(f"❌ Error starting frontend: {e}")
            return None
    
    def check_dependencies(self):
        """Vérifier les dépendances requises."""
        print("🔍 Checking dependencies...")
        
        required_packages = [
            ("fastapi", "Backend API framework"),
            ("uvicorn", "ASGI server for backend"),
            ("aiohttp", "HTTP client for frontend"),
            ("websockets", "WebSocket support"),
            ("chainlit", "Web interface framework")
        ]
        
        missing = []
        for package, description in required_packages:
            try:
                __import__(package)
                print(f"  ✅ {package} - {description}")
            except ImportError:
                print(f"  ❌ {package} - {description} (MISSING)")
                missing.append(package)
        
        if missing:
            print(f"\n📦 Installing missing packages: {', '.join(missing)}")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install"
                ] + missing, check=True)
                print("✅ All dependencies installed successfully!")
                return True
            except Exception as e:
                print(f"❌ Failed to install dependencies: {e}")
                print("   Please install manually:")
                print(f"   pip install {' '.join(missing)}")
                return False
        
        print("✅ All dependencies are available!")
        return True
    
    def signal_handler(self, sig, frame):
        """Gestionnaire de signal pour arrêt propre."""
        print("\n🛑 Shutting down TradingAgents Web GUI...")
        self.running = False
        
        if self.backend_process:
            print("🔄 Stopping backend service...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            print("🔄 Stopping frontend interface...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        print("👋 TradingAgents Web GUI stopped successfully!")
        sys.exit(0)
    
    def open_browser(self, url, delay=3):
        """Ouvrir le navigateur après un délai."""
        def delayed_open():
            time.sleep(delay)
            if self.running:
                print(f"🌐 Opening browser at {url}")
                try:
                    webbrowser.open(url)
                except Exception as e:
                    print(f"⚠️  Could not open browser: {e}")
                    print(f"   Please open {url} manually")
        
        threading.Thread(target=delayed_open, daemon=True).start()
    
    def monitor_processes(self):
        """Surveiller les processus en arrière-plan."""
        def monitor():
            while self.running:
                time.sleep(5)
                
                # Vérifier le backend
                if self.backend_process and self.backend_process.poll() is not None:
                    print("⚠️  Backend process died unexpectedly!")
                    if self.running:
                        print("🔄 Attempting to restart backend...")
                        self.backend_process = self.start_backend()
                
                # Vérifier le frontend
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("⚠️  Frontend process died unexpectedly!")
                    if self.running:
                        print("🔄 Attempting to restart frontend...")
                        self.frontend_process = self.start_frontend()
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def run(self):
        """Lancer l'ensemble du système."""
        
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                 TradingAgents Web GUI Launcher                  ║
║                                                                  ║
║  🚀 Automated startup for complete trading interface            ║
║                                                                  ║
║  Components:                                                     ║
║  • Backend Service (FastAPI) → Port 8001                        ║
║  • Web Interface (Chainlit) → Port 8000                         ║
║  • Real-time WebSocket → Auto-configured                        ║
║                                                                  ║
║  Press Ctrl+C to stop all services                              ║
╚══════════════════════════════════════════════════════════════════╝
        """)
        
        # Configurer le gestionnaire de signal
        signal.signal(signal.SIGINT, self.signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Vérifier les dépendances
        if not self.check_dependencies():
            print("❌ Dependency check failed. Please resolve the issues above.")
            sys.exit(1)
        
        # Vérifier les fichiers requis
        required_files = ["trading_service.py", "trading_web_gui.py"]
        for file in required_files:
            if not Path(file).exists():
                print(f"❌ Required file not found: {file}")
                print("   Make sure you're in the correct directory with all required files.")
                sys.exit(1)
        
        print("✅ All required files found!")
        
        # Démarrer le backend
        backend = self.start_backend()
        if backend is None and not self.wait_for_service("http://localhost:8001/api/health", 5):
            print("❌ Failed to start or connect to backend service!")
            sys.exit(1)
        
        # Attendre que le backend soit prêt
        if not self.wait_for_service("http://localhost:8001/api/health", 30):
            print("❌ Backend service failed to start properly!")
            self.signal_handler(None, None)
            sys.exit(1)
        
        print("✅ Backend service is ready!")
        
        # Démarrer le frontend
        frontend = self.start_frontend()
        if frontend is None:
            print("❌ Failed to start frontend interface!")
            self.signal_handler(None, None)
            sys.exit(1)
        
        # Attendre que le frontend soit prêt
        if not self.wait_for_service("http://localhost:8000", 30):
            print("❌ Frontend interface failed to start properly!")
            self.signal_handler(None, None)
            sys.exit(1)
        
        print("✅ Frontend interface is ready!")
        
        # Démarrer la surveillance des processus
        self.monitor_processes()
        
        # Ouvrir le navigateur
        self.open_browser("http://localhost:8000", delay=2)
        
        # Afficher les informations de connexion
        print(f"""
🎉 TradingAgents Web GUI is now running!

📍 Access Points:
  • Web Interface: http://localhost:8000
  • Backend API: http://localhost:8001
  • API Documentation: http://localhost:8001/docs
  • Health Check: http://localhost:8001/api/health

🎯 How to Use:
  1. The web interface should open in your browser
  2. Click "🔬 Nouvelle Analyse" to start a trading analysis
  3. Configure your analysis parameters (ticker, date, analysts)
  4. Watch the real-time multi-agent analysis unfold
  5. Review the generated reports and insights

💡 Tips:
  • Keep this terminal open to see service logs
  • Use Ctrl+C to stop all services cleanly
  • If issues occur, check the logs below

🔄 Services are running and being monitored...
        """)
        
        # Attendre les processus
        try:
            while self.running:
                time.sleep(1)
                
                # Vérifier si les processus sont encore actifs
                if self.backend_process and self.backend_process.poll() is not None:
                    if self.running:
                        print("Backend process has stopped")
                        
                if self.frontend_process and self.frontend_process.poll() is not None:
                    if self.running:
                        print("Frontend process has stopped")
                
        except KeyboardInterrupt:
            self.signal_handler(None, None)

def main():
    """Point d'entrée principal."""
    launcher = TradingGUILauncher()
    launcher.run()

if __name__ == "__main__":
    main()