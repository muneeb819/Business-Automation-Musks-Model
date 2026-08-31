import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings
import ssl
from sqlalchemy.engine import make_url

url = make_url(settings.DATABASE_URL)
query = dict(url.query)
connect_args = {}
if query.get('sslmode') in ('require', 'verify-ca', 'verify-full'):
    ssl_ctx = ssl.create_default_context()
    if query.get('sslmode') == 'require':
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
    connect_args['ssl'] = ssl_ctx
url = url.set(query={})

engine = create_async_engine(url, connect_args=connect_args)

async def drop_all():
    async with engine.begin() as conn:
        # Get all tables
        result = await conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in result]
        print('Dropping tables:', tables)
        
        for table in tables:
            await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
        
        print('All tables dropped.')

asyncio.run(drop_all())
