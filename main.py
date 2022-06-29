from aiohttp import web
from asyncio import run
from gino import Gino

app = web.Application()
db = Gino()


'''Models'''

class AnnounceModel(db.Model):
    __tablename__ = 'announce'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    user = db.Column(db.Integer, nullable=False, default=1)
    create_time = db.Column(db.DateTime, server_default=db.func.now())


async def orm_context(app):
    print('Start')
    await db.set_bind('postgres://admin:admin@127.0.0.1:5050/aiohttp_db')
    await db.gino.create_all()
    yield
    await db.pop_bind().close()
    print('Finish')


class AnnounceView(web.View):

    async def get(self):

        pass


app.router.add_routes(
    [
        web.get('/announce/{announce_id:\d+}', AnnounceView),
        web.post('/announce/', AnnounceView)
     ]
)

app.cleanup_ctx.append(orm_context)
web.run_app(app)
