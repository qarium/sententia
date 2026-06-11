# Running the Application

SententiaApp is a domain-agnostic container. The root cell (main) handles component composition.
Operating modes are mutually exclusive: either REST resources via FastAPI, or MCP tools via MCP Server.

## Registering REST Resources

Each resource exposes a `url_rule` through its property.
Register a resource by passing it to `add_rest_resource`:

  app = SententiaApp()
  app.add_rest_resource(resource)

## Registering MCP Tools

Register a tool by passing it to `add_mcp_tool`:

  app = SententiaApp()
  app.add_mcp_tool(tool)

## Starting the Server

The server mode depends on the registered handlers:
- tools → MCP Server (Streamable HTTP transport)
- resources → FastAPI (uvicorn)

  app.run(host="0.0.0.0", port=8000)
