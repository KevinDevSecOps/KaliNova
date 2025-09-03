"""
Módulo de análisis de red avanzado con GraphQL
"""

import graphene
from graphene import ObjectType, String, List, Float

class NetworkScanResult(ObjectType):
    """Type GraphQL para resultados de red"""
    target = String()
    open_ports = List(String)
    services = List(String)
    vulnerabilities = List(String)
    risk_score = Float()

class NetworkQuery(ObjectType):
    """Queries GraphQL para análisis de red"""
    scan_network = graphene.List(
        NetworkScanResult,
        target=graphene.String(required=True)
    )
    
    def resolve_scan_network(self, info, target):
        """Resolver para escaneo de red"""
        scanner = NetworkScanner()
        results = scanner.advanced_scan(target)
        return [NetworkScanResult(**result) for result in results]

# Schema GraphQL
schema = graphene.Schema(query=NetworkQuery)