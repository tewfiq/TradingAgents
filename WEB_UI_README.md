# 🚀 TradingAgents Advanced UXD GUI Web Interface

A sophisticated web application that transforms the powerful TradingAgents CLI into an intuitive, terminal-inspired web interface with advanced UX design and real-time agent orchestration.

## ✨ Features

### 🎯 Core Capabilities
- **Terminal-Inspired Design**: Dark theme with monospace fonts and terminal aesthetics
- **Real-time Agent Orchestration**: Live visualization of multi-agent trading workflows
- **Interactive Configuration**: Visual setup for complex trading parameters
- **Advanced Data Visualization**: Professional trading charts and analytics
- **Mobile-Responsive**: Optimized for desktop, tablet, and mobile trading
- **Live Progress Tracking**: Real-time status updates and progress monitoring

### 📊 Advanced Components

#### Agent Orchestration Dashboard
- **Workflow Visualization**: Interactive diagram showing agent progression
- **Real-time Status Updates**: Live agent state monitoring with color-coded indicators
- **Timeline View**: Chronological visualization of agent activities
- **Team-based Organization**: Grouped by functional teams (Analyst, Research, Trading, Risk, Portfolio)

#### Trading Analytics Suite
- **Advanced Stock Charts**: Candlestick charts with technical indicators (SMA, RSI)
- **Sentiment Analysis**: Real-time market sentiment gauges and visualization
- **Portfolio Performance**: Comprehensive portfolio tracking and analysis
- **Risk Metrics**: Advanced risk assessment with radar charts and metrics

#### Interactive Configuration Builder
- **Step-by-step Setup**: Guided configuration process with visual feedback
- **Dynamic Analyst Selection**: Choose and configure different AI analysts
- **Parameter Customization**: Visual controls for research depth, LLM providers, and more
- **Real-time Validation**: Instant feedback on configuration choices

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Required packages (see `requirements.txt`)
- TradingAgents framework installed

### Installation & Setup

1. **Clone and navigate to the repository:**
   ```bash
   cd /path/to/tradingagents
   ```

2. **Install web UI dependencies:**
   ```bash
   pip install chainlit plotly yfinance
   # or install all requirements
   pip install -r requirements.txt
   ```

3. **Start the web interface:**
   ```bash
   python start_web_ui.py
   ```
   
   Or manually:
   ```bash
   chainlit run web_ui.py --host 0.0.0.0 --port 8000
   ```

4. **Open your browser:**
   - Local: http://localhost:8000
   - Network: http://your-ip:8000

## 💻 User Interface Guide

### Getting Started
1. **Welcome Screen**: Terminal-inspired welcome with feature overview
2. **Configuration**: Click "🔧 Configure Analysis" to set up parameters
3. **Analysis Setup**: 
   - Enter ticker symbol (e.g., AAPL, GOOGL, SPY)
   - Select analysis date
   - Choose AI analysts for your analysis
   - Configure research depth and LLM settings
4. **Start Analysis**: Click "🚀 Start Analysis" to begin the multi-agent workflow
5. **Monitor Progress**: Watch real-time agent activity and report generation

### Dashboard Features

#### 📊 Agent Orchestration Dashboard
- **Status Overview**: Real-time agent status with emoji indicators
  - ⏳ Pending - Agent waiting to start
  - 🔄 In Progress - Agent actively working  
  - ✅ Completed - Agent finished successfully
  - ❌ Error - Agent encountered an issue

- **Workflow Visualization**: Interactive diagram showing:
  - Agent progression through workflow stages
  - Team-based organization
  - Real-time status updates
  - Progress indicators

#### 📈 Market Visualization
- **Stock Charts**: Advanced candlestick charts with:
  - Price action visualization
  - Moving averages (SMA 20, SMA 50)
  - RSI technical indicator
  - Volume analysis
  - Terminal-inspired dark theme

- **Sentiment Analysis**: Market sentiment visualization with:
  - Gauge charts for sentiment scores
  - Color-coded indicators
  - Real-time updates

- **Portfolio Analytics**: Comprehensive portfolio view with:
  - Asset allocation pie charts
  - Performance metrics
  - Risk assessment
  - Return analysis

### Command Interface
The web UI supports terminal-style commands:
- `/status` - View current agent status
- `/config` - Open configuration form
- `/reset` - Reset all settings
- `/help` - Show help information

## 🎨 Design System

### Terminal-Inspired Theme
- **Color Palette**:
  - Primary: `#00ff88` (Terminal Green)
  - Secondary: `#ff6b6b` (Error Red)
  - Accent: `#4dabf7` (Info Blue)
  - Warning: `#ffd43b` (Warning Yellow)
  - Background: `#0a0a0a` (Deep Black)
  - Paper: `#1a1a1a` (Dark Grey)

- **Typography**:
  - Primary: JetBrains Mono
  - Secondary: Fira Code
  - Fallback: Monaco, Consolas, monospace

- **Visual Effects**:
  - Glowing text effects
  - Terminal-style borders
  - Smooth animations
  - Responsive design

### Component Architecture
- **Chainlit Framework**: Modern chat-based interface
- **Plotly Charts**: Interactive data visualization
- **Custom CSS**: Terminal-inspired styling
- **React Components**: Advanced trading widgets

## 🔧 Configuration

### Environment Variables
```bash
# Server configuration
CHAINLIT_HOST=0.0.0.0
CHAINLIT_PORT=8000
CHAINLIT_HEADLESS=false

# Performance settings
CHAINLIT_ENABLE_TELEMETRY=false
CHAINLIT_WATCH=false
```

### Configuration Files
- `.chainlit/config.toml` - Chainlit application settings
- `public/terminal-theme.css` - Custom terminal styling
- `components/trading_dashboard.py` - Advanced trading components

## 📊 Agent Workflow

The web interface visualizes the complete TradingAgents workflow:

1. **Analyst Team** 🔍
   - Market Analyst: Technical analysis and market trends
   - Social Analyst: Social media sentiment analysis
   - News Analyst: News impact and sentiment
   - Fundamentals Analyst: Company fundamentals and metrics

2. **Research Team** 🧠
   - Bull Researcher: Positive investment case
   - Bear Researcher: Risk factors and concerns
   - Research Manager: Final investment recommendation

3. **Trading Team** 💼
   - Trader: Trade execution planning and strategy

4. **Risk Management** ⚠️
   - Risky Analyst: Aggressive risk assessment
   - Neutral Analyst: Balanced risk evaluation
   - Safe Analyst: Conservative risk analysis

5. **Portfolio Management** 📈
   - Portfolio Manager: Final trade decision and approval

## 🛠️ Technical Architecture

### Frontend Stack
- **Chainlit**: Chat-based web interface framework
- **Plotly.js**: Interactive data visualization
- **Custom CSS**: Terminal-inspired design system
- **WebSocket**: Real-time communication

### Backend Integration
- **TradingAgents Graph**: Multi-agent orchestration
- **LangGraph**: Workflow management
- **Real-time Streaming**: Live agent updates
- **State Management**: Persistent session state

### Data Visualization
- **Financial Charts**: Candlestick, line, and bar charts
- **Technical Indicators**: RSI, moving averages, volume
- **Portfolio Analytics**: Allocation, performance, risk metrics
- **Agent Visualization**: Workflow diagrams and timelines

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Change the port
   export CHAINLIT_PORT=8001
   python start_web_ui.py
   ```

2. **Missing Dependencies**
   ```bash
   pip install chainlit plotly yfinance pandas numpy
   ```

3. **Configuration Issues**
   - Check `.chainlit/config.toml` exists
   - Verify `public/terminal-theme.css` is present
   - Ensure components directory is accessible

4. **Performance Issues**
   - Disable telemetry: `CHAINLIT_ENABLE_TELEMETRY=false`
   - Reduce chart data: Modify time periods in configuration
   - Check system resources and memory usage

### Health Check
Run the startup script for automated health checks:
```bash
python start_web_ui.py
```

The script checks:
- Python version compatibility
- Required dependencies
- Configuration files
- Port availability
- Component integrity

## 🚀 Advanced Usage

### Custom Charts
Extend the trading dashboard with custom visualizations:
```python
from components.trading_dashboard import trading_dashboard

# Create custom chart
custom_chart = await trading_dashboard.create_stock_chart("AAPL", "6mo")
await cl.Plotly(figure=custom_chart).send()
```

### Agent Status Monitoring
Monitor agent progress programmatically:
```python
from web_ui import web_state

# Check agent status
status = web_state.agent_status["Market Analyst"]
print(f"Market Analyst status: {status}")
```

### Configuration Customization
Modify analysis parameters:
```python
# Update analysis configuration
web_state.analysis_state.update({
    "ticker": "TSLA",
    "research_depth": 3,
    "llm_provider": "anthropic"
})
```

## 📈 Performance Optimization

### Best Practices
1. **Efficient Data Loading**: Use appropriate time periods for charts
2. **Memory Management**: Clear old analysis data regularly
3. **Network Optimization**: Minimize unnecessary data transfers
4. **Responsive Design**: Optimize for different screen sizes

### Monitoring
- Use browser dev tools to monitor performance
- Check network requests and data usage
- Monitor memory consumption during long analysis

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Install development dependencies
3. Make changes to web UI components
4. Test with various configurations
5. Submit pull request

### Code Style
- Follow Python PEP 8 guidelines
- Use type hints for function parameters
- Document complex functions
- Maintain terminal-inspired design consistency

## 📄 License

This web interface is part of the TradingAgents framework. See the main repository LICENSE file for details.

## 🙏 Acknowledgments

- **Tauric Research**: Core TradingAgents framework
- **Chainlit**: Modern chat-based web interface framework
- **Plotly**: Interactive data visualization library
- **Terminal Design Inspiration**: Classic terminal interfaces and modern CLI tools

---

Built with ❤️ by the TradingAgents team • [GitHub](https://github.com/TauricResearch) • Advanced AI Trading Platform