"""
TradingAgents Advanced UXD GUI Web Application
Built on top of Chainlit with terminal-inspired design and real-time agent orchestration
"""

import asyncio
import datetime
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import chainlit as cl
from chainlit.types import AskUserMessage, UIMessagePayload
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from cli.models import AnalystType
from cli.utils import *
from components.trading_dashboard import trading_dashboard, agent_viz

# Global state management
class WebUIState:
    def __init__(self):
        self.current_session = None
        self.graph = None
        self.analysis_state = {
            "ticker": None,
            "analysis_date": None,
            "analysts": [],
            "research_depth": 1,
            "llm_provider": "openai",
            "backend_url": "https://api.openai.com/v1",
            "shallow_thinker": "gpt-4o-mini",
            "deep_thinker": "gpt-4o",
        }
        self.agent_status = {
            # Analyst Team
            "Market Analyst": "pending",
            "Social Analyst": "pending", 
            "News Analyst": "pending",
            "Fundamentals Analyst": "pending",
            # Research Team
            "Bull Researcher": "pending",
            "Bear Researcher": "pending",
            "Research Manager": "pending",
            # Trading Team
            "Trader": "pending",
            # Risk Management Team
            "Risky Analyst": "pending",
            "Neutral Analyst": "pending",
            "Safe Analyst": "pending",
            # Portfolio Management Team
            "Portfolio Manager": "pending",
        }
        self.reports = {
            "market_report": None,
            "sentiment_report": None,
            "news_report": None,
            "fundamentals_report": None,
            "investment_plan": None,
            "trader_investment_plan": None,
            "final_trade_decision": None,
        }
        self.live_messages = []
        self.tool_calls = []

web_state = WebUIState()

@cl.on_chat_start
async def start():
    """Initialize the web interface with terminal-inspired welcome screen."""
    
    # Send welcome message with terminal-style formatting
    welcome_message = """
# 🚀 TradingAgents - Advanced UXD GUI

```
╔══════════════════════════════════════════════════════════════════╗
║                    TradingAgents Web Interface                   ║
║              Multi-Agents LLM Financial Trading Framework       ║
║                                                                  ║
║  Workflow: Analyst → Research → Trading → Risk → Portfolio      ║
║                                                                  ║
║           Built by Tauric Research - Web Enhanced CLI           ║
╚══════════════════════════════════════════════════════════════════╝
```

Welcome to the advanced web interface for TradingAgents! This interface combines the power of our sophisticated CLI with modern web UX.

**Available Features:**
- 📊 Real-time Agent Orchestration Dashboard
- 📈 Interactive Financial Data Visualization  
- ⚙️ Visual Configuration Builder
- 📱 Responsive Design for Mobile Trading
- 🔄 Live Status Updates & Progress Tracking
- 📄 Rich Report Generation & Export

Ready to start your financial analysis? Use the configuration panel below to set up your trading parameters.
    """
    
    await cl.Message(content=welcome_message).send()
    
    # Create interactive configuration form
    await show_configuration_form()

async def show_configuration_form():
    """Display the interactive configuration form."""
    
    # Create configuration actions
    actions = [
        cl.Action(
            name="configure_analysis",
            value="start_config",
            label="🔧 Configure Analysis",
            description="Set up your trading analysis parameters"
        ),
        cl.Action(
            name="view_dashboard",
            value="dashboard",
            label="📊 Agent Dashboard",
            description="View real-time agent status and progress"
        ),
        cl.Action(
            name="market_data",
            value="market_viz",
            label="📈 Market Visualization",
            description="Interactive charts and market data"
        )
    ]
    
    await cl.Message(
        content="**Choose an action to get started:**",
        actions=actions
    ).send()

@cl.action_callback("configure_analysis")
async def configure_analysis(action):
    """Handle configuration form."""
    
    # Step 1: Ticker Symbol
    ticker_msg = await cl.AskUserMessage(
        content="**Step 1: Ticker Symbol**\n\nEnter the ticker symbol to analyze:",
        timeout=60
    ).send()
    
    if ticker_msg:
        web_state.analysis_state["ticker"] = ticker_msg['content'].upper()
        
        # Step 2: Analysis Date
        date_msg = await cl.AskUserMessage(
            content=f"**Step 2: Analysis Date**\n\nEnter analysis date (YYYY-MM-DD) or press Enter for today:",
            timeout=60
        ).send()
        
        if date_msg:
            date_input = date_msg['content'].strip()
            if not date_input:
                date_input = datetime.datetime.now().strftime("%Y-%m-%d")
            web_state.analysis_state["analysis_date"] = date_input
            
            # Step 3: Select Analysts
            analyst_actions = [
                cl.Action(name="analyst_market", value="market", label="📊 Market Analyst"),
                cl.Action(name="analyst_social", value="social", label="📱 Social Analyst"), 
                cl.Action(name="analyst_news", value="news", label="📰 News Analyst"),
                cl.Action(name="analyst_fundamentals", value="fundamentals", label="📈 Fundamentals Analyst"),
            ]
            
            await cl.Message(
                content="**Step 3: Select Analysts**\n\nChoose which analysts to include in your analysis:",
                actions=analyst_actions
            ).send()

@cl.action_callback("analyst_market")
async def select_market_analyst(action):
    """Add market analyst to selection."""
    if "market" not in web_state.analysis_state["analysts"]:
        web_state.analysis_state["analysts"].append("market")
    await update_analyst_selection()

@cl.action_callback("analyst_social") 
async def select_social_analyst(action):
    """Add social analyst to selection."""
    if "social" not in web_state.analysis_state["analysts"]:
        web_state.analysis_state["analysts"].append("social")
    await update_analyst_selection()

@cl.action_callback("analyst_news")
async def select_news_analyst(action):
    """Add news analyst to selection.""" 
    if "news" not in web_state.analysis_state["analysts"]:
        web_state.analysis_state["analysts"].append("news")
    await update_analyst_selection()

@cl.action_callback("analyst_fundamentals")
async def select_fundamentals_analyst(action):
    """Add fundamentals analyst to selection."""
    if "fundamentals" not in web_state.analysis_state["analysts"]:
        web_state.analysis_state["analysts"].append("fundamentals")
    await update_analyst_selection()

async def update_analyst_selection():
    """Update the analyst selection display."""
    selected = ", ".join(web_state.analysis_state["analysts"])
    
    if len(web_state.analysis_state["analysts"]) >= 1:
        start_action = cl.Action(
            name="start_analysis",
            value="begin",
            label="🚀 Start Analysis",
            description="Begin the multi-agent trading analysis"
        )
        
        await cl.Message(
            content=f"**Selected Analysts:** {selected}\n\nReady to start analysis?",
            actions=[start_action]
        ).send()

@cl.action_callback("start_analysis")
async def start_analysis(action):
    """Begin the multi-agent analysis with real-time updates."""
    
    # Show analysis starting message
    await cl.Message(
        content=f"""
**🚀 Starting Analysis**

```
Ticker: {web_state.analysis_state['ticker']}
Date: {web_state.analysis_state['analysis_date']}
Analysts: {', '.join(web_state.analysis_state['analysts'])}
```

**Agent Orchestration Status:**
""").send()
    
    # Initialize the trading graph
    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = web_state.analysis_state["research_depth"]
    config["max_risk_discuss_rounds"] = web_state.analysis_state["research_depth"]
    config["llm_provider"] = web_state.analysis_state["llm_provider"]
    config["backend_url"] = web_state.analysis_state["backend_url"]
    
    web_state.graph = TradingAgentsGraph(
        web_state.analysis_state["analysts"], 
        config=config, 
        debug=True
    )
    
    # Start real-time analysis
    await run_real_time_analysis()

async def run_real_time_analysis():
    """Run the analysis with real-time web updates."""
    
    # Create agent status message that we'll update
    status_msg = await cl.Message(content="Initializing agents...").send()
    
    # Initialize state
    init_state = web_state.graph.propagator.create_initial_state(
        web_state.analysis_state["ticker"],
        web_state.analysis_state["analysis_date"]
    )
    args = web_state.graph.propagator.get_graph_args()
    
    # Stream the analysis with updates
    async for chunk in web_state.graph.graph.astream(init_state, **args):
        await process_analysis_chunk(chunk, status_msg)
    
    # Analysis complete
    await cl.Message(content="✅ **Analysis Complete!** Check the reports above for detailed insights.").send()

async def process_analysis_chunk(chunk, status_msg):
    """Process each chunk of the analysis stream and update the UI."""
    
    # Update agent statuses based on chunk content
    if "market_report" in chunk and chunk["market_report"]:
        web_state.agent_status["Market Analyst"] = "completed"
        web_state.reports["market_report"] = chunk["market_report"]
        await send_report_update("Market Analysis", chunk["market_report"])
        
    if "sentiment_report" in chunk and chunk["sentiment_report"]:
        web_state.agent_status["Social Analyst"] = "completed"
        web_state.reports["sentiment_report"] = chunk["sentiment_report"]
        await send_report_update("Social Sentiment Analysis", chunk["sentiment_report"])
        
    if "news_report" in chunk and chunk["news_report"]:
        web_state.agent_status["News Analyst"] = "completed"
        web_state.reports["news_report"] = chunk["news_report"]
        await send_report_update("News Analysis", chunk["news_report"])
        
    if "fundamentals_report" in chunk and chunk["fundamentals_report"]:
        web_state.agent_status["Fundamentals Analyst"] = "completed"
        web_state.reports["fundamentals_report"] = chunk["fundamentals_report"]
        await send_report_update("Fundamentals Analysis", chunk["fundamentals_report"])
    
    # Handle research team updates
    if "investment_debate_state" in chunk and chunk["investment_debate_state"]:
        debate_state = chunk["investment_debate_state"]
        if "judge_decision" in debate_state and debate_state["judge_decision"]:
            web_state.agent_status["Research Manager"] = "completed"
            web_state.reports["investment_plan"] = debate_state["judge_decision"]
            await send_report_update("Research Team Decision", debate_state["judge_decision"])
    
    # Handle trading team updates
    if "trader_investment_plan" in chunk and chunk["trader_investment_plan"]:
        web_state.agent_status["Trader"] = "completed"
        web_state.reports["trader_investment_plan"] = chunk["trader_investment_plan"]
        await send_report_update("Trading Plan", chunk["trader_investment_plan"])
    
    # Handle risk management updates
    if "risk_debate_state" in chunk and chunk["risk_debate_state"]:
        risk_state = chunk["risk_debate_state"]
        if "judge_decision" in risk_state and risk_state["judge_decision"]:
            web_state.agent_status["Portfolio Manager"] = "completed"
            web_state.reports["final_trade_decision"] = risk_state["judge_decision"]
            await send_report_update("Portfolio Manager Decision", risk_state["judge_decision"])
    
    # Update the status display
    await update_agent_status_display(status_msg)

async def send_report_update(title: str, content: str):
    """Send a report update to the UI."""
    await cl.Message(
        content=f"""
## 📊 {title}

{content}

---
        """
    ).send()

async def update_agent_status_display(status_msg):
    """Update the agent status display."""
    
    status_content = "**🤖 Agent Status Dashboard**\n\n"
    status_content += "```\n"
    
    # Group agents by team
    teams = {
        "Analyst Team": ["Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst"],
        "Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],
        "Trading Team": ["Trader"],
        "Risk Management": ["Risky Analyst", "Neutral Analyst", "Safe Analyst"],
        "Portfolio Management": ["Portfolio Manager"],
    }
    
    for team_name, agents in teams.items():
        status_content += f"\n{team_name}:\n"
        for agent in agents:
            status = web_state.agent_status.get(agent, "pending")
            emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "error": "❌"}.get(status, "❓")
            status_content += f"  {emoji} {agent}: {status}\n"
    
    status_content += "```"
    
    # Update the existing message
    status_msg.content = status_content
    await status_msg.update()

@cl.action_callback("view_dashboard")
async def view_dashboard(action):
    """Show the agent orchestration dashboard."""
    await show_agent_dashboard()

async def show_agent_dashboard():
    """Display the real-time agent dashboard."""
    
    dashboard_content = """
# 📊 Agent Orchestration Dashboard

## Current Analysis State
    """
    
    if web_state.analysis_state["ticker"]:
        dashboard_content += f"""
**Ticker:** {web_state.analysis_state["ticker"]}
**Analysis Date:** {web_state.analysis_state["analysis_date"]}
**Selected Analysts:** {', '.join(web_state.analysis_state["analysts"])}
        """
    else:
        dashboard_content += "\n*No analysis configured yet. Use the Configure Analysis option to get started.*"
    
    dashboard_content += "\n\n## Agent Status Overview\n"
    
    # Create status visualization
    teams = {
        "🔍 Analyst Team": ["Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst"],
        "🧠 Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],
        "💼 Trading Team": ["Trader"],
        "⚠️ Risk Management": ["Risky Analyst", "Neutral Analyst", "Safe Analyst"],
        "📈 Portfolio Management": ["Portfolio Manager"],
    }
    
    for team_name, agents in teams.items():
        dashboard_content += f"\n### {team_name}\n"
        for agent in agents:
            status = web_state.agent_status.get(agent, "pending")
            emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "error": "❌"}.get(status, "❓")
            dashboard_content += f"- {emoji} **{agent}**: {status.title()}\n"
    
    await cl.Message(content=dashboard_content).send()
    
    # Add visual workflow diagram
    workflow_chart = await agent_viz.create_workflow_diagram(web_state.agent_status)
    await cl.Plotly(figure=workflow_chart).send()
    
    # Add agent timeline if there's activity
    timeline_chart = await agent_viz.create_agent_timeline([])
    await cl.Plotly(figure=timeline_chart).send()

@cl.action_callback("market_data")
async def show_market_visualization(action):
    """Show interactive market data visualization."""
    
    await cl.Message(content="# 📈 Interactive Market Visualization\n\nGenerating advanced trading charts and analysis...").send()
    
    # Use ticker from current analysis or default
    ticker = web_state.analysis_state.get("ticker", "SPY")
    
    # Create advanced stock chart
    stock_chart = await trading_dashboard.create_stock_chart(ticker, "1mo")
    await cl.Plotly(figure=stock_chart).send()
    
    # Create sentiment gauge (sample data)
    sentiment_chart = await trading_dashboard.create_sentiment_gauge(0.3)
    await cl.Plotly(figure=sentiment_chart).send()
    
    # Create portfolio performance
    portfolio_chart = await trading_dashboard.create_portfolio_performance({})
    await cl.Plotly(figure=portfolio_chart).send()
    
    # Create risk metrics
    risk_chart = await trading_dashboard.create_risk_metrics_chart({})
    await cl.Plotly(figure=risk_chart).send()
    
    await cl.Message(content="✨ **Advanced Trading Dashboard Complete!** These charts provide comprehensive market analysis and portfolio insights.").send()

def create_sample_chart():
    """Create a sample financial chart for demonstration."""
    
    # Sample data for demonstration
    dates = [f"2024-05-{i:02d}" for i in range(1, 11)]
    prices = [150 + i * 2 + (i % 3) * 5 for i in range(10)]
    volumes = [1000000 + i * 100000 for i in range(10)]
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Stock Price', 'Volume'),
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3]
    )
    
    # Add price chart
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=prices,
            mode='lines+markers',
            name='Price',
            line=dict(color='#00ff88', width=2),
            marker=dict(size=6)
        ),
        row=1, col=1
    )
    
    # Add volume chart
    fig.add_trace(
        go.Bar(
            x=dates,
            y=volumes,
            name='Volume',
            marker_color='#ff6b6b',
            opacity=0.7
        ),
        row=2, col=1
    )
    
    # Update layout with terminal-inspired dark theme
    fig.update_layout(
        title="Market Data Visualization",
        template="plotly_dark",
        height=600,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Monaco, monospace", color="white"),
        title_font=dict(size=20, color="#00ff88")
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    
    return fig

@cl.on_message
async def handle_message(message: cl.Message):
    """Handle user messages and commands."""
    
    content = message.content.lower().strip()
    
    # Handle terminal-style commands
    if content.startswith("/"):
        await handle_command(content)
        return
    
    # Handle general chat
    await cl.Message(
        content=f"I received: {message.content}\n\nUse the action buttons above to configure and run analysis, or try these commands:\n- `/status` - View agent status\n- `/help` - Show available commands\n- `/reset` - Reset configuration"
    ).send()

async def handle_command(command: str):
    """Handle terminal-style commands."""
    
    if command == "/status":
        await show_agent_dashboard()
    elif command == "/help":
        await show_help()
    elif command == "/reset":
        await reset_configuration()
    elif command == "/config":
        await show_configuration_form()
    else:
        await cl.Message(content=f"Unknown command: {command}\n\nType `/help` for available commands.").send()

async def show_help():
    """Show help information."""
    
    help_content = """
# 🆘 TradingAgents Web UI - Help

## Available Commands
- `/status` - View current agent status dashboard
- `/config` - Open configuration form
- `/reset` - Reset all configuration
- `/help` - Show this help message

## Getting Started
1. Click **🔧 Configure Analysis** to set up your analysis parameters
2. Select your desired analysts and configure settings
3. Click **🚀 Start Analysis** to begin the multi-agent workflow
4. Monitor progress in real-time through the dashboard

## Features
- **Real-time Agent Orchestration**: Watch as different AI agents collaborate
- **Interactive Configuration**: Visual setup for complex trading parameters  
- **Live Status Updates**: See agent progress and reports as they're generated
- **Terminal-inspired Design**: Familiar CLI experience in a modern web interface

## Support
Built by Tauric Research - Advanced AI Trading Framework
    """
    
    await cl.Message(content=help_content).send()

async def reset_configuration():
    """Reset the configuration state."""
    
    web_state.analysis_state = {
        "ticker": None,
        "analysis_date": None,
        "analysts": [],
        "research_depth": 1,
        "llm_provider": "openai",
        "backend_url": "https://api.openai.com/v1",
        "shallow_thinker": "gpt-4o-mini",
        "deep_thinker": "gpt-4o",
    }
    
    # Reset agent statuses
    for agent in web_state.agent_status:
        web_state.agent_status[agent] = "pending"
    
    # Reset reports
    for report in web_state.reports:
        web_state.reports[report] = None
    
    await cl.Message(content="🔄 **Configuration Reset**\n\nAll settings have been cleared. Use the Configure Analysis option to start fresh.").send()
    await show_configuration_form()

if __name__ == "__main__":
    import os
    # Set Chainlit configuration
    os.environ["CHAINLIT_HOST"] = "0.0.0.0"
    os.environ["CHAINLIT_PORT"] = "8000"
    
    # Run the Chainlit app
    cl.run()