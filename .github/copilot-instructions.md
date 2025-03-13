# Copilot Instruction Rules for Python Development

## Introduction
This document outlines the rules and best practices for Python development, focusing on clean code architecture, object-oriented programming (OOP), and leveraging Python 3.11 features. Adherence to these guidelines ensures maintainable, scalable, and high-quality code.

---

## General Guidelines
- Follow PEP 8 for code style.
- Use meaningful and descriptive variable, function, and class names.
- Keep functions and classes small and focused on a single responsibility.
- Avoid deeply nested code; strive for simplicity and readability.

---

## Code Architecture
- Emphasize modular design and separation of concerns.
- Use design patterns where applicable (e.g., Singleton, Factory, Strategy).
- Organize code into logical packages and modules.
- Ensure clear boundaries between layers (e.g., API, business logic, and data layers).

---

## Object-Oriented Programming (OOP) Practices
- Use classes to encapsulate data and behavior.
- Follow SOLID principles:
  - **S**ingle Responsibility Principle
  - **O**pen/Closed Principle
  - **L**iskov Substitution Principle
  - **I**nterface Segregation Principle
  - **D**ependency Inversion Principle
- Prefer composition over inheritance when appropriate.
- Use abstract base classes and interfaces to define contracts.

---

## Type Hints and Annotations
- Use Python's type hinting system for all function signatures and class attributes.
- Avoid the use of `Any` type hints; be as specific as possible.
- Leverage `typing` and `collections.abc` modules for complex types.
- Example:
  ```python
  from typing import List

  def calculate_average(scores: List[int]) -> float:
      return sum(scores) / len(scores)
  ```

---

## Python 3.11 Features
- Use `Self` type for method chaining in class methods.
- Leverage `dataclasses` for simple data structures.
- Explore `match` statements for pattern matching.
- Example:
  ```python
  class Example:
      def method(self) -> Self:
          # Perform some operation
          return self
  ```

---

## Google Docstring Standards
- Use Google-style docstrings for all public modules, classes, and functions.
- Include sections for Args, Returns, Raises, and Examples.
- Example:
  ```python
  def add_numbers(a: int, b: int) -> int:
      """
      Adds two numbers.

      Args:
          a (int): The first number.
          b (int): The second number.

      Returns:
          int: The sum of the two numbers.

      Example:
          >>> add_numbers(2, 3)
          5
      """
      return a + b
  ```

---

## Best Practices
- Write unit tests for all new code.
- Use `pytest` for testing.
- Avoid code duplication and strive for DRY (Don't Repeat Yourself).
- Document all assumptions and edge cases.
- Use `httpx` over `requests` for HTTP operations.
- Use `pydantic v2` for data validation and parsing.

---

## Preferred Libraries and Tools
- **HTTP Operations**: Use `httpx` for asynchronous and synchronous HTTP requests.
- **Data Validation**: Use `pydantic v2` for robust data validation and parsing.

---

## Examples
### Using `httpx` for HTTP Requests
```python
import httpx

async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
```

### Using `pydantic` for Data Validation
```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
```

---