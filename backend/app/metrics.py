from prometheus_client import Counter, Histogram


HTTP_REQUESTS = Counter(
    "gitagpt_http_requests_total", "HTTP requests", ["method", "path", "status"]
)
HTTP_LATENCY = Histogram(
    "gitagpt_http_request_duration_seconds", "HTTP request latency", ["method", "path"]
)
MODEL_REQUESTS = Counter(
    "gitagpt_model_requests_total", "Model generation attempts", ["provider", "outcome"]
)
RETRIEVAL_LATENCY = Histogram(
    "gitagpt_retrieval_duration_seconds", "Retrieval latency"
)
