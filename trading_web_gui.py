"""
TradingAgents Web GUI Frontend
Interface web qui se connecte au service backend TradingAgents
"""

import asyncio
import json
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional
import chainlit as cl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import websockets

# Configuration du service backend
BACKEND_URL = "http://localhost:8001"
WS_URL = "ws://localhost:8001"

# État global de l'interface
class WebGUIState:
    def __init__(self):
        self.current_session_id = None
        self.backend_connected = False
        self.analysis_config = {
            "ticker": None,
            "analysis_date": None,
            "analysts": [],
            "research_depth": 1,
            "llm_provider": "openai"
        }
        self.reports = {}
        self.agent_status = {}
        self.websocket = None
        self.monitoring_active = False

gui_state = WebGUIState()

async def check_backend_connection():
    """Vérifier la connexion au backend."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BACKEND_URL}/api/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    health_data = await response.json()
                    gui_state.backend_connected = True
                    return health_data
    except Exception as e:
        print(f"Backend connection failed: {e}")
    
    gui_state.backend_connected = False
    return None

@cl.on_chat_start
async def start():
    """Initialiser l'interface web."""
    
    welcome_message = """
# 🚀 TradingAgents Web GUI

```
╔══════════════════════════════════════════════════════════════════╗
║                   TradingAgents Web Interface                    ║
║             Interface GUI pour TradingAgents Service             ║
║                                                                  ║
║  Backend Service ──── HTTP/WebSocket ──── Web Interface         ║
║                                                                  ║
║              🔌 Connexion au service TradingAgents...            ║
╚══════════════════════════════════════════════════════════════════╝
```

**🔌 Vérification de la connexion au service backend...**
    """
    
    await cl.Message(content=welcome_message).send()
    
    # Vérifier la connexion au backend
    health_data = await check_backend_connection()
    
    if health_data:
        status_message = f"""
✅ **Service Backend Connecté!**

```
Service: {health_data.get('service', 'TradingAgents Backend')}
Version: {health_data.get('version', '1.0.0')}
Status: {health_data.get('status', 'unknown')}
TradingAgents: {'✅ Available' if health_data.get('trading_agents_available') else '🎭 Demo Mode'}
Sessions Actives: {health_data.get('active_sessions', 0)}
Clients Connectés: {health_data.get('connected_clients', 0)}
```

**🎯 Service opérationnel et prêt pour les analyses!**
        """
        await cl.Message(content=status_message).send()
        await show_main_interface()
    else:
        await cl.Message(content="""
❌ **Service Backend Non Disponible**

**🔧 Pour démarrer le service TradingAgents:**

1. **Ouvrez un nouveau terminal** dans le dossier TradingAgents
2. **Exécutez la commande:** 
   ```bash
   python trading_service.py
   ```
3. **Attendez le message:** "TradingAgents Backend Service started"
4. **Rechargez cette interface web**

**📍 Le service doit tourner sur:** http://localhost:8001

**🆘 Si le problème persiste:**
- Vérifiez que les dépendances sont installées: `pip install fastapi uvicorn`
- Vérifiez que le port 8001 n'est pas occupé
- Consultez les logs dans le terminal du service
        """).send()

async def show_main_interface():
    """Afficher l'interface principale."""
    
    actions = [
        cl.Action(
            name="new_analysis",
            value="new",
            label="🔬 Nouvelle Analyse",
            description="Démarrer une nouvelle analyse de trading avec TradingAgents"
        ),
        cl.Action(
            name="check_status",
            value="status", 
            label="📊 Statut du Service",
            description="Vérifier l'état du service backend et des sessions actives"
        ),
        cl.Action(
            name="list_sessions",
            value="sessions",
            label="📋 Sessions Actives",
            description="Voir toutes les sessions d'analyse en cours"
        ),
        cl.Action(
            name="view_reports",
            value="reports",
            label="📄 Mes Rapports",
            description="Consulter les rapports de la session active"
        )
    ]
    
    await cl.Message(
        content="**🎛️ TradingAgents Web Interface - Sélectionnez une action:**",
        actions=actions
    ).send()

@cl.action_callback("new_analysis")
async def start_new_analysis(action):
    """Démarrer une nouvelle analyse."""
    
    await cl.Message(content="""
**🔬 Configuration de Nouvelle Analyse**

Nous allons configurer votre analyse de trading étape par étape.
Cette interface se connecte au service TradingAgents qui tourne en arrière-plan.

Commençons par les paramètres de base...
    """).send()
    
    # Étape 1: Ticker
    ticker_msg = await cl.AskUserMessage(
        content="**📊 Étape 1: Ticker Symbol**\n\nEntrez le symbole du ticker à analyser (exemples: AAPL, GOOGL, TSLA, SPY, NVDA):",
        timeout=60
    ).send()
    
    if ticker_msg:
        ticker = ticker_msg['output'].upper().strip()
        gui_state.analysis_config["ticker"] = ticker
        
        await cl.Message(content=f"✅ **Ticker sélectionné:** {ticker}").send()
        
        # Étape 2: Date
        date_msg = await cl.AskUserMessage(
            content=f"**📅 Étape 2: Date d'Analyse**\n\nEntrez la date d'analyse (YYYY-MM-DD) ou laissez vide pour aujourd'hui ({datetime.now().strftime('%Y-%m-%d')}):",
            timeout=60
        ).send()
        
        if date_msg:
            date_input = date_msg['output'].strip()
            if not date_input:
                date_input = datetime.now().strftime("%Y-%m-%d")
            gui_state.analysis_config["analysis_date"] = date_input
            
            await cl.Message(content=f"✅ **Date d'analyse:** {date_input}").send()
            
            # Étape 3: Sélection des analystes
            await cl.Message(content="""
**🤖 Étape 3: Sélection des Analystes IA**

Choisissez les spécialistes IA qui composeront votre équipe d'analyse.
Chaque analyste apporte une expertise unique:

- **📊 Market Analyst**: Analyse technique et tendances de marché
- **📱 Social Analyst**: Sentiment des réseaux sociaux et communautés  
- **📰 News Analyst**: Impact des actualités et événements
- **📈 Fundamentals Analyst**: Analyse fondamentale et financière

Sélectionnez au moins un analyste pour votre équipe:
            """).send()
            
            analyst_actions = [
                cl.Action(name="select_market", value="market", label="📊 Market Analyst"),
                cl.Action(name="select_social", value="social", label="📱 Social Analyst"),
                cl.Action(name="select_news", value="news", label="📰 News Analyst"),
                cl.Action(name="select_fundamentals", value="fundamentals", label="📈 Fundamentals Analyst"),
            ]
            
            await cl.Message(
                content="**Cliquez pour ajouter des analystes à votre équipe:**",
                actions=analyst_actions
            ).send()

@cl.action_callback("select_market")
async def select_market_analyst(action):
    if "market" not in gui_state.analysis_config["analysts"]:
        gui_state.analysis_config["analysts"].append("market")
        await cl.Message(content="✅ **Market Analyst** ajouté à l'équipe").send()
    await update_analyst_selection()

@cl.action_callback("select_social")
async def select_social_analyst(action):
    if "social" not in gui_state.analysis_config["analysts"]:
        gui_state.analysis_config["analysts"].append("social")
        await cl.Message(content="✅ **Social Analyst** ajouté à l'équipe").send()
    await update_analyst_selection()

@cl.action_callback("select_news")
async def select_news_analyst(action):
    if "news" not in gui_state.analysis_config["analysts"]:
        gui_state.analysis_config["analysts"].append("news")
        await cl.Message(content="✅ **News Analyst** ajouté à l'équipe").send()
    await update_analyst_selection()

@cl.action_callback("select_fundamentals")
async def select_fundamentals_analyst(action):
    if "fundamentals" not in gui_state.analysis_config["analysts"]:
        gui_state.analysis_config["analysts"].append("fundamentals")
        await cl.Message(content="✅ **Fundamentals Analyst** ajouté à l'équipe").send()
    await update_analyst_selection()

async def update_analyst_selection():
    """Mettre à jour la sélection des analystes."""
    if not gui_state.analysis_config["analysts"]:
        return
        
    selected = ", ".join([a.title() for a in gui_state.analysis_config["analysts"]])
    
    config_summary = f"""
**📋 Résumé de la Configuration:**

```
Ticker Symbol:     {gui_state.analysis_config["ticker"]}
Date d'Analyse:    {gui_state.analysis_config["analysis_date"]}
Équipe d'Analystes: {selected}
Taille de l'Équipe: {len(gui_state.analysis_config["analysts"])} spécialistes
Type d'Analyse:    {'Complète' if len(gui_state.analysis_config["analysts"]) >= 3 else 'Ciblée'}
```

**🎯 Configuration prête pour le lancement!**
    """
    
    await cl.Message(content=config_summary).send()
    
    if len(gui_state.analysis_config["analysts"]) >= 1:
        launch_actions = [
            cl.Action(
                name="launch_analysis",
                value="launch",
                label="🚀 Lancer l'Analyse",
                description="Démarrer l'analyse avec le service TradingAgents"
            ),
            cl.Action(
                name="add_more_analysts",
                value="more",
                label="➕ Ajouter d'Autres Analystes",
                description="Ajouter plus d'analystes à l'équipe"
            )
        ]
        
        await cl.Message(
            content="**🎯 Prêt à lancer l'analyse multi-agents!**",
            actions=launch_actions
        ).send()

@cl.action_callback("add_more_analysts")
async def add_more_analysts(action):
    """Permettre d'ajouter plus d'analystes."""
    current = set(gui_state.analysis_config["analysts"])
    available_actions = []
    
    if "market" not in current:
        available_actions.append(cl.Action(name="select_market", value="market", label="📊 Market Analyst"))
    if "social" not in current:
        available_actions.append(cl.Action(name="select_social", value="social", label="📱 Social Analyst"))
    if "news" not in current:
        available_actions.append(cl.Action(name="select_news", value="news", label="📰 News Analyst"))
    if "fundamentals" not in current:
        available_actions.append(cl.Action(name="select_fundamentals", value="fundamentals", label="📈 Fundamentals Analyst"))
    
    if available_actions:
        await cl.Message(
            content="**➕ Analystes Disponibles:**",
            actions=available_actions
        ).send()
    else:
        await cl.Message(content="✅ **Tous les analystes sont déjà sélectionnés!**").send()

@cl.action_callback("launch_analysis")
async def launch_analysis(action):
    """Lancer l'analyse via le service backend."""
    
    await cl.Message(content="""
🚀 **Lancement de l'Analyse Multi-Agents**

```
╔═══════════════════════════════════════════════════════════════╗
║                    DÉMARRAGE DE L'ANALYSE                    ║
╠═══════════════════════════════════════════════════════════════╣
║  🔄 Connexion au service TradingAgents...                    ║
║  📡 Transmission de la configuration...                      ║
║  🤖 Initialisation des agents IA...                          ║
╚═══════════════════════════════════════════════════════════════╝
```

**⏳ Veuillez patienter...**
    """).send()
    
    try:
        # Préparer la requête
        analysis_request = {
            "ticker": gui_state.analysis_config["ticker"],
            "analysis_date": gui_state.analysis_config["analysis_date"],
            "analysts": gui_state.analysis_config["analysts"],
            "research_depth": gui_state.analysis_config["research_depth"],
            "llm_provider": gui_state.analysis_config["llm_provider"]
        }
        
        # Envoyer la requête au backend
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BACKEND_URL}/api/analysis/start", 
                json=analysis_request,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    gui_state.current_session_id = result["session_id"]
                    
                    await cl.Message(content=f"""
✅ **Analyse Démarrée avec Succès!**

```
╔═══════════════════════════════════════════════════════════════╗
║                     ANALYSE EN COURS                         ║
╠═══════════════════════════════════════════════════════════════╣
║  Session ID: {gui_state.current_session_id}                                    ║
║  Status: {result["status"]}                                        ║
║  Ticker: {gui_state.analysis_config["ticker"]}                                        ║
║  Date: {gui_state.analysis_config["analysis_date"]}                                    ║
║  Analystes: {len(gui_state.analysis_config["analysts"])} spécialistes                                ║
╚═══════════════════════════════════════════════════════════════╝
```

**🔄 Démarrage du monitoring temps réel...**
                    """).send()
                    
                    # Démarrer le suivi temps réel
                    await start_realtime_monitoring()
                    
                else:
                    error_text = await response.text()
                    await cl.Message(content=f"❌ **Erreur lors du démarrage:** HTTP {response.status}\n\nDétails: {error_text}").send()
    
    except asyncio.TimeoutError:
        await cl.Message(content="⏰ **Timeout de connexion** - Le service backend ne répond pas dans les temps.").send()
    except Exception as e:
        await cl.Message(content=f"""
❌ **Erreur de Connexion au Service**

**Erreur:** {str(e)}

**🔧 Solutions possibles:**
1. Vérifiez que le service TradingAgents tourne: `python trading_service.py`
2. Vérifiez l'URL du service: {BACKEND_URL}
3. Vérifiez votre connexion réseau
4. Redémarrez le service backend si nécessaire
        """).send()

async def start_realtime_monitoring():
    """Démarrer le monitoring temps réel via WebSocket."""
    
    gui_state.monitoring_active = True
    
    status_msg = await cl.Message(content="🔄 **Initialisation du Monitoring Temps Réel**\n\nConnexion au flux WebSocket...").send()
    
    try:
        ws_url = f"{WS_URL}/ws/{gui_state.current_session_id}"
        
        async with websockets.connect(ws_url, timeout=10) as websocket:
            gui_state.websocket = websocket
            
            await cl.Message(content="""
✅ **Connexion WebSocket Établie!**

🔄 **Écoute des mises à jour en temps réel...**
- Progression des agents IA
- Génération des rapports d'analyse  
- Statuts en temps réel
- Notifications d'événements

**Restez connecté pour voir l'analyse se dérouler en direct!**
            """).send()
            
            # Créer le tableau de bord de progression
            progress_msg = await cl.Message(content="📊 **Tableau de Bord - En attente des premiers événements...**").send()
            
            async for message in websocket:
                if not gui_state.monitoring_active:
                    break
                    
                try:
                    data = json.loads(message)
                    await process_realtime_update(data, status_msg, progress_msg)
                except json.JSONDecodeError:
                    continue
                
    except websockets.exceptions.ConnectionClosed:
        await cl.Message(content="🔌 **Connexion WebSocket fermée** - Passage en mode polling HTTP...").send()
        await start_http_polling(status_msg)
    except Exception as e:
        await cl.Message(content=f"""
⚠️ **Connexion WebSocket échouée:** {str(e)}

🔄 **Basculement vers le polling HTTP** pour continuer le suivi...
        """).send()
        await start_http_polling(status_msg)

async def process_realtime_update(data: Dict, status_msg, progress_msg):
    """Traiter les mises à jour temps réel."""
    
    if data.get("type") == "ping":
        return  # Ignorer les pings
    
    elif data["type"] == "status_update":
        status_msg.content = f"""
🔄 **Status en Temps Réel**

```
Status: {data.get('status', 'unknown')}
Étape: {data.get('current_step', 'En cours...')}
Message: {data.get('message', 'Traitement...')}
```
        """
        await status_msg.update()
        
    elif data["type"] == "agent_update":
        agent = data.get("agent", "Unknown")
        agent_status = data.get("status", "unknown")
        
        # Mettre à jour le statut de l'agent
        gui_state.agent_status[agent] = agent_status
        
        # Mettre à jour le tableau de bord
        await update_progress_dashboard(progress_msg)
        
        # Notification pour agent terminé
        if agent_status == "completed":
            await cl.Message(content=f"✅ **{agent}** a terminé son analyse avec succès!").send()
        elif agent_status == "in_progress":
            await cl.Message(content=f"🔄 **{agent}** analyse en cours...").send()
            
    elif data["type"] == "new_report":
        agent = data.get("agent", "Unknown Agent")
        report_type = data.get("report_type", "unknown")
        content = data.get("content", "")
        
        # Stocker le rapport
        gui_state.reports[report_type] = content
        
        # Afficher le nouveau rapport avec formatage amélioré
        await cl.Message(content=f"""
# 📊 Rapport de {agent}

{content}

---
**⏰ Généré le:** {datetime.now().strftime('%H:%M:%S')}
        """).send()
        
    elif data["type"] == "analysis_complete":
        gui_state.monitoring_active = False
        
        completion_summary = f"""
🎉 **ANALYSE TERMINÉE AVEC SUCCÈS!**

```
╔═══════════════════════════════════════════════════════════════╗
║                    ANALYSE COMPLÉTÉE                         ║
╠═══════════════════════════════════════════════════════════════╣
║  Session: {gui_state.current_session_id}                                    ║
║  Ticker: {gui_state.analysis_config["ticker"]}                                        ║
║  Rapports Générés: {len(gui_state.reports)}                                   ║
║  Durée: {datetime.now().strftime('%H:%M:%S')}                                      ║
╚═══════════════════════════════════════════════════════════════╝
```

**📄 Tous les rapports d'analyse ont été générés avec succès!**

**🎯 Actions disponibles:**
- Consultez les rapports détaillés ci-dessus
- Exportez les résultats si nécessaire
- Lancez une nouvelle analyse avec d'autres paramètres
        """
        
        await cl.Message(content=completion_summary).send()
        
        # Afficher les actions post-analyse
        post_actions = [
            cl.Action(name="new_analysis", value="new", label="🔬 Nouvelle Analyse"),
            cl.Action(name="view_reports", value="reports", label="📄 Voir Tous les Rapports"),
            cl.Action(name="check_status", value="status", label="📊 Statut du Service")
        ]
        
        await cl.Message(
            content="**🎛️ Que souhaitez-vous faire maintenant?**",
            actions=post_actions
        ).send()
        
    elif data["type"] == "error":
        gui_state.monitoring_active = False
        await cl.Message(content=f"""
❌ **Erreur lors de l'Analyse**

**Détails:** {data.get('error', 'Erreur inconnue')}

**🔧 Actions recommandées:**
1. Vérifiez les paramètres de configuration
2. Relancez l'analyse avec des paramètres différents  
3. Consultez les logs du service backend
4. Contactez le support technique si le problème persiste
        """).send()

async def update_progress_dashboard(progress_msg):
    """Mettre à jour le tableau de bord de progression."""
    
    # Organiser les agents par équipe
    teams = {
        "🔍 Équipe d'Analyse": ["Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst"],
        "🧠 Équipe de Recherche": ["Bull Researcher", "Bear Researcher", "Research Manager"],
        "💼 Équipe de Trading": ["Trader"],
        "⚠️ Gestion des Risques": ["Risky Analyst", "Neutral Analyst", "Safe Analyst"],
        "📈 Gestion de Portfolio": ["Portfolio Manager"],
    }
    
    dashboard_content = "📊 **Tableau de Bord Multi-Agents**\n\n"
    
    for team_name, agents in teams.items():
        dashboard_content += f"### {team_name}\n"
        
        for agent in agents:
            status = gui_state.agent_status.get(agent, "pending")
            
            if status == "completed":
                emoji = "✅"
                status_text = "Terminé"
            elif status == "in_progress":
                emoji = "🔄"
                status_text = "En cours"
            elif status == "error":
                emoji = "❌"
                status_text = "Erreur"
            else:
                emoji = "⏳"
                status_text = "En attente"
            
            dashboard_content += f"- {emoji} **{agent}**: {status_text}\n"
        
        dashboard_content += "\n"
    
    # Statistiques globales
    total_agents = sum(len(agents) for agents in teams.values())
    completed_agents = sum(1 for status in gui_state.agent_status.values() if status == "completed")
    progress_percent = (completed_agents / total_agents * 100) if total_agents > 0 else 0
    
    dashboard_content += f"""
**📈 Progression Globale:** {completed_agents}/{total_agents} agents ({progress_percent:.1f}%)
**📄 Rapports Générés:** {len(gui_state.reports)}
**⏰ Dernière Mise à Jour:** {datetime.now().strftime('%H:%M:%S')}
    """
    
    progress_msg.content = dashboard_content
    await progress_msg.update()

async def start_http_polling(status_msg):
    """Démarrer le polling HTTP si WebSocket échoue."""
    
    if not gui_state.current_session_id:
        return
    
    polling_msg = await cl.Message(content="🔄 **Mode Polling HTTP Activé**\n\nVérification du statut toutes les 5 secondes...").send()
    
    while gui_state.current_session_id and gui_state.monitoring_active:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{BACKEND_URL}/api/analysis/{gui_state.current_session_id}/status",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        status_data = await response.json()
                        
                        # Mettre à jour le statut
                        polling_msg.content = f"""
🔄 **Polling HTTP - Status de l'Analyse**

```
Session: {gui_state.current_session_id}
Status: {status_data["status"]}
Étape: {status_data.get("current_step", "Unknown")}
Rapports: {len(status_data.get("reports", {}))}
```

**⏰ Prochaine vérification dans 5 secondes...**
                        """
                        await polling_msg.update()
                        
                        # Vérifier les nouveaux rapports
                        for report_type, content in status_data.get("reports", {}).items():
                            if report_type not in gui_state.reports:
                                gui_state.reports[report_type] = content
                                await cl.Message(content=f"""
# 📊 {report_type.replace('_', ' ').title()}

{content}

---
                                """).send()
                        
                        # Vérifier si terminé
                        if status_data["status"] == "completed":
                            gui_state.monitoring_active = False
                            await cl.Message(content="🎉 **Analyse Terminée!** (détectée via polling HTTP)").send()
                            break
                        elif status_data["status"] == "error":
                            gui_state.monitoring_active = False
                            error_msg = status_data.get("error", "Erreur inconnue")
                            await cl.Message(content=f"❌ **Erreur d'Analyse:** {error_msg}").send()
                            break
                            
        except Exception as e:
            await cl.Message(content=f"⚠️ Erreur de polling: {str(e)}").send()
            
        await asyncio.sleep(5)

@cl.action_callback("check_status")
async def check_backend_status(action):
    """Vérifier le statut du service backend."""
    
    await cl.Message(content="🔍 **Vérification du statut du service...**").send()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BACKEND_URL}/api/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    health_data = await response.json()
                    
                    status_content = f"""
# 🏥 Statut du Service TradingAgents

## ✅ Service En Ligne et Opérationnel

```
╔═══════════════════════════════════════════════════════════════╗
║                     SERVICE STATUS                           ║
╠═══════════════════════════════════════════════════════════════╣
║  Service: {health_data.get("service", "TradingAgents Backend")}                        ║
║  Version: {health_data.get("version", "1.0.0")}                                     ║
║  Status: {health_data.get("status", "unknown").upper()}                                      ║
║  Framework: {'✅ TradingAgents' if health_data.get('trading_agents_available') else '🎭 Demo Mode'}                             ║
║  Sessions: {health_data.get("active_sessions", 0)} actives                                ║
║  Clients: {health_data.get("connected_clients", 0)} connectés                             ║
║  Timestamp: {health_data.get("timestamp", "unknown")}                      ║
╚═══════════════════════════════════════════════════════════════╝
```

## 🔗 Endpoints Disponibles

- **API Health:** `GET /api/health`
- **Start Analysis:** `POST /api/analysis/start`
- **Get Status:** `GET /api/analysis/{{session_id}}/status`
- **List Sessions:** `GET /api/sessions`
- **WebSocket:** `WS /ws/{{session_id}}`

## 📍 URLs de Service

- **Backend API:** {BACKEND_URL}
- **Documentation:** {BACKEND_URL}/docs
- **WebSocket Base:** {WS_URL}

**🎯 Le service est prêt pour les analyses!**
                    """
                    
                    await cl.Message(content=status_content).send()
                else:
                    await cl.Message(content=f"❌ **Service Non Disponible** - Code HTTP: {response.status}").send()
    except Exception as e:
        await cl.Message(content=f"""
❌ **Erreur de Connexion au Service**

**Erreur:** {str(e)}

**🔧 Actions recommandées:**
1. Vérifiez que le service TradingAgents tourne: `python trading_service.py`
2. Vérifiez l'URL du service: {BACKEND_URL}
3. Vérifiez que le port 8001 n'est pas bloqué
4. Redémarrez le service si nécessaire
        """).send()

@cl.action_callback("list_sessions")
async def list_sessions(action):
    """Lister toutes les sessions d'analyse."""
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BACKEND_URL}/api/sessions", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    sessions_data = await response.json()
                    sessions = sessions_data.get("sessions", [])
                    
                    if not sessions:
                        await cl.Message(content="📋 **Aucune session active** - Aucune analyse en cours actuellement.").send()
                        return
                    
                    sessions_content = f"""
# 📋 Sessions d'Analyse Actives

**Total:** {len(sessions)} sessions

"""
                    
                    for i, session in enumerate(sessions, 1):
                        status_emoji = {
                            "running": "🔄",
                            "completed": "✅", 
                            "error": "❌",
                            "starting": "🚀"
                        }.get(session.get("status", "unknown"), "❓")
                        
                        sessions_content += f"""
## {i}. Session {session.get("session_id", "unknown")[:8]}...

```
Status: {status_emoji} {session.get("status", "unknown").title()}
Ticker: {session.get("ticker", "N/A")}
Date: {session.get("analysis_date", "N/A")}
Analystes: {", ".join(session.get("analysts", []))}
Début: {session.get("start_time", "N/A")[:19]}
Rapports: {session.get("reports_count", 0)}
```
"""
                    
                    await cl.Message(content=sessions_content).send()
                    
                    # Actions pour se connecter à une session
                    if gui_state.current_session_id:
                        await cl.Message(content=f"🔗 **Session active:** {gui_state.current_session_id[:8]}...").send()
                    else:
                        await cl.Message(content="💡 **Conseil:** Vous pouvez démarrer une nouvelle analyse pour créer une session.").send()
                        
                else:
                    await cl.Message(content="❌ **Erreur lors de la récupération des sessions**").send()
                    
    except Exception as e:
        await cl.Message(content=f"❌ **Erreur de connexion:** {str(e)}").send()

@cl.action_callback("view_reports")
async def view_reports(action):
    """Afficher les rapports de la session active."""
    
    if not gui_state.current_session_id:
        await cl.Message(content="❌ **Aucune session active** - Démarrez une analyse d'abord.").send()
        return
    
    if not gui_state.reports:
        await cl.Message(content="📄 **Aucun rapport disponible** - L'analyse est peut-être encore en cours.").send()
        return
    
    await cl.Message(content=f"""
# 📄 Rapports de la Session Active

**Session ID:** {gui_state.current_session_id}
**Rapports Disponibles:** {len(gui_state.reports)}

---
    """).send()
    
    # Afficher chaque rapport
    for report_type, content in gui_state.reports.items():
        report_title = report_type.replace('_', ' ').title()
        await cl.Message(content=f"""
# 📊 {report_title}

{content}

---
        """).send()

@cl.on_message
async def handle_message(message: cl.Message):
    """Gérer les messages utilisateur."""
    
    content = message.content.lower().strip()
    
    if content.startswith("/"):
        if content == "/health":
            await check_backend_status(None)
        elif content == "/status":
            if gui_state.current_session_id:
                await cl.Message(content=f"📊 **Session active:** {gui_state.current_session_id}").send()
            else:
                await cl.Message(content="❌ **Aucune session active** - Démarrez une nouvelle analyse.").send()
        elif content == "/sessions":
            await list_sessions(None)
        elif content == "/reset":
            gui_state.current_session_id = None
            gui_state.analysis_config = {
                "ticker": None,
                "analysis_date": None,
                "analysts": [],
                "research_depth": 1,
                "llm_provider": "openai"
            }
            gui_state.reports = {}
            gui_state.agent_status = {}
            gui_state.monitoring_active = False
            await cl.Message(content="🔄 **Interface réinitialisée** - Prêt pour une nouvelle analyse.").send()
            await show_main_interface()
        elif content == "/help":
            await cl.Message(content="""
# 🆘 Aide - TradingAgents Web GUI

## 📋 Commandes Disponibles
- `/health` - Vérifier le statut du service backend
- `/status` - Afficher la session active
- `/sessions` - Lister toutes les sessions
- `/reset` - Réinitialiser l'interface
- `/help` - Afficher cette aide

## 🚀 Comment Utiliser
1. **Nouvelle Analyse** - Cliquez sur "🔬 Nouvelle Analyse"
2. **Configurez** - Sélectionnez ticker, date, et analystes
3. **Lancez** - Démarrez l'analyse multi-agents
4. **Suivez** - Regardez les rapports en temps réel

## 🔧 Dépannage
- Vérifiez que le service backend tourne sur le port 8001
- Utilisez `/health` pour diagnostiquer les problèmes
- Redémarrez le service si nécessaire

**Built with ❤️ by TradingAgents Team**
            """).send()
        else:
            await cl.Message(content=f"❓ **Commande inconnue:** `{content}`\n\nTapez `/help` pour voir les commandes disponibles.").send()
    else:
        await cl.Message(content=f"""
💬 **Message reçu:** {message.content}

**🎛️ Interface Interactive**
Utilisez les boutons d'action ci-dessous pour interagir avec TradingAgents, ou tapez une commande commençant par `/`.

**Commandes rapides:** `/help`, `/health`, `/status`, `/sessions`
        """).send()

if __name__ == "__main__":
    import os
    os.environ["CHAINLIT_HOST"] = "0.0.0.0"
    os.environ["CHAINLIT_PORT"] = "8000"
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                TradingAgents Web GUI Frontend                    ║
║                                                                  ║
║  🌐 Interface Web: http://localhost:8000                         ║
║  🔌 Backend Service: http://localhost:8001                       ║
║                                                                  ║
║  Assurez-vous que le service backend tourne avant de démarrer   ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    cl.run()