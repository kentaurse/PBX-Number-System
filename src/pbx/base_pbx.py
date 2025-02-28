from abc import ABC, abstractmethod

class BasePBX(ABC):
    """Base class for PBX implementations"""
    
    def __init__(self, config):
        self.config = config
        self.connected = False
    
    @abstractmethod
    async def connect(self):
        """Establish connection to PBX"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from PBX"""
        pass
        
    @abstractmethod
    async def get_incoming_calls(self):
        """Get incoming call data"""
        pass 