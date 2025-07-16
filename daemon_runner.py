#!/usr/bin/env python3
"""
Daemon Runner para Sistema de Automação de Apostas
Executa e monitora continuamente o sistema principal
"""

import os
import sys
import time
import subprocess
import signal
import json
from datetime import datetime
from pathlib import Path

class BettingDaemon:
    def __init__(self):
        self.base_dir = Path("/home/ubuntu/betting_automation")
        self.run_script = self.base_dir / "run.sh"
        self.log_dir = self.base_dir / "logs"
        self.daemon_log = self.log_dir / "daemon.log"
        self.status_file = self.base_dir / "daemon_status.json"
        
        self.process = None
        self.running = False
        self.restart_count = 0
        self.max_restarts = 10
        self.restart_delay = 30  # segundos
        
        # Criar diretórios necessários
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar handlers de sinal
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _log(self, message):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] DAEMON: {message}"
        print(log_message)
        
        # Escrever no arquivo de log
        with open(self.daemon_log, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    
    def _update_status(self, status, details=None):
        """Atualiza arquivo de status"""
        status_data = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "restart_count": self.restart_count,
            "pid": self.process.pid if self.process else None,
            "details": details
        }
        
        with open(self.status_file, "w", encoding="utf-8") as f:
            json.dump(status_data, f, indent=2)
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais de interrupção"""
        self._log(f"Recebido sinal {signum}, parando daemon...")
        self.stop()
        sys.exit(0)
    
    def _start_betting_system(self):
        """Inicia o sistema de apostas"""
        try:
            self._log("Iniciando sistema de automação de apostas...")
            
            # Mudar para diretório do projeto
            os.chdir(self.base_dir)
            
            # Executar script principal em modo daemon
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            
            # Comando para executar o sistema principal diretamente
            cmd = [
                "bash", "-c",
                "source venv/bin/activate && python3 src/main.py"
            ]
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                env=env,
                cwd=self.base_dir
            )
            
            self._log(f"Sistema iniciado com PID: {self.process.pid}")
            self._update_status("running", f"PID: {self.process.pid}")
            
            return True
            
        except Exception as e:
            self._log(f"Erro ao iniciar sistema: {e}")
            self._update_status("error", str(e))
            return False
    
    def _monitor_process(self):
        """Monitora o processo principal"""
        while self.running and self.process:
            try:
                # Verificar se processo ainda está rodando
                poll_result = self.process.poll()
                
                if poll_result is not None:
                    # Processo terminou
                    self._log(f"Processo terminou com código: {poll_result}")
                    
                    # Ler saída do processo
                    if self.process.stdout:
                        output = self.process.stdout.read()
                        if output:
                            self._log(f"Saída do processo: {output}")
                    
                    self.process = None
                    
                    if self.running and self.restart_count < self.max_restarts:
                        self._log(f"Reiniciando sistema (tentativa {self.restart_count + 1}/{self.max_restarts})...")
                        self.restart_count += 1
                        time.sleep(self.restart_delay)
                        
                        if self._start_betting_system():
                            continue
                        else:
                            self._log("Falha ao reiniciar sistema")
                            break
                    else:
                        self._log("Limite de reinicializações atingido ou daemon parado")
                        break
                
                # Aguardar antes da próxima verificação
                time.sleep(10)
                
            except Exception as e:
                self._log(f"Erro no monitoramento: {e}")
                time.sleep(10)
    
    def start(self):
        """Inicia o daemon"""
        self._log("Iniciando daemon de automação de apostas...")
        self.running = True
        self.restart_count = 0
        
        # Verificar se ambiente está configurado
        if not (self.base_dir / ".env").exists():
            self._log("ERRO: Arquivo .env não encontrado!")
            self._update_status("error", "Arquivo .env não encontrado")
            return False
        
        if not (self.base_dir / "venv").exists():
            self._log("ERRO: Ambiente virtual não encontrado!")
            self._update_status("error", "Ambiente virtual não encontrado")
            return False
        
        # Iniciar sistema
        if self._start_betting_system():
            self._monitor_process()
        else:
            self._log("Falha ao iniciar sistema inicial")
            self._update_status("error", "Falha ao iniciar sistema")
            return False
        
        self._log("Daemon finalizado")
        self._update_status("stopped")
        return True
    
    def stop(self):
        """Para o daemon"""
        self._log("Parando daemon...")
        self.running = False
        
        if self.process:
            try:
                self._log(f"Terminando processo {self.process.pid}...")
                self.process.terminate()
                
                # Aguardar término gracioso
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self._log("Forçando término do processo...")
                    self.process.kill()
                    self.process.wait()
                
                self._log("Processo terminado")
                
            except Exception as e:
                self._log(f"Erro ao parar processo: {e}")
        
        self._update_status("stopped")
    
    def status(self):
        """Retorna status atual"""
        if self.status_file.exists():
            with open(self.status_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"status": "unknown"}

def main():
    daemon = BettingDaemon()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            daemon.start()
        elif command == "stop":
            daemon.stop()
        elif command == "status":
            status = daemon.status()
            print(json.dumps(status, indent=2))
        else:
            print("Uso: python3 daemon_runner.py [start|stop|status]")
    else:
        # Modo padrão: iniciar daemon
        daemon.start()

if __name__ == "__main__":
    main()
