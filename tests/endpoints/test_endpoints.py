from typing import Any

import pytest
from sententia.endpoints import MCPTool, RESTResource

# --- Contract tests ---


def test_restresource_importable():
    assert RESTResource is not None


def test_mcptool_importable():
    assert MCPTool is not None


def test_restresource_has_url_rule_property():
    assert hasattr(RESTResource, "url_rule")


def test_restresource_has_http_methods():
    assert hasattr(RESTResource, "get")
    assert hasattr(RESTResource, "post")
    assert hasattr(RESTResource, "put")
    assert hasattr(RESTResource, "delete")


def test_mcptool_has_name_description():
    assert hasattr(MCPTool, "name")
    assert hasattr(MCPTool, "description")
    assert hasattr(MCPTool, "execute")


# --- Logical tests ---


class _StubRESTResource(RESTResource):
    url_rule = "/test"

    def get(self, *args: Any, **kwargs: Any) -> Any:
        return "get-response"


def test_restresource_get_raises_not_implemented():
    resource = RESTResource()
    with pytest.raises(NotImplementedError, match="Method Not Allowed"):
        resource.get()


def test_restresource_post_raises_not_implemented():
    resource = RESTResource()
    with pytest.raises(NotImplementedError, match="Method Not Allowed"):
        resource.post()


def test_restresource_url_rule_raises_not_implemented():
    resource = RESTResource()
    with pytest.raises(NotImplementedError):
        _ = resource.url_rule


def test_mcptool_execute_raises_not_implemented():
    tool = MCPTool()
    with pytest.raises(NotImplementedError):
        tool.execute()


def test_mcptool_name_raises_not_implemented():
    tool = MCPTool()
    with pytest.raises(NotImplementedError):
        _ = tool.name


def test_mcptool_description_raises_not_implemented():
    tool = MCPTool()
    with pytest.raises(NotImplementedError):
        _ = tool.description


def test_restresource_subclass_url_rule():
    assert _StubRESTResource.url_rule == "/test"


def test_mcptool_subclass_properties():
    class StubTool(MCPTool):
        name = "test"
        description = "desc"

    tool = StubTool()
    assert tool.name == "test"
    assert tool.description == "desc"
