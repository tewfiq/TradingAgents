"""
TradingAgents Backend Service
Expose TradingAgents CLI via FastAPI pour interface web
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import threading
import time
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.default_config import DEFAULT_CONFIG
    from cli.models import AnalystType
    from cli.utils import *
    TRADING_AGENTS_AVAILABLE = True
    logger.info("✅ TradingAgents framework loaded successfully")
except ImportError as e:
    TRADING_AGENTS_AVAILABLE = False
    logger.warning(f"⚠️ TradingAgents not available: {e}")

# Models pour l'API
class AnalysisRequest(BaseModel):
    ticker: str
    analysis_date: str
    analysts: List[str]
    research_depth: int = 1
    llm_provider: str = "openai"
    backend_url: str = "https://api.openai.com/v1"

class AnalysisStatus(BaseModel):
    session_id: str
    status: str
    progress: Dict[str, str]
    current_step: str
    reports: Dict[str, Any]

class SessionInfo(BaseModel):
    session_id: str
    status: str
    ticker: str
    analysis_date: str
    analysts: List[str]
    start_time: str
    reports_count: int

# Service Backend
class TradingAgentsService:
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
        logger.info("🚀 TradingAgents Service initialized")
        
    async def start_analysis(self, request: AnalysisRequest) -> str:
        """Démarrer une nouvelle analyse."""
        session_id = str(uuid.uuid4())
        
        logger.info(f"📊 Starting new analysis session: {session_id}")
        logger.info(f"   Ticker: {request.ticker}")
        logger.info(f"   Analysts: {request.analysts}")
        
        # Initialiser la session
        self.active_sessions[session_id] = {
            "request": request,
            "status": "starting",
            "progress": {
                "Market Analyst": "pending",
                "Social Analyst": "pending",
                "News Analyst": "pending",
                "Fundamentals Analyst": "pending",
                "Bull Researcher": "pending",
                "Bear Researcher": "pending",
                "Research Manager": "pending",
                "Trader": "pending",
                "Risky Analyst": "pending",
                "Neutral Analyst": "pending",
                "Safe Analyst": "pending",
                "Portfolio Manager": "pending",
            },
            "reports": {},
            "graph": None,
            "start_time": datetime.now(),
            "current_step": "Initializing"
        }
        
        # Démarrer l'analyse en arrière-plan
        asyncio.create_task(self._run_analysis(session_id))
        
        return session_id
    
    async def _run_analysis(self, session_id: str):
        """Exécuter l'analyse en arrière-plan."""
        session = self.active_sessions[session_id]
        request = session["request"]
        
        try:
            session["status"] = "running"
            session["current_step"] = "Initializing TradingAgents"
            
            # Notifier le début
            await self._notify_websocket(session_id, {
                "type": "status_update", 
                "status": "running",
                "message": "Analysis started",
                "current_step": "Initializing TradingAgents"
            })
            
            if TRADING_AGENTS_AVAILABLE:
                await self._run_real_analysis(session_id)
            else:
                await self._run_demo_analysis(session_id)
            
            # Analyse terminée
            session["status"] = "completed"
            session["current_step"] = "Analysis completed"
            await self._notify_websocket(session_id, {
                "type": "analysis_complete",
                "session_id": session_id,
                "final_reports": session["reports"]
            })
            
            logger.info(f"✅ Analysis completed for session: {session_id}")
            
        except Exception as e:
            logger.error(f"❌ Analysis error for session {session_id}: {str(e)}")
            session["status"] = "error"
            session["error"] = str(e)
            await self._notify_websocket(session_id, {
                "type": "error",
                "error": str(e)
            })
    
    async def _run_real_analysis(self, session_id: str):
        """Exécuter l'analyse réelle avec TradingAgents."""
        session = self.active_sessions[session_id]
        request = session["request"]
        
        # Initialiser TradingAgents
        config = DEFAULT_CONFIG.copy()
        config["max_debate_rounds"] = request.research_depth
        config["llm_provider"] = request.llm_provider
        config["backend_url"] = request.backend_url
        
        graph = TradingAgentsGraph(request.analysts, config=config, debug=True)
        session["graph"] = graph
        
        # Initialiser l'état
        init_state = graph.propagator.create_initial_state(
            request.ticker, request.analysis_date
        )
        args = graph.propagator.get_graph_args()
        
        # Streamer l'analyse
        async for chunk in graph.graph.astream(init_state, **args):
            await self._process_chunk(session_id, chunk)
    
    async def _run_demo_analysis(self, session_id: str):
        """Exécuter une analyse démo."""
        session = self.active_sessions[session_id]
        request = session["request"]
        
        logger.info(f"🎭 Running demo analysis for session: {session_id}")
        
        # Simulation des agents
        agents_mapping = {
            "market": "Market Analyst",
            "social": "Social Analyst", 
            "news": "News Analyst",
            "fundamentals": "Fundamentals Analyst"
        }
        
        selected_agents = [agents_mapping.get(analyst, analyst) for analyst in request.analysts if analyst in agents_mapping]
        
        for agent in selected_agents:
            # Agent en cours
            session["progress"][agent] = "in_progress"
            session["current_step"] = f"Running {agent}"
            
            await self._notify_websocket(session_id, {
                "type": "agent_update",
                "agent": agent,
                "status": "in_progress",
                "current_step": f"Running {agent}"
            })
            
            # Simulation du temps de traitement
            await asyncio.sleep(3)
            
            # Agent terminé avec rapport
            session["progress"][agent] = "completed"
            report_content = await self._generate_demo_report(agent, request.ticker)
            session["reports"][f"{agent.lower().replace(' ', '_')}_report"] = report_content
            
            await self._notify_websocket(session_id, {
                "type": "new_report",
                "agent": agent,
                "report_type": f"{agent.lower().replace(' ', '_')}_report",
                "content": report_content
            })
            
            await self._notify_websocket(session_id, {
                "type": "agent_update", 
                "agent": agent,
                "status": "completed"
            })
    
    async def _generate_demo_report(self, agent: str, ticker: str) -> str:
        """Générer un rapport démo."""
        
        reports = {
            "Market Analyst": f"""
# 📊 Market Analysis Report - {ticker}

## Technical Analysis Summary
- **Current Trend:** Bullish momentum detected
- **Support Level:** Strong support at $145.20
- **Resistance Level:** Key resistance at $162.80
- **RSI:** 58.3 (Neutral zone)
- **Volume:** Above average on recent sessions

## Key Findings
- Price action shows bullish continuation pattern
- Moving averages alignment suggests upward momentum
- Options flow indicates institutional interest

## Recommendation
**Target:** $158.50 (short-term), $165.00 (medium-term)
**Stop Loss:** $142.00

*This is a demo analysis for demonstration purposes.*
            """,
            
            "Social Analyst": f"""
# 📱 Social Sentiment Analysis - {ticker}

## Sentiment Overview
- **Overall Score:** 67/100 (Moderately Positive)
- **Trend:** Improving (+12% over 7 days)
- **Volume:** 2.3x normal discussion levels

## Platform Analysis
- **Twitter/X:** 72% positive mentions
- **Reddit:** 68% bullish sentiment in r/investing
- **StockTwits:** 69% bullish sentiment
- **Discord:** Active discussion, moderate FOMO

## Key Drivers
- Positive earnings expectations
- Sector rotation trends
- Influencer mentions driving retail interest

*This is a demo analysis for demonstration purposes.*
            """,
            
            "News Analyst": f"""
# 📰 News Impact Analysis - {ticker}

## News Sentiment Summary
- **Headline Sentiment:** Positive (74/100)
- **Coverage Quality:** High-quality financial media
- **Market Impact:** Medium-High potential

## Recent Headlines
- "Company beats quarterly expectations"
- "Analysts upgrade price targets"
- "Sector tailwinds support growth"
- "Management signals confident outlook"

## Upcoming Catalysts
- Quarterly earnings call next week
- Industry conference presentation
- Potential partnership announcements

*This is a demo analysis for demonstration purposes.*
            """,
            
            "Fundamentals Analyst": f"""
# 📈 Fundamental Analysis - {ticker}

## Financial Health
- **Revenue Growth:** 12.5% YoY
- **Profit Margins:** Expanding (+150 bps)
- **Debt-to-Equity:** 0.35 (Conservative)
- **ROE:** 18.2% (Top quartile)

## Valuation Metrics
- **P/E Ratio:** 22.5x (vs sector 26.8x)
- **PEG Ratio:** 1.2 (Reasonable)
- **Price-to-Sales:** 3.4x (In-line)

## Growth Drivers
- Market share expansion
- Product launch momentum
- Operating leverage improving

## Price Target: $172.00

*This is a demo analysis for demonstration purposes.*
            """
        }
        
        return reports.get(agent, f"# {agent} Report\n\nAnalysis for {ticker} completed successfully.")
    
    async def _process_chunk(self, session_id: str, chunk: Dict):
        """Traiter chaque chunk de l'analyse."""
        session = self.active_sessions[session_id]
        
        # Mettre à jour les rapports
        report_types = {
            "market_report": "Market Analyst",
            "sentiment_report": "Social Analyst", 
            "news_report": "News Analyst",
            "fundamentals_report": "Fundamentals Analyst",
            "trader_investment_plan": "Trader",
            "final_trade_decision": "Portfolio Manager"
        }
        
        for report_type, agent_name in report_types.items():
            if report_type in chunk and chunk[report_type]:
                session["reports"][report_type] = chunk[report_type]
                session["progress"][agent_name] = "completed"
                
                # Notifier le nouveau rapport
                await self._notify_websocket(session_id, {
                    "type": "new_report",
                    "report_type": report_type,
                    "agent": agent_name,
                    "content": chunk[report_type]
                })
                
                await self._notify_websocket(session_id, {
                    "type": "agent_update",
                    "agent": agent_name,
                    "status": "completed"
                })
        
        # Mettre à jour le statut global
        await self._notify_websocket(session_id, {
            "type": "chunk_update",
            "chunk": chunk,
            "progress": session["progress"]
        })
    
    async def _notify_websocket(self, session_id: str, message: Dict):
        """Notifier via WebSocket."""
        if session_id in self.websocket_connections:
            try:
                await self.websocket_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.warning(f"WebSocket notification failed for {session_id}: {e}")
                # Connection fermée
                if session_id in self.websocket_connections:
                    del self.websocket_connections[session_id]
    
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Obtenir le statut d'une session."""
        return self.active_sessions.get(session_id)
    
    def get_all_sessions(self) -> List[SessionInfo]:
        """Obtenir toutes les sessions."""
        sessions = []
        for session_id, session_data in self.active_sessions.items():
            request = session_data["request"]
            sessions.append(SessionInfo(
                session_id=session_id,
                status=session_data["status"],
                ticker=request.ticker,
                analysis_date=request.analysis_date,
                analysts=request.analysts,
                start_time=session_data["start_time"].isoformat(),
                reports_count=len(session_data["reports"])
            ))
        return sessions

# Initialiser le service
trading_service = TradingAgentsService()
app = FastAPI(
    title="TradingAgents Backend API", 
    version="1.0.0",
    description="Backend service for TradingAgents multi-agent trading framework"
)

# CORS pour l'interface web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Page d'accueil de l'API."""
    return {
        "service": "TradingAgents Backend API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "start_analysis": "POST /api/analysis/start",
            "get_status": "GET /api/analysis/{session_id}/status",
            "list_sessions": "GET /api/sessions",
            "websocket": "WS /ws/{session_id}"
        }
    }

@app.post("/api/analysis/start")
async def start_analysis(request: AnalysisRequest):
    """Démarrer une nouvelle analyse."""
    logger.info(f"📊 New analysis request: {request.ticker} with analysts: {request.analysts}")
    
    session_id = await trading_service.start_analysis(request)
    return {
        "session_id": session_id, 
        "status": "started",
        "ticker": request.ticker,
        "analysts": request.analysts
    }

@app.get("/api/analysis/{session_id}/status")
async def get_analysis_status(session_id: str):
    """Obtenir le statut d'une analyse."""
    session = trading_service.get_session_status(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "status": session["status"],
        "current_step": session.get("current_step", "Unknown"),
        "progress": session.get("progress", {}),
        "reports": session["reports"],
        "start_time": session["start_time"].isoformat(),
        "error": session.get("error")
    }

@app.get("/api/sessions")
async def list_sessions():
    """Liste toutes les sessions d'analyse."""
    sessions = trading_service.get_all_sessions()
    return {
        "sessions": sessions,
        "total": len(sessions)
    }

@app.delete("/api/analysis/{session_id}")
async def delete_session(session_id: str):
    """Supprimer une session."""
    if session_id in trading_service.active_sessions:
        del trading_service.active_sessions[session_id]
        if session_id in trading_service.websocket_connections:
            del trading_service.websocket_connections[session_id]
        return {"message": "Session deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket pour mises à jour en temps réel."""
    await websocket.accept()
    trading_service.websocket_connections[session_id] = websocket
    
    logger.info(f"🔌 WebSocket connected for session: {session_id}")
    
    try:
        # Envoyer le statut initial si la session existe
        if session_id in trading_service.active_sessions:
            session = trading_service.active_sessions[session_id]
            await websocket.send_text(json.dumps({
                "type": "initial_status",
                "status": session["status"],
                "progress": session.get("progress", {}),
                "reports": session["reports"]
            }))
        
        while True:
            # Garder la connexion vivante
            await asyncio.sleep(30)
            await websocket.send_text(json.dumps({"type": "ping"}))
            
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket disconnected for session: {session_id}")
        if session_id in trading_service.websocket_connections:
            del trading_service.websocket_connections[session_id]
    except Exception as e:
        logger.error(f"❌ WebSocket error for session {session_id}: {e}")
        if session_id in trading_service.websocket_connections:
            del trading_service.websocket_connections[session_id]

@app.get("/api/health")
async def health_check():
    """Vérification de santé du service."""
    return {
        "status": "healthy",
        "service": "TradingAgents Backend",
        "version": "1.0.0",
        "trading_agents_available": TRADING_AGENTS_AVAILABLE,
        "active_sessions": len(trading_service.active_sessions),
        "connected_clients": len(trading_service.websocket_connections),
        "timestamp": datetime.now().isoformat()
    }

@app.on_event("startup")
async def startup_event():
    """Événement de démarrage."""
    logger.info("🚀 TradingAgents Backend Service started")
    logger.info(f"   TradingAgents Framework: {'✅ Available' if TRADING_AGENTS_AVAILABLE else '⚠️ Demo Mode'}")

@app.on_event("shutdown") 
async def shutdown_event():
    """Événement d'arrêt."""
    logger.info("🛑 TradingAgents Backend Service shutting down")

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║               TradingAgents Backend Service                      ║
║                                                                  ║
║  🚀 Starting FastAPI service...                                 ║
║  📍 API: http://localhost:8001                                   ║
║  📚 Docs: http://localhost:8001/docs                             ║
║  🔌 WebSocket: ws://localhost:8001/ws/{session_id}               ║
║                                                                  ║
║  Press Ctrl+C to stop                                           ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")