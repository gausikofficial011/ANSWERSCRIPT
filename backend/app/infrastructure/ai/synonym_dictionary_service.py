"""
infrastructure/ai/synonym_dictionary_service.py — Synonym Dictionary Service
"""

from __future__ import annotations


class SynonymDictionaryService:
    """
    Expands expected keywords to include configured synonym rings for flexible matching.
    """

    def __init__(self) -> None:
        # Predefined synonym rings mapping keywords to their equivalent phrases
        self.synonyms = {
            "gravity": [
                "gravitational force",
                "attractive force",
                "pulling force",
                "pull force",
                "attractive power"
            ],
            "orbit": [
                "orbiting",
                "revolving",
                "moving around",
                "orbits"
            ],
            "energy": [
                "power"
            ],
            "pump blood": [
                "pumps blood",
                "pumping blood",
                "circulate blood",
                "circulating blood",
                "circulates blood",
                "blood circulation",
                "pump to circulate blood",
                "pump to circulate"
            ],
            "carbon dioxide": [
                "co2"
            ],
            "glucose": [
                "sugar",
                "energy"
            ],
            "inertia": [
                "resistance to change",
                "inertial",
                "things keep doing what they are doing",
                "keep doing what they are doing"
            ],
            "invisible force": [
                "attractive force",
                "gravitational force",
                "gravity",
                "pulling force",
                "pull force",
                "force",
                "attractive power",
                "invisible pull force"
            ],
            "planets in orbit": [
                "planets orbiting",
                "orbiting the sun",
                "orbiting",
                "orbit",
                "revolving"
            ],
            "ground": [
                "earth",
                "earth's surface",
                "ground"
            ],
            "pulls objects": [
                "pulls things",
                "pulling things",
                "pull force",
                "pull",
                "attracts objects"
            ],
            "removing carbon dioxide": [
                "transporting carbon dioxide away",
                "carbon dioxide wastes",
                "co2 removal",
                "removing co2"
            ],
            "wastes": [
                "carbon dioxide wastes",
                "wastes away",
                "waste products",
                "waste"
            ],
            "tissues": [
                "body",
                "body tissues",
                "veins",
                "cells"
            ],
            "external force": [
                "force",
                "force hits them",
                "unbalanced force",
                "external forces"
            ],
            "rest": [
                "things keep doing what they are doing",
                "keep doing what they are doing",
                "not moving"
            ],
            "motion": [
                "things keep doing what they are doing",
                "keep doing what they are doing",
                "moving"
            ]
        }

    def expand_keywords(self, keywords: list[str]) -> set[str]:
        """
        Expands a list of expected keywords using synonym rings.
        """
        expanded = set()
        for kw in keywords:
            expanded.add(kw)
            clean_kw = kw.strip().lower()
            
            # 1. Check direct matches in the synonym rings
            if clean_kw in self.synonyms:
                for syn in self.synonyms[clean_kw]:
                    expanded.add(syn)
            
            # 2. Check if clean_kw matches any ring key, adding all related synonyms
            for key, syns in self.synonyms.items():
                if key == clean_kw:
                    for syn in syns:
                        expanded.add(syn)
                elif clean_kw in syns:
                    expanded.add(key)
                    for syn in syns:
                        expanded.add(syn)
                        
        return expanded
