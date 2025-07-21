#!/usr/bin/env python3
"""
Script de test pour vérifier tous les endpoints de l'API AI PACS
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, endpoint, description, data=None):
    """Teste un endpoint et affiche le résultat"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data if data else {})
        
        if response.status_code == 200:
            print(f"✅ {description}")
            print(f"   URL: {endpoint}")
            result = response.json()
            if isinstance(result, dict) and 'status' in result:
                print(f"   Status: {result['status']}")
            print()
            return True
        else:
            print(f"❌ {description}")
            print(f"   URL: {endpoint}")
            print(f"   Status Code: {response.status_code}")
            print()
            return False
    except Exception as e:
        print(f"❌ {description}")
        print(f"   URL: {endpoint}")
        print(f"   Erreur: {e}")
        print()
        return False

def main():
    print("🧪 Test des Endpoints AI PACS")
    print("=" * 60)
    
    # Test de connectivité
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Serveur non accessible. Assurez-vous que python app_dev.py est lancé.")
            return
    except:
        print("❌ Serveur non accessible. Assurez-vous que python app_dev.py est lancé.")
        return
    
    success_count = 0
    total_count = 0
    
    # Tests des endpoints
    endpoints = [
        ("GET", "/", "Page d'accueil"),
        ("GET", "/health", "Health check"),
        ("GET", "/api/v1/dicom/status", "Statut serveur DICOM"),
        ("GET", "/api/v1/dicom/connections", "Connexions DICOM"),
        ("POST", "/api/v1/dicom/test-connection", "Test connexion PACS"),
        ("GET", "/api/v1/dicom/received-studies", "Études reçues"),
        ("GET", "/api/v1/dicom/statistics", "Statistiques DICOM"),
        ("GET", "/api/v1/ai/models", "Modèles IA disponibles"),
        ("POST", "/api/v1/ai/analyze?file_id=test123", "Analyse IA", {"file_id": "test123"}),
        ("GET", "/api/v1/ai/status", "Statut moteur IA"),
        ("GET", "/api/v1/reports/", "Liste des rapports"),
        ("GET", "/api/v1/reports/1", "Rapport spécifique"),
        ("GET", "/api/v1/reports/statistics/summary", "Statistiques rapports"),
        ("GET", "/api/v1/monitoring/health", "Monitoring santé"),
        ("GET", "/api/v1/monitoring/metrics", "Métriques système"),
    ]
    
    for method, endpoint, description, *data in endpoints:
        total_count += 1
        data = data[0] if data else None
        if test_endpoint(method, endpoint, description, data):
            success_count += 1
    
    print("=" * 60)
    print(f"📊 Résultats des tests: {success_count}/{total_count} endpoints fonctionnels")
    
    if success_count == total_count:
        print("🎉 Tous les endpoints fonctionnent parfaitement !")
        print("\n🌐 Accès à l'application :")
        print(f"   • API: {BASE_URL}")
        print(f"   • Documentation: {BASE_URL}/api/v1/docs")
        print(f"   • Health Check: {BASE_URL}/health")
    else:
        print("⚠️  Certains endpoints ont des problèmes.")
        print("Vérifiez les logs du serveur pour plus de détails.")
    
    print("\n🛠️  Fonctionnalités disponibles :")
    print("   ✅ API REST complète (15+ endpoints)")
    print("   ✅ Gestion DICOM (statut, connexions, études)")
    print("   ✅ Moteur IA (modèles, analyse, statut)")
    print("   ✅ Rapports (génération, consultation, stats)")
    print("   ✅ Monitoring (santé, métriques système)")
    print("   ✅ Documentation interactive (Swagger)")

if __name__ == "__main__":
    main()
