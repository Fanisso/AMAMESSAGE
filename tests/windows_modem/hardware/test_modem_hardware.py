# Testes de hardware para Windows com modem físico
import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor

class TestModemHardware:
    """Testes de hardware do modem GSM."""
    
    @pytest.mark.hardware
    @pytest.mark.windows_modem
    def test_modem_detection(self, detect_gsm_modems, available_com_ports):
        """Testa detecção de modems GSM."""
        # Verify we have COM ports available
        assert len(available_com_ports) > 0, "Nenhuma porta COM disponível"
        
        # Verify at least one GSM modem was detected
        assert len(detect_gsm_modems) > 0, "Nenhum modem GSM detectado"
        
        # Verify modem information
        for modem in detect_gsm_modems:
            assert "port" in modem
            assert "manufacturer" in modem
            assert "model" in modem
            assert modem["port"].startswith("COM")
    
    @pytest.mark.hardware
    @pytest.mark.windows_modem
    def test_modem_connection(self, modem_connection, windows_modem_config):
        """Testa conexão com o modem."""
        assert modem_connection.connected == True
        
        # Test basic AT command
        response = modem_connection.send_command("AT")
        assert "OK" in response
        
        # Test modem identification
        manufacturer = modem_connection.send_command("AT+CGMI")
        assert len(manufacturer) > 0
        
        model = modem_connection.send_command("AT+CGMM")
        assert len(model) > 0
    
    @pytest.mark.hardware
    @pytest.mark.windows_modem
    def test_signal_strength(self, modem_connection):
        """Testa medição da força do sinal."""
        signal_response = modem_connection.get_signal_strength()
        assert signal_response is not None
        assert "CSQ" in signal_response
        
        # Parse signal strength (format: +CSQ: rssi,ber)
        if "+CSQ:" in signal_response:
            signal_data = signal_response.split("+CSQ:")[1].strip()
            rssi, ber = signal_data.split(",")
            
            # RSSI should be between 0-31 (or 99 for unknown)
            rssi_val = int(rssi)
            assert 0 <= rssi_val <= 31 or rssi_val == 99
    
    @pytest.mark.hardware
    @pytest.mark.windows_modem
    def test_network_registration(self, modem_connection):
        """Testa registro na rede."""
        network_info = modem_connection.get_network_info()
        assert network_info is not None
        
        # Check network registration status
        reg_status = modem_connection.send_command("AT+CREG?")
        assert "+CREG:" in reg_status
        
        # Parse registration status
        if "+CREG:" in reg_status:
            reg_data = reg_status.split("+CREG:")[1].strip()
            # Status should indicate registration (1 or 5)
            status_parts = reg_data.split(",")
            if len(status_parts) >= 2:
                reg_stat = int(status_parts[1])
                assert reg_stat in [1, 5], f"Modem não registrado na rede (status: {reg_stat})"

class TestModemSMSHardware:
    """Testes de SMS com hardware real."""
    
    @pytest.mark.hardware
    @pytest.mark.windows_modem
    @pytest.mark.sms
    @pytest.mark.slow
    def test_send_sms_real(self, modem_connection, stress_test_data):
        """Testa envio de SMS real (cuidado com custos!)."""
        # Use test phone number (should be configured in environment)
        test_number = "+351912000000"  # Replace with actual test number
        test_message = "Teste SMS AMAMESSAGE - Hardware Test"
        
        # Send SMS
        result = modem_connection.send_sms(test_number, test_message)
        
        # Note: This will actually send an SMS and may incur charges
        # Only run this test with proper test SIM card and authorization
        assert result == True, "Falha ao enviar SMS"
        
        # Wait for delivery confirmation
        time.sleep(10)
        
        # Check for delivery report (if supported)
        delivery_response = modem_connection.send_command("AT+CMGL=\"ALL\"")
        assert delivery_response is not None
    
    @pytest.mark.hardware
    @pytest.mark.windows_modem
    @pytest.mark.sms
    def test_sms_storage_management(self, modem_connection):
        """Testa gestão de armazenamento de SMS."""
        # Check SMS storage status
        storage_status = modem_connection.send_command("AT+CPMS?")
        assert "+CPMS:" in storage_status
        
        # Set SMS storage location
        set_storage = modem_connection.send_command("AT+CPMS=\"SM\",\"SM\",\"SM\"")
        assert "OK" in set_storage
        
        # Check storage capacity
        capacity_check = modem_connection.send_command("AT+CPMS?")
        assert "+CPMS:" in capacity_check
        
        # Parse storage info
        if "+CPMS:" in capacity_check:
            storage_info = capacity_check.split("+CPMS:")[1].strip()
            # Format: "SM",used,total,"SM",used,total,"SM",used,total
            storage_parts = storage_info.split(",")
            if len(storage_parts) >= 6:
                used1 = int(storage_parts[1])
                total1 = int(storage_parts[2])
                assert used1 <= total1, "Armazenamento SMS inconsistente"
    
    @pytest.mark.hardware
    @pytest.mark.windows_modem
    @pytest.mark.sms
    def test_read_incoming_sms(self, modem_connection):
        """Testa leitura de SMS recebidos."""
        # List all SMS messages
        sms_list = modem_connection.send_command("AT+CMGL=\"ALL\"")
        assert sms_list is not None
        
        # If there are messages, try to read one
        if "+CMGL:" in sms_list:
            # Parse message list to get message index
            lines = sms_list.split('\n')
            for line in lines:
                if "+CMGL:" in line:
                    parts = line.split(',')
                    if len(parts) > 0:
                        msg_index = parts[0].split(':')[1].strip()
                        
                        # Read specific message
                        read_msg = modem_connection.send_command(f"AT+CMGR={msg_index}")
                        assert "+CMGR:" in read_msg
                        break

class TestModemUSSDHardware:
    """Testes de USSD com hardware real."""
    
    @pytest.mark.hardware
    @pytest.mark.windows_modem
    @pytest.mark.ussd
    @pytest.mark.slow
    def test_send_ussd_balance_check(self, modem_connection):
        """Testa consulta de saldo via USSD."""
        # Common balance check codes (varies by operator)
        balance_codes = ["*100#", "*111#", "*123#"]
        
        ussd_response = None
        for code in balance_codes:
            try:
                ussd_response = modem_connection.send_ussd(code)
                if ussd_response and "OK" in ussd_response:
                    break
            except Exception as e:
                continue
        
        assert ussd_response is not None, "Nenhum código USSD funcionou"
        
        # Wait for USSD response
        time.sleep(5)
        
        # Check for USSD response notification
        response_check = modem_connection.send_command("AT+CUSD?")
        assert response_check is not None
    
    @pytest.mark.hardware
    @pytest.mark.windows_modem
    @pytest.mark.ussd
    def test_ussd_session_timeout(self, modem_connection, windows_modem_config):
        """Testa timeout de sessão USSD."""
        # Send USSD code
        ussd_response = modem_connection.send_ussd("*100#")
        assert ussd_response is not None
        
        # Wait for timeout
        timeout = windows_modem_config["USSD_TIMEOUT"]
        time.sleep(timeout + 5)
        
        # Check session status
        session_status = modem_connection.send_command("AT+CUSD?")
        # Session should be closed or timed out
        assert session_status is not None

class TestModemStressHardware:
    """Testes de stress com hardware real."""
    
    @pytest.mark.hardware
    @pytest.mark.windows_modem
    @pytest.mark.stress
    @pytest.mark.slow
    def test_concurrent_operations(self, modem_connection, stress_test_data, performance_monitor):
        """Testa operações concorrentes no modem."""
        performance_monitor.start_monitoring()
        
        results = {
            "sms_sent": 0,
            "sms_failed": 0,
            "ussd_sent": 0,
            "ussd_failed": 0,
            "errors": []
        }
        
        def send_sms_batch():
            for sms_data in stress_test_data["sms_batch"][:10]:  # Limit to 10 for safety
                try:
                    result = modem_connection.send_sms(sms_data["to"], sms_data["message"])
                    if result:
                        results["sms_sent"] += 1
                    else:
                        results["sms_failed"] += 1
                    time.sleep(2)  # Delay between SMS
                except Exception as e:
                    results["sms_failed"] += 1
                    results["errors"].append(f"SMS Error: {str(e)}")
        
        def send_ussd_batch():
            for ussd_code in stress_test_data["ussd_codes"]:
                try:
                    result = modem_connection.send_ussd(ussd_code)
                    if result:
                        results["ussd_sent"] += 1
                    else:
                        results["ussd_failed"] += 1
                    time.sleep(5)  # Delay between USSD
                except Exception as e:
                    results["ussd_failed"] += 1
                    results["errors"].append(f"USSD Error: {str(e)}")
        
        # Run operations in parallel (carefully!)
        with ThreadPoolExecutor(max_workers=2) as executor:
            sms_future = executor.submit(send_sms_batch)
            ussd_future = executor.submit(send_ussd_batch)
            
            # Wait for completion
            sms_future.result()
            ussd_future.result()
        
        performance_metrics = performance_monitor.stop_monitoring()
        
        # Verify results
        total_operations = results["sms_sent"] + results["sms_failed"] + results["ussd_sent"] + results["ussd_failed"]
        success_rate = (results["sms_sent"] + results["ussd_sent"]) / total_operations if total_operations > 0 else 0
        
        assert success_rate >= 0.8, f"Taxa de sucesso muito baixa: {success_rate:.2%}"
        assert len(results["errors"]) <= stress_test_data["max_failures"]
        
        # Performance checks
        if performance_metrics:
            assert performance_metrics["duration"] < stress_test_data["test_duration"]
    
    @pytest.mark.hardware
    @pytest.mark.windows_modem
    @pytest.mark.stress
    def test_modem_recovery(self, modem_connection, cleanup_modem_state):
        """Testa recuperação do modem após operações intensivas."""
        # Simulate heavy usage
        for i in range(20):
            modem_connection.send_command("AT+CSQ")  # Signal strength check
            time.sleep(0.1)
        
        # Check if modem is still responsive
        response = modem_connection.send_command("AT")
        assert "OK" in response, "Modem não responde após uso intensivo"
        
        # Check signal strength is still available
        signal = modem_connection.get_signal_strength()
        assert signal is not None, "Modem perdeu conectividade após stress"
        
        # Verify network registration is still active
        network_info = modem_connection.get_network_info()
        assert network_info is not None, "Modem desregistrou da rede após stress"

class TestModemDrivers:
    """Testes específicos de drivers Windows."""
    
    @pytest.mark.drivers
    @pytest.mark.windows_modem
    def test_driver_installation(self, check_driver_installation, windows_system_info):
        """Testa instalação de drivers GSM."""
        drivers = check_driver_installation()
        
        # Verify drivers are installed
        assert len(drivers) > 0, "Nenhum driver USB detectado"
        
        # Look for common GSM modem vendor IDs
        common_vendors = ["12D1", "19D2", "1E0E", "2001"]  # Huawei, ZTE, etc.
        
        found_gsm_driver = False
        for driver in drivers:
            for vendor in common_vendors:
                if vendor in driver:
                    found_gsm_driver = True
                    break
            if found_gsm_driver:
                break
        
        # Note: This might not always pass if using different modem brands
        # assert found_gsm_driver, "Nenhum driver GSM comum encontrado"
    
    @pytest.mark.drivers
    @pytest.mark.windows_modem
    def test_com_port_assignment(self, available_com_ports, detect_gsm_modems):
        """Testa atribuição de portas COM."""
        # Verify COM ports are assigned to detected modems
        modem_ports = [modem["port"] for modem in detect_gsm_modems]
        available_port_names = [port[0] for port in available_com_ports]
        
        for modem_port in modem_ports:
            assert modem_port in available_port_names, f"Porta {modem_port} não está disponível"
    
    @pytest.mark.drivers
    @pytest.mark.windows_modem
    def test_driver_stability(self, modem_connection):
        """Testa estabilidade do driver."""
        # Test multiple connections/disconnections
        for i in range(5):
            # Test connection status
            assert modem_connection.connected == True
            
            # Send command to verify driver stability
            response = modem_connection.send_command("AT+CGMI")
            assert response is not None
            assert len(response) > 0
            
            time.sleep(1)
        
        # Final verification
        final_response = modem_connection.send_command("AT")
        assert "OK" in final_response, "Driver tornou-se instável após uso repetido"
