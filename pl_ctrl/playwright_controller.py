'''
Author: Abel
Date: 2023-01-05 12:05:59
LastEditTime: 2023-05-22 16:04:06
'''
from pathlib import Path
from playwright.async_api import Browser, PlaywrightContextManager

class NewBrowser(PlaywrightContextManager):
    '''继承基准async_playwright，在上下文中创建browser'''
    def __init__(self, *args, **kwargs):
        self.headless = kwargs.pop('headless', True)
        self.remote_port = kwargs.pop('remote_port', None)
        super().__init__(*args, **kwargs)

    async def __aenter__(self):
        playwright = await super().__aenter__()
        args=[
                '--disable-blink-features=AutomationControlled',
                '--start-maximized'
            ]
        if self.remote_port:
            args.append(f'--remote-debugging-port={self.remote_port}')
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=args
        )
        return self.browser
    
    async def start(self):
        return await self.__aenter__()
    
    async def close(self):
        return await self.__aexit__()
    
    async def __aexit__(self, *args):
        await self.browser.close()
        await super().__aexit__(*args)

class NewContext:
    '''在上下文中创建 context，集成 cookie 控制'''
    def __init__(self, browser: Browser, state_path: str):
        '''
        args
        ----
        state_path: 用户态的保存路径
        '''
        self.browser = browser
        self.path = state_path
        p = Path(state_path)
        p.touch(exist_ok=True)
        if p.stat().st_size == 0:
            p.write_text('{}')

    async def new_context(self):
        context = await self.browser.new_context(
            storage_state=self.path,
            viewport={'width': 1920, 'height': 1080}
            )
        await context.add_init_script(path='statics/stealth.min.js')
        return context
    
    async def start(self):
        return await self.__aenter__()

    async def __aenter__(self):
        self.context = await self.new_context()
        return self.context
    
    async def __aexit__(self, *args):
        await self.context.storage_state(path=self.path)
        await self.context.close()
