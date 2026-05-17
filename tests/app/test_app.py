from __future__ import annotations

import inspect
from unittest.mock import MagicMock, patch

import pytest
from sententia.app.app import SententiaApp
from sententia.endpoints import MCPTool, RESTResource


class TestSententiaAppContract:
    """Contract tests for SententiaApp."""

    def test_importable_from_facade(self):
        """SententiaApp must be importable from sententia.app."""
        assert callable(SententiaApp)

    def test_has_add_rest_resource_method(self):
        """SententiaApp must have add_rest_resource(resource) method."""
        assert hasattr(SententiaApp, "add_rest_resource")

    def test_has_add_mcp_tool_method(self):
        """SententiaApp must have add_mcp_tool(tool) method."""
        assert hasattr(SententiaApp, "add_mcp_tool")

    def test_has_run_method(self):
        """SententiaApp must have run(host, port) method."""
        assert hasattr(SententiaApp, "run")

    def test_constructor_no_params(self):
        """SententiaApp constructor must accept no parameters."""
        sig = inspect.signature(SententiaApp.__init__)
        params = [p for p in sig.parameters if p != "self"]
        assert len(params) == 0

    def test_add_rest_resource_accepts_restresource(self):
        """add_rest_resource must accept a RESTResource parameter."""
        hints = {}
        for key, val in SententiaApp.add_rest_resource.__annotations__.items():
            hints[key] = val
        assert "resource" in hints or hasattr(SententiaApp.add_rest_resource, "__wrapped__")

    def test_run_has_host_and_port_params(self):
        """run must have host and port parameters with defaults."""
        sig = inspect.signature(SententiaApp.run)
        assert "host" in sig.parameters
        assert "port" in sig.parameters
        assert sig.parameters["host"].default == "0.0.0.0"
        assert sig.parameters["port"].default == 8000

    def test_init_has_tools_and_mcp_attributes(self):
        app = SententiaApp()
        assert hasattr(app, "_tools")
        assert hasattr(app, "_mcp")
        assert app._tools == []
        assert app._mcp is None


class TestSententiaAppLogic:
    """Logic tests for SententiaApp REST and MCP modes."""

    def test_sententia_app_creation(self):
        """SententiaApp can be created without arguments."""
        app = SententiaApp()
        assert app is not None

    def test_add_rest_resource_registers_routes(self):
        """Adding resources registers their URL rules on the FastAPI app."""
        app = SententiaApp()

        class FakeSearchResource(RESTResource):
            url_rule = "/search"

            def post(self, *args, **kwargs):
                return {"ok": True}

        class FakeFilesResource(RESTResource):
            url_rule = "/files/{path:path}"

            def get(self, *args, **kwargs):
                return {"ok": True}

        class FakeAskResource(RESTResource):
            url_rule = "/ask"

            def post(self, *args, **kwargs):
                return {"ok": True}

        app.add_rest_resource(FakeSearchResource())
        app.add_rest_resource(FakeAskResource())
        app.add_rest_resource(FakeFilesResource())

        routes = [(r.path, r.methods) for r in app._app.routes if hasattr(r, "methods")]
        assert ("/search", {"POST"}) in routes
        assert ("/ask", {"POST"}) in routes
        assert ("/files/{path:path}", {"GET"}) in routes
        # Non-overridden methods must NOT be registered
        assert ("/search", {"GET"}) not in routes
        assert ("/search", {"PUT"}) not in routes
        assert ("/search", {"DELETE"}) not in routes
        assert ("/files/{path:path}", {"POST"}) not in routes
        assert ("/ask", {"GET"}) not in routes

    def test_add_rest_resource_tracks_resources(self):
        """add_rest_resource tracks registered resources."""
        app = SententiaApp()

        class FakeResource(RESTResource):
            url_rule = "/test"

            def post(self, *args, **kwargs):
                return {"ok": True}

        app.add_rest_resource(FakeResource())
        assert len(app._resources) == 1

    def test_app_add_mcp_tool_registers_in_mcp(self):
        app = SententiaApp()
        mock_tool = MagicMock(spec=MCPTool)
        mock_tool.name = "test_tool"
        mock_tool.description = "A test tool"
        mock_tool.execute = MagicMock(return_value={"result": "ok"})

        app.add_mcp_tool(mock_tool)

        assert len(app._tools) == 1
        assert app._mcp is not None

    @patch("sententia.app.app.uvicorn")
    def test_app_run_fastapi_mode(self, mock_uvicorn):
        app = SententiaApp()
        app.run(host="127.0.0.1", port=9000)

        mock_uvicorn.run.assert_called_once_with(app._app, host="127.0.0.1", port=9000)

    @patch("sententia.app.app.uvicorn")
    def test_app_run_default_host_port(self, mock_uvicorn):
        app = SententiaApp()
        app.run()

        mock_uvicorn.run.assert_called_once_with(app._app, host="0.0.0.0", port=8000)

    def test_app_run_mcp_mode(self):
        app = SententiaApp()
        mock_tool = MagicMock(spec=MCPTool)
        mock_tool.name = "search"
        mock_tool.description = "Search tool"
        mock_tool.execute = MagicMock(return_value=[])

        app.add_mcp_tool(mock_tool)
        app._mcp.run = MagicMock()
        app._mcp.settings = MagicMock()

        app.run(host="127.0.0.1", port=9000)

        assert app._mcp.settings.host == "127.0.0.1"
        assert app._mcp.settings.port == 9000
        app._mcp.run.assert_called_once_with(transport="streamable-http")

    def test_app_run_raises_on_mixed_modes(self):
        app = SententiaApp()
        mock_resource = MagicMock(spec=RESTResource)
        mock_resource.url_rule = "/test"
        mock_resource.post = MagicMock()

        mock_tool = MagicMock(spec=MCPTool)
        mock_tool.name = "test"
        mock_tool.description = "test tool"
        mock_tool.execute = MagicMock()

        app.add_rest_resource(mock_resource)
        app.add_mcp_tool(mock_tool)

        with pytest.raises(RuntimeError, match="mutually exclusive"):
            app.run()

    def test_app_add_mcp_tool_multiple_tools(self):
        app = SententiaApp()
        for i in range(3):
            mock_tool = MagicMock(spec=MCPTool)
            mock_tool.name = f"tool_{i}"
            mock_tool.description = f"Tool {i}"
            mock_tool.execute = MagicMock()
            app.add_mcp_tool(mock_tool)

        assert len(app._tools) == 3

    def test_app_wrapper_has_correct_name_and_doc(self):
        from sententia.app.app import _create_wrapper  # noqa: PLC0415

        mock_tool = MagicMock(spec=MCPTool)
        mock_tool.name = "search"
        mock_tool.description = "Search for docs"
        mock_tool.execute = MagicMock(return_value=[])

        wrapper = _create_wrapper(mock_tool)

        assert wrapper.__name__ == "search"
        assert wrapper.__doc__ == "Search for docs"

    def test_app_wrapper_propagates_execute_errors(self):
        from sententia.app.app import _create_wrapper  # noqa: PLC0415

        mock_tool = MagicMock(spec=MCPTool)
        mock_tool.name = "failing"
        mock_tool.description = "A failing tool"
        mock_tool.execute = MagicMock(side_effect=RuntimeError("tool error"))

        wrapper = _create_wrapper(mock_tool)

        with pytest.raises(RuntimeError, match="tool error"):
            wrapper()
