import re
import argparse

def replace_upstream_localhost(config_content, upstream_name, new_ip):
    # 正则表达式匹配整个 upstream 块
    pattern = rf'(upstream\s+{re.escape(upstream_name)}\s*{{[^}}]*}})'
    match = re.search(pattern, config_content, re.DOTALL)

    if not match:
        raise ValueError(f"未找到名为 '{upstream_name}' 的 upstream 块")

    upstream_block = match.group(1)

    # 替换 server localhost:xxx 为 server new_ip:xxx
    def replace_server(match):
        port = match.group(2)
        return f'server {new_ip}:{port}'

    updated_block = re.sub(r'(server\s+)localhost:(\d+)', replace_server, upstream_block)

    # 替换原配置内容中的 upstream 块
    updated_config = config_content.replace(upstream_block, updated_block)
    return updated_config


# 示例用法
if __name__ == "__main__":
    input_file = "/etc/nginx/conf.d/liao_pastel-upstream-serv.conf"
    output_file = "nginx_updated.conf"
    # new_ip = "18.101.190.34"
    parser = argparse.ArgumentParser(description="解析 Nginx 配置文件中的 upstream server 地址")    
    parser.add_argument("--server", required=True, help="要查找的 upstream 名称")
    parser.add_argument("--dns", required=True, help="要更新的服务器地址")
    args = parser.parse_args()

    with open(input_file, 'r') as f:
        config = f.read()

    try:
        updated_config = replace_upstream_localhost(config, args.server, args.dns)
        
        with open(output_file, 'w') as f:
            f.write(updated_config)

        print(f"✅ 成功更新 upstream '{args.server}'，结果已保存到 '{output_file}'")
    except ValueError as e:
        print(f"❌ 错误：{e}")