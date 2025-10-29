# tests/test_normalization.py

import pytest
from umbrella_analysis.normalization import (
    GeneticNormalizer,
    BiochemicalNormalizer,
    PhysicalNormalizer
)


# --- Pruebas para GeneticNormalizer ---

def test_genetic_normalizer_success():
    """Prueba que los datos genéticos válidos se normalizan correctamente."""
    normalizer = GeneticNormalizer()
    raw_data = {
        "sample_id": "g-123",
        "raw_sequence": " atcg GTC "  # Prueba de limpieza (espacios, mayús/minús)
    }
    result = normalizer.normalize(raw_data)

    assert result["sample_id"] == "g-123"
    assert result["sequence"] == "ATCGGTC"  # Secuencia limpiada
    assert result["type"] == "genetic"
    assert "G-VIRUS" in result["detected_mutations"]


def test_genetic_normalizer_critical_mutation():
    """Prueba la detección de mutaciones críticas (T-Virus)."""
    normalizer = GeneticNormalizer()
    raw_data = {"sample_id": "g-124", "raw_sequence": "ATCGT"}
    result = normalizer.normalize(raw_data)

    assert "T-VIRUS" in result["detected_mutations"]


def test_genetic_normalizer_invalid_data():
    """Prueba que los datos sin campos requeridos lanzan ValueError."""
    normalizer = GeneticNormalizer()
    # Falta 'raw_sequence'
    raw_data = {"sample_id": "g-125"}

    with pytest.raises(ValueError, match="Falta campo requerido"):
        normalizer.normalize(raw_data)


# --- Pruebas para BiochemicalNormalizer ---

def test_biochemical_normalizer_success():
    """Prueba la normalización de datos bioquímicos (parsing de string)."""
    normalizer = BiochemicalNormalizer()
    raw_data = {
        "sample_id": "b-001",
        "toxin_level": "85.5 ppm",  # Prueba de parsing de string
        "protein_x": 10.1
    }
    result = normalizer.normalize(raw_data)

    assert result["sample_id"] == "b-001"
    assert result["toxin_level"] == 85.5  # Debe ser float
    assert result["protein_x_level"] == 10.1
    assert result["type"] == "biochemical"


def test_biochemical_normalizer_invalid_toxin():
    """Prueba que un formato de toxina inválido lanza ValueError."""
    normalizer = BiochemicalNormalizer()
    raw_data = {
        "sample_id": "b-002",
        "toxin_level": "alto",  # Formato inválido
        "protein_x": 10.1
    }

    with pytest.raises(ValueError, match="Formato de toxin_level inválido"):
        normalizer.normalize(raw_data)


# --- Pruebas para PhysicalNormalizer ---

def test_physical_normalizer_success():
    """Prueba la normalización de datos físicos (parsing de string y anidado)."""
    normalizer = PhysicalNormalizer()
    raw_data = {
        "subject_id": "s-01",
        "vitals": {
            "heart_rate": 75,
            "spo2": "98%"  # Prueba de limpieza de string
        }
    }
    result = normalizer.normalize(raw_data)

    assert result["subject_id"] == "s-01"
    assert result["heart_rate"] == 75
    assert result["spo2"] == 98  # Debe ser int
    assert result["type"] == "physical"


def test_physical_normalizer_missing_vitals():
    """Prueba que los signos vitales opcionales se manejan como None."""
    normalizer = PhysicalNormalizer()
    raw_data = {
        "subject_id": "s-02",
        "vitals": {}  # Sin datos
    }
    result = normalizer.normalize(raw_data)

    assert result["subject_id"] == "s-02"
    assert result["heart_rate"] is None
    assert result["spo2"] is None


def test_physical_normalizer_missing_id():
    """Prueba que la falta de subject_id lanza ValueError."""
    normalizer = PhysicalNormalizer()
    raw_data = {"vitals": {"heart_rate": 80}}

    with pytest.raises(ValueError, match="Falta subject_id"):
        normalizer.normalize(raw_data)