import logging
import warnings


def setup_third_party_logging(logging_level=logging.INFO):

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="SPARQLWrapper")
    logging.getLogger("SPARQLWrapper").disabled = True

    # Suppress specific loggers likely used by LangGraph / ChatLLaMA
    logging.getLogger("langgraph").setLevel(logging_level)
    logging.getLogger("httpx").setLevel(logging_level)  # if using httpx
    logging.getLogger("urllib3").setLevel(logging_level)  # if using requests
    logging.getLogger("uvicorn").setLevel(logging_level)  # sometimes used for servers

    # Optional: completely silence a specific logger
    logging.getLogger("langgraph.server").propagate = False
