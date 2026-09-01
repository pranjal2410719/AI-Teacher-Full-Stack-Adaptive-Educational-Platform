import numpy as np
import pydantic
from pydantic import BaseModel, Field
from typing import List, Optional

class ConceptItem(BaseModel):
    name: str
    depth: str
    key_points: List[str]

class LessonPlan(BaseModel):
    title: str
    level: str
    duration_minutes: int
    concepts: List[ConceptItem]

plan = LessonPlan(
    title="Introduction to Neural Networks",
    level="beginner",
    duration_minutes=15,
    concepts=[
        ConceptItem(name="Perceptron", depth="basic", key_points=["Inputs", "Weights", "Activation"]),
        ConceptItem(name="Feedforward", depth="basic", key_points=["Layer propagation", "Output"])
    ]
)
print("Pydantic Schema Validation OK:", plan.model_dump_json()[:50])

emb1 = np.array([0.1, 0.2, 0.9])
emb2 = np.array([0.15, 0.22, 0.88])
emb3 = np.array([0.9, 0.1, 0.05])
mat = np.vstack([emb1, emb2, emb3])
mat_norm = mat / np.linalg.norm(mat, axis=1, keepdims=True)
query = np.array([0.12, 0.21, 0.89])
query_norm = query / np.linalg.norm(query)
scores = np.dot(mat_norm, query_norm)
best_idx = int(np.argmax(scores))
print("Numpy Vector Similarity Top Score:", float(np.max(scores)), "Best index:", best_idx)
