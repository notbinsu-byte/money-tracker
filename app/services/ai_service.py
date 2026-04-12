import json
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.budget import Budget

# Coalesce NULL currency to "USD"
_tx_currency = func.coalesce(Transaction.currency, "USD")

SYSTEM_PROMPT = """You are a helpful financial data analyst assistant for a personal Money Tracker application. You help users understand their spending patterns, income, budgets, and financial trends.

You have access to tools that query the user's financial database. Use them to provide accurate, data-driven answers. When analyzing data:
- Always use the tools to fetch real data before answering questions about finances
- Present numbers clearly with currency formatting
- Highlight important patterns, anomalies, or concerns
- Give actionable suggestions when appropriate
- Be concise but thorough
- If the user asks about data that doesn't exist, let them know clearly

You can help with questions like:
- "How much did I spend this month?"
- "What are my top expense categories?"
- "Am I over budget on anything?"
- "Show me my income vs expenses trend"
- "Compare my spending this month vs last month"
- "What's my average monthly spending on food?"
- "How are my savings goals?"
"""

# Tool definitions for Claude
TOOLS = [
    {
        "name": "get_monthly_totals",
        "description": "Get total income, expenses, and net for a specific month, broken down by currency. Use this to answer questions about monthly spending, income, or net savings.",
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "The year (e.g. 2026)"},
                "month": {"type": "integer", "description": "The month (1-12)"},
            },
            "required": ["year", "month"],
        },
    },
    {
        "name": "get_category_breakdown",
        "description": "Get spending or income breakdown by category for a specific month. Shows how much was spent/earned in each category. Use this to answer questions about where money goes or top spending categories.",
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "The year (e.g. 2026)"},
                "month": {"type": "integer", "description": "The month (1-12)"},
                "type": {"type": "string", "enum": ["expense", "income"], "description": "Whether to get expense or income breakdown"},
            },
            "required": ["year", "month", "type"],
        },
    },
    {
        "name": "get_budget_summary",
        "description": "Get all budget limits and how much has been spent against them for a specific month. Shows budget amount, spent amount, remaining, and percentage used. Use this to check if the user is over or under budget.",
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "The year (e.g. 2026)"},
                "month": {"type": "integer", "description": "The month (1-12)"},
            },
            "required": ["year", "month"],
        },
    },
    {
        "name": "get_recent_transactions",
        "description": "Get the most recent transactions. Use this to show recent activity or find specific transactions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Number of transactions to return (default 10, max 50)"},
            },
            "required": [],
        },
    },
    {
        "name": "get_yearly_summary",
        "description": "Get a full year summary with monthly income/expense/net trends broken down by currency. Use this for yearly overviews, trends, or comparing months within a year.",
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "The year (e.g. 2026)"},
            },
            "required": ["year"],
        },
    },
    {
        "name": "search_transactions",
        "description": "Search transactions by description, category, date range, amount range, or type. Use this to find specific transactions or filter by criteria.",
        "input_schema": {
            "type": "object",
            "properties": {
                "search": {"type": "string", "description": "Search term to match against transaction descriptions"},
                "type": {"type": "string", "enum": ["expense", "income"], "description": "Filter by transaction type"},
                "category_name": {"type": "string", "description": "Filter by category name (partial match)"},
                "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "amount_min": {"type": "number", "description": "Minimum amount"},
                "amount_max": {"type": "number", "description": "Maximum amount"},
                "limit": {"type": "integer", "description": "Max results (default 20, max 100)"},
            },
            "required": [],
        },
    },
    {
        "name": "get_spending_by_category_over_time",
        "description": "Get spending for a specific category across multiple months. Use this to track how spending in one category changes over time.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category_name": {"type": "string", "description": "The category name to track"},
                "months": {"type": "integer", "description": "Number of months to look back (default 6, max 24)"},
            },
            "required": ["category_name"],
        },
    },
    {
        "name": "get_savings_goals",
        "description": "Get all savings goals with progress. Shows goal name, target amount, current amount, percentage saved, deadline, and completion status. Use this to answer questions about savings progress or financial targets.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["active", "completed", "all"], "description": "Filter by status (default: all)"},
            },
            "required": [],
        },
    },
    {
        "name": "get_current_date",
        "description": "Get today's date. Use this to know the current date for relative queries like 'this month' or 'last month'.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, date):
            return o.isoformat()
        return super().default(o)


def _serialize(obj):
    return json.loads(json.dumps(obj, cls=DecimalEncoder))


def execute_tool(tool_name: str, tool_input: dict, db: Session):
    """Execute a tool call and return the result."""
    if tool_name == "get_monthly_totals":
        from app.services.transaction_service import get_monthly_totals
        result = get_monthly_totals(db, tool_input["year"], tool_input["month"])
        return _serialize(result)

    elif tool_name == "get_category_breakdown":
        from app.services.transaction_service import get_category_breakdown
        result = get_category_breakdown(
            db, tool_input["year"], tool_input["month"], tool_input.get("type", "expense")
        )
        return _serialize(result)

    elif tool_name == "get_budget_summary":
        from app.services.budget_service import get_budget_summary
        result = get_budget_summary(db, tool_input["year"], tool_input["month"])
        return _serialize(result)

    elif tool_name == "get_recent_transactions":
        limit = min(tool_input.get("limit", 10), 50)
        txns = (
            db.query(Transaction)
            .order_by(Transaction.date.desc(), Transaction.created_at.desc())
            .limit(limit)
            .all()
        )
        return _serialize([
            {
                "id": t.id,
                "type": t.type,
                "amount": t.amount,
                "currency": t.currency or "USD",
                "description": t.description,
                "date": t.date,
                "category": t.category.name if t.category else "Unknown",
                "category_icon": t.category.icon if t.category else "",
                "notes": t.notes,
            }
            for t in txns
        ])

    elif tool_name == "get_yearly_summary":
        from app.services.report_service import yearly_summary
        result = yearly_summary(db, tool_input["year"])
        return _serialize(result)

    elif tool_name == "search_transactions":
        query = db.query(Transaction).outerjoin(Category, Transaction.category_id == Category.id)
        if tool_input.get("search"):
            query = query.filter(Transaction.description.ilike(f"%{tool_input['search']}%"))
        if tool_input.get("type"):
            query = query.filter(Transaction.type == tool_input["type"])
        if tool_input.get("category_name"):
            query = query.filter(Category.name.ilike(f"%{tool_input['category_name']}%"))
        if tool_input.get("date_from"):
            query = query.filter(Transaction.date >= tool_input["date_from"])
        if tool_input.get("date_to"):
            query = query.filter(Transaction.date <= tool_input["date_to"])
        if tool_input.get("amount_min") is not None:
            query = query.filter(Transaction.amount >= tool_input["amount_min"])
        if tool_input.get("amount_max") is not None:
            query = query.filter(Transaction.amount <= tool_input["amount_max"])
        limit = min(tool_input.get("limit", 20), 100)
        txns = query.order_by(Transaction.date.desc()).limit(limit).all()
        return _serialize([
            {
                "id": t.id,
                "type": t.type,
                "amount": t.amount,
                "currency": t.currency or "USD",
                "description": t.description,
                "date": t.date,
                "category": t.category.name if t.category else "Unknown",
                "category_icon": t.category.icon if t.category else "",
            }
            for t in txns
        ])

    elif tool_name == "get_spending_by_category_over_time":
        from dateutil.relativedelta import relativedelta
        months_back = min(tool_input.get("months", 6), 24)
        cat_name = tool_input["category_name"]
        today = date.today()
        result = []
        for i in range(months_back - 1, -1, -1):
            d = today - relativedelta(months=i)
            total = (
                db.query(func.coalesce(func.sum(Transaction.amount), 0))
                .join(Category, Transaction.category_id == Category.id)
                .filter(Category.name.ilike(f"%{cat_name}%"))
                .filter(Transaction.type == "expense")
                .filter(extract("year", Transaction.date) == d.year)
                .filter(extract("month", Transaction.date) == d.month)
                .scalar()
            )
            result.append({
                "year": d.year,
                "month": d.month,
                "total": float(total) if total else 0.0,
            })
        return _serialize(result)

    elif tool_name == "get_savings_goals":
        from app.models.savings_goal import SavingsGoal
        query = db.query(SavingsGoal)
        status = tool_input.get("status", "all")
        if status == "active":
            query = query.filter(SavingsGoal.is_completed == False)
        elif status == "completed":
            query = query.filter(SavingsGoal.is_completed == True)
        goals = query.order_by(SavingsGoal.created_at.desc()).all()
        return _serialize([
            {
                "name": g.name,
                "target_amount": g.target_amount,
                "current_amount": g.current_amount or 0,
                "currency": g.currency or "USD",
                "percentage": round(float(g.current_amount or 0) / float(g.target_amount) * 100, 1) if g.target_amount else 0,
                "deadline": g.deadline,
                "is_completed": g.is_completed,
                "icon": g.icon,
            }
            for g in goals
        ])

    elif tool_name == "get_current_date":
        today = date.today()
        return {"date": today.isoformat(), "year": today.year, "month": today.month, "day": today.day}

    return {"error": f"Unknown tool: {tool_name}"}


def _get_anthropic_client():
    """Create Anthropic client with appropriate configuration.

    Supports:
    - Standard ANTHROPIC_API_KEY
    - Custom base URL + auth token with Bearer auth (e.g. corporate proxy)
    """
    import anthropic
    from app.config import settings

    if settings.ANTHROPIC_BASE_URL and settings.ANTHROPIC_AUTH_TOKEN:
        # Corporate proxy setup — uses Bearer token in Authorization header
        return anthropic.Anthropic(
            api_key="placeholder",
            base_url=settings.ANTHROPIC_BASE_URL,
            default_headers={
                "Authorization": f"Bearer {settings.ANTHROPIC_AUTH_TOKEN}",
            },
        )
    elif settings.ANTHROPIC_API_KEY:
        return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    else:
        return None


def _get_model():
    from app.config import settings
    model = settings.ANTHROPIC_MODEL
    # Map display names to proxy/API model IDs
    model_map = {
        "claude-4.6-opus": "claude-opus-4-6",
        "claude-4.6-sonnet": "claude-sonnet-4-6",
    }
    return model_map.get(model, model)


def chat_with_ai(message: str, conversation_history: list, db: Session) -> dict:
    """Send a message to Claude with tool access to the financial database.

    Returns {"response": str, "conversation_history": list}
    """
    from app.config import settings

    client = _get_anthropic_client()
    if not client:
        return {
            "response": "AI chat is not configured. Please set ANTHROPIC_API_KEY (or ANTHROPIC_BASE_URL + ANTHROPIC_AUTH_TOKEN) in your .env file.",
            "conversation_history": conversation_history,
        }

    model = _get_model()

    # Build messages list
    messages = list(conversation_history)
    messages.append({"role": "user", "content": message})

    # Agentic loop: keep calling Claude until we get a final text response
    max_iterations = 10
    for _ in range(max_iterations):
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Collect assistant content blocks
        assistant_content = response.content

        # Add assistant message to history
        messages.append({"role": "assistant", "content": assistant_content})

        # If the model wants to use tools, execute them
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in assistant_content:
                if block.type == "tool_use":
                    try:
                        result = execute_tool(block.name, block.input, db)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, cls=DecimalEncoder),
                        })
                    except Exception as e:
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps({"error": str(e)}),
                            "is_error": True,
                        })

            # Add tool results as user message
            messages.append({"role": "user", "content": tool_results})
        else:
            # Final response - extract text
            text_parts = [block.text for block in assistant_content if hasattr(block, "text")]
            final_text = "\n".join(text_parts) if text_parts else "I couldn't generate a response."

            # Serialize conversation history (convert content blocks to dicts)
            serialized_history = _serialize_messages(messages)

            return {
                "response": final_text,
                "conversation_history": serialized_history,
            }

    return {
        "response": "I encountered too many tool calls. Please try a simpler question.",
        "conversation_history": _serialize_messages(messages),
    }


def _serialize_messages(messages: list) -> list:
    """Convert Anthropic message objects to JSON-serializable dicts."""
    serialized = []
    for msg in messages:
        if isinstance(msg.get("content"), list):
            content = []
            for block in msg["content"]:
                if hasattr(block, "type"):
                    # Anthropic content block object
                    if block.type == "text":
                        content.append({"type": "text", "text": block.text})
                    elif block.type == "tool_use":
                        content.append({
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        })
                elif isinstance(block, dict):
                    content.append(block)
            serialized.append({"role": msg["role"], "content": content})
        else:
            serialized.append(msg)
    return serialized
