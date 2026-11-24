"""Avatar Generation Service."""

from services.avatar_generator.cv_parser import cv_parser
from services.avatar_generator.generator import avatar_generator

__all__ = ['cv_parser', 'avatar_generator']