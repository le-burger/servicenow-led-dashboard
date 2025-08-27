import asyncio
from aiohttp import web
import aiohttp_cors
from typing import Dict, Any
import json


class WebDisplay(IDisplay):
    """Web-based display with live updates"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.port = self.config.get('port', 8080)
        self.app = web.Application()
        self.current_data = None
        self.websockets = set()

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Setup web server"""
        # Setup routes
        self.app.router.add_get('/', self.index)
        self.app.router.add_get('/ws', self.websocket_handler)
        self.app.router.add_get('/api/data', self.get_data)

        # Setup CORS
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*"
            )
        })

        for route in list(self.app.router.routes()):
            cors.add(route)

        # Start server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()

        print(f"Web display available at http://localhost:{self.port}")
        return True

    async def render(self, screen_data: ScreenData) -> None:
        """Send data to all connected clients"""
        self.current_data = screen_data

        # Broadcast to websockets
        if self.websockets:
            message = json.dumps({
                'type': 'update',
                'data': self._serialize_screen_data(screen_data)
            })

            await asyncio.gather(
                *[ws.send_str(message) for ws in self.websockets],
                return_exceptions=True
            )

    async def websocket_handler(self, request):
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.websockets.add(ws)

        try:
            # Send current data
            if self.current_data:
                await ws.send_str(json.dumps({
                    'type': 'initial',
                    'data': self._serialize_screen_data(self.current_data)
                }))

            async for msg in ws:
                # Handle client messages if needed
                pass

        finally:
            self.websockets.discard(ws)

        return ws

    async def index(self, request):
        """Serve the web interface"""
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>ServiceNow Dashboard</title>
            <style>
                body { 
                    background: #000; 
                    color: #0f0; 
                    font-family: monospace;
                    padding: 20px;
                }
                #display { 
                    border: 2px solid #0f0; 
                    padding: 20px;
                    min-height: 400px;
                }
                .alert { 
                    color: #f00; 
                    animation: blink 1s infinite;
                }
                @keyframes blink {
                    50% { opacity: 0; }
                }
            </style>
        </head>
        <body>
            <h1>ServiceNow LED Dashboard (Web View)</h1>
            <div id="display"></div>
            <script>
                const ws = new WebSocket('ws://localhost:''' + str(self.port) + '''/ws');
                ws.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    updateDisplay(message.data);
                };

                function updateDisplay(data) {
                    const display = document.getElementById('display');
                    // Render the screen data
                    display.innerHTML = formatScreenData(data);
                }

                function formatScreenData(data) {
                    // Format the screen data as HTML
                    let html = '<h2>' + data.title + '</h2>';
                    // Add more formatting logic here
                    return html;
                }
            </script>
        </body>
        </html>
        '''
        return web.Response(text=html, content_type='text/html')