import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from contextlib import contextmanager

from ai_game_dev.engines.base import EngineGenerationResult

@dataclass
class ProjectInfo:
    id: str
    name: str
    description: str
    engine: str
    complexity: str
    art_style: str
    created_at: datetime
    updated_at: datetime
    status: str
    project_path: Optional[str] = None
    generated_files: Dict[str, str] = None
    build_instructions: List[str] = None
    asset_requirements: Dict[str, List[str]] = None

    def __post_init__(self):
        if self.generated_files is None:
            self.generated_files = {}
        if self.build_instructions is None:
            self.build_instructions = []
        if self.asset_requirements is None:
            self.asset_requirements = {}

class ProjectManager:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path.home() / ".ai-game-dev" / "projects.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    engine TEXT NOT NULL,
                    complexity TEXT NOT NULL,
                    art_style TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    project_path TEXT,
                    generated_files TEXT,
                    build_instructions TEXT,
                    asset_requirements TEXT
                )
            """)
            conn.commit()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def create_project(
        self,
        name: str,
        description: str,
        engine: str,
        complexity: str = "intermediate",
        art_style: str = "modern"
    ) -> ProjectInfo:
        project_id = str(uuid.uuid4())
        now = datetime.now()
        
        project = ProjectInfo(
            id=project_id,
            name=name,
            description=description,
            engine=engine,
            complexity=complexity,
            art_style=art_style,
            created_at=now,
            updated_at=now,
            status="created"
        )
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO projects (
                    id, name, description, engine, complexity, art_style,
                    created_at, updated_at, status, project_path,
                    generated_files, build_instructions, asset_requirements
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project.id, project.name, project.description, project.engine,
                project.complexity, project.art_style, project.created_at.isoformat(),
                project.updated_at.isoformat(), project.status, project.project_path,
                json.dumps(project.generated_files), json.dumps(project.build_instructions),
                json.dumps(project.asset_requirements)
            ))
            conn.commit()
        
        return project

    def update_project_with_result(self, project_id: str, result: EngineGenerationResult) -> ProjectInfo:
        now = datetime.now()
        
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE projects SET
                    updated_at = ?,
                    status = ?,
                    project_path = ?,
                    generated_files = ?,
                    build_instructions = ?,
                    asset_requirements = ?
                WHERE id = ?
            """, (
                now.isoformat(),
                "generated",
                str(result.project_path) if result.project_path else None,
                json.dumps(result.generated_files),
                json.dumps(result.build_instructions),
                json.dumps(result.asset_requirements),
                project_id
            ))
            conn.commit()
        
        return self.get_project(project_id)

    def get_project(self, project_id: str) -> Optional[ProjectInfo]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            
        if not row:
            return None
        
        return self._row_to_project(row)

    def list_projects(self, limit: int = 50, offset: int = 0) -> List[ProjectInfo]:
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM projects 
                ORDER BY updated_at DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset)).fetchall()
        
        return [self._row_to_project(row) for row in rows]

    def get_recent_projects(self, limit: int = 10) -> List[ProjectInfo]:
        return self.list_projects(limit=limit)

    def delete_project(self, project_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()
            return cursor.rowcount > 0

    def _row_to_project(self, row: sqlite3.Row) -> ProjectInfo:
        return ProjectInfo(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            engine=row["engine"],
            complexity=row["complexity"],
            art_style=row["art_style"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            status=row["status"],
            project_path=row["project_path"],
            generated_files=json.loads(row["generated_files"] or "{}"),
            build_instructions=json.loads(row["build_instructions"] or "[]"),
            asset_requirements=json.loads(row["asset_requirements"] or "{}")
        )

    def get_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            total_projects = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
            
            engine_counts = conn.execute("""
                SELECT engine, COUNT(*) as count 
                FROM projects 
                GROUP BY engine
            """).fetchall()
            
            status_counts = conn.execute("""
                SELECT status, COUNT(*) as count 
                FROM projects 
                GROUP BY status
            """).fetchall()
        
        return {
            "total_projects": total_projects,
            "projects_by_engine": {row[0]: row[1] for row in engine_counts},
            "projects_by_status": {row[0]: row[1] for row in status_counts}
        }