Agent-X
=======

Agent REPL



Gestor de paquetes Python
-------------------------

- UV
    - $ uv init
        - Crea proyecto
    - $ uv add <dependencia 1> <dependencia 2> ...
        - Agrega dependencia
    - $ uv sync
        - Actualiza ambiente del proyecto

- PIP
    $ pip freeze > requirements.txt
    $ pip install -r requirements.txt

LLMs
----

- Externos
    - OpenAI

- Locales
    - Ollama
        - $ ollama run <modelo>
        - $ ollama list 
            - Modelos instalados localmente

        - Modelos Locales
            - gemma3:270m
            - gemma3:1b
            - deepseek-r1:1.5b
            - qwen3:1.7b

        - Modelos Externos
            - GPT
                - gpt-3.5-turbo

Python
------

- Dependencias
    - python-dotenv
        - Gestiona variables de entorno
    - black
        - Formato

    - langchain
        - Framework LLMs

    - chromadb
        - Base de Datos de vectores 
    
    - isort
        - Formato

    - langchain
        - langchain-ollama
        - langchain-openai
        - langchain-tavily
        - langchain-pinecone
        - langchainhub
            - pypdf

    - pydantic
        - Python data validation


LangChain
---------

    Custom Tool
    -----------
    
        @tool
        def get_text_length(text: str) -> int:
            """Return the length of a text by characters"""
            return len(text)
        -> Decorardor. @tool
        -> Requiere comentario para que las LLMs decidan ocuparlas

Frontend
--------

- streamlit
    streamlit run frontend.py 