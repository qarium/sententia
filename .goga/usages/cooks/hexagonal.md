# Hexagonal Architecture (Ports & Adapters)

## Purpose

This practice describes the Hexagonal Architecture pattern applied to the adapters
of the Sententia service (API Adapter and MCP Adapter).

## Principle

An Adapter operates at the boundary of the Domain Layer and performs two functions:
1. Translates external requests (HTTP for the API Adapter, MCP Protocol for the MCP Adapter) into Domain Layer calls
2. Converts Domain Layer results (dict/list) into Response Models (Pydantic Models)

The Domain Layer (index, rag, storage) is protocol-agnostic and unaware of Response Models.

## Application

- **API Adapter** (sententia/api/*) — translates HTTP requests into Domain Layer calls, converts results into Pydantic Models
- **MCP Adapter** (sententia/mcp/*) — translates MCP Protocol tool calls into Domain Layer calls, converts results into Pydantic Models

## Rules

- Adapters must not contain Business Logic — only Routing and Data Conversion
- The Domain Layer must not import types from the Adapter
- Request Models and Response Models belong to the Adapter, not the Domain Layer