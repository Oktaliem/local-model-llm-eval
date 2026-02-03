"""
Template service for managing evaluation templates.
Extracted from app.py to separate backend concerns.
"""
import sqlite3
import json
import os
import uuid
from typing import List, Dict, Any, Optional

# Database path - default to data/ directory
DB_NAME = os.getenv("DB_NAME", "llm_judge.db")
DB_PATH = os.getenv("DB_PATH", "data/llm_judge.db")


def create_evaluation_template(
    template_name: str,
    evaluation_type: str,
    template_config: Dict[str, Any],
    template_description: Optional[str] = None,
    industry: Optional[str] = None,
    created_by: Optional[str] = None,
    is_predefined: bool = False
) -> str:
    """Create a new evaluation template.
    
    Returns:
        template_id: Unique identifier for the template
    """
    template_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO evaluation_templates 
        (template_id, template_name, template_description, industry, evaluation_type,
         template_config, is_predefined, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        template_id,
        template_name,
        template_description,
        industry,
        evaluation_type,
        json.dumps(template_config),
        1 if is_predefined else 0,
        created_by
    ))
    
    conn.commit()
    conn.close()
    return template_id


def get_evaluation_template(template_id: str) -> Optional[Dict[str, Any]]:
    """Get an evaluation template by template_id."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT * FROM evaluation_templates WHERE template_id = ?', (template_id,))
    row = c.fetchone()
    
    if row:
        columns = [description[0] for description in c.description]
        result = dict(zip(columns, row))
        result['template_config'] = json.loads(result['template_config'])
        result['is_predefined'] = bool(result['is_predefined'])
    else:
        result = None
    
    conn.close()
    return result


def get_all_evaluation_templates(
    evaluation_type: Optional[str] = None,
    industry: Optional[str] = None,
    include_predefined: bool = True,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get all evaluation templates, optionally filtered by type and industry."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    query = 'SELECT * FROM evaluation_templates WHERE 1=1'
    params = []
    
    if evaluation_type:
        query += ' AND evaluation_type = ?'
        params.append(evaluation_type)
    
    if industry:
        query += ' AND industry = ?'
        params.append(industry)
    
    if not include_predefined:
        query += ' AND is_predefined = 0'
    
    query += ' ORDER BY usage_count DESC, created_at DESC LIMIT ?'
    params.append(limit)
    
    c.execute(query, params)
    
    columns = [description[0] for description in c.description]
    templates = []
    for row in c.fetchall():
        template = dict(zip(columns, row))
        template['template_config'] = json.loads(template['template_config'])
        template['is_predefined'] = bool(template['is_predefined'])
        templates.append(template)
    
    conn.close()
    return templates


def delete_evaluation_template(template_id: str) -> bool:
    """Delete an evaluation template (only if not predefined)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if template is predefined
    c.execute('SELECT is_predefined FROM evaluation_templates WHERE template_id = ?', (template_id,))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return False
    
    if row[0]:  # Predefined templates cannot be deleted
        conn.close()
        return False
    
    c.execute('DELETE FROM evaluation_templates WHERE template_id = ?', (template_id,))
    conn.commit()
    conn.close()
    return True


def apply_template_to_evaluation(template_id: str, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply a template configuration to evaluation data.
    
    Returns:
        Modified evaluation data with template configuration applied
    """
    template = get_evaluation_template(template_id)
    if not template:
        return evaluation_data
    
    config = template['template_config']
    evaluation_type = template['evaluation_type']
    
    # Apply template based on evaluation type
    if evaluation_type == 'comprehensive':
        # Template can modify metrics weights, prompts, task type
        if 'metrics' in config:
            evaluation_data['metric_weights'] = config['metrics']
        if 'prompt_modifiers' in config:
            evaluation_data['prompt_modifiers'] = config['prompt_modifiers']
        if 'task_type' in config:
            evaluation_data['task_type'] = config['task_type']
    elif evaluation_type == 'code_evaluation':
        if 'quality_weights' in config:
            evaluation_data['quality_weights'] = config['quality_weights']
        if 'strict_mode' in config:
            evaluation_data['strict_mode'] = config['strict_mode']
    
    return evaluation_data

