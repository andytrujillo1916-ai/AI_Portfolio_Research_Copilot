import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

def call_llm(prompt, task_type="general"):
    model_map = {
        "reasoning": "claude-opus-4-20250514",
        "general": "claude-sonnet-4-20250514", 
        "classify": "claude-haiku-4-5-20251001",
        "summarize": "claude-haiku-4-5-20251001",
    }
    model = model_map.get(task_type, "claude-sonnet-4-20250514")
    
    response = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text