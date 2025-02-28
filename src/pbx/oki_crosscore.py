import asyncio
import struct
from datetime import datetime
from .base_pbx import BasePBX

class OKICrossCoreHandler(BasePBX):
    def __init__(self, config):
        super().__init__(config)
        self.host = config['host']
        self.port = config['port']
        self.reader = None
        self.writer = None
        
    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.host, 
                self.port
            )
            self.connected = True
            print(f"Connected to OKI CrossCore2 at {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.connected = False
            
    async def get_incoming_calls(self):
        if not self.connected:
            await self.connect()
            
        while self.connected:
            try:
                data = await self.reader.read(1024)
                if data:
                    # Parse incoming call data
                    # Format will depend on OKI's protocol specification
                    call_data = self._parse_call_data(data)
                    yield call_data
            except Exception as e:
                print(f"Error reading data: {e}")
                self.connected = False
                
    async def _send_init_sequence(self):
        """初期化シーケンスを送信"""
        init_command = b'\x02INIT\x03'  # 仮の初期化コマンド
        self.writer.write(init_command)
        await self.writer.drain()
        
    async def disconnect(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        self.connected = False
        
    def _parse_call_data(self, raw_data):
        """OKI CrossCore2の着信データをパース"""
        try:
            # 実際のプロトコル仕様に合わせて実装
            # これは仮の実装です
            if raw_data.startswith(b'\x02'):  # STX
                data_str = raw_data[1:-1].decode('utf-8')
                parts = data_str.split(',')
                
                return {
                    'timestamp': datetime.now(),
                    'caller_number': parts[1] if len(parts) > 1 else None,
                    'called_number': parts[2] if len(parts) > 2 else None,
                    'pbx_type': 'OKI_CROSSCORE'
                }
        except Exception as e:
            self.logger.error(f"Failed to parse call data: {e}")
            return None 