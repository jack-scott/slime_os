import serial
import serial.tools.list_ports
import subprocess
import time
import sys

class PicoController:
    def __init__(self):
        self.port = self.find_pico()
        if not self.port:
            raise Exception("Pico not found!")
        print(f"Found Pico on {self.port}")
    
    def find_pico(self):
        """Auto-detect Pico"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if '2e8a' in port.hwid.lower() or 'Pico' in port.description:
                return port.device
        return None
    
    def force_stop(self):
        """Force interrupt the running program"""
        print("Forcing interrupt...")
        try:
            ser = serial.Serial(self.port, 115200, timeout=1)
            
            # Send break
            ser.send_break(duration=0.2)
            time.sleep(0.1)
            
            # Send multiple Ctrl-C
            for _ in range(10):
                ser.write(b'\x03')
                time.sleep(0.03)
            
            # # Soft reset
            # ser.write(b'\x04')
            # time.sleep(0.5)
            
            ser.close()
            print("✓ Interrupted successfully")
            return True
            
        except Exception as e:
            print(f"✗ Interrupt failed: {e}")
            return False
    
    def upload(self, local_file, remote_file=None):
        """Upload file to Pico"""
        if remote_file is None:
            remote_file = f':{local_file}'
        
        # First, force stop
        self.force_stop()
        time.sleep(1)
        
        # Then upload
        print(f"Uploading {local_file}...")
        result = subprocess.run(
            ['mpremote', 'connect', self.port, 'fs', 'cp', local_file, remote_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✓ Upload successful")
            return True
        else:
            print(f"✗ Upload failed: {result.stderr}")
            return False
    
    def reset(self):
        """Reset the Pico"""
        subprocess.run(['mpremote', 'connect', self.port, 'reset'])
        print("✓ Pico reset")

# Usage
if __name__ == '__main__':
    pico = PicoController()
    pico.upload('/home/jack/Documents/projects/slime_os/slime_os_2/main.py', ':main.py')
    pico.reset()