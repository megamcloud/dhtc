from aiohttp import web
from jinja2 import Environment, PackageLoader, select_autoescape

import dhtc


class WebHandler(object):
    def __init__(self, db: dhtc.Database):
        self.db = db
        self.env = Environment(
            loader=PackageLoader("dhtc", "templates"),
            autoescape=select_autoescape(["html"])
        )

    def build_page(self, template, ctx):
        tpl = self.env.get_template(template)
        return web.Response(body=tpl.render(ctx), content_type="text/html")

    async def handle_root(self, req):
        return self.build_page("dashboard.html", {
            "info_hash_count": self.db.get_count(),
            "bootstrap_nodes": dhtc.BOOTSTRAP_NODES
        })

    async def handle_dashboard(self, req):
        return self.build_page("dashboard.html", {
            "info_hash_count": self.db.get_count(),
            "bootstrap_nodes": dhtc.BOOTSTRAP_NODES
        })

    async def handle_search_get(self, req):
        return self.build_page("search.html", {
            "placeholder": self.db.get_random_title()
        })

    async def handle_search_post(self, req):
        data = req.post()
        print(data)
        return self.build_page("search.html", {
            "placeholder": ""
        })

    async def handle_discover_request_get(self, req):
        return self.build_page("discover.html", {
            "items": self.db.get_x_random()
        })

    async def handle_discover_request_post(self, req):
        return self.build_page("discover.html", {})


async def create_webserver(db, host, port):
    wh = WebHandler(db)
    app = web.Application()
    app.add_routes([
        web.get("/", wh.handle_root),
        web.get("/dashboard", wh.handle_dashboard),
        web.get("/search", wh.handle_search_get),
        web.post("/search", wh.handle_search_post),
        web.get("/discover", wh.handle_discover_request_get),
        web.post("/discover", wh.handle_discover_request_post)
    ])
    r = web.AppRunner(app)
    await r.setup()
    s = web.TCPSite(r, host, port)
    await s.start()
