#!/usr/bin/env python3
"""
MiProxy Gateway - Unix Socket 反向代理服务
将 fnOS 网关的请求代理到 mihomo 的 HTTP 服务
"""

import socket
import threading
import http.client
import os
import sys
from datetime import datetime

# 配置
SOCKET_PATH = os.environ.get('SOCKET_PATH', '/tmp/miproxy.sock')
MIHOMO_HOST = os.environ.get('MIHOMO_HOST', '127.0.0.1')
MIHOMO_PORT = int(os.environ.get('MIHOMO_PORT', '9090'))
UI_DIR = os.environ.get('UI_DIR', '/app/ui')
LOG_FILE = os.environ.get('LOG_FILE', '/tmp/miproxy_gateway.log')

def log(msg):
    """写入日志"""
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except:
        pass

def proxy_request(client_socket, client_address):
    """代理 HTTP 请求到 mihomo"""
    try:
        # 接收请求数据
        request_data = b''
        while True:
            chunk = client_socket.recv(4096)
            request_data += chunk
            if b'\r\n\r\n' in request_data or not chunk:
                break
            if len(request_data) > 65536:
                break

        if not request_data:
            client_socket.close()
            return

        # 解析请求行
        try:
            request_text = request_data.decode('utf-8', errors='ignore')
            lines = request_text.split('\r\n')
            if not lines:
                client_socket.close()
                return
            request_line = lines[0]
            parts = request_line.split(' ')
            if len(parts) < 2:
                client_socket.close()
                return
            method = parts[0]
            path = parts[1]
        except Exception as e:
            log(f"解析请求失败: {e}")
            client_socket.close()
            return

        # 静态文件服务
        static_paths = ['/ui/zashboard/', '/ui/metacubexd/', '/ui/assets/', '/ui/images/']
        if any(path.startswith(p) for p in static_paths):
            serve_static(client_socket, path)
            return

        # API 请求 -> 代理到 mihomo
        proxy_to_mihomo(client_socket, method, path, request_data)

    except Exception as e:
        log(f"处理请求异常: {e}")
    finally:
        try:
            client_socket.close()
        except:
            pass

def serve_static(client_socket, path):
    """服务静态文件"""
    file_path = path[4:] if path.startswith('/ui/') else path
    full_path = os.path.join(UI_DIR, file_path)
    
    # 安全检查：防止路径穿越
    real_ui_dir = os.path.realpath(UI_DIR)
    real_file_path = os.path.realpath(full_path)
    if not real_file_path.startswith(real_ui_dir):
        send_error(client_socket, 403, "Forbidden")
        return
    
    if os.path.isfile(full_path):
        ext = os.path.splitext(full_path)[1].lower()
        mime_types = {
            '.html': 'text/html',
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.woff2': 'font/woff2',
            '.woff': 'font/woff',
            '.ttf': 'font/ttf',
        }
        mime_type = mime_types.get(ext, 'application/octet-stream')
        
        with open(full_path, 'rb') as f:
            content = f.read()
        
        response = f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\nContent-Length: {len(content)}\r\n\r\n".encode() + content
        client_socket.sendall(response)
    else:
        send_error(client_socket, 404, "Not Found")

def proxy_to_mihomo(client_socket, method, path, request_data):
    """代理请求到 mihomo"""
    try:
        conn = http.client.HTTPConnection(MIHOMO_HOST, MIHOMO_PORT, timeout=30)
        conn.request(method, path, body=request_data)
        response = conn.getresponse()
        response_body = response.read()
        
        headers = []
        for name, value in response.getheaders():
            if name.lower() not in ['transfer-encoding', 'connection']:
                headers.append((name, value))
        
        status_line = f"HTTP/1.1 {response.status} {response.reason}\r\n"
        client_socket.sendall(status_line.encode())
        for name, value in headers:
            client_socket.sendall(f"{name}: {value}\r\n".encode())
        client_socket.sendall(b"\r\n")
        client_socket.sendall(response_body)
        conn.close()
    except Exception as e:
        log(f"代理到 mihomo 失败: {e}")
        send_error(client_socket, 502, "Bad Gateway")

def send_error(client_socket, code, message):
    """发送错误响应"""
    body = f"<html><body><h1>{code} {message}</h1></body></html>"
    response = f"HTTP/1.1 {code} {message}\r\nContent-Type: text/html\r\nContent-Length: {len(body)}\r\n\r\n{body}"
    try:
        client_socket.sendall(response.encode())
    except:
        pass

def main():
    """主函数"""
    log(f"Gateway 启动，监听 {SOCKET_PATH}")
    
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
    
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(SOCKET_PATH)
    server.listen(128)
    os.chmod(SOCKET_PATH, 0o777)
    
    log(f"Gateway 已启动，代理到 {MIHOMO_HOST}:{MIHOMO_PORT}")
    
    try:
        while True:
            client_socket, client_address = server.accept()
            thread = threading.Thread(target=proxy_request, args=(client_socket, client_address))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        log("Gateway 停止")
    finally:
        server.close()
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

if __name__ == '__main__':
    main()
