from tool_registry import register_tool

@register_tool()
def get_user_location() -> str:
    """Get the user's location. Returns the city name if available, otherwise returns the country name."""
    return "New York"
@register_tool()
def get_city_weather(city: str) -> str:
    """Get the weather for a specific city."""
    return "25 degrees Celsius"

