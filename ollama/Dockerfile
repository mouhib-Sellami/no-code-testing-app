FROM ollama/ollama:latest

RUN ollama serve & \
    sleep 5 && \
    ollama pull qwen3:14b && \
    ollama pull mxbai-embed-large && \
    pkill ollama

EXPOSE 11434

CMD ["ollama", "serve"]