"""
Audio Processor Module
Processa áudios do WhatsApp usando Whisper (local) ou Vosk como fallback

Features:
- Converte OGG para WAV usando FFmpeg
- Transcreve com OpenAI Whisper (local)
- Fallback para Vosk se Whisper falhar
- Retorna texto transcrito
"""

import os
import logging
import subprocess
from pathlib import Path
from typing import Optional

# Configurar logging
logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self, whisper_model='small', use_vosk_fallback=True):
        """
        Inicializa o processador de áudio
        
        Args:
            whisper_model: Tamanho do modelo Whisper (tiny, base, small, medium, large)
            use_vosk_fallback: Se True, usa Vosk como fallback
        """
        self.whisper_model = whisper_model
        self.use_vosk_fallback = use_vosk_fallback
        self.whisper_loaded = False
        self.vosk_loaded = False
        
        # Adicionar FFmpeg ao PATH se instalado via chocolatey
        ffmpeg_paths = [
            r"C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin",
            r"C:\ffmpeg\bin",
            r"C:\Program Files\ffmpeg\bin"
        ]
        for ffmpeg_path in ffmpeg_paths:
            if os.path.exists(ffmpeg_path) and ffmpeg_path not in os.environ.get('PATH', ''):
                os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ['PATH']
                logger.info(f"✅ FFmpeg adicionado ao PATH: {ffmpeg_path}")
                break
        
        # Tentar carregar Whisper
        try:
            import whisper
            self.whisper = whisper.load_model(whisper_model)
            self.whisper_loaded = True
            logger.info(f"✅ Whisper modelo '{whisper_model}' carregado")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível carregar Whisper: {e}")
            
            if use_vosk_fallback:
                try:
                    from vosk import Model, KaldiRecognizer
                    import json
                    
                    # Baixar modelo Vosk se necessário
                    model_path = "models/vosk-model-small-pt-0.3"
                    if not os.path.exists(model_path):
                        logger.error(f"❌ Modelo Vosk não encontrado em {model_path}")
                        logger.info("📥 Baixe em: https://alphacephei.com/vosk/models")
                    else:
                        self.vosk_model = Model(model_path)
                        self.vosk_loaded = True
                        logger.info("✅ Vosk carregado como fallback")
                except Exception as e2:
                    logger.error(f"❌ Falha ao carregar Vosk: {e2}")
    
    def convert_audio(self, input_path: str, output_path: str = None) -> Optional[str]:
        """
        Converte áudio para WAV usando FFmpeg
        
        Args:
            input_path: Caminho do arquivo de entrada (.ogg, .mp3, etc)
            output_path: Caminho de saída (.wav). Se None, usa temp
            
        Returns:
            Caminho do arquivo WAV ou None em caso de erro
        """
        try:
            if output_path is None:
                output_path = input_path.replace('.ogg', '.wav').replace('.mp3', '.wav')
            
            # Comando FFmpeg: converter para WAV 16kHz mono
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-ar', '16000',  # 16kHz
                '-ac', '1',       # Mono
                '-y',             # Sobrescrever
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            
            logger.info(f"✅ Áudio convertido: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro no FFmpeg: {e.stderr.decode()}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao converter áudio: {e}")
            return None
    
    def transcribe_whisper(self, audio_path: str) -> Optional[str]:
        """
        Transcreve áudio usando Whisper
        
        Args:
            audio_path: Caminho do arquivo de áudio
            
        Returns:
            Texto transcrito ou None
        """
        if not self.whisper_loaded:
            logger.warning("⚠️ Whisper não está disponível")
            return None
        
        try:
            result = self.whisper.transcribe(
                audio_path,
                language='pt',
                task='transcribe'
            )
            
            text = result['text'].strip()
            logger.info(f"✅ Whisper transcreveu: {text[:100]}...")
            return text
            
        except Exception as e:
            logger.error(f"❌ Erro no Whisper: {e}")
            return None
    
    def transcribe_vosk(self, audio_path: str) -> Optional[str]:
        """
        Transcreve áudio usando Vosk (fallback)
        
        Args:
            audio_path: Caminho do arquivo WAV
            
        Returns:
            Texto transcrito ou None
        """
        if not self.vosk_loaded:
            logger.warning("⚠️ Vosk não está disponível")
            return None
        
        try:
            import wave
            import json
            from vosk import KaldiRecognizer
            
            wf = wave.open(audio_path, "rb")
            
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000, 32000, 48000]:
                logger.error("❌ Formato de áudio inválido para Vosk")
                return None
            
            rec = KaldiRecognizer(self.vosk_model, wf.getframerate())
            rec.SetWords(True)
            
            result_text = []
            
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if 'text' in result:
                        result_text.append(result['text'])
            
            # Resultado final
            final_result = json.loads(rec.FinalResult())
            if 'text' in final_result:
                result_text.append(final_result['text'])
            
            text = ' '.join(result_text).strip()
            logger.info(f"✅ Vosk transcreveu: {text[:100]}...")
            return text
            
        except Exception as e:
            logger.error(f"❌ Erro no Vosk: {e}")
            return None
    
    def process_audio(self, audio_path: str, delete_after: bool = True) -> Optional[str]:
        """
        Pipeline completo: converte e transcreve áudio
        
        Args:
            audio_path: Caminho do arquivo de áudio
            delete_after: Se True, apaga arquivos temporários
            
        Returns:
            Texto transcrito ou None
        """
        logger.info(f"🎤 Processando áudio: {audio_path}")
        
        # 1. Tentar Whisper direto (aceita OGG/MP3 sem conversão)
        text = None
        wav_path = None
        
        if self.whisper_loaded:
            logger.info(f"🤖 Tentando Whisper direto (sem conversão)...")
            text = self.transcribe_whisper(audio_path)
        
        # 2. Se falhar, tentar converter para WAV e tentar novamente
        if text is None:
            logger.info(f"⚠️ Whisper direto falhou, tentando converter...")
            wav_path = self.convert_audio(audio_path)
            if wav_path:
                if self.whisper_loaded:
                    text = self.transcribe_whisper(wav_path)
                
                # 3. Fallback para Vosk
                if text is None and self.vosk_loaded:
                    logger.info("⚠️ Tentando Vosk como fallback...")
                    text = self.transcribe_vosk(wav_path)
            else:
                logger.error("❌ Falha na conversão de áudio (FFmpeg pode não estar disponível)")
        
        # 4. Cleanup
        if delete_after:
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                if os.path.exists(wav_path) and wav_path != audio_path:
                    os.remove(wav_path)
                logger.info("🗑️ Arquivos temporários removidos")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao remover arquivos: {e}")
        
        if text:
            logger.info(f"✅ Transcrição completa: {len(text)} caracteres")
        else:
            logger.error("❌ Falha na transcrição")
        
        return text

# =========================================
# Uso Standalone
# =========================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    processor = AudioProcessor(whisper_model='small')
    
    # Teste
    test_audio = "temp/test_audio.ogg"
    if os.path.exists(test_audio):
        result = processor.process_audio(test_audio, delete_after=False)
        print(f"\n📝 Resultado: {result}")
    else:
        print(f"❌ Arquivo de teste não encontrado: {test_audio}")
