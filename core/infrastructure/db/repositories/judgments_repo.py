"""Repository for judgments"""
from typing import List, Dict, Any, Optional
from core.infrastructure.db.connection import get_db_connection


class JudgmentsRepository:
    """Repository for managing judgments in the database"""

    def save(
        self,
        question: str,
        response_a: str,
        response_b: str,
        model_a: str,
        model_b: str,
        judge_model: str,
        judgment: str,
        judgment_type: str,
        evaluation_id: Optional[str] = None,
        metrics_json: Optional[str] = None,
        trace_json: Optional[str] = None,
    ) -> int:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO judgments 
            (evaluation_id, question, response_a, response_b, model_a, model_b, 
             judge_model, judgment, judgment_type, metrics_json, trace_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evaluation_id,
                question,
                response_a,
                response_b,
                model_a,
                model_b,
                judge_model,
                judgment,
                judgment_type,
                metrics_json,
                trace_json,
            ),
        )
        conn.commit()
        judgment_id = c.lastrowid
        conn.close()
        return judgment_id

    def get_all(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            """
            SELECT * FROM judgments 
            ORDER BY created_at DESC 
            LIMIT ?
            """,
            (limit,),
        )
        columns = [desc[0] for desc in c.description]
        results = [dict(zip(columns, row)) for row in c.fetchall()]
        conn.close()
        return results


