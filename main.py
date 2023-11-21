'''
Author: Abel
Date: 2023-05-22 09:03:40
LastEditTime: 2023-11-21 18:04:48
'''
import time
import click
import asyncio
from random import randint
from datetime import datetime, timedelta
from pl_ctrl import NewBrowser, NewContext
from _logger import MyLogger
from pathlib import Path
from common import Config, Account
from playwright.async_api import Page, Response

CONFIG = Config.load('config.yaml')
logger = MyLogger(CONFIG.debug_level)
# HOST = 'https://cccc.gg'
HOST = 'https://1100.gg'

class CheckIn:
    '''自动签到'''
    def __init__(self, account: Account):
        self.account = account
        self.logger = logger.bind(ps=account)
        self.__state_file = f'{account.name}.json'

    @property
    def state_path(self):
        '''用户态的保存路径'''
        dir = Path('state')
        dir.mkdir(exist_ok=True)
        p = dir / self.__state_file
        p.touch(exist_ok=True)
        if p.stat().st_size == 0:
            p.write_text('{}')
        return p

    def listen_check_in(self, page: Page):
        '''监听签到结果'''
        async def on_response(resp: Response):
            '''监听器'''
            check_in_url = f'{HOST}/user/checkin'
            if resp.url == check_in_url:
                # 返回json时才解析
                if resp.headers['content-type'] == 'application/json':
                    data = await resp.json()
                    msg = data.get('msg', '未能获取签到流量')
                    traffic = data.get('traffic', '未知')
                    self.logger.success(f'{msg}, 当前流量: {traffic}')
                else:
                    self.logger.warning('出错啦，可能是已经签到过了')
        page.on('response', on_response)
    
    async def login(self, page: Page):
        '''登录'''
        # 登录
        self.logger.debug('正在进入登录页面')
        login_url = f'{HOST}/auth/login'
        await page.goto(login_url, timeout=120000)
        # 等待页面跳转至主页（如果登录已失效的话）
        try:
            url = f'{HOST}/user'
            await page.wait_for_url(url)
            self.logger.info('使用缓存登录成功')
        except Exception:
            self.logger.info('登录已失效，正在准备重新登录')
            # 填写登录信息
            self.logger.debug('输入账号')
            await page.fill('//input[@id="email"]', self.account.email)
            self.logger.debug('输入密码')
            await page.fill('//input[@id="password"]', self.account.password)
            self.logger.debug('点击登录')
            await page.click('text=登录')
            # 点击登录后，偶发需要等待较长时间才能跳转至主页
            await page.wait_for_url(url, timeout=120000)

        # 等待页面加载完成
        self.logger.debug('等待页面加载完成')
        await page.wait_for_load_state('networkidle')
    
    async def check_in(self, page: Page):
        # 执行签到js
        await page.evaluate('index.checkin();')
        # 获取签到结果
        self.logger.debug('等待签到结果')
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)
        btn = await page.query_selector('text=已签到')
        if btn:
            attr = await btn.get_attribute('disabled')
            if attr:
                if attr == 'disabled':
                    self.logger.success('签到成功')
                    return
        self.logger.error('签到失败')
    
    @logger.catch
    async def run(self):
        '''签到主程序'''
        self.logger.info('开始签到')
        for i in range(1, CONFIG.retry_times + 1):
            try:
                self.logger.debug(f'第 {i} 次尝试')
                async with NewBrowser(headless=CONFIG.headless, remote_port=CONFIG.remote_port) as browser:
                    self.logger.debug('浏览器已启动, Headless: %s' % CONFIG.headless)
                    async with NewContext(browser, self.state_path) as context:
                        self.logger.debug('用户态已加载')
                        page = await context.new_page()
                        self.listen_check_in(page)
                        await self.login(page)  # 登录
                        # 签到
                        self.logger.debug('登录成功，准备签到')
                        await self.check_in(page)
                        break
            except Exception as e:
                self.logger.error(e)

async def async_run():
    for idx, account in enumerate(CONFIG.accounts, 1):
        check_in = CheckIn(account)
        await check_in.run()
        if idx < len(CONFIG.accounts):
            __delay = randint(60, 5 * 60)
            logger.info(f'{account}签到完成，等待 {__delay} 秒后开始下一个账号的签到')
            await asyncio.sleep(__delay)
    logger.info('所有账号签到完成')
    

async def run_delay():
    '''为避免在固定时间点同时签到，设置随机延时'''
    # 延时时间为 0~1小时
    delay = randint(0, 60 * 60)
    now = datetime.now()
    t = now + timedelta(seconds=delay)
    logger.info(f'延时 {delay} 秒后开始签到, 预计签到时间: {t.strftime("%Y-%m-%d %H:%M:%S")}, 共有 {len(CONFIG.accounts)} 个账号')
    await asyncio.sleep(delay)
    await async_run()

async def async_run_forever():
    '''每天运行一次，具体时间由 run_delay 决定'''
    logger.success('程序已启动, 每天 %s 运行一次签到程序' % CONFIG.run_time)
    while True:
        t = time.strftime('%H:%M')
        if t == CONFIG.run_time:
            logger.debug('当日签到程序已启动')
            asyncio.create_task(run_delay())
            await asyncio.sleep(60 * 60)
        await asyncio.sleep(60)

if __name__ == '__main__':
    @click.group
    def cli():
        ...
    
    @cli.command
    def run():
        '''立即运行一次签到程序'''
        asyncio.run(async_run())
    
    @cli.command
    def run_forever():
        '''每天运行一次签到程序, 具体时间由配置文件决定'''
        asyncio.run(async_run_forever())

    cli()
