"""
Test data for e2e tests
"""

# Sample questions for testing
SAMPLE_QUESTIONS = {
    "simple": "What is the capital of France?",
    "technical": "Explain machine learning in simple terms.",
    "math": "What is 2 + 2?",
    "coding": "Write a Python function to calculate factorial.",
    "comparison": "Compare Python and JavaScript programming languages."
}

# Sample responses for testing
SAMPLE_RESPONSES = {
    "short": "Paris is the capital of France.",
    "detailed": "The capital of France is Paris, a beautiful city known for its art, culture, and history. It has been the capital since 987 AD.",
    "technical": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. It uses algorithms to identify patterns and make predictions.",
    "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)"
}

# Sample code for code evaluation tests
SAMPLE_CODE = {
    "valid": "def add(a, b):\n    return a + b",
    "invalid_syntax": "def add(a, b\n    return a + b",  # Missing closing parenthesis
    "with_error": "def divide(a, b):\n    return a / b\n\nresult = divide(10, 0)"  # Division by zero
}

