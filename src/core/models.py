"""Data models for the dashboard"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

@dataclass
class IncidentData:
    """Incident data model"""
    number: str
    priority: int
    state: str
    short_description: str
    assignment_group: str = None
    opened_at: datetime = None
    resolved_at: datetime = None

@dataclass
class ServiceRequestData:
    """Service request data model"""
    number: str
    state: str
    short_description: str
    assignment_group: str = None
    approval: str = None
    opened_at: datetime = None

@dataclass
class SystemHealthData:
    """System health data model"""
    name: str
    status: str
    response_time: float = 0.0
    last_check: datetime = None

@dataclass
class DashboardMetrics:
    """Aggregated dashboard metrics"""
    incidents: Dict[str, Any] = field(default_factory=dict)
    service_requests: Dict[str, Any] = field(default_factory=dict)
    system_health: Dict[str, Any] = field(default_factory=dict)
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)