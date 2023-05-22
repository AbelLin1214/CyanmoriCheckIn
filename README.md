<!--
 * @Author: Abel
 * @Date: 2023-05-22 10:49:38
 * @LastEditTime: 2023-05-22 16:01:21
-->
## 青森自动签到

用于每天自动登录`https://cccc.gg`并完成签到，获取免费流量

本项目支持多账号，在`config.yaml`下填写相应的账号信息即可

## Usage

首先复制一份`demo_config.yaml`，保存为`config.yaml`并修改相应配置

### python执行

请自行使用`Conda`、`pipenv`等创建虚拟环境，随后运行以下命令安装依赖

```shell
pip install -r requirements.txt
pip install playwright
playwright install chromium
```

安装完依赖后，执行`python main.py`即可运行程序

### Docker

建议使用`docker compose`

```shell
docker compose up -d
```
