import re

# Read template
with open('desktop/dashboard.html', 'r', encoding='utf-8') as f:
    template = f.read()

top = template.split('<div class="content-scroll">')[0] + '<div class="content-scroll">\n'
bottom = '\n    </div>\n  </div>\n</div>\n' # matching the closing tags of content-scroll, main-panel, desktop-app

def get_mobile_parts(page):
    with open(f'mobile/{page}', 'r', encoding='utf-8') as f:
        html = f.read()
    
    styles = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
    styles = styles.group(1) if styles else ""
    # remove mobile specific wrappers
    styles = re.sub(r'html,body\{.*?\}|body\{.*?\}|\.phone-wrap\{.*?\}|\.phone\{.*?\}|\.status-bar\{.*?\}|\.bottom-nav\{.*?\}|\.page-title\{.*?\}|\.back-btn\{.*?\}|\.[\w\-]*?-scroll\{.*?\}|\.[\w\-]*?-header\{.*?\}', '', styles, flags=re.DOTALL)
    
    scripts = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
    scripts = scripts.group(1) if scripts else ""
    
    return styles, scripts

def generate_page(name, title, active_nav, content_html):
    t = top.replace('class="nav-item-desk active"', 'class="nav-item-desk"')
    t = t.replace(f'href="{active_nav}" class="nav-item-desk"', f'href="{active_nav}" class="nav-item-desk active"')
    t = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', t)
    
    styles, scripts = get_mobile_parts(active_nav)
    
    # inject styles
    t = t.replace('</style>', f'{styles}\n</style>')
    
    full = t + content_html + bottom + f'<script>\n{scripts}\n</script>\n</body>\n</html>'
    with open(f'desktop/{name}', 'w', encoding='utf-8') as f:
        f.write(full)
    print(f"Generated {name}")

# 1. Twin
generate_page('twin.html', 'TwinFi AI - Living Twin', 'twin.html', '''
<div class="page-title" style="font-family:var(--font-display);font-size:24px;font-weight:700;margin-bottom:20px;">👤 Living Financial Twin</div>
<div class="main-grid" style="grid-template-columns: 1fr 350px;">
  <div>
    <div class="kpi-row" style="grid-template-columns: repeat(3, 1fr);">
      <div class="kpi-desk"><div class="kd-icon">💰</div><div class="kd-label">Current NW</div><div class="kd-value" style="color:var(--success)">₹16.2L</div></div>
      <div class="kpi-desk"><div class="kd-icon">🔮</div><div class="kd-label">Predicted NW</div><div class="kd-value" style="color:var(--cyan)">₹48.5L</div></div>
      <div class="kpi-desk"><div class="kd-icon">🎯</div><div class="kd-label">Goal Progress</div><div class="kd-value" style="color:#C77DFF">64%</div></div>
      <div class="kpi-desk"><div class="kd-icon">⚡</div><div class="kd-label">Risk Level</div><div class="kd-value" style="color:var(--warning)">Medium</div></div>
      <div class="kpi-desk"><div class="kd-icon">🏦</div><div class="kd-label">Total Assets</div><div class="kd-value" style="color:var(--success)">₹34.8L</div></div>
      <div class="kpi-desk"><div class="kd-icon">📉</div><div class="kd-label">Liabilities</div><div class="kd-value" style="color:var(--danger)">₹18.6L</div></div>
    </div>
    
    <div class="section-card" style="margin-bottom:20px;">
      <div class="sc-header"><div class="sc-title">🕐 Twin Learning Events</div></div>
      <div class="tl-item"><div class="tl-dot" style="background:rgba(0,255,157,0.15);color:var(--success)">📊</div><div class="tl-content"><div class="tl-event">SIP increased to ₹15,000</div><div class="tl-time">Today · Detected by Twin</div><div class="tl-badge" style="background:rgba(0,255,157,0.1);color:var(--success)">+Positive Signal</div></div></div>
      <div class="tl-item" style="margin-top:10px;"><div class="tl-dot" style="background:rgba(255,184,0,0.15);color:var(--warning)">⚠️</div><div class="tl-content"><div class="tl-event">Lifestyle inflation detected</div><div class="tl-time">3 days ago · Dining spend ↑42%</div><div class="tl-badge" style="background:rgba(255,184,0,0.1);color:var(--warning)">Review Suggested</div></div></div>
    </div>
  </div>
  
  <div>
    <div class="section-card" style="background:linear-gradient(135deg,rgba(0,245,255,0.05),rgba(138,43,226,0.05));text-align:center;padding:30px;">
      <div class="twin-status">
        <div class="twin-avatar-ring" style="margin:0 auto 10px;width:80px;height:80px;">
          <svg viewBox="0 0 60 60" fill="none"><circle cx="30" cy="30" r="26" stroke="url(#tg)" stroke-width="1.5" stroke-dasharray="6 4"/><defs><linearGradient id="tg" x1="0" y1="0" x2="60" y2="60" gradientUnits="userSpaceOnUse"><stop stop-color="#00F5FF"/><stop offset="1" stop-color="#8A2BE2"/></linearGradient></defs></svg>
          <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:30px;">🧬</div>
        </div>
        <div class="twin-name" style="font-weight:700;font-size:18px;">Arjun's Financial Twin</div>
        <div style="font-size:12px;color:var(--text-secondary);margin-bottom:12px;">Learned from 847 financial events</div>
        <div style="color:var(--cyan);font-weight:700;font-size:12px;">87% confidence</div>
      </div>
      <div style="position:relative;height:300px;margin-top:20px;">
        <canvas id="twinCanvas" width="250" height="300"></canvas>
      </div>
    </div>
  </div>
</div>
''')

# 2. Network
generate_page('network.html', 'TwinFi AI - Twin Network', 'network.html', '''
<div class="page-title" style="font-family:var(--font-display);font-size:24px;font-weight:700;margin-bottom:20px;">🕸️ Financial Twin Network</div>
<div class="main-grid" style="grid-template-columns: 1fr 350px;">
  <div class="section-card">
    <div class="network-canvas-wrap" style="height:500px;">
      <canvas id="networkCanvas" width="600" height="500"></canvas>
    </div>
    <div class="node-legend" style="margin-top:20px;border:none;">
      <div class="legend-item"><div class="legend-dot" style="background:#00F5FF"></div>You</div>
      <div class="legend-item"><div class="legend-dot" style="background:#00FF9D"></div>Family</div>
      <div class="legend-item"><div class="legend-dot" style="background:#8A2BE2"></div>Investments</div>
      <div class="legend-item"><div class="legend-dot" style="background:#FF4D6D"></div>Loans</div>
      <div class="legend-item"><div class="legend-dot" style="background:#FFB800"></div>Business</div>
    </div>
  </div>
  
  <div>
    <div class="node-detail animate-fade-in" id="nodeDetail" style="margin:0 0 20px 0;">
      <div class="nd-header">
        <div class="nd-avatar" id="nodeIcon">👤</div>
        <div>
          <div class="nd-name" id="nodeName">Select a node</div>
          <div class="nd-role" id="nodeRole">...</div>
        </div>
      </div>
      <div class="nd-metrics">
        <div class="ndm"><div class="ndm-val" style="color:var(--cyan)" id="nm1">-</div><div class="ndm-lbl">Assets</div></div>
        <div class="ndm"><div class="ndm-val" style="color:var(--success)" id="nm2">-</div><div class="ndm-lbl">Credit</div></div>
        <div class="ndm"><div class="ndm-val" style="color:var(--warning)" id="nm3">-</div><div class="ndm-lbl">Risk Level</div></div>
      </div>
    </div>
    
    <div class="section-card">
      <div class="rel-title">All Financial Connections</div>
      <div class="rel-item" onclick="selectNode('Priya','💑','Spouse – Joint Account','₹8.2L','742','Medium')">
        <div class="rel-icon" style="background:rgba(0,255,157,0.12)">💑</div>
        <div><div class="rel-name">Priya Mehta</div><div class="rel-type">Spouse · Joint Account</div></div>
        <div class="rel-amount" style="color:var(--success)">₹8.2L</div>
      </div>
      <div class="rel-item" onclick="selectNode('Ramesh (Father)','👴','Parent – Dependent','₹2.1L','680','Low')">
        <div class="rel-icon" style="background:rgba(0,245,255,0.1)">👴</div>
        <div><div class="rel-name">Ramesh Mehta</div><div class="rel-type">Father · Dependent</div></div>
        <div class="rel-amount" style="color:var(--cyan)">₹2.1L</div>
      </div>
      <div class="rel-item" onclick="selectNode('Axis Bank Loan','🏦','Home Loan – Active','₹14.5L','—','High')">
        <div class="rel-icon" style="background:rgba(255,77,109,0.1)">🏦</div>
        <div><div class="rel-name">Axis Bank</div><div class="rel-type">Home Loan · Active</div></div>
        <div class="rel-amount" style="color:var(--danger)">₹14.5L</div>
      </div>
    </div>
  </div>
</div>
''')

# 3. Economy
generate_page('economy.html', 'TwinFi AI - Economy Sim', 'economy.html', '''
<div class="page-title" style="font-family:var(--font-display);font-size:24px;font-weight:700;margin-bottom:20px;">🌐 Economy Simulator</div>
<div class="impact-summary animate-fade-in" style="grid-template-columns: repeat(4, 1fr); margin:0 0 20px 0;">
  <div class="impact-card" style="border-color:rgba(255,77,109,0.3)">
    <div class="ic-icon">💰</div><div class="ic-label">Savings Impact</div>
    <div class="ic-value" style="color:var(--danger)" id="savingsImpact">-₹12K</div>
    <div class="ic-change" style="color:var(--danger)">↓ 2.8% decrease</div>
  </div>
  <div class="impact-card" style="border-color:rgba(255,184,0,0.3)">
    <div class="ic-icon">🏠</div><div class="ic-label">EMI Change</div>
    <div class="ic-value" style="color:var(--warning)" id="emiImpact">+₹2.1K</div>
    <div class="ic-change" style="color:var(--warning)">↑ Rate hike effect</div>
  </div>
  <div class="impact-card" style="border-color:rgba(0,245,255,0.3)">
    <div class="ic-icon">📈</div><div class="ic-label">Investment</div>
    <div class="ic-value" style="color:var(--success)" id="investImpact">+₹8.4K</div>
    <div class="ic-change" style="color:var(--success)">↑ Market up</div>
  </div>
  <div class="impact-card" style="border-color:rgba(138,43,226,0.3)">
    <div class="ic-icon">⭐</div><div class="ic-label">Credit Score</div>
    <div class="ic-value" style="color:#C77DFF" id="creditImpact">782</div>
    <div class="ic-change" style="color:var(--success)">→ No change</div>
  </div>
</div>

<div class="main-grid" style="grid-template-columns: 1fr 400px;">
  <div class="impact-chart-card" style="margin:0;">
    <div class="ic-chart-title"><span>Twin State Impact Trajectory</span><span class="live-badge">● LIVE SIM</span></div>
    <div class="ic-chart-wrap" style="height:350px;">
      <canvas id="impactChart"></canvas>
    </div>
  </div>
  
  <div>
    <div class="sliders-section section-card" style="margin-bottom:20px;padding:20px;">
      <div class="sliders-title">⚙️ Adjust Economy Variables</div>
      <div class="slider-group">
        <div class="slider-row"><div class="slider-label">📊 Inflation Rate</div><div class="slider-value" id="inflVal">5.2%</div></div>
        <input type="range" class="range-slider" id="inflation" min="2" max="15" value="5.2" step="0.1" oninput="updateEconomy()"/>
      </div>
      <div class="slider-group">
        <div class="slider-row"><div class="slider-label">🏛️ Repo Rate</div><div class="slider-value" id="repoVal">6.5%</div></div>
        <input type="range" class="range-slider" id="repo" min="4" max="10" value="6.5" step="0.25" oninput="updateEconomy()"/>
      </div>
      <div class="slider-group">
        <div class="slider-row"><div class="slider-label">🥇 Gold Price / 10g</div><div class="slider-value" id="goldVal">₹72K</div></div>
        <input type="range" class="range-slider" id="gold" min="50000" max="120000" value="72000" step="1000" oninput="updateEconomy()"/>
      </div>
      <div class="slider-group">
        <div class="slider-row"><div class="slider-label">📉 Stock Market Return</div><div class="slider-value" id="marketVal">12%</div></div>
        <input type="range" class="range-slider" id="market" min="-30" max="40" value="12" step="1" oninput="updateEconomy()"/>
      </div>
    </div>
    
    <div class="ai-analysis" style="margin:0;">
      <div class="aa-title">🧠 AI Twin Analysis</div>
      <div class="aa-item"><div class="aa-icon">🛡️</div><div class="aa-text"><strong>High Resilience:</strong> Your 6-month emergency fund completely buffers you against mild recessions.</div></div>
      <div class="aa-item"><div class="aa-icon">⚠️</div><div class="aa-text"><strong>Rate Sensitivity:</strong> Home loan EMI is your biggest risk if RBI hikes rates above 8%.</div></div>
    </div>
  </div>
</div>
''')

# 4. Investments
generate_page('investments.html', 'TwinFi AI - Investments', 'investments.html', '''
<div class="page-title" style="font-family:var(--font-display);font-size:24px;font-weight:700;margin-bottom:20px;">📊 AI Investment Portfolio</div>
<div class="main-grid" style="grid-template-columns: 1fr 400px;">
  <div>
    <div class="section-card" style="margin-bottom:20px;">
      <div class="pf-header" style="display:flex;justify-content:space-between;margin-bottom:20px;">
        <div>
          <div style="font-size:12px;color:var(--text-secondary);">Total Portfolio Value</div>
          <div style="font-family:var(--font-display);font-size:32px;font-weight:700;">₹12.4L</div>
          <div style="color:var(--success);font-size:14px;font-weight:600;">+₹1.8L (17.2%) All Time</div>
        </div>
        <div class="ai-badge" style="background:var(--gradient-main);color:#000;padding:6px 12px;border-radius:20px;font-weight:700;font-size:12px;align-self:flex-start;">🤖 Optimal Allocation</div>
      </div>
      <div style="height:300px;position:relative;">
        <canvas id="portfolioChart"></canvas>
      </div>
    </div>
    
    <div class="section-card">
      <div style="font-size:16px;font-weight:700;margin-bottom:16px;">AI Rebalancing Suggestions</div>
      <div style="display:flex;gap:12px;align-items:flex-start;padding:12px;background:rgba(255,184,0,0.1);border:1px solid rgba(255,184,0,0.3);border-radius:12px;">
        <div style="font-size:20px;">⚖️</div>
        <div>
          <div style="font-weight:700;font-size:14px;">Equity Overweight Detected</div>
          <div style="font-size:12px;color:var(--text-secondary);margin-top:4px;">Nifty run-up has pushed equity allocation to 72% (Target: 60%). Shift ₹1.2L to Debt/Gold to maintain risk profile.</div>
        </div>
        <button style="padding:6px 16px;background:var(--warning);border:none;border-radius:20px;color:#000;font-weight:700;font-size:12px;cursor:pointer;">Rebalance</button>
      </div>
    </div>
  </div>
  
  <div>
    <div class="section-card" style="margin-bottom:20px;">
      <div style="font-weight:700;font-size:16px;margin-bottom:16px;">Holdings</div>
      <div class="asset-item" style="display:flex;justify-content:space-between;margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.05);">
        <div><div style="font-weight:700;font-size:14px;">Parag Parikh Flexi</div><div style="font-size:11px;color:var(--text-secondary);">Equity MF</div></div>
        <div style="text-align:right;"><div style="font-family:var(--font-mono);font-weight:700;">₹4.8L</div><div style="color:var(--success);font-size:11px;">+28.4%</div></div>
      </div>
      <div class="asset-item" style="display:flex;justify-content:space-between;margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.05);">
        <div><div style="font-weight:700;font-size:14px;">HDFC Index</div><div style="font-size:11px;color:var(--text-secondary);">Large Cap</div></div>
        <div style="text-align:right;"><div style="font-family:var(--font-mono);font-weight:700;">₹2.4L</div><div style="color:var(--success);font-size:11px;">+18.2%</div></div>
      </div>
      <div class="asset-item" style="display:flex;justify-content:space-between;margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.05);">
        <div><div style="font-weight:700;font-size:14px;">SGB 2026</div><div style="font-size:11px;color:var(--text-secondary);">Gold</div></div>
        <div style="text-align:right;"><div style="font-family:var(--font-mono);font-weight:700;">₹1.5L</div><div style="color:var(--success);font-size:11px;">+14.8%</div></div>
      </div>
      <div class="asset-item" style="display:flex;justify-content:space-between;margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.05);">
        <div><div style="font-weight:700;font-size:14px;">SBI FD</div><div style="font-size:11px;color:var(--text-secondary);">Debt</div></div>
        <div style="text-align:right;"><div style="font-family:var(--font-mono);font-weight:700;">₹3.2L</div><div style="color:var(--success);font-size:11px;">+6.5%</div></div>
      </div>
    </div>
  </div>
</div>
''')

# 5. Fraud
generate_page('fraud.html', 'TwinFi AI - Fraud Intel', 'fraud.html', '''
<div class="page-title" style="font-family:var(--font-display);font-size:24px;font-weight:700;margin-bottom:20px;">🛡️ Fraud Intelligence</div>
<div class="main-grid" style="grid-template-columns: 1fr 350px;">
  <div>
    <div class="risk-radar animate-fade-in" style="margin:0 0 20px 0;">
      <div class="radar-score">
        <canvas id="scoreGauge" width="100" height="100"></canvas>
        <div class="rs-label">Risk Score</div>
        <div class="rs-sublabel">✅ LOW RISK</div>
      </div>
      <div class="radar-info" style="margin-left:20px;">
        <div class="ri-title" style="font-size:20px;">Account Shield: Active</div>
        <div class="ri-desc">AI monitoring 24/7. 1 suspicious activity detected this month.</div>
        <div class="risk-bars">
          <div class="rb-item"><div class="rb-label">Identity</div><div class="rb-bar"><div class="rb-fill" style="width:12%;background:var(--success)"></div></div></div>
          <div class="rb-item"><div class="rb-label">Transaction</div><div class="rb-bar"><div class="rb-fill" style="width:28%;background:var(--warning)"></div></div></div>
          <div class="rb-item"><div class="rb-label">Account</div><div class="rb-bar"><div class="rb-fill" style="width:8%;background:var(--success)"></div></div></div>
        </div>
      </div>
    </div>
    
    <div class="suspicious-list animate-fade-in delay-300" style="padding:0;">
      <div class="sl-title">⚠️ Flagged Transactions</div>
      <div class="suspicious-item si-medium">
        <div class="si-icon" style="background:rgba(255,184,0,0.12)">🌍</div>
        <div class="si-info">
          <div class="si-title">International Transfer — Dubai</div>
          <div class="si-desc">Unusual location. Never transacted in Dubai before. Jul 8, 2026 · 2:14 AM</div>
          <div class="si-meta">
            <span class="si-badge si-risk-med">Medium Risk</span>
            <span class="si-badge" style="background:rgba(255,255,255,0.06);color:var(--text-secondary)">New Location</span>
          </div>
        </div>
        <div class="si-amount" style="color:var(--warning)">₹4,200</div>
      </div>
      <div class="suspicious-item si-low">
        <div class="si-icon" style="background:rgba(0,245,255,0.08)">🛒</div>
        <div class="si-info">
          <div class="si-title">Multiple Merchant — Same Card</div>
          <div class="si-desc">4 online transactions within 6 minutes. Possible card cloning check. Jul 7, 2026</div>
          <div class="si-meta">
            <span class="si-badge si-risk-low">Low Risk</span>
            <span class="si-badge" style="background:rgba(255,255,255,0.06);color:var(--text-secondary)">Pattern Alert</span>
          </div>
        </div>
        <div class="si-amount" style="color:var(--cyan)">₹1,840</div>
      </div>
    </div>
  </div>
  
  <div>
    <div class="radar-canvas-card animate-fade-in delay-200" style="margin:0 0 20px 0;">
      <div class="rcc-title"><span>🎯 Live Threat Radar</span><span class="live-badge">● LIVE</span></div>
      <canvas id="radarCanvas" width="300" height="200" style="width:100%"></canvas>
    </div>
    
    <div class="map-card animate-fade-in delay-400" style="margin:0;">
      <div class="mc-title">📍 Location Map</div>
      <div class="map-visual" style="height:200px;">
        <div class="map-dot map-you" style="left:50%;top:50%;"></div>
        <div class="map-dot map-suspicious" style="left:70%;top:30%;"></div>
      </div>
    </div>
  </div>
</div>
''')
