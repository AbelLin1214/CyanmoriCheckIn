'''
Author: Abel
Date: 2023-05-22 09:03:40
LastEditTime: 2023-05-22 14:23:16
'''
import asyncio
from environs import Env
from random import randint
from datetime import datetime, timedelta
from pl_ctrl import NewBrowser, NewContext
from _logger import MyLogger
from playwright.async_api import Page, Response

env = Env()
env.read_env()
headless = env.bool('HEADLESS', True)
remote_port = env.int('REMOTE_PORT', None)
debug_level = env.str('DEBUG_LEVEL', 'DEBUG')
email = env.str('CCCC_EMAIL')
password = env.str('CCCC_PASSWORD')
logger = MyLogger(debug_level).bind(ps=f'CheckIn({email})')

def listen_check_in(page: Page):
    '''监听签到结果'''
    async def on_response(resp: Response):
        '''监听器'''
        check_in_url = 'https://cccc.gg/user/checkin'
        if resp.url == check_in_url:
            # 返回json时才解析
            if resp.headers['content-type'] == 'application/json':
                data = await resp.json()
                msg = data.get('msg', '未能获取签到流量')
                traffic = data.get('traffic', '未知')
                logger.success(f'{msg}, 当前流量: {traffic}')
            else:
                logger.warning('出错啦，可能是已经签到过了')
    page.on('response', on_response)

async def run():
    '''签到主程序'''
    logger.info('开始签到')
    async with NewBrowser(headless=headless, remote_port=remote_port) as browser:
        logger.debug('浏览器已启动, Headless: %s' % headless)
        async with NewContext(browser, 'state.json') as context:
            logger.debug('用户态已加载')
            page = await context.new_page()
            listen_check_in(page)
            # 登录
            logger.debug('正在进入登录页面')
            login_url = 'https://cccc.gg/auth/login'
            await page.goto(login_url)
            # 等待页面跳转至主页（如果登录已失效的话）
            try:
                url = 'https://cccc.gg/user'
                await page.wait_for_url(url)
            except Exception:
                logger.info('登录已失效，正在准备重新登录')
                # 填写登录信息
                logger.debug('输入账号')
                await page.fill('//input[@id="email"]', email)
                logger.debug('输入密码')
                await page.fill('//input[@id="password"]', password)
                logger.debug('点击登录')
                await page.click('text=登录')
                await page.wait_for_url(url)

            # 等待页面加载完成
            logger.debug('等待页面加载完成')
            await page.wait_for_load_state('networkidle')

            # 签到
            logger.debug('登录成功，准备签到')
            await page.evaluate('index.checkin();')

            # 获取签到结果
            logger.debug('等待签到结果')
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)
            logger.debug('获取签到结果')
            btn = await page.query_selector('text=已签到')
            if btn:
                attr = await btn.get_attribute('disabled')
                if attr:
                    if attr == 'disabled':
                        logger.success('签到成功')
                        return
            logger.error('签到失败')

async def run_delay():
    '''为避免在固定时间点同时签到，设置随机延时'''
    # 延时时间为 0~1小时
    delay = randint(0, 60 * 60)
    now = datetime.now()
    t = now + timedelta(seconds=delay)
    logger.info(f'延时 {delay} 秒后开始签到, 预计签到时间: {t.strftime("%Y-%m-%d %H:%M:%S")}')
    await asyncio.sleep(delay)
    await run()

async def run_forever():
    '''每天运行一次，具体时间由 run_delay 决定'''
    logger.success('程序已启动')
    while True:
        try:
            logger.debug('当日签到程序已启动')
            asyncio.create_task(run_delay())
        except Exception as e:
            logger.error(e)
        finally:
            logger.info('等待一天后再次运行')
            await asyncio.sleep(60*60*24)

if __name__ == '__main__':
    asyncio.run(run_forever())
    # asyncio.run(run())
