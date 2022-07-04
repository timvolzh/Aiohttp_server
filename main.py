import json
import asyncpg
import pydantic

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

    async def to_dict(self):
        return {'id': self.id,
                'create_time': str(self.create_time),
                'title': self.title,
                'description': self.description,
                'user': self.user,
                }


async def orm_context(app):
    print('Start')
    await db.set_bind('postgres://admin:admin@127.0.0.1:5050/aiohttp_db')
    await db.gino.create_all()
    yield
    await db.pop_bind().close()
    print('Finish')


'''Views'''


class AnnounceView(web.View):

    async def get(self):
        announce_id = int(self.request.match_info['announce_id'])
        announce = await AnnounceModel.get(announce_id)
        if not announce:
            return web.HTTPNotFound(text=json.dumps({'error': 'object not found'}), content_type='application/json')
        return web.json_response(await announce.to_dict())

    async def post(self):
        announce_data = await self.request.json()
        try:
            new_announce = await AnnounceModel.create(**announce_data)
        except asyncpg.exceptions.UniqueViolationError:
            raise web.HTTPBadRequest(text=json.dumps({'error': 'already exist'}), content_type='application/json')
        return web.json_response({'id': new_announce.id})

    async def patch(self):
        announce_data = await self.request.json()
        announce_id = int(self.request.match_info['announce_id'])
        announce_for_update = await AnnounceModel.get(announce_id)
        if not announce_for_update:
            raise web.HTTPNotFound(text=json.dumps({'error': 'object not found'}), content_type='application/json')
        try:
            updated_announce = await announce_for_update.update(**announce_data).apply()
        except Exception as e:
            print(e)

    async def delete(self):
        announce_id = int(self.request.match_info['announce_id'])
        announce_for_delete = await AnnounceModel.get(announce_id)
        if not announce_for_delete:
            raise web.HTTPNotFound(text=json.dumps({'error': 'object not found'}), content_type='application/json')
        deleted_announce = await announce_for_delete.delete()
        return web.json_response({'status': 'success'})


app.router.add_routes(
    [
        web.post('/announce/', AnnounceView),
        web.get('/announce/{announce_id:\d+}', AnnounceView),
        web.patch('/announce/{announce_id:\d+}', AnnounceView),
        web.delete('/announce/{announce_id:\d+}', AnnounceView),
    ]
)

app.cleanup_ctx.append(orm_context)
web.run_app(app)

