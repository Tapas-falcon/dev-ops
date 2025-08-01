#!/bin/bash

# 从环境变量中读取配置
DEPLOY_TARGET=${DEPLOY_TARGET}
EC2_USER=${PROD_EC2_USER}
MAIN_SERVER=${PROD_EC2_PUBLIC_DNS}
STANDBY_SERVER=${PROD_EC2_STANDBY_PUBLIC_DNS}
set -e  # 出错立即退出

# 从环境变量中读取配置
echo "Deploy target: $DEPLOY_TARGET"
echo "Image: $IMAGE_NAME:$IMAGE_TAG"
echo "Project name: $PROJECT_NAME"
echo "EC2 user: $PROD_EC2_USER"
echo "Main server: $PROD_EC2_PUBLIC_DNS"

IMAGE_NAME=${IMAGE_NAME}
IMAGE_TAG=${IMAGE_TAG}
PROJECT_NAME=${PROJECT_NAME}
DOCKER_USERNAME=${DOCKER_USERNAME}
DOCKER_PASSWORD=${DOCKER_PASSWORD}

# ===== 定义部署函数 =====
deploy_to_server() {
  local SERVER="$1"
  echo "🚀 Deploying to server: $SERVER"

  scp -o StrictHostKeyChecking=no docker-compose.yml "$SERVER":/home/${SERVER%%@*}/${PROJECT_NAME}/ || { echo "Failed to copy docker-compose.yml"; exit 1; }

  ssh -tt -o LogLevel=VERBOSE -o StrictHostKeyChecking=no "$SERVER" <<EOF
    set -x

    cd /home/${SERVER%%@*}/${PROJECT_NAME}

    # 获取旧镜像标签
    OLD_IMAGE_TAGS=\$(docker ps -a --filter "name=${PROJECT_NAME}" --format "{{.Image}}" | grep ${IMAGE_NAME} | awk -F: '{print \$2}')
    echo "Old image tags: \$OLD_IMAGE_TAGS"

    # 停止旧容器
    if docker-compose ps | grep ${PROJECT_NAME}; then
      docker-compose down || { echo "Failed to stop containers"; exit 1; }
    fi

    # 删除旧镜像
    if [ -z "\$OLD_IMAGE_TAGS" ]; then
      echo "No existing container found. Skipping old image removal."
    else
      for OLD_IMAGE_TAG in \$OLD_IMAGE_TAGS; do
        echo "Old image tag: \$OLD_IMAGE_TAG"
        docker image rm "${IMAGE_NAME}:\$OLD_IMAGE_TAG" || echo "Failed to remove old image (\$OLD_IMAGE_TAG)"
      done
    fi

    # Docker 登录
    if ! docker info | grep -q "Username:"; then
      echo "\${DOCKER_PASSWORD}" | docker login -u "\${DOCKER_USERNAME}" --password-stdin
    else
      echo "Already logged in to Docker Hub."
    fi

    # 拉取最新镜像
    echo "Pulling latest image... ${IMAGE_NAME}:${IMAGE_TAG}"
    docker pull ${IMAGE_NAME}:${IMAGE_TAG}
    docker images | grep ${IMAGE_TAG} || { echo "Image pull failed!"; exit 1; }

    # 检查 docker-compose.yml 是否有效
    IMAGE_TAG=${IMAGE_TAG} docker-compose config || { echo "docker-compose.yml validation failed!"; exit 1; }

    # 启动服务
    IMAGE_TAG=${IMAGE_TAG} docker-compose up -d ${PROJECT_NAME} || { echo "Failed to start service"; exit 1; }

    echo '✅ Deployment completed successfully!'
    exit 0
EOF
}

# ===== 根据用户选择定义服务器列表 =====
case "${DEPLOY_TARGET}" in
  "prod-server001")
    SERVERS=(
      "${EC2_USER}@${MAIN_SERVER}"
    )
    ;;
  "prod-server02")
    SERVERS=(
      "${EC2_USER}@${STANDBY_SERVER}"
    )
    ;;
  "staging-server01")
    SERVERS=(
      "${EC2_USER}@51.92.166.192"
    )
    ;;
  *)
    echo "⚠️ Unknown deploy target: ${DEPLOY_TARGET}"
    exit 1
    ;;
esac

# ===== 循环部署 =====
for server in "${SERVERS[@]}"; do
  if [ -n "$server" ]; then
    echo "Deploying to server: $server"
    deploy_to_server "$server"
  else
    echo "⚠️ Skipped empty server entry"
  fi
done

echo "✅ All deployments completed successfully."
exit 0