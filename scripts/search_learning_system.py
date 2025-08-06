#!/usr/bin/env python3
"""
Self-Learning Search Enhancement System for i3-help

Tracks unsuccessful searches, analyzes patterns, and automatically improves
the search dictionaries to create a self-healing, adaptive help system.

Features:
- Failed search detection and tracking
- Pattern analysis for improvement opportunities
- Automatic dictionary enhancement suggestions
- Smart growth limits and data management
- Learning feedback from user interactions
- Self-healing and maintenance mechanisms

This system learns from user behavior to continuously improve search accuracy
and coverage, making the i3-help utility more effective over time.
"""

import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import difflib

@dataclass
class FailedSearch:
    """Represents a failed search attempt"""
    query: str
    timestamp: float
    result_count: int
    suggested_matches: List[str]
    user_selected: Optional[str] = None
    user_feedback: Optional[str] = None  # "helpful", "not_helpful", "ignore"
    session_id: str = ""

@dataclass
class LearningInsight:
    """Represents a learning insight from pattern analysis"""
    pattern_type: str  # "typo", "synonym", "intent", "missing_term"
    original_term: str
    suggested_mapping: str
    confidence_score: float
    evidence_count: int
    first_seen: float
    last_seen: float
    user_confirmations: int = 0
    user_rejections: int = 0

@dataclass
class LearningConfig:
    """Configuration for the learning system"""
    max_failed_searches: int = 1000
    max_insights: int = 500
    min_confidence_threshold: float = 0.3
    auto_apply_threshold: float = 0.8
    cleanup_age_days: int = 30
    min_evidence_count: int = 2
    max_suggestions_per_query: int = 5
    typo_similarity_threshold: float = 0.6
    synonym_similarity_threshold: float = 0.4

class SearchLearningSystem:
    """Self-learning system for improving search functionality"""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.learning_data_path = data_path / 'learning_data.json'
        self.dictionaries_path = data_path / 'search_dictionaries.json'
        self.suggestions_path = data_path / 'learning_suggestions.json'
        
        self.config = LearningConfig()
        self.failed_searches: List[FailedSearch] = []
        self.insights: List[LearningInsight] = []
        self.dictionaries = {"synonyms": {}, "intents": {}, "typos": {}}
        
        self.load_learning_data()
        self.load_dictionaries()
    
    def load_learning_data(self) -> None:
        """Load learning data from storage"""
        try:
            if self.learning_data_path.exists():
                with open(self.learning_data_path, 'r') as f:
                    data = json.load(f)
                    
                    # Load failed searches
                    self.failed_searches = [
                        FailedSearch(**search_data) 
                        for search_data in data.get('failed_searches', [])
                    ]
                    
                    # Load insights
                    self.insights = [
                        LearningInsight(**insight_data)
                        for insight_data in data.get('insights', [])
                    ]
                    
                    # Load config if present
                    if 'config' in data:
                        for key, value in data['config'].items():
                            if hasattr(self.config, key):
                                setattr(self.config, key, value)
        except Exception as e:
            print(f"Warning: Could not load learning data: {e}")
    
    def save_learning_data(self) -> None:
        """Save learning data to storage"""
        try:
            data = {
                'failed_searches': [asdict(search) for search in self.failed_searches],
                'insights': [asdict(insight) for insight in self.insights],
                'config': asdict(self.config),
                'last_updated': time.time(),
                'version': '1.0'
            }
            
            # Ensure directory exists
            self.learning_data_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.learning_data_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save learning data: {e}")
    
    def load_dictionaries(self) -> None:
        """Load current search dictionaries"""
        try:
            if self.dictionaries_path.exists():
                with open(self.dictionaries_path, 'r') as f:
                    self.dictionaries = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load dictionaries: {e}")
    
    def save_dictionaries(self) -> None:
        """Save updated dictionaries"""
        try:
            with open(self.dictionaries_path, 'w') as f:
                json.dump(self.dictionaries, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save dictionaries: {e}")
    
    def record_failed_search(self, query: str, result_count: int, 
                           suggested_matches: List[str] = None,
                           session_id: str = "") -> None:
        """Record a failed or poor search result"""
        if not query.strip():
            return
        
        failed_search = FailedSearch(
            query=query.lower().strip(),
            timestamp=time.time(),
            result_count=result_count,
            suggested_matches=suggested_matches or [],
            session_id=session_id
        )
        
        self.failed_searches.append(failed_search)
        
        # Maintain size limits
        if len(self.failed_searches) > self.config.max_failed_searches:
            self.failed_searches = self.failed_searches[-self.config.max_failed_searches:]
        
        # Analyze for immediate learning opportunities
        self._analyze_recent_failure(failed_search)
        
        self.save_learning_data()
    
    def record_user_selection(self, query: str, selected_binding: str) -> None:
        """Record when user selects a binding after a search"""
        # Find recent failed search for this query
        recent_searches = [
            search for search in reversed(self.failed_searches[-10:])
            if search.query == query.lower().strip() and 
               search.user_selected is None and
               time.time() - search.timestamp < 300  # Within 5 minutes
        ]
        
        if recent_searches:
            recent_searches[0].user_selected = selected_binding
            self._analyze_user_selection(recent_searches[0])
            self.save_learning_data()
    
    def record_user_feedback(self, query: str, feedback: str) -> None:
        """Record user feedback on suggestions"""
        recent_searches = [
            search for search in reversed(self.failed_searches[-5:])
            if search.query == query.lower().strip() and
               time.time() - search.timestamp < 300
        ]
        
        if recent_searches:
            recent_searches[0].user_feedback = feedback
            self.save_learning_data()
    
    def _analyze_recent_failure(self, failed_search: FailedSearch) -> None:
        """Analyze a recent failure for learning opportunities"""
        query = failed_search.query
        
        # Check for typos by comparing with existing dictionary terms
        self._check_for_typos(query)
        
        # Look for synonym opportunities
        if failed_search.suggested_matches:
            self._analyze_potential_synonyms(query, failed_search.suggested_matches)
        
        # Check for intent patterns
        self._analyze_intent_patterns(query)
    
    def _analyze_user_selection(self, search: FailedSearch) -> None:
        """Analyze user selection to learn new mappings"""
        if not search.user_selected:
            return
        
        query = search.query
        selected = search.user_selected.lower()
        
        # Extract keywords from the selected binding
        selected_words = re.findall(r'\b\w+\b', selected)
        query_words = re.findall(r'\b\w+\b', query)
        
        # Look for synonym opportunities
        for q_word in query_words:
            for s_word in selected_words:
                if q_word != s_word and len(q_word) > 2 and len(s_word) > 2:
                    self._suggest_synonym_mapping(q_word, s_word, evidence_source="user_selection")
    
    def _check_for_typos(self, query: str) -> None:
        """Check if query might be a typo of existing terms"""
        existing_terms = set()
        
        # Collect existing terms from dictionaries
        for synonyms in self.dictionaries.get('synonyms', {}).values():
            existing_terms.update(synonyms)
        existing_terms.update(self.dictionaries.get('synonyms', {}).keys())
        existing_terms.update(self.dictionaries.get('typos', {}).values())
        
        # Find close matches
        close_matches = difflib.get_close_matches(
            query, existing_terms, n=3, cutoff=self.config.typo_similarity_threshold
        )
        
        for match in close_matches:
            confidence = difflib.SequenceMatcher(None, query, match).ratio()
            self._add_insight(
                pattern_type="typo",
                original_term=query,
                suggested_mapping=match,
                confidence_score=confidence,
                evidence_source="similarity_analysis"
            )
    
    def _analyze_potential_synonyms(self, query: str, suggested_matches: List[str]) -> None:
        """Analyze suggested matches for synonym opportunities"""
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        
        for match in suggested_matches:
            match_words = set(re.findall(r'\b\w+\b', match.lower()))
            
            # Find words that appear in match but not in query
            potential_synonyms = match_words - query_words
            
            for q_word in query_words:
                for potential_synonym in potential_synonyms:
                    if len(q_word) > 2 and len(potential_synonym) > 2:
                        # Calculate similarity
                        similarity = difflib.SequenceMatcher(
                            None, q_word, potential_synonym
                        ).ratio()
                        
                        if similarity > self.config.synonym_similarity_threshold:
                            self._suggest_synonym_mapping(
                                q_word, potential_synonym, 
                                confidence_score=similarity,
                                evidence_source="match_analysis"
                            )
    
    def _analyze_intent_patterns(self, query: str) -> None:
        """Analyze query for intent patterns"""
        # Common intent patterns
        intent_patterns = {
            r'\b(open|launch|start)\s+(\w+)': 'launch_application',
            r'\b(take|make|capture)\s+(screenshot|picture|snap)': 'screenshot',
            r'\b(change|adjust|set)\s+(volume|sound)': 'audio_control',
            r'\b(switch|go|move)\s+(workspace|desktop)': 'workspace_navigation',
            r'\b(close|kill|exit)\s+(window|app)': 'window_management'
        }
        
        for pattern, intent_category in intent_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                self._add_insight(
                    pattern_type="intent",
                    original_term=query,
                    suggested_mapping=intent_category,
                    confidence_score=0.7,
                    evidence_source="pattern_matching"
                )
    
    def _suggest_synonym_mapping(self, original: str, synonym: str, 
                               confidence_score: float = 0.5,
                               evidence_source: str = "analysis") -> None:
        """Suggest a new synonym mapping"""
        self._add_insight(
            pattern_type="synonym",
            original_term=original,
            suggested_mapping=synonym,
            confidence_score=confidence_score,
            evidence_source=evidence_source
        )
    
    def _add_insight(self, pattern_type: str, original_term: str, 
                    suggested_mapping: str, confidence_score: float,
                    evidence_source: str = "") -> None:
        """Add a learning insight"""
        # Check if this insight already exists
        existing_insight = None
        for insight in self.insights:
            if (insight.pattern_type == pattern_type and 
                insight.original_term == original_term and
                insight.suggested_mapping == suggested_mapping):
                existing_insight = insight
                break
        
        current_time = time.time()
        
        if existing_insight:
            # Update existing insight
            existing_insight.evidence_count += 1
            existing_insight.last_seen = current_time
            existing_insight.confidence_score = min(
                1.0, existing_insight.confidence_score + 0.1
            )
        else:
            # Create new insight
            insight = LearningInsight(
                pattern_type=pattern_type,
                original_term=original_term,
                suggested_mapping=suggested_mapping,
                confidence_score=confidence_score,
                evidence_count=1,
                first_seen=current_time,
                last_seen=current_time
            )
            self.insights.append(insight)
        
        # Maintain size limits
        if len(self.insights) > self.config.max_insights:
            # Remove oldest, lowest confidence insights
            self.insights.sort(key=lambda x: (x.confidence_score, x.last_seen))
            self.insights = self.insights[-self.config.max_insights:]
    
    def get_improvement_suggestions(self) -> Dict[str, List[Dict]]:
        """Get suggestions for improving the search dictionaries"""
        suggestions = {
            'typo': [],
            'typos': [],  # alias for backward compatibility
            'synonym': [],
            'synonyms': [],  # alias for backward compatibility
            'intent': [],
            'intents': [],  # alias for backward compatibility
            'high_confidence': []
        }
        
        for insight in self.insights:
            if (insight.evidence_count >= self.config.min_evidence_count and
                insight.confidence_score >= self.config.min_confidence_threshold):
                
                suggestion = {
                    'original': insight.original_term,
                    'suggestion': insight.suggested_mapping,
                    'confidence': insight.confidence_score,
                    'evidence_count': insight.evidence_count,
                    'confirmations': insight.user_confirmations,
                    'rejections': insight.user_rejections
                }
                
                # Add to both singular and plural forms for compatibility
                pattern_type = insight.pattern_type
                if pattern_type in suggestions:
                    suggestions[pattern_type].append(suggestion)
                
                # Also add to plural form if it exists
                plural_form = pattern_type + 's'
                if plural_form in suggestions:
                    suggestions[plural_form].append(suggestion)
                
                # High confidence suggestions for auto-application
                if insight.confidence_score >= self.config.auto_apply_threshold:
                    suggestions['high_confidence'].append(suggestion)
        
        # Sort by confidence and evidence
        for category in suggestions:
            suggestions[category].sort(
                key=lambda x: (x['confidence'], x['evidence_count']), 
                reverse=True
            )
        
        return suggestions
    
    def apply_high_confidence_suggestions(self) -> int:
        """Automatically apply high confidence suggestions"""
        suggestions = self.get_improvement_suggestions()
        applied_count = 0
        
        for suggestion in suggestions['high_confidence']:
            pattern_type = None
            for category, items in suggestions.items():
                if suggestion in items and category != 'high_confidence':
                    pattern_type = category
                    break
            
            if not pattern_type:
                continue
            
            original = suggestion['original']
            mapping = suggestion['suggestion']
            
            try:
                if pattern_type == 'typos':
                    if original not in self.dictionaries.get('typos', {}):
                        self.dictionaries.setdefault('typos', {})[original] = mapping
                        applied_count += 1
                
                elif pattern_type == 'synonyms':
                    synonyms = self.dictionaries.setdefault('synonyms', {})
                    if mapping in synonyms:
                        if original not in synonyms[mapping]:
                            synonyms[mapping].append(original)
                            applied_count += 1
                    else:
                        synonyms[original] = [mapping]
                        applied_count += 1
                
                elif pattern_type == 'intents':
                    intents = self.dictionaries.setdefault('intents', {})
                    if mapping in intents:
                        if original not in intents[mapping]:
                            intents[mapping].append(original)
                            applied_count += 1
                    else:
                        intents[original] = [mapping]
                        applied_count += 1
                        
            except Exception as e:
                print(f"Warning: Could not apply suggestion: {e}")
        
        if applied_count > 0:
            self.save_dictionaries()
        
        return applied_count
    
    def cleanup_old_data(self) -> int:
        """Clean up old learning data"""
        cutoff_time = time.time() - (self.config.cleanup_age_days * 24 * 3600)
        
        # Clean old failed searches
        original_search_count = len(self.failed_searches)
        self.failed_searches = [
            search for search in self.failed_searches
            if search.timestamp > cutoff_time
        ]
        
        # Clean old insights with low confidence
        original_insight_count = len(self.insights)
        self.insights = [
            insight for insight in self.insights
            if (insight.last_seen > cutoff_time or 
                insight.confidence_score > self.config.min_confidence_threshold)
        ]
        
        removed_count = (original_search_count - len(self.failed_searches) + 
                        original_insight_count - len(self.insights))
        
        if removed_count > 0:
            self.save_learning_data()
        
        return removed_count
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about the learning system"""
        current_time = time.time()
        recent_failures = [
            search for search in self.failed_searches
            if current_time - search.timestamp < 24 * 3600  # Last 24 hours
        ]
        
        return {
            'total_failed_searches': len(self.failed_searches),
            'recent_failed_searches': len(recent_failures),
            'total_insights': len(self.insights),
            'high_confidence_insights': len([
                insight for insight in self.insights
                if insight.confidence_score >= self.config.auto_apply_threshold
            ]),
            'user_confirmed_insights': len([
                insight for insight in self.insights
                if insight.user_confirmations > 0
            ]),
            'pattern_breakdown': {
                pattern_type: len([
                    insight for insight in self.insights
                    if insight.pattern_type == pattern_type
                ])
                for pattern_type in ['typo', 'synonym', 'intent']
            },
            'dictionary_sizes': {
                'synonyms': len(self.dictionaries.get('synonyms', {})),
                'intents': len(self.dictionaries.get('intents', {})),
                'typos': len(self.dictionaries.get('typos', {}))
            }
        }
    
    def suggest_closest_matches(self, query: str, available_bindings: List[str]) -> List[str]:
        """Suggest closest matches for a failed search"""
        if not query.strip():
            return []
        
        # Use difflib to find close matches
        suggestions = difflib.get_close_matches(
            query.lower(), 
            [binding.lower() for binding in available_bindings],
            n=self.config.max_suggestions_per_query,
            cutoff=0.3
        )
        
        # Find original casing
        suggestion_map = {binding.lower(): binding for binding in available_bindings}
        return [suggestion_map.get(suggestion, suggestion) for suggestion in suggestions]
