import asyncio
from config.config import PBX_CONFIG
from pbx.oki_crosscore import OKICrossCoreHandler
from db.database import Database
from utils.logger import setup_logger

async def main():
    logger = setup_logger()
    db = Database()
    pbx_handler = OKICrossCoreHandler(PBX_CONFIG['OKI_CROSSCORE'])
    
    try:
        await db.connect()
        await pbx_handler.connect()
        
        async for call_data in pbx_handler.get_incoming_calls():
            if call_data:
                logger.info(f"Incoming call detected: {call_data}")
                await db.save_call_data(call_data)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await pbx_handler.disconnect()
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 