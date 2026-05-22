# AI Portfolio Research Copilot – Development Workflow

## Prerequisites

- **Python 3.11+**
- **Conda** or **pip**
- **Git**
- **A text editor or IDE** (VS Code, Cursor, PyCharm, etc.)

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/AI_Portfolio_Research_Copilot.git
cd AI_Portfolio_Research_Copilot
```

### 2. Set Up Conda Environment

Create a fresh environment with Python 3.11:

```bash
conda create -n ai_portfolio_research python=3.11 -y
conda activate ai_portfolio_research
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If you're adding new packages:
```bash
pip install <package_name>
pip freeze > requirements.txt
```

### 4. Verify Setup

```bash
# Check Python version
python --version

# Quick import test
python -c "import streamlit; import pandas; import yfinance; print('All imports OK')"
```

---

## Running the App

### Start the Streamlit Dashboard

```bash
streamlit run src/app.py
```

The app will open at `http://localhost:8501` in your default browser.

### Deactivate the Environment

When done:
```bash
conda deactivate
```

---

## Development Workflow

### Before Making Changes

1. **Pull the latest code:**
   ```bash
   git pull origin main
   ```

2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Activate the environment:**
   ```bash
   conda activate ai_portfolio_research
   ```

### Making Code Changes

#### Small changes (UI tweaks, bug fixes)
1. Edit the relevant file (e.g., `src/ui_sections.py`)
2. Test in the running Streamlit app (it auto-reloads)
3. Commit and push when satisfied

#### Larger changes (new module, new signal scoring)
1. Create or modify the module
2. **Test in isolation first:**
   ```bash
   python -c "from new_module import function_name; print(function_name(...))"
   ```
3. Test in the full app
4. Run a quick syntax check:
   ```bash
   python -m py_compile src/*.py
   ```

### After Changes: Commit and Push

```bash
# Stage your changes
git add src/module_name.py

# Commit with a clear message
git commit -m "Add feature: signal_engine news-aware scoring"

# Push to your branch
git push origin feature/your-feature-name

# Create a pull request on GitHub
```

---

## Working with Copilot / Codex

### Safe Copilot Usage

✅ **Good use cases:**
- Generate boilerplate code (imports, function stubs)
- Write test cases
- Explain existing code
- Suggest refactoring for clarity
- Help with documentation

❌ **Avoid:**
- Trading logic or order placement
- Financial advice generation
- Bypassing fallback error handling
- Removing safety checks

### Copilot Prompts

**Example safe prompt:**
```
# In src/signal_engine.py
# TODO: Add function to calculate RSI indicator
# Use pandas rolling windows, return 0-100 scale
# No trading signals yet, just calculation
```

**Unsafe prompt:**
```
# Create a function that places buy orders when RSI > 70
```

### Code Review Checklist Before Merging

- [ ] No `import broker_api` or similar
- [ ] No `execute_trade()` or trading execution code
- [ ] Error handling for missing data (fallbacks present)
- [ ] Function docstrings are present
- [ ] Code is student-readable (avoid over-optimization)
- [ ] README / docs updated if user-facing change
- [ ] Tests run without errors

---

## Testing Your Changes

### Manual Testing in the App

1. Start the app: `streamlit run src/app.py`
2. Navigate to the section you modified
3. Check for:
   - No red error messages
   - Data displays correctly
   - Forms submit without errors
   - Charts render without data gaps

### Unit Testing (Optional)

Test a module in isolation:

```bash
# Test signal_engine
python -c "
from src.signal_engine import generate_signal

signal = generate_signal(
    'AAPL',
    {'price': 150, 'change_pct': 2.0},
    {'return_pct': 5.0, 'volatility_pct': 15, 'max_drawdown_pct': -5}
)
print('Signal:', signal['signal'])
print('Score:', signal['score'])
"
```

---

## Common Development Tasks

### Add a New Signal Scoring Factor

1. Open `src/signal_engine.py`
2. Edit the `quant_score` or `news_score` calculation
3. Add a comment explaining the logic
4. Adjust bounds to keep score in 0–100 range
5. Test with `generate_signal()` directly
6. Commit with a clear message like: `"Update signal_engine: add volatility factor"`

### Add a New Render Function (UI Section)

1. Open `src/ui_sections.py`
2. Add function: `def render_my_section(symbol, ...):` with docstring
3. Import any dependencies at the top
4. Import and call in `src/app.py` in appropriate order
5. Test in running Streamlit app
6. Commit with: `"Add UI section: my_section"`

### Add a New Data Source

1. Open `src/market_data.py`
2. Add function with yfinance as primary, mock as fallback:
   ```python
   def get_my_data(symbol):
       try:
           # real data
       except:
           # fallback mock
           return {"source": "mock", "error": "...", "data": {...}}
   ```
3. Import and test
4. Call from relevant `render_*()` function
5. Commit with: `"Add market_data: my_data source"`

---

## Git Best Practices

### Commit Messages

Use clear, descriptive messages:

```
❌ "fix bug"
❌ "update stuff"

✅ "Fix: prediction_log CSV parsing for empty time_horizon field"
✅ "Feature: add equity curve to backtest results"
✅ "Docs: update current_architecture.md for news_engine"
```

### Branch Naming

```
feature/signal-engine-v2
bugfix/news-engine-empty-titles
docs/add-development-guide
```

### Keeping Branches Up-to-Date

```bash
# Before pushing, rebase on latest main
git fetch origin
git rebase origin/main
git push origin feature/your-feature
```

---

## Safety Rules

### The Golden Rule: Research-Only

This tool is **not** a trading bot. Every feature must pass:

1. **No trading execution:** No orders, no account changes
2. **No broker APIs:** No live account connections
3. **No financial advice:** Signals are research context, not recommendations
4. **Clear disclaimers:** All UI text says "research-only" or "learning"

### Before Committing Code

Ask yourself:
- Could this accidentally place a trade? → Don't commit
- Does this require a broker account? → Don't commit
- Does this claim to predict the future? → Reword or don't commit
- Is this research context or learning? → OK to commit

---

## Troubleshooting

### Import Errors

```bash
# If you see "ModuleNotFoundError: No module named 'xyz'"
pip install xyz
```

### Streamlit Won't Start

```bash
# Make sure you're in the repo root and environment is active
pwd  # should show .../AI_Portfolio_Research_Copilot
conda info --envs  # should show ai_portfolio_research with *

# Then try:
streamlit run src/app.py
```

### Stale Streamlit Cache

Streamlit caches function results. To clear:

```bash
# Restart the app or press R in the browser
# Or delete the cache directory:
rm -rf ~/.streamlit/cache
```

### yfinance Returns Mock Data

Check the sidebar "System Status" section. If it says `"source": "mock"`, yfinance may be rate-limited or offline. This is normal — the app gracefully falls back.

---

## Documentation

### Updating Docs

- **Architecture changes?** → Update `docs/current_architecture.md`
- **New workflow?** → Update `docs/development_workflow.md`
- **User features?** → Update `README.md`
- **Agent updates?** → Update `docs/agent_workflow.md`

Commit docs updates together with code:
```bash
git add src/my_module.py docs/current_architecture.md
git commit -m "Feature: add X; docs: update architecture"
```

---

## Getting Help

- **Syntax errors?** → Run `python -m py_compile src/<file>.py`
- **Logic issues?** → Test in isolation with simple print statements
- **Streamlit quirks?** → Check [Streamlit docs](https://docs.streamlit.io)
- **yfinance issues?** → Check [yfinance docs](https://github.com/ranaroussi/yfinance)

---

## Next Steps for Contributors

1. ✅ Clone repo, set up environment
2. ✅ Read `docs/current_architecture.md`
3. ✅ Run the app locally to understand the UI flow
4. ✅ Make a small change (e.g., tweak a signal threshold)
5. ✅ Commit and push a feature branch
6. ✅ Submit a pull request with a clear description

Happy researching! 🚀

