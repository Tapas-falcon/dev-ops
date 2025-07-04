import re
import argparse

def get_upstream_server_address(config_content, upstream_name):
    # 匹配整个 upstream 块
    pattern = rf'(upstream\s+{re.escape(upstream_name)}\s*{{[^}}]*}})'
    match = re.search(pattern, config_content, re.DOTALL)

    if not match:
        raise ValueError(f"未找到名为 '{upstream_name}' 的 upstream 块")

    upstream_block = match.group(1)

    # 提取 server 行
    # server_match = re.search(r'server\s+([^\s;]+)', upstream_block)
    server_match = re.search(r'\bserver\b\s+([^;\{\}\s]+)', upstream_block)
    if server_match:
        ip_or_host = server_match.group(1).split(':')[0].strip()
        return ip_or_host
    else:
        raise ValueError(f"在 upstream '{upstream_name}' 中未找到 server 地址")

# 示例用法
if __name__ == "__main__":
    # input_file = "./nginx_updated.conf"
    input_file = "/etc/nginx/conf.d/liao_pastel-upstream-serv.conf"
    parser = argparse.ArgumentParser(description="解析 Nginx 配置文件中的 upstream server 地址")    
    parser.add_argument("--server", required=True, help="要查找的 upstream 名称")
    args = parser.parse_args()

    with open(input_file, 'r') as f:
        config = f.read()

    try:
        # 获取当前 server 地址
        server_address = get_upstream_server_address(config, args.server)
        print(f"{server_address}")

    except ValueError as e:
        print(f"❌ Error: {e}")