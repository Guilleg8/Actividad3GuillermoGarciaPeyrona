
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Set
from pydantic import BaseModel, Field, ValidationError, field_validator



class DataNormalizer(ABC):

    @abstractmethod
    def normalize(self, raw_data: Any) -> Dict[str, Any]:
        pass


class GeneticDataModel(BaseModel):
    sample_id: str
    sequence: str
    detected_mutations: Set[str] = Field(default_factory=set)
    type: str = "genetic"
    metadata: Optional[Dict[str, Any]] = None


class BiochemicalDataModel(BaseModel):
    sample_id: str
    toxin_level: float
    protein_x_level: float
    type: str = "biochemical"


class PhysicalDataModel(BaseModel):
    subject_id: str
    heart_rate: Optional[int] = None
    spo2: Optional[int] = None
    type: str = "physical"


class GeneticNormalizer(DataNormalizer):

    def normalize(self, raw_data: Any) -> Dict[str, Any]:
        try:
            if "raw_sequence" in raw_data:
                sequence = raw_data["raw_sequence"].strip().replace(" ", "").upper()
                raw_data["sequence"] = sequence

            model = GeneticDataModel.model_validate(raw_data)

            if "T" in model.sequence:
                model.detected_mutations.add("T-VIRUS")
            if "G" in model.sequence:
                model.detected_mutations.add("G-VIRUS")

            return model.model_dump()

        except ValidationError as e:
            raise ValueError(f"Datos genéticos inválidos: {e}")
        except KeyError as e:
            raise ValueError(f"Falta campo requerido en datos genéticos: {e}")


class BiochemicalNormalizer(DataNormalizer):

    class BiochemicalInput(BaseModel):
        sample_id: str
        toxin_level_str: str = Field(..., alias="toxin_level")
        protein_x: float

        @field_validator('toxin_level_str')
        def clean_toxin(cls, v: str) -> float:
            try:
                return float(v.split()[0])
            except (ValueError, IndexError):
                raise ValueError("Formato de toxin_level inválido")

    def normalize(self, raw_data: Any) -> Dict[str, Any]:
        try:
            input_model = self.BiochemicalInput.model_validate(raw_data)

            output_data = {
                "sample_id": input_model.sample_id,
                "toxin_level": input_model.toxin_level_str,
                "protein_x_level": input_model.protein_x
            }

            model = BiochemicalDataModel.model_validate(output_data)
            return model.model_dump()

        except ValidationError as e:
            raise ValueError(f"Datos bioquímicos inválidos: {e}")


class PhysicalNormalizer(DataNormalizer):

    def normalize(self, raw_data: Any) -> Dict[str, Any]:
        try:
            subject_id = raw_data.get("subject_id")
            if not subject_id:
                raise ValueError("Falta subject_id")

            vitals = raw_data.get("vitals", {})

            spo2_raw = vitals.get("spo2")
            spo2_clean = None
            if isinstance(spo2_raw, str):
                spo2_clean = int(spo2_raw.replace("%", "").strip())
            elif isinstance(spo2_raw, (int, float)):
                spo2_clean = int(spo2_raw)

            normalized_data = {
                "subject_id": subject_id,
                "heart_rate": vitals.get("heart_rate"),
                "spo2": spo2_clean
            }

            model = PhysicalDataModel.model_validate(normalized_data)
            return model.model_dump()

        except ValidationError as e:
            raise ValueError(f"Datos físicos inválidos: {e}")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Error normalizando datos físicos: {e}")