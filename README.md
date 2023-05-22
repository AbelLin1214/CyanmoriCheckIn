<!--
 * @Author: Abel
 * @Date: 2023-05-22 10:49:38
 * @LastEditTime: 2023-05-22 11:28:26
-->
## 青森自动签到

用于每天自动登录`https://cccc.gg`并完成签到，获取免费流量

## Usage

首先参考``docker-compose.yaml``下的`environment`设置好环境变量

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
./build.sh
docker compose logs -f
```

当然，如果你的compose版本较老（使用docker-compose而非docker compose），你可以选择更新版本，或者使用以下命令

```shell
docker-compose up -d --build && docker-compose logs -f
```