import streamlit as st
import torch
import subprocess
import re
from typing import Tuple, Optional

class GPUDetector:
    def __init__(self):
        self.gpu_info = None
        self.vram_gb = 0
        self.device = "cpu"
        self.optimal_model = "base"
    
    def detect_gpu(self) -> Tuple[bool, str, float]:
        """GPU 감지 및 VRAM 확인"""
        try:
            # CUDA 사용 가능 여부 확인
            if not torch.cuda.is_available():
                st.warning("CUDA를 사용할 수 없습니다. PyTorch가 CUDA를 지원하지 않거나 GPU 드라이버가 설치되지 않았습니다.")
                return False, "CPU", 0.0
            
            # GPU 정보 수집
            gpu_count = torch.cuda.device_count()
            if gpu_count == 0:
                st.warning("CUDA 디바이스를 찾을 수 없습니다.")
                return False, "CPU", 0.0
            
            # 첫 번째 GPU 정보 가져오기
            gpu_name = torch.cuda.get_device_name(0)
            
            # nvidia-smi로 VRAM 정보 가져오기
            vram_gb = self._get_vram_from_nvidia_smi()
            
            if vram_gb == 0:
                # nvidia-smi 실패 시 PyTorch로 추정
                vram_gb = self._estimate_vram_from_torch()
            
            # GTX 1650 특별 처리 (4GB VRAM)
            if "GTX 1650" in gpu_name or "1650" in gpu_name or "GeForce GTX 1650" in gpu_name:
                vram_gb = 4.0  # GTX 1650은 4GB VRAM
            
            # 기타 GPU들에 대한 VRAM 추정
            if vram_gb < 2.0:  # VRAM이 너무 작으면 추정값 사용
                if "RTX" in gpu_name:
                    if "3080" in gpu_name or "4070" in gpu_name:
                        vram_gb = 10.0
                    elif "3060" in gpu_name:
                        vram_gb = 8.0
                    elif "2060" in gpu_name:
                        vram_gb = 6.0
                elif "GTX" in gpu_name:
                    if "1660" in gpu_name:
                        vram_gb = 6.0
                    elif "1650" in gpu_name:
                        vram_gb = 4.0
                    elif "1060" in gpu_name:
                        vram_gb = 6.0
            
            self.gpu_info = {
                "name": gpu_name,
                "count": gpu_count,
                "vram_gb": vram_gb
            }
            
            return True, gpu_name, vram_gb
            
        except Exception as e:
            st.warning(f"GPU 감지 실패: {str(e)}")
            st.info("CPU 모드로 실행됩니다.")
            return False, "CPU", 0.0
    
    def _get_vram_from_nvidia_smi(self) -> float:
        """nvidia-smi로 VRAM 정보 가져오기"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                vram_mb = int(result.stdout.strip().split('\n')[0])
                return vram_mb / 1024  # MB를 GB로 변환
            return 0.0
            
        except Exception:
            return 0.0
    
    def _estimate_vram_from_torch(self) -> float:
        """PyTorch로 VRAM 추정"""
        try:
            # GPU 메모리 정보 가져오기
            total_memory = torch.cuda.get_device_properties(0).total_memory
            return total_memory / (1024**3)  # bytes를 GB로 변환
        except Exception:
            return 0.0
    
    def select_optimal_whisper_model(self, vram_gb: float) -> str:
        """VRAM 용량에 따른 최적 Whisper 모델 선택"""
        if vram_gb >= 10:
            return "large-v3"  # 10-12GB 필요
        elif vram_gb >= 7:
            return "medium"    # 7GB 필요
        elif vram_gb >= 6:
            return "small"     # 6GB 이상에서 small 사용
        elif vram_gb >= 2:
            return "base"      # 2-5GB에서 base 사용 (4GB 포함)
        else:
            return "tiny"      # 1GB 필요
    
    def get_device_info(self) -> dict:
        """디바이스 정보 반환"""
        gpu_available, gpu_name, vram_gb = self.detect_gpu()
        
        if gpu_available:
            optimal_model = self.select_optimal_whisper_model(vram_gb)
            device = "cuda"
        else:
            optimal_model = "base"  # CPU에서는 base 모델 사용
            device = "cpu"
        
        return {
            "gpu_available": gpu_available,
            "gpu_name": gpu_name,
            "vram_gb": vram_gb,
            "device": device,
            "optimal_model": optimal_model
        }

def get_whisper_model_info() -> dict:
    """Whisper 모델별 VRAM 요구사항 정보"""
    return {
        "tiny": {"vram_gb": 1, "description": "CPU로도 실행 가능"},
        "base": {"vram_gb": 2, "description": "보급형 GPU로도 실행 가능"},
        "small": {"vram_gb": 4, "description": "RTX 2060 이상 권장"},
        "medium": {"vram_gb": 7, "description": "RTX 3060 이상 권장"},
        "large-v3": {"vram_gb": 10, "description": "RTX 3080 또는 RTX 4070 이상 권장"}
    }

def display_gpu_status():
    """GPU 상태를 Streamlit에 표시"""
    detector = GPUDetector()
    device_info = detector.get_device_info()
    
    if device_info["gpu_available"]:
        # 간결한 한 줄 표시
        st.success(f"✅ GPU 감지됨: {device_info['gpu_name']} ({device_info['vram_gb']:.1f}GB VRAM)")
        
        # 모델별 VRAM 요구사항 표시 (간결하게)
        model_info = get_whisper_model_info()
        st.write("**Whisper 모델별 VRAM 요구사항:**")
        for model, info in model_info.items():
            status = "✅" if device_info["vram_gb"] >= info["vram_gb"] else "❌"
            st.write(f"{status} **{model}**: {info['vram_gb']}GB - {info['description']}")
    else:
        st.warning("⚠️ GPU를 감지할 수 없습니다. CPU 모드로 실행됩니다.")
        st.info("🎯 CPU 모드: BART 모델 사용")
    
    return device_info
