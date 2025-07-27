# Configuração para testes Windows com modem físico
import pytest
import serial
import serial.tools.list_ports
import subprocess
import platform
import winreg
from pathlib import Path

@pytest.fixture(scope="session")
def windows_modem_config():
    """Configuração para testes Windows com modem físico."""
    return {
        "ENV": "windows_modem",
        "PLATFORM": "Windows",
        "MODEM_TIMEOUT": 30,
        "BAUDRATE": 115200,
        "SMS_TIMEOUT": 60,
        "USSD_TIMEOUT": 45,
        "MAX_RETRIES": 3
    }

@pytest.fixture(scope="session")
def available_com_ports():
    """Lista portas COM disponíveis no sistema."""
    ports = serial.tools.list_ports.comports()
    return [(port.device, port.description, port.hwid) for port in ports]

@pytest.fixture(scope="session")  
def detect_gsm_modems(available_com_ports):
    """Detecta modems GSM conectados."""
    gsm_modems = []
    
    for port, description, hwid in available_com_ports:
        try:
            # Test if port responds to AT commands
            ser = serial.Serial(port, 115200, timeout=5)
            ser.write(b'AT\r\n')
            response = ser.readline().decode().strip()
            
            if 'OK' in response:
                # Test if it's a GSM modem
                ser.write(b'AT+CGMI\r\n')  # Get manufacturer
                manufacturer = ser.readline().decode().strip()
                
                ser.write(b'AT+CGMM\r\n')  # Get model
                model = ser.readline().decode().strip()
                
                gsm_modems.append({
                    "port": port,
                    "description": description,
                    "hwid": hwid,
                    "manufacturer": manufacturer,
                    "model": model
                })
            
            ser.close()
        except Exception as e:
            continue
    
    return gsm_modems

@pytest.fixture(scope="function")
def modem_connection(detect_gsm_modems):
    """Conexão com modem GSM para testes."""
    if not detect_gsm_modems:
        pytest.skip("Nenhum modem GSM detectado")
    
    # Use the first available modem
    modem_info = detect_gsm_modems[0]
    
    class ModemConnection:
        def __init__(self, port, baudrate=115200):
            self.port = port
            self.baudrate = baudrate
            self.serial = None
            self.connected = False
        
        def connect(self):
            try:
                self.serial = serial.Serial(
                    self.port, 
                    self.baudrate, 
                    timeout=10
                )
                
                # Test connection
                self.serial.write(b'AT\r\n')
                response = self.serial.readline().decode().strip()
                
                if 'OK' in response:
                    self.connected = True
                    return True
                    
            except Exception as e:
                return False
            
            return False
        
        def send_command(self, command, timeout=10):
            if not self.connected:
                return None
            
            try:
                self.serial.timeout = timeout
                self.serial.write(f'{command}\r\n'.encode())
                response = self.serial.readline().decode().strip()
                return response
            except Exception as e:
                return None
        
        def send_sms(self, number, message):
            if not self.connected:
                return False
            
            try:
                # Set text mode
                self.send_command('AT+CMGF=1')
                
                # Set recipient
                self.send_command(f'AT+CMGS="{number}"')
                
                # Send message
                self.serial.write(f'{message}\x1A'.encode())
                response = self.serial.readline().decode().strip()
                
                return 'OK' in response
                
            except Exception as e:
                return False
        
        def send_ussd(self, code):
            if not self.connected:
                return None
            
            try:
                response = self.send_command(f'AT+CUSD=1,"{code}",15', timeout=30)
                return response
            except Exception as e:
                return None
        
        def get_signal_strength(self):
            if not self.connected:
                return None
            
            response = self.send_command('AT+CSQ')
            return response
        
        def get_network_info(self):
            if not self.connected:
                return None
            
            operator = self.send_command('AT+COPS?')
            return operator
        
        def close(self):
            if self.serial and self.serial.is_open:
                self.serial.close()
            self.connected = False
    
    connection = ModemConnection(modem_info["port"])
    
    if connection.connect():
        yield connection
    else:
        pytest.skip(f"Não foi possível conectar ao modem em {modem_info['port']}")
    
    connection.close()

@pytest.fixture
def windows_system_info():
    """Informações do sistema Windows."""
    return {
        "platform": platform.platform(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version()
    }

@pytest.fixture
def check_driver_installation():
    """Verifica instalação de drivers GSM."""
    def check_drivers():
        drivers_found = []
        
        try:
            # Check Windows Device Manager via registry
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SYSTEM\CurrentControlSet\Enum\USB") as usb_key:
                
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(usb_key, i)
                        if "VID_" in subkey_name:
                            drivers_found.append(subkey_name)
                        i += 1
                    except WindowsError:
                        break
                        
        except Exception as e:
            pass
        
        return drivers_found
    
    return check_drivers

@pytest.fixture
def hardware_diagnostics(modem_connection):
    """Diagnósticos de hardware do modem."""
    def run_diagnostics():
        if not modem_connection.connected:
            return {"status": "error", "message": "Modem não conectado"}
        
        diagnostics = {
            "connection": "OK",
            "signal_strength": modem_connection.get_signal_strength(),
            "network_info": modem_connection.get_network_info(),
            "manufacturer": modem_connection.send_command("AT+CGMI"),
            "model": modem_connection.send_command("AT+CGMM"),
            "firmware": modem_connection.send_command("AT+CGMR"),
            "sim_status": modem_connection.send_command("AT+CPIN?"),
            "sms_storage": modem_connection.send_command("AT+CPMS?")
        }
        
        return diagnostics
    
    return run_diagnostics

@pytest.fixture
def performance_monitor():
    """Monitor de performance para testes de modem."""
    import time
    import psutil
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.metrics = {}
        
        def start_monitoring(self):
            self.start_time = time.time()
            self.metrics["cpu_start"] = psutil.cpu_percent()
            self.metrics["memory_start"] = psutil.virtual_memory().percent
        
        def stop_monitoring(self):
            if self.start_time:
                self.metrics["duration"] = time.time() - self.start_time
                self.metrics["cpu_end"] = psutil.cpu_percent()
                self.metrics["memory_end"] = psutil.virtual_memory().percent
                
                return self.metrics
            return None
    
    return PerformanceMonitor()

@pytest.fixture
def stress_test_data():
    """Dados para testes de stress do modem."""
    return {
        "sms_batch": [
            {"to": "+351910000001", "message": f"Teste SMS stress #{i}"}
            for i in range(1, 101)
        ],
        "ussd_codes": [
            "*100#", "*101#", "*102#", "*111*1#", "*222#"
        ],
        "concurrent_operations": 5,
        "test_duration": 300,  # 5 minutes
        "max_failures": 10
    }

@pytest.fixture
def cleanup_modem_state(modem_connection):
    """Limpa estado do modem após testes."""
    yield
    
    if modem_connection.connected:
        # Clear any pending operations
        modem_connection.send_command("AT+CMGD=1,4")  # Delete all SMS
        modem_connection.send_command("AT+CUSD=2")     # Cancel USSD
        modem_connection.send_command("ATZ")           # Reset modem
        
        # Wait for reset
        import time
        time.sleep(2)

@pytest.fixture
def mock_windows_registry():
    """Mock do registro Windows para testes."""
    class MockRegistry:
        def __init__(self):
            self.keys = {
                "modem_drivers": ["USB\\VID_12D1&PID_1F01", "USB\\VID_19D2&PID_0031"],
                "com_ports": ["COM3", "COM4", "COM5"]
            }
        
        def get_installed_drivers(self):
            return self.keys["modem_drivers"]
        
        def get_com_ports(self):
            return self.keys["com_ports"]
    
    return MockRegistry()
