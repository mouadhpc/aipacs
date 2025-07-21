import pytest
import torch
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from src.ai_engine.processor import AIProcessor, Finding, AIResults

@pytest.fixture
def ai_processor():
    processor = AIProcessor()
    return processor

@pytest.fixture
def mock_dicom_dataset():
    mock_ds = Mock()
    mock_ds.get.side_effect = lambda x, default: {
        'Modality': 'CT',
        'StudyInstanceUID': '1.2.3',
        'SeriesInstanceUID': '1.2.3.4',
        'SOPInstanceUID': '1.2.3.4.5',
        'WindowCenter': 40,
        'WindowWidth': 400
    }.get(x, default)
    mock_ds.pixel_array = np.random.rand(512, 512)
    return mock_ds

@pytest.mark.asyncio
async def test_load_model(ai_processor):
    # Test avec modèle de démonstration
    await ai_processor.load_model()
    assert ai_processor.model is not None
    assert ai_processor.model_version == '1.0.0'

@pytest.mark.asyncio
async def test_prepare_image(ai_processor, mock_dicom_dataset, tmp_path):
    # Création d'une image DICOM temporaire
    image_path = tmp_path / 'test.dcm'
    with patch('pydicom.dcmread') as mock_dcmread:
        mock_dcmread.return_value = mock_dicom_dataset
        tensor = await ai_processor._prepare_image(image_path, mock_dicom_dataset)
    
    assert tensor is not None
    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape[0] == 1  # Batch dimension
    assert tensor.shape[1] == 1  # Channel dimension

@pytest.mark.asyncio
async def test_analyze_image(ai_processor, mock_dicom_dataset, tmp_path):
    image_path = tmp_path / 'test.dcm'
    
    with patch('pydicom.dcmread') as mock_dcmread:
        mock_dcmread.return_value = mock_dicom_dataset
        results = await ai_processor.analyze_image(image_path, mock_dicom_dataset)
    
    assert results is not None
    assert isinstance(results, AIResults)
    assert results.modality == 'CT'
    assert isinstance(results.findings, list)

def test_normalize_ct_image(ai_processor, mock_dicom_dataset):
    pixel_array = mock_dicom_dataset.pixel_array
    normalized = ai_processor._apply_ct_window(pixel_array, mock_dicom_dataset)
    
    assert normalized.min() >= 0
    assert normalized.max() <= 1
    assert normalized.shape == pixel_array.shape

def test_normalize_mr_image(ai_processor):
    test_array = np.random.rand(512, 512) * 1000
    normalized = ai_processor._normalize_mr_image(test_array)
    
    assert normalized.min() >= 0
    assert normalized.max() <= 1
    assert normalized.shape == test_array.shape

def test_normalize_xray_image(ai_processor):
    test_array = np.random.rand(512, 512) * 1000
    normalized = ai_processor._normalize_xray_image(test_array)
    
    assert normalized.min() >= 0
    assert normalized.max() <= 1
    assert normalized.shape == test_array.shape

@pytest.mark.asyncio
async def test_analyze_by_modality(ai_processor, mock_dicom_dataset):
    # Test pour chaque modalité
    modalities = ['CT', 'MR', 'CR', 'MG']
    image_tensor = torch.randn(1, 1, 512, 512)
    
    for modality in modalities:
        mock_dicom_dataset.get.side_effect = lambda x, default: modality if x == 'Modality' else default
        findings = await ai_processor._analyze_by_modality(image_tensor, modality, mock_dicom_dataset)
        
        assert isinstance(findings, list)
        if findings:  # Si des anomalies sont détectées
            assert all(isinstance(f, Finding) for f in findings)
            assert all(f.confidence > 0 for f in findings)

def test_calculate_overall_confidence(ai_processor):
    findings = [
        Finding(
            type='test',
            confidence=0.8,
            location=(0, 0, 10, 10),
            description='Test finding',
            severity='medium'
        ),
        Finding(
            type='test',
            confidence=0.6,
            location=(20, 20, 10, 10),
            description='Test finding',
            severity='low'
        )
    ]
    
    confidence = ai_processor._calculate_overall_confidence(findings)
    assert confidence == 0.7  # (0.8 + 0.6) / 2

def test_empty_findings_confidence(ai_processor):
    confidence = ai_processor._calculate_overall_confidence([])
    assert confidence == 0.0