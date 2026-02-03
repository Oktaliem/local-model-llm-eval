"""Sanitize model outputs to remove noise and unwanted content"""
import re


def sanitize_model_output(text: str) -> str:
    """
    Remove unwanted content from model outputs.

    Strips <think> blocks and other noise that can interfere
    with evaluation.
    """
    if not text:
        return ""

    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


