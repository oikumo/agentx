# MCP Server X

## Running the Server

### Run the server in streamable-http default mode

```bash
uv run server.py
```

### Run the server in stdio mode (required for Claude)

```bash
uv run server.py stdio
```


## Test with MCP Inspector (Anthropic)

* Documentation
  - https://modelcontextprotocol.io/docs/tools/inspector

* Run
```commandline
```bash
npx @modelcontextprotocol/inspector
```

### Output

MCP Inspector output should be like as follows

```
Starting MCP inspector...
⚙️ Proxy server listening on 127.0.0.1:6277
🔑 Session token: 3bfbe238c862a189df058632deae6bcc21cea40c2df55f58ca98c7288125fd00
Use this token to authenticate requests or set DANGEROUSLY_OMIT_AUTH=true to disable auth

🔗 Open inspector with token pre-filled:
   http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=3bfbe238cd00

🔍 MCP Inspector is up and running at http://127.0.0.1:6274 🚀
```

USE GENERATED URL TO OPEN IT EASILY
```
🔗 Open inspector with token pre-filled:
 http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=3bfbe238cd00
```   

### MCP Inspector usage

* Select **Streamable HTTP** transport and connect to MCP URL (must end with /mcp for "Streamable HTTP" option):
```
Use URL from MCP Server 
Like: http://localhost:8000/mcp
```

## Claude Code connection

* Claude Code uses `stdio`

### Local Config

* In root project folder add the file .mcp.json

.mcp.json
```json
{
  "mcpServers": {
    "mcp_server_x": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/oikumo/develop/mcp_server_x",
        "run",
        "server.py",
        "stdio"        
      ]
    }
  }
}
```

### Global Config

```bash
cd mcp_server_x
claude mcp add mcp_server_x -- uv run server.py stdio
claude mcp list
claude
```

#### Verify the server is up with cURL

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

