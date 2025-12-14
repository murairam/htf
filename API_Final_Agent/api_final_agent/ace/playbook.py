"""
Playbook data model and management for the ACE Plant-Based Packaging Intelligence system.

The playbook accumulates domain knowledge about plant-based product analysis,
scoring rules, ultra-processing pitfalls, packaging patterns, and go-to-market insights.
"""
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import threading

from . import config as config_module
from .config import PLAYBOOK_SECTIONS, SECTION_PREFIXES, PlaybookConfig


@dataclass
class Bullet:
    """A single knowledge bullet in the playbook."""
    id: str
    content: str
    helpful_count: int = 0
    misused_count: int = 0
    irrelevant_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Bullet":
        return cls(**data)
    
    def mark_helpful(self):
        self.helpful_count += 1
        self.updated_at = datetime.utcnow().isoformat()
    
    def mark_misused(self):
        self.misused_count += 1
        self.updated_at = datetime.utcnow().isoformat()
    
    def mark_irrelevant(self):
        self.irrelevant_count += 1
        self.updated_at = datetime.utcnow().isoformat()
    
    @property
    def effectiveness_score(self) -> float:
        """Calculate effectiveness score for ranking/pruning."""
        total = self.helpful_count + self.misused_count + self.irrelevant_count
        if total == 0:
            return 0.0
        return (self.helpful_count - self.misused_count) / total
    
    def format_for_prompt(self) -> str:
        """Format bullet for inclusion in LLM prompts."""
        return f"[{self.id}] helpful={self.helpful_count} misused={self.misused_count} :: {self.content}"


@dataclass
class Playbook:
    """
    The evolving playbook for Plant-Based Packaging Intelligence domain.
    
    Sections: scoring_rules, plant_based_heuristics, ultra_processing_pitfalls, 
              packaging_patterns, go_to_market_rules
    """
    scoring_rules: List[Bullet] = field(default_factory=list)
    plant_based_heuristics: List[Bullet] = field(default_factory=list)
    ultra_processing_pitfalls: List[Bullet] = field(default_factory=list)
    packaging_patterns: List[Bullet] = field(default_factory=list)
    go_to_market_rules: List[Bullet] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.metadata:
            self.metadata = {
                "version": "1.0",
                "domain": "plant_based_packaging_intelligence",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "total_updates": 0
            }
    
    def get_section(self, section_name: str) -> List[Bullet]:
        """Get bullets from a specific section."""
        return getattr(self, section_name, [])
    
    def add_bullet(self, section: str, content: str) -> Bullet:
        """Add a new bullet to the specified section."""
        prefix = SECTION_PREFIXES.get(section, "unk")
        section_list = self.get_section(section)
        
        counter = len(section_list) + 1
        bullet_id = f"{prefix}-{counter:05d}"
        
        existing_ids = {b.id for b in section_list}
        while bullet_id in existing_ids:
            counter += 1
            bullet_id = f"{prefix}-{counter:05d}"
        
        bullet = Bullet(id=bullet_id, content=content)
        section_list.append(bullet)
        
        self.metadata["updated_at"] = datetime.utcnow().isoformat()
        self.metadata["total_updates"] = self.metadata.get("total_updates", 0) + 1
        
        return bullet
    
    def get_bullet_by_id(self, bullet_id: str) -> Optional[Bullet]:
        """Find a bullet by its ID across all sections."""
        for section in PLAYBOOK_SECTIONS:
            for bullet in self.get_section(section):
                if bullet.id == bullet_id:
                    return bullet
        return None
    
    def update_bullet_tags(self, bullet_evaluations: List[Dict[str, str]]):
        """Update bullet counts based on Reflector evaluation."""
        for eval_info in bullet_evaluations:
            bullet_id = eval_info.get("id")
            tag = eval_info.get("tag", "irrelevant")
            
            bullet = self.get_bullet_by_id(bullet_id)
            if bullet:
                if tag == "helpful":
                    bullet.mark_helpful()
                elif tag == "misused":
                    bullet.mark_misused()
                else:
                    bullet.mark_irrelevant()
    
    def get_all_bullets(self) -> List[Bullet]:
        """Get all bullets across all sections."""
        all_bullets = []
        for section in PLAYBOOK_SECTIONS:
            all_bullets.extend(self.get_section(section))
        return all_bullets
    
    def format_for_prompt(self) -> str:
        """Format the entire playbook for inclusion in LLM prompts."""
        sections = []
        
        for section_name in PLAYBOOK_SECTIONS:
            section_bullets = self.get_section(section_name)
            if section_bullets:
                header = section_name.upper().replace("_", " ")
                bullets_text = "\n".join(b.format_for_prompt() for b in section_bullets)
                sections.append(f"### {header}\n{bullets_text}")
        
        if not sections:
            return "(Playbook is empty - no accumulated knowledge yet)"
        
        return "\n\n".join(sections)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the playbook."""
        stats = {
            "total_bullets": 0,
            "sections": {}
        }
        for section in PLAYBOOK_SECTIONS:
            bullets = self.get_section(section)
            stats["sections"][section] = len(bullets)
            stats["total_bullets"] += len(bullets)
        
        stats["metadata"] = self.metadata
        return stats
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert playbook to dictionary for JSON serialization."""
        return {
            "scoring_rules": [b.to_dict() for b in self.scoring_rules],
            "plant_based_heuristics": [b.to_dict() for b in self.plant_based_heuristics],
            "ultra_processing_pitfalls": [b.to_dict() for b in self.ultra_processing_pitfalls],
            "packaging_patterns": [b.to_dict() for b in self.packaging_patterns],
            "go_to_market_rules": [b.to_dict() for b in self.go_to_market_rules],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Playbook":
        """Create playbook from dictionary."""
        playbook = cls()
        
        for section in PLAYBOOK_SECTIONS:
            section_data = data.get(section, [])
            section_list = []
            for bullet_data in section_data:
                section_list.append(Bullet.from_dict(bullet_data))
            setattr(playbook, section, section_list)
        
        playbook.metadata = data.get("metadata", {})
        return playbook


class PlaybookManager:
    """Manages playbook persistence and thread-safe operations."""
    
    def __init__(self, config: PlaybookConfig = None):
        self.config = config or PlaybookConfig()
        self._playbook: Optional[Playbook] = None
        self._lock = threading.RLock()
    
    def load(self) -> Playbook:
        """Load playbook from disk or create empty one."""
        with self._lock:
            path = Path(self.config.path)
            
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self._playbook = Playbook.from_dict(data)
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Warning: Could not load playbook, creating new one: {e}")
                    self._playbook = Playbook()
            else:
                self._playbook = Playbook()
            
            return self._playbook
    
    def save(self):
        """Save playbook to disk."""
        with self._lock:
            if self._playbook is None:
                return
            
            path = Path(self.config.path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._playbook.to_dict(), f, indent=2, ensure_ascii=False)
    
    def get_playbook(self) -> Playbook:
        """Get the current playbook, loading if necessary."""
        with self._lock:
            if self._playbook is None:
                return self.load()
            return self._playbook
    
    def apply_operations(self, operations: List[Dict[str, Any]]) -> List[Bullet]:
        """Apply Curator operations to the playbook."""
        added_bullets = []
        
        with self._lock:
            playbook = self.get_playbook()
            
            for op in operations:
                op_type = op.get("type", "").upper()
                section = op.get("section", "heuristics")
                content = op.get("content", "")
                
                if op_type == "ADD" and content.strip():
                    if section not in PLAYBOOK_SECTIONS:
                        section = "heuristics"
                    
                    bullet = playbook.add_bullet(section, content.strip())
                    added_bullets.append(bullet)
            
            self.save()
        
        return added_bullets
    
    def update_tags(self, bullet_evaluations: List[Dict[str, str]]):
        """Update bullet tags based on Reflector feedback."""
        with self._lock:
            playbook = self.get_playbook()
            playbook.update_bullet_tags(bullet_evaluations)
            self.save()


def compute_semantic_similarity(text1: str, text2: str) -> float:
    """Compute semantic similarity between two texts using word overlap."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union)


def deduplicate_playbook(playbook: Playbook, threshold: float = 0.85) -> List[str]:
    """Remove semantically similar bullets from the playbook."""
    removed_ids = []
    
    for section in PLAYBOOK_SECTIONS:
        section_list = playbook.get_section(section)
        if len(section_list) < 2:
            continue
        
        to_remove = set()
        
        for i, bullet1 in enumerate(section_list):
            if bullet1.id in to_remove:
                continue
            
            for bullet2 in section_list[i+1:]:
                if bullet2.id in to_remove:
                    continue
                
                similarity = compute_semantic_similarity(bullet1.content, bullet2.content)
                
                if similarity >= threshold:
                    if bullet1.effectiveness_score >= bullet2.effectiveness_score:
                        to_remove.add(bullet2.id)
                    else:
                        to_remove.add(bullet1.id)
                        break
        
        section_list[:] = [b for b in section_list if b.id not in to_remove]
        removed_ids.extend(to_remove)
    
    return removed_ids