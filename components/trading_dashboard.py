"""
Advanced Trading Dashboard Components
Custom Chainlit components for sophisticated trading interface
"""

import chainlit as cl
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import yfinance as yf

class TradingDashboard:
    """Advanced trading dashboard with real-time charts and analytics."""
    
    def __init__(self):
        self.theme_colors = {
            'primary': '#00ff88',
            'secondary': '#ff6b6b', 
            'accent': '#4dabf7',
            'warning': '#ffd43b',
            'success': '#51cf66',
            'bg': '#0a0a0a',
            'paper': '#1a1a1a',
            'text': '#ffffff'
        }
    
    async def create_stock_chart(self, ticker: str, period: str = "1mo") -> go.Figure:
        """Create an advanced stock price chart with technical indicators."""
        
        try:
            # Fetch stock data
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                return self._create_error_chart(f"No data available for {ticker}")
            
            # Create subplots
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=(
                    f'{ticker} Stock Price & Volume',
                    'Technical Indicators', 
                    'Volume Analysis'
                ),
                row_heights=[0.6, 0.2, 0.2]
            )
            
            # Main price chart with candlesticks
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='Price',
                    increasing_line_color=self.theme_colors['success'],
                    decreasing_line_color=self.theme_colors['secondary']
                ),
                row=1, col=1
            )
            
            # Add moving averages
            if len(df) >= 20:
                df['SMA_20'] = df['Close'].rolling(window=20).mean()
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['SMA_20'],
                        name='SMA 20',
                        line=dict(color=self.theme_colors['accent'], width=2),
                        opacity=0.8
                    ),
                    row=1, col=1
                )
            
            if len(df) >= 50:
                df['SMA_50'] = df['Close'].rolling(window=50).mean()
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['SMA_50'],
                        name='SMA 50',
                        line=dict(color=self.theme_colors['warning'], width=2),
                        opacity=0.8
                    ),
                    row=1, col=1
                )
            
            # RSI indicator
            rsi = self._calculate_rsi(df['Close'])
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=rsi,
                    name='RSI',
                    line=dict(color=self.theme_colors['primary'], width=2),
                    yaxis='y2'
                ),
                row=2, col=1
            )
            
            # Add RSI overbought/oversold lines
            fig.add_hline(y=70, line_dash="dash", line_color=self.theme_colors['secondary'], row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color=self.theme_colors['success'], row=2, col=1)
            
            # Volume chart
            colors = ['green' if close >= open else 'red' for close, open in zip(df['Close'], df['Open'])]
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df['Volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.7
                ),
                row=3, col=1
            )
            
            # Update layout with terminal theme
            fig.update_layout(
                title=f"{ticker} Advanced Trading Chart",
                template="plotly_dark",
                height=800,
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="JetBrains Mono, monospace", color=self.theme_colors['text']),
                title_font=dict(size=24, color=self.theme_colors['primary'])
            )
            
            # Update axes
            fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
            fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
            
            # Update RSI y-axis
            fig.update_yaxes(range=[0, 100], row=2, col=1)
            
            return fig
            
        except Exception as e:
            return self._create_error_chart(f"Error loading data for {ticker}: {str(e)}")
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _create_error_chart(self, error_message: str) -> go.Figure:
        """Create an error chart when data is unavailable."""
        fig = go.Figure()
        fig.add_annotation(
            text=error_message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color=self.theme_colors['secondary'])
        )
        fig.update_layout(
            template="plotly_dark",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="JetBrains Mono, monospace"),
            title="Chart Error"
        )
        return fig
    
    async def create_sentiment_gauge(self, sentiment_score: float) -> go.Figure:
        """Create a sentiment analysis gauge chart."""
        
        # Normalize sentiment score to 0-100 scale
        normalized_score = (sentiment_score + 1) * 50  # Assuming sentiment is between -1 and 1
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = normalized_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Market Sentiment", 'font': {'color': self.theme_colors['text']}},
            delta = {'reference': 50, 'increasing': {'color': self.theme_colors['success']}, 'decreasing': {'color': self.theme_colors['secondary']}},
            gauge = {
                'axis': {'range': [None, 100], 'tickcolor': self.theme_colors['text']},
                'bar': {'color': self.theme_colors['primary']},
                'steps': [
                    {'range': [0, 25], 'color': self.theme_colors['secondary']},
                    {'range': [25, 50], 'color': self.theme_colors['warning']},
                    {'range': [50, 75], 'color': self.theme_colors['accent']},
                    {'range': [75, 100], 'color': self.theme_colors['success']}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            template="plotly_dark",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="JetBrains Mono, monospace", color=self.theme_colors['text'])
        )
        
        return fig
    
    async def create_portfolio_performance(self, portfolio_data: Dict[str, Any]) -> go.Figure:
        """Create portfolio performance visualization."""
        
        # Sample portfolio data structure
        if not portfolio_data:
            portfolio_data = {
                'positions': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'],
                'values': [25000, 20000, 18000, 15000, 12000],
                'returns': [5.2, -2.1, 8.7, -1.5, 12.3],
                'weights': [27.8, 22.2, 20.0, 16.7, 13.3]
            }
        
        # Create subplots for portfolio visualization
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Portfolio Allocation', 'Position Returns', 'Value Distribution', 'Performance Metrics'),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "table"}]]
        )
        
        # Portfolio allocation pie chart
        fig.add_trace(
            go.Pie(
                labels=portfolio_data['positions'],
                values=portfolio_data['weights'],
                name="Allocation",
                marker_colors=[self.theme_colors['primary'], self.theme_colors['accent'], 
                              self.theme_colors['success'], self.theme_colors['warning'], 
                              self.theme_colors['secondary']]
            ),
            row=1, col=1
        )
        
        # Returns bar chart
        colors = [self.theme_colors['success'] if r > 0 else self.theme_colors['secondary'] 
                 for r in portfolio_data['returns']]
        fig.add_trace(
            go.Bar(
                x=portfolio_data['positions'],
                y=portfolio_data['returns'],
                name="Returns (%)",
                marker_color=colors
            ),
            row=1, col=2
        )
        
        # Value distribution
        fig.add_trace(
            go.Bar(
                x=portfolio_data['positions'],
                y=portfolio_data['values'],
                name="Value ($)",
                marker_color=self.theme_colors['accent']
            ),
            row=2, col=1
        )
        
        # Performance metrics table
        metrics_data = [
            ['Total Value', f"${sum(portfolio_data['values']):,.0f}"],
            ['Total Return', f"{np.mean(portfolio_data['returns']):.2f}%"],
            ['Best Performer', f"{portfolio_data['positions'][np.argmax(portfolio_data['returns'])]}"],
            ['Worst Performer', f"{portfolio_data['positions'][np.argmin(portfolio_data['returns'])]}"]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Metric', 'Value'],
                           fill_color=self.theme_colors['primary'],
                           font=dict(color='black', size=12)),
                cells=dict(values=list(zip(*metrics_data)),
                          fill_color=self.theme_colors['paper'],
                          font=dict(color=self.theme_colors['text'], size=11))
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title="Portfolio Performance Dashboard",
            template="plotly_dark",
            height=600,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="JetBrains Mono, monospace", color=self.theme_colors['text']),
            title_font=dict(size=20, color=self.theme_colors['primary'])
        )
        
        return fig
    
    async def create_risk_metrics_chart(self, risk_data: Dict[str, float]) -> go.Figure:
        """Create risk metrics visualization."""
        
        if not risk_data:
            risk_data = {
                'VaR_95': -0.05,
                'VaR_99': -0.08,
                'Expected_Shortfall': -0.12,
                'Sharpe_Ratio': 1.2,
                'Beta': 1.05,
                'Max_Drawdown': -0.15,
                'Volatility': 0.18
            }
        
        # Create radar chart for risk metrics
        categories = list(risk_data.keys())
        values = list(risk_data.values())
        
        # Normalize values for radar chart (0-100 scale)
        normalized_values = []
        for cat, val in zip(categories, values):
            if 'VaR' in cat or 'Drawdown' in cat:
                # For negative risk metrics, invert and scale
                normalized_values.append(max(0, (1 + val) * 100))
            elif 'Sharpe' in cat:
                # Scale Sharpe ratio (typical range 0-3)
                normalized_values.append(min(100, val * 33.33))
            elif 'Beta' in cat:
                # Scale Beta (typical range 0.5-1.5)
                normalized_values.append(min(100, (val - 0.5) * 100))
            else:
                # Scale volatility and other metrics
                normalized_values.append(min(100, val * 100))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=normalized_values,
            theta=categories,
            fill='toself',
            fillcolor=f'rgba(0, 255, 136, 0.2)',
            line=dict(color=self.theme_colors['primary'], width=3),
            marker=dict(color=self.theme_colors['primary'], size=8),
            name='Risk Profile'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(color=self.theme_colors['text']),
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                angularaxis=dict(
                    tickfont=dict(color=self.theme_colors['text'], size=12),
                    gridcolor='rgba(255,255,255,0.1)'
                )
            ),
            title="Risk Metrics Profile",
            template="plotly_dark",
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="JetBrains Mono, monospace", color=self.theme_colors['text']),
            title_font=dict(size=18, color=self.theme_colors['primary'])
        )
        
        return fig

class AgentOrchestrationVisualization:
    """Visualization for multi-agent workflow orchestration."""
    
    def __init__(self):
        self.agent_colors = {
            'Market Analyst': '#4dabf7',
            'Social Analyst': '#22d3ee', 
            'News Analyst': '#ffd43b',
            'Fundamentals Analyst': '#da77f2',
            'Bull Researcher': '#51cf66',
            'Bear Researcher': '#ff6b6b',
            'Research Manager': '#00ff88',
            'Trader': '#ff922b',
            'Risky Analyst': '#ff6b6b',
            'Neutral Analyst': '#868e96',
            'Safe Analyst': '#51cf66',
            'Portfolio Manager': '#00ff88'
        }
    
    async def create_workflow_diagram(self, agent_statuses: Dict[str, str]) -> go.Figure:
        """Create a visual workflow diagram showing agent progress."""
        
        # Define workflow stages and positions
        workflow_layout = {
            'Analyst Team': {
                'agents': ['Market Analyst', 'Social Analyst', 'News Analyst', 'Fundamentals Analyst'],
                'position': (1, 4)
            },
            'Research Team': {
                'agents': ['Bull Researcher', 'Bear Researcher', 'Research Manager'],
                'position': (2, 3)
            },
            'Trading Team': {
                'agents': ['Trader'],
                'position': (3, 1)
            },
            'Risk Management': {
                'agents': ['Risky Analyst', 'Neutral Analyst', 'Safe Analyst'],
                'position': (4, 3)
            },
            'Portfolio Management': {
                'agents': ['Portfolio Manager'],
                'position': (5, 1)
            }
        }
        
        fig = go.Figure()
        
        # Add nodes for each agent
        for team, info in workflow_layout.items():
            stage, num_agents = info['position']
            agents = info['agents']
            
            for i, agent in enumerate(agents):
                status = agent_statuses.get(agent, 'pending')
                color = self.agent_colors.get(agent, '#868e96')
                
                # Determine node style based on status
                if status == 'completed':
                    marker_symbol = 'circle'
                    marker_size = 30
                    opacity = 1.0
                elif status == 'in_progress':
                    marker_symbol = 'circle-open'
                    marker_size = 35
                    opacity = 0.8
                else:  # pending
                    marker_symbol = 'circle-dot'
                    marker_size = 25
                    opacity = 0.5
                
                # Position agents vertically within their stage
                y_offset = (i - (num_agents - 1) / 2) * 0.5
                
                fig.add_trace(go.Scatter(
                    x=[stage],
                    y=[y_offset],
                    mode='markers+text',
                    marker=dict(
                        symbol=marker_symbol,
                        size=marker_size,
                        color=color,
                        opacity=opacity,
                        line=dict(width=3, color='white')
                    ),
                    text=[agent.replace(' ', '<br>')],
                    textposition='bottom center',
                    textfont=dict(size=10, color='white'),
                    name=agent,
                    hovertemplate=f"<b>{agent}</b><br>Status: {status}<extra></extra>"
                ))
        
        # Add workflow arrows
        arrow_positions = [(1, 2), (2, 3), (3, 4), (4, 5)]
        for start, end in arrow_positions:
            fig.add_annotation(
                x=end, y=0,
                ax=start, ay=0,
                xref='x', yref='y',
                axref='x', ayref='y',
                arrowhead=3,
                arrowsize=2,
                arrowwidth=3,
                arrowcolor='#00ff88',
                opacity=0.7
            )
        
        # Add team labels
        team_names = list(workflow_layout.keys())
        for i, team in enumerate(team_names, 1):
            fig.add_annotation(
                x=i, y=2,
                text=f"<b>{team}</b>",
                showarrow=False,
                font=dict(size=14, color='#00ff88'),
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor='#00ff88',
                borderwidth=1
            )
        
        fig.update_layout(
            title="Multi-Agent Workflow Orchestration",
            template="plotly_dark",
            height=600,
            width=1000,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="JetBrains Mono, monospace", color='white'),
            title_font=dict(size=20, color='#00ff88'),
            xaxis=dict(
                title="Workflow Stage",
                range=[0.5, 5.5],
                tickvals=[1, 2, 3, 4, 5],
                ticktext=['Analysis', 'Research', 'Trading', 'Risk', 'Portfolio'],
                showgrid=False,
                zeroline=False
            ),
            yaxis=dict(
                title="",
                range=[-2.5, 2.5],
                showgrid=False,
                zeroline=False,
                showticklabels=False
            )
        )
        
        return fig
    
    async def create_agent_timeline(self, agent_history: List[Dict]) -> go.Figure:
        """Create a timeline visualization of agent activities."""
        
        if not agent_history:
            # Sample data for demonstration
            agent_history = [
                {'agent': 'Market Analyst', 'start_time': '09:00:00', 'end_time': '09:05:23', 'status': 'completed'},
                {'agent': 'Social Analyst', 'start_time': '09:05:30', 'end_time': '09:08:45', 'status': 'completed'},
                {'agent': 'News Analyst', 'start_time': '09:09:00', 'end_time': '09:12:10', 'status': 'completed'},
                {'agent': 'Bull Researcher', 'start_time': '09:12:15', 'end_time': '09:15:30', 'status': 'in_progress'},
                {'agent': 'Bear Researcher', 'start_time': '09:15:35', 'end_time': '', 'status': 'pending'}
            ]
        
        fig = go.Figure()
        
        for i, activity in enumerate(agent_history):
            agent = activity['agent']
            color = self.agent_colors.get(agent, '#868e96')
            
            # Convert time strings to datetime for plotting
            start = datetime.strptime(activity['start_time'], '%H:%M:%S') if activity['start_time'] else datetime.now()
            end = datetime.strptime(activity['end_time'], '%H:%M:%S') if activity['end_time'] else datetime.now()
            
            if activity['status'] == 'pending':
                continue
            
            fig.add_trace(go.Scatter(
                x=[start, end],
                y=[i, i],
                mode='lines+markers',
                line=dict(color=color, width=8),
                marker=dict(size=10, color=color),
                name=agent,
                hovertemplate=f"<b>{agent}</b><br>Duration: {activity['start_time']} - {activity['end_time']}<extra></extra>"
            ))
            
            # Add agent label
            fig.add_annotation(
                x=start,
                y=i,
                text=agent,
                showarrow=False,
                xanchor='right',
                font=dict(size=12, color='white'),
                xshift=-10
            )
        
        fig.update_layout(
            title="Agent Execution Timeline",
            template="plotly_dark",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="JetBrains Mono, monospace", color='white'),
            title_font=dict(size=18, color='#00ff88'),
            xaxis=dict(
                title="Time",
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)'
            ),
            yaxis=dict(
                title="Agents",
                showgrid=False,
                showticklabels=False
            ),
            showlegend=False
        )
        
        return fig

# Create global instances
trading_dashboard = TradingDashboard()
agent_viz = AgentOrchestrationVisualization()