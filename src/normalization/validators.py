# src/umbrella_analysis/normalization/validators.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Set
from pydantic import BaseModel, Field, ValidationError, field_validator


# --- Interfaz Base ---

class DataNormalizer(ABC):
    """
    Interfaz abstracta (ABC) para un normalizador de datos.

    Cada servicio (Genético, Bioquímico, Físico) usará una implementación
    de esta clase para validar y limpiar sus datos de entrada.
    """

    @abstractmethod
    def normalize(self, raw_data: Any) -> Dict[str, Any]:
        """
        Valida, limpia y transforma datos crudos en un diccionario estandarizado.

        Args:
            raw_data: Los datos de entrada (podrían ser un dict, un JSON, etc.)

        Returns:
            Un diccionario con la estructura normalizada.

        Raises:
            ValueError: Si los datos fallan la validación.
        """
        pass


# --- Modelos de Datos (Schemas de Pydantic) ---
# Estos modelos definen la *salida* estandarizada

class GeneticDataModel(BaseModel):
    """Schema para datos genéticos normalizados."""
    sample_id: str
    sequence: str
    detected_mutations: Set[str] = Field(default_factory=set)
    type: str = "genetic"  # Campo clave para el Orchestrator
    metadata: Optional[Dict[str, Any]] = None


class BiochemicalDataModel(BaseModel):
    """Schema para datos bioquímicos normalizados."""
    sample_id: str
    toxin_level: float
    protein_x_level: float
    type: str = "biochemical"  # Campo clave para el Orchestrator


class PhysicalDataModel(BaseModel):
    """Schema para datos físicos (signos vitales) normalizados."""
    subject_id: str
    heart_rate: Optional[int] = None
    spo2: Optional[int] = None  # Saturación de oxígeno
    type: str = "physical"  # Campo clave para el Orchestrator


# --- Implementaciones Concretas del Normalizador ---

class GeneticNormalizer(DataNormalizer):
    """Normaliza y valida datos genéticos."""

    def normalize(self, raw_data: Any) -> Dict[str, Any]:
        try:
            # 1. Limpieza de datos (lógica de normalización)
            if "raw_sequence" in raw_data:
                # Limpia la secuencia: quita espacios/saltos, pasa a mayúsculas
                sequence = raw_data["raw_sequence"].strip().replace(" ", "").upper()
                raw_data["sequence"] = sequence

            # 2. Validación usando Pydantic
            model = GeneticDataModel.model_validate(raw_data)

            # 3. Lógica de normalización post-validación (extracción simple)
            if "T" in model.sequence:
                model.detected_mutations.add("T-VIRUS")
            if "G" in model.sequence:
                model.detected_mutations.add("G-VIRUS")

            # Retorna como diccionario
            return model.model_dump()

        except ValidationError as e:
            raise ValueError(f"Datos genéticos inválidos: {e}")
        except KeyError as e:
            raise ValueError(f"Falta campo requerido en datos genéticos: {e}")


class BiochemicalNormalizer(DataNormalizer):
    """Normaliza y valida datos bioquímicos."""

    # Usamos un modelo Pydantic interno para la *entrada*
    # para manejar campos con nombres diferentes
    class BiochemicalInput(BaseModel):
        sample_id: str
        toxin_level_str: str = Field(..., alias="toxin_level")  # Espera 'toxin_level'
        protein_x: float

        @field_validator('toxin_level_str')
        def clean_toxin(cls, v: str) -> float:
            # Normaliza "80.5 ppm" -> 80.5
            try:
                return float(v.split()[0])
            except (ValueError, IndexError):
                raise ValueError("Formato de toxin_level inválido")

    def normalize(self, raw_data: Any) -> Dict[str, Any]:
        try:
            # 1. Valida y transforma la entrada
            input_model = self.BiochemicalInput.model_validate(raw_data)

            # 2. Mapea al modelo de salida estandarizado
            output_data = {
                "sample_id": input_model.sample_id,
                "toxin_level": input_model.toxin_level_str,  # ya es float
                "protein_x_level": input_model.protein_x
            }

            # 3. Valida el modelo de salida
            model = BiochemicalDataModel.model_validate(output_data)
            return model.model_dump()

        except ValidationError as e:
            raise ValueError(f"Datos bioquímicos inválidos: {e}")


class PhysicalNormalizer(DataNormalizer):
    """Normaliza y valida datos físicos (signos vitales)."""

    def normalize(self, raw_data: Any) -> Dict[str, Any]:
        try:
            # Los datos físicos pueden venir anidados (ej: {'vitals': {'hr': 70}})
            subject_id = raw_data.get("subject_id")
            if not subject_id:
                raise ValueError("Falta subject_id")

            vitals = raw_data.get("vitals", {})

            # Normalización de O2 (ej. "98%" -> 98)
            spo2_raw = vitals.get("spo2")
            spo2_clean = None
            if isinstance(spo2_raw, str):
                spo2_clean = int(spo2_raw.replace("%", "").strip())
            elif isinstance(spo2_raw, (int, float)):
                spo2_clean = int(spo2_raw)

            # Construye el dict para el modelo Pydantic
            normalized_data = {
                "subject_id": subject_id,
                "heart_rate": vitals.get("heart_rate"),
                "spo2": spo2_clean
            }

            # Valida contra el modelo de salida
            model = PhysicalDataModel.model_validate(normalized_data)
            return model.model_dump()

        except ValidationError as e:
            raise ValueError(f"Datos físicos inválidos: {e}")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Error normalizando datos físicos: {e}")