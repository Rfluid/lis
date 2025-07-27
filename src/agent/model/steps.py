from enum import Enum


class Steps(Enum):
    context_incrementer = "context_incrementer"

    context_builder = (
        "context_builder"  # Builds the context for the given chat interface.
    )

    evaluate_tools = "evaluate_tools"  # Decides if will search the calendar, search other sources or just generate the response and send back.

    search_calendars = (
        "search_calendars"  # Search the calendar for the requested information.
    )
    get_current_date = (
        "get_current_date"  # Get the current date to search the calendar.
    )
    rag = "rag"  # Enhances the response by searching other sources.
    generate_response = (
        "generate_response"  # Generates response for the given chat interface.
    )

    # Actions after response generation
    modify_calendar = "modify_calendar"

    error_handler = "error_handler"  # Handles errors that may occur during the process.

    end = "end"  # We have this item only to be able to use on conditional edges.
