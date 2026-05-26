"""
LLM Response Parsing Utilities
==============================
Robust JSON parsing for LLM responses that may not be perfectly formatted.
"""

import json
import re
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def extract_json_from_text(text: str, json_type: str = "object") -> Optional[Dict | List]:
    """
    Extract JSON from LLM response text that may contain additional content.
    
    Args:
        text: Raw LLM response text
        json_type: "object" for JSON objects, "array" for JSON arrays, "any" for either
        
    Returns:
        Parsed JSON object/array or None if extraction fails
    """
    if not text or not isinstance(text, str):
        return None
    
    text = text.strip()
    
    # Try direct parsing first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from text
    # Pattern for JSON objects
    if json_type != "array":
        obj_pattern = r'\{[\s\S]*\}'
        match = re.search(obj_pattern, text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    
    # Pattern for JSON arrays
    if json_type != "object":
        array_pattern = r'\[[\s\S]*\]'
        match = re.search(array_pattern, text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    
    # Try markdown code block extraction
    code_pattern = r'```(?:json)?\s*([\s\S]*?)```'
    match = re.search(code_pattern, text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
    
    logger.warning(f"Failed to extract JSON from text: {text[:100]}...")
    return None


def parse_llm_json_list(text: str, item_type: type = dict) -> List[Any]:
    """
    Parse a list of items from LLM response.
    
    Args:
        text: Raw LLM response
        item_type: Expected type of items (dict, str, etc.)
        
    Returns:
        List of parsed items
    """
    extracted = extract_json_from_text(text, json_type="array")
    
    if isinstance(extracted, list):
        return extracted
    elif isinstance(extracted, dict) and "items" in extracted:
        return extracted.get("items", [])
    elif isinstance(extracted, dict) and "results" in extracted:
        return extracted.get("results", [])
    
    return []


def parse_llm_json_object(text: str) -> Optional[Dict]:
    """
    Parse a JSON object from LLM response.
    
    Args:
        text: Raw LLM response
        
    Returns:
        Parsed dictionary or None
    """
    return extract_json_from_text(text, json_type="object")


def safe_json_parse(text: str, default: Any = None) -> Any:
    """
    Safely parse JSON with a default fallback.
    
    Args:
        text: JSON string
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return extract_json_from_text(text) or default
    except Exception as e:
        logger.warning(f"Safe JSON parse failed: {e}")
        return default


def validate_schema(data: Dict, required_fields: List[str]) -> bool:
    """
    Validate that a dictionary has all required fields.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        True if all required fields present and non-empty
    """
    if not isinstance(data, dict):
        return False
    
    for field in required_fields:
        if field not in data or not data[field]:
            logger.warning(f"Missing or empty required field: {field}")
            return False
    
    return True


def fix_malformed_json(text: str) -> Optional[str]:
    """
    Attempt to fix common JSON formatting issues.
    
    Args:
        text: Potentially malformed JSON
        
    Returns:
        Fixed JSON string or None
    """
    if not text:
        return None
    
    # Remove common prefixes/suffixes
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    # Try to validate
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass
    
    # Try removing trailing commas (common issue)
    try:
        fixed = re.sub(r',\s*([}\]])', r'\1', text)
        json.loads(fixed)
        return fixed
    except json.JSONDecodeError:
        pass
    
    return None
