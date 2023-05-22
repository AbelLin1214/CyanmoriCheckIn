###
 # @Author: Abel
 # @Date: 2023-04-20 13:49:14
 # @LastEditTime: 2023-04-22 12:09:55
### 
echo -e "\033[32m building docker image... \033[0m"
echo ""
docker compose up -d --build
echo "pruning docker images..."
docker image prune -f
echo ""
echo -e "\033[32m done \033[0m"
