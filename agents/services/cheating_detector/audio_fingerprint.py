"""
Audio Fingerprinting for Multi-Speaker Detection.

Detects if multiple people are speaking (someone helping the candidate).

Uses:
- Voice embeddings (speaker verification)
- Pitch analysis (different vocal characteristics)
- Spectral features (voice "fingerprint")
"""

import librosa
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import cosine

logger = logging.getLogger(__name__)

class AudioFingerprinter:
    """
    Multi-speaker detection using audio fingerprinting.
    
    Detects:
    1. Multiple distinct voices in audio
    2. Voice changes (impersonation or assistance)
    3. Background voices (someone helping)
    """
    
    def __init__(self):
        """Initialize audio fingerprinter."""
        logger.info("Initializing Audio Fingerprinter...")
        
        # Parameters
        self.segment_duration = 2.0  # seconds
        self.hop_length = 512
        self.n_mfcc = 20
        
        # Thresholds
        self.MIN_SEGMENTS = 5  # Minimum segments needed for analysis
        self.CLUSTER_EPS = 0.3  # DBSCAN epsilon for clustering
        
        logger.info("✅ Audio Fingerprinter initialized")
    
    def detect_multiple_speakers(self, audio_path: str) -> Dict:
        """
        Detect if multiple speakers are present in audio.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Multi-speaker detection results
        """
        logger.info(f"Detecting multiple speakers: {audio_path}")
        
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=16000)
            duration = librosa.get_duration(y=y, sr=sr)
            
            if duration < 5.0:
                logger.warning("Audio too short for reliable speaker detection")
                return {
                    'multiple_speakers_detected': False,
                    'num_speakers': 1,
                    'confidence': 0.5,
                    'warning': 'Audio too short for analysis'
                }
            
            # Extract voice embeddings from segments
            embeddings = self._extract_segment_embeddings(y, sr)
            
            if len(embeddings) < self.MIN_SEGMENTS:
                logger.warning(f"Insufficient segments: {len(embeddings)}")
                return {
                    'multiple_speakers_detected': False,
                    'num_speakers': 1,
                    'confidence': 0.5,
                    'warning': 'Insufficient voiced segments'
                }
            
            # Cluster embeddings to identify distinct speakers
            num_speakers, labels = self._cluster_speakers(embeddings)
            
            # Calculate confidence
            confidence = self._calculate_confidence(embeddings, labels, num_speakers)
            
            # Additional verification: pitch analysis
            pitch_verification = self._verify_with_pitch(y, sr, labels)
            
            multiple_speakers = num_speakers > 1 and pitch_verification
            
            result = {
                'multiple_speakers_detected': multiple_speakers,
                'num_speakers': int(num_speakers),
                'confidence': round(confidence, 3),
                'segments_analyzed': len(embeddings),
                'pitch_verification': pitch_verification,
                'speaker_distribution': self._get_speaker_distribution(labels)
            }
            
            logger.info(f"✅ Speaker detection: {num_speakers} speakers detected")
            return result
            
        except Exception as e:
            logger.error(f"Multi-speaker detection failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                'multiple_speakers_detected': False,
                'num_speakers': 1,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _extract_segment_embeddings(
        self,
        y: np.ndarray,
        sr: int
    ) -> List[np.ndarray]:
        """
        Extract voice embeddings from audio segments.
        
        Each segment is represented by MFCC features.
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            List of embedding vectors
        """
        # Calculate segment length in samples
        segment_samples = int(self.segment_duration * sr)
        hop_samples = segment_samples // 2  # 50% overlap
        
        embeddings = []
        
        # Process segments
        for start in range(0, len(y) - segment_samples, hop_samples):
            end = start + segment_samples
            segment = y[start:end]
            
            # Check if segment has speech (energy threshold)
            energy = np.sum(segment ** 2) / len(segment)
            
            if energy < 0.001:  # Too quiet, likely silence
                continue
            
            # Extract MFCC features (voice fingerprint)
            mfcc = librosa.feature.mfcc(
                y=segment,
                sr=sr,
                n_mfcc=self.n_mfcc,
                hop_length=self.hop_length
            )
            
            # Average over time to get single vector per segment
            embedding = np.mean(mfcc, axis=1)
            
            # Normalize
            embedding = embedding / np.linalg.norm(embedding)
            
            embeddings.append(embedding)
        
        logger.debug(f"Extracted {len(embeddings)} segment embeddings")
        return embeddings
    
    def _cluster_speakers(
        self,
        embeddings: List[np.ndarray]
    ) -> Tuple[int, np.ndarray]:
        """
        Cluster embeddings to identify distinct speakers.
        
        Uses DBSCAN clustering (density-based).
        
        Args:
            embeddings: List of embedding vectors
            
        Returns:
            (num_speakers, cluster_labels)
        """
        # Convert to matrix
        X = np.array(embeddings)
        
        # DBSCAN clustering
        clustering = DBSCAN(
            eps=self.CLUSTER_EPS,
            min_samples=3,
            metric='cosine'
        ).fit(X)
        
        labels = clustering.labels_
        
        # Count speakers (exclude noise points labeled as -1)
        unique_labels = set(labels)
        unique_labels.discard(-1)
        num_speakers = len(unique_labels)
        
        # If no clusters found, assume 1 speaker
        if num_speakers == 0:
            num_speakers = 1
            labels = np.zeros(len(embeddings), dtype=int)
        
        logger.debug(f"Clustering found {num_speakers} speaker(s)")
        return num_speakers, labels
    
    def _calculate_confidence(
        self,
        embeddings: List[np.ndarray],
        labels: np.ndarray,
        num_speakers: int
    ) -> float:
        """
        Calculate confidence in speaker detection.
        
        High confidence if:
        - Clusters are well-separated
        - Each cluster has multiple samples
        - Low variance within clusters
        
        Args:
            embeddings: Embedding vectors
            labels: Cluster labels
            num_speakers: Number of detected speakers
            
        Returns:
            Confidence score (0-1)
        """
        if num_speakers == 1:
            return 0.9  # High confidence in single speaker
        
        X = np.array(embeddings)
        
        # Calculate inter-cluster distance
        cluster_centers = []
        for speaker_id in range(num_speakers):
            mask = labels == speaker_id
            if np.sum(mask) > 0:
                center = np.mean(X[mask], axis=0)
                cluster_centers.append(center)
        
        if len(cluster_centers) < 2:
            return 0.5
        
        # Average pairwise distance between clusters
        inter_distances = []
        for i in range(len(cluster_centers)):
            for j in range(i+1, len(cluster_centers)):
                dist = 1 - cosine(cluster_centers[i], cluster_centers[j])
                inter_distances.append(dist)
        
        avg_inter_distance = np.mean(inter_distances)
        
        # Intra-cluster variance
        intra_variances = []
        for speaker_id in range(num_speakers):
            mask = labels == speaker_id
            cluster_points = X[mask]
            
            if len(cluster_points) > 1:
                center = cluster_centers[speaker_id]
                variance = np.mean([
                    cosine(point, center) for point in cluster_points
                ])
                intra_variances.append(variance)
        
        avg_intra_variance = np.mean(intra_variances) if intra_variances else 0
        
        # Confidence based on separation
        # High inter-distance and low intra-variance = high confidence
        confidence = avg_inter_distance * (1 - avg_intra_variance)
        
        return min(max(confidence, 0.0), 1.0)
    
    def _verify_with_pitch(
        self,
        y: np.ndarray,
        sr: int,
        labels: np.ndarray
    ) -> bool:
        """
        Verify multi-speaker detection using pitch analysis.
        
        Different speakers typically have different pitch ranges.
        
        Args:
            y: Audio time series
            sr: Sample rate
            labels: Speaker cluster labels
            
        Returns:
            True if pitch analysis confirms multiple speakers
        """
        try:
            # Extract pitch
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            
            # Get pitch values over time
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if len(pitch_values) < 10:
                return False
            
            # Calculate pitch statistics for segments
            segment_samples = int(self.segment_duration * sr)
            hop_samples = segment_samples // 2
            
            pitch_per_segment = []
            for start in range(0, len(y) - segment_samples, hop_samples):
                end = start + segment_samples
                # Get pitches in this time range
                start_time = start / sr
                end_time = end / sr
                
                # Approximate pitch for this segment
                segment_pitches = pitch_values[:min(len(pitch_values), 20)]
                if segment_pitches:
                    avg_pitch = np.mean(segment_pitches)
                    pitch_per_segment.append(avg_pitch)
            
            if len(pitch_per_segment) < 5:
                return False
            
            # Check if pitch varies significantly (different speakers)
            pitch_std = np.std(pitch_per_segment)
            pitch_mean = np.mean(pitch_per_segment)
            
            # Coefficient of variation
            cv = pitch_std / pitch_mean if pitch_mean > 0 else 0
            
            # Significant variation suggests multiple speakers
            return cv > 0.15  # 15% variation
            
        except Exception as e:
            logger.debug(f"Pitch verification failed: {e}")
            return False
    
    def _get_speaker_distribution(self, labels: np.ndarray) -> Dict[int, float]:
        """
        Get distribution of segments per speaker.
        
        Args:
            labels: Speaker cluster labels
            
        Returns:
            Dict mapping speaker_id to percentage of segments
        """
        unique, counts = np.unique(labels[labels >= 0], return_counts=True)
        total = len(labels[labels >= 0])
        
        distribution = {
            int(speaker_id): float(count / total)
            for speaker_id, count in zip(unique, counts)
        }
        
        return distribution

# Global instance
audio_fingerprinter = AudioFingerprinter()