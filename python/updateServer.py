import re
import argparse

def replace_upstream_localhost(config_content, upstream_name, new_ip):
    # 正则表达式匹配整个 upstream 块
    pattern = rf'(upstream\s+{re.escape(upstream_name)}\s*{{[^}}]*}})'
    match = re.search(pattern, config_content, re.DOTALL)

    if not match:
        raise ValueError(f"未找到名为 '{upstream_name}' 的 upstream 块")

    upstream_block = match.group(1)
    print(f"找到 upstream 块：\n{upstream_block}")

    # 替换 server localhost:xxx 为 server new_ip:xxx

    updated_block = updated_block = re.sub(
        r'server\s+[\w\-\.]+:(\d+);',
        fr'server {new_ip}:\1;',
        upstream_block
    )

    # 替换原配置内容中的 upstream 块
    updated_config = config_content.replace(upstream_block, updated_block)
    return updated_config


# 示例用法
if __name__ == "__main__":
    input_file = "liao_pastel-upstream-serv.conf"
    # input_file = "/etc/nginx/conf.d/liao_pastel-upstream-serv.conf"
    output_file = "nginx_updated.conf"
    # new_ip = "18.101.190.34"
    parser = argparse.ArgumentParser(description="解析 Nginx 配置文件中的 upstream server 地址")    
    parser.add_argument("--server", required=True, help="要查找的 upstream 名称")
    parser.add_argument("--dns", required=True, help="要更新的服务器地址")
    args = parser.parse_args()
    print(f"正在更新 upstream '{args.server}' 的服务器地址为 '{args.dns}'...")
    with open(input_file, 'r') as f:
        config = f.read()

    try:
        updated_config = replace_upstream_localhost(config, args.server, args.dns)
        
        with open(output_file, 'w') as f:
            f.write(updated_config)

        print(f"✅ 成功更新 upstream '{args.server}'，结果已保存到 '{output_file}'")
    except ValueError as e:
        print(f"❌ 错误：{e}")